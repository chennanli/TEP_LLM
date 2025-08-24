# imports
from openai import OpenAI
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import json
import base64
import matplotlib

# Load environment variables first
load_dotenv()
import pandas as pd
import asyncio

matplotlib.use("Agg")

from prompts import EXPLAIN_PROMPT, EXPLAIN_ROOT, SYSTEM_MESSAGE
from multi_llm_client import MultiLLMClient

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load and validate configuration
def load_config(file_path):
    with open(file_path, "r") as config_file:
        config = json.load(config_file)

    # Validate models configuration
    if "models" not in config:
        raise ValueError("Missing 'models' configuration")

    # Check enabled models in both 'models' section and 'lmstudio' section
    enabled_models = [name for name, cfg in config["models"].items() if cfg.get("enabled", False)]

    # Also check LMStudio
    if config.get("lmstudio", {}).get("enabled", False):
        enabled_models.append("lmstudio")

    if not enabled_models:
        raise ValueError("At least one model must be enabled (check 'models' section and 'lmstudio' configuration)")

    # Validate fault_trigger_consecutive_step
    if not isinstance(config["fault_trigger_consecutive_step"], int) or config["fault_trigger_consecutive_step"] < 1:
        raise ValueError(
            f"Invalid fault_trigger_consecutive_step: {config['fault_trigger_consecutive_step']}. "
            f"Must be an integer >= 1."
        )

    # Validate topkfeatures
    if not isinstance(config["topkfeatures"], int) or not (1 <= config["topkfeatures"] <= 20):
        raise ValueError(
            f"Invalid topkfeatures: {config['topkfeatures']}. "
            f"Must be an integer between 1 and 20."
        )

    # Validate prompt
    valid_prompts = ["explain", "explain root"]
    if config["prompt"] not in valid_prompts:
        raise ValueError(f"Invalid prompt: {config['prompt']}. Must be one of {valid_prompts}.")

    return config
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "..", "config.json")
    # Load the configuration
    config = load_config(config_path)

    PROMPT_SELECT = EXPLAIN_PROMPT if config["prompt"] == "explain" else EXPLAIN_ROOT
    fault_trigger_consecutive_step = config["fault_trigger_consecutive_step"]

    # Initialize Multi-LLM Client
    multi_llm_client = MultiLLMClient(config)

    print("✅ Config loaded and Multi-LLM client initialized")
    print(f"📊 Enabled models: {multi_llm_client.enabled_models}")

    # Register shutdown callback to stop simulation when premium models auto-shutdown
    def simulation_shutdown_callback():
        """Callback to stop simulation when premium models are auto-disabled"""
        global _simulation_auto_stopped
        _simulation_auto_stopped = True
        logger.warning("🛡️ TEP simulation auto-stopped due to premium model shutdown")
        # Note: The actual simulation stopping will be handled by the unified control panel
        # This just sets a flag that can be checked via API

    multi_llm_client.register_shutdown_callback(simulation_shutdown_callback)

except Exception as e:
    print("❌ Error loading config:", e)
    raise
# === Live ingestion setup: PCA model and state ===
from typing import Optional, Dict, Any, List
from collections import deque
from fastapi import Body

from model import FaultDetectionModel

# Feature columns to use for PCA (match bridge mapping and frontend columnFilter subset)
FEATURE_COLUMNS: List[str] = [
    "A Feed", "D Feed", "E Feed", "A and C Feed", "Recycle Flow",
    "Reactor Feed Rate", "Reactor Pressure", "Reactor Level", "Reactor Temperature",
    "Purge Rate", "Product Sep Temp", "Product Sep Level", "Product Sep Pressure",
    "Product Sep Underflow", "Stripper Level", "Stripper Pressure", "Stripper Underflow",
    "Stripper Temp", "Stripper Steam Flow", "Compressor Work", "Reactor Coolant Temp",
    "Separator Coolant Temp"
]

# Train PCA model on normal operation (fault0.csv) restricted to FEATURE_COLUMNS
import pandas as _pd

try:
    _train_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "fault0.csv")
    _train_df = _pd.read_csv(_train_path)
    if "time" in _train_df.columns:
        _train_df = _train_df.drop(columns=["time"])  # drop timestamp col if present
    missing_cols = [c for c in FEATURE_COLUMNS if c not in _train_df.columns]
    if missing_cols:
        raise RuntimeError(f"Training data missing expected columns: {missing_cols}")
    _train_df = _train_df[FEATURE_COLUMNS]

    pca_model = FaultDetectionModel(n_components=0.9, alpha=config.get("anomaly_threshold", 0.01))
    pca_model.fit(_train_df)
    print("✅ PCA model trained on normal operation (fault0.csv) with", len(FEATURE_COLUMNS), "features")
except Exception as e:
    print("❌ Failed to initialize PCA model:", e)
    raise

# Live state
LIVE_WINDOW_SIZE = int(config.get("pca_window_size", 20))
consecutive_anomalies_required = int(config.get("fault_trigger_consecutive_step", 6))
# Decimation and LLM rate limit (runtime configurable)
decimation_N = int(config.get("decimation_N", 1))  # 1 = no decimation
llm_min_interval_seconds = int(config.get("llm_min_interval_seconds", 60))
# Feature-shift retrigger controls
feature_shift_jaccard_threshold = float(config.get("feature_shift_jaccard_threshold", 0.6))
feature_shift_min_interval_seconds = int(config.get("feature_shift_min_interval_seconds", 120))

# Cost protection state
_simulation_auto_stopped = False

_consecutive_anomalies = 0
_last_analysis_result: Optional[Dict[str, Any]] = None
_last_llm_trigger_time: float = 0.0
_last_llm_top_features: list[str] = []

# Keep a short history of recent analyses to reduce UI flicker
_analysis_history: deque[Dict[str, Any]] = deque(maxlen=6)

# Buffers
# live_buffer now stores aggregated rows used for PCA/LLM and includes t2/anomaly/time
live_buffer: deque[Dict[str, float]] = deque(maxlen=LIVE_WINDOW_SIZE)
_recent_raw_rows: deque[Dict[str, float]] = deque(maxlen=decimation_N)
_aggregated_count: int = 0

# Helper: build feature comparison text against normal means
import pandas as _pd2

try:
    _stats_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stats", "features_mean_std.csv")
    _normal_stats = _pd2.read_csv(_stats_path).set_index("feature")
except Exception as e:
    print("⚠️ Could not load normal stats for comparison:", e)
    _normal_stats = None


def build_live_feature_comparison(feature_series: Dict[str, List[float]]) -> str:
    """
    Build a compact, explicit comparison for the LLM using the preloaded
    baseline (features_mean_std.csv). Always returns up to 6 lines like:
      1. Reactor Temperature: Fault=120.45 | Normal=120.40 | Δ=0.05 (0.04%) | z=2.10
    If baseline is missing, we still provide the latest values with a note.
    """
    lines: list[str] = ["Top 6 Contributing Features (Fault vs Normal):"]
    idx = 1
    for feat, series in feature_series.items():
        if not series:
            continue
        last_val = float(series[-1])
        if _normal_stats is not None and feat in _normal_stats.index:
            norm_mean = float(_normal_stats.loc[feat, "mean"]) if "mean" in _normal_stats.columns else 0.0
            norm_std = float(_normal_stats.loc[feat, "std"]) if "std" in _normal_stats.columns else 0.0
            delta = last_val - norm_mean
            denom = norm_mean if abs(norm_mean) > 1e-9 else 1e-9
            pct = (delta / denom) * 100.0
            z = delta / (norm_std if norm_std > 1e-12 else 1e9)
            lines.append(f"{idx}. {feat}: Fault={last_val:.3f} | Normal={norm_mean:.3f} | Δ={delta:.3f} ({pct:.2f}%) | z={z:.2f}")
        else:
            lines.append(f"{idx}. {feat}: Fault={last_val:.3f} | Normal=NA (baseline not loaded)")
        idx += 1
    return "\n".join(lines)


# --- Lightweight rotating logs (size-limited) ---
import logging
from logging.handlers import RotatingFileHandler

_logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(_logs_dir, exist_ok=True)
_log_path = os.path.join(_logs_dir, "backend.log")
logger = logging.getLogger("faultexplainer")
logger.setLevel(logging.INFO)
if not logger.handlers:
    _h = RotatingFileHandler(_log_path, maxBytes=1_000_000, backupCount=3)
    _h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(_h)
# ------------------------------------------------
# --- Temporary diagnostics (can be removed later) ---
_diag_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagnostics")
os.makedirs(_diag_dir, exist_ok=True)


# Persistent analysis history file
_history_file = os.path.join(_diag_dir, 'analysis_history.jsonl')
# Markdown history file
_history_md_file = os.path.join(_diag_dir, 'analysis_history.md')
# Per-day Markdown history folder
_history_days_dir = os.path.join(_diag_dir, 'analysis_history')
os.makedirs(_history_days_dir, exist_ok=True)



sse_logger = logging.getLogger("diag.sse")
if not sse_logger.handlers:
    _h_sse = RotatingFileHandler(os.path.join(_diag_dir, "sse.log"), maxBytes=500_000, backupCount=1)
    _h_sse.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    sse_logger.addHandler(_h_sse)
sse_logger.setLevel(logging.INFO)

ingest_logger = logging.getLogger("diag.ingest")
if not ingest_logger.handlers:
    _h_ing = RotatingFileHandler(os.path.join(_diag_dir, "ingest.log"), maxBytes=1_000_000, backupCount=1)
    _h_ing.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    ingest_logger.addHandler(_h_ing)
ingest_logger.setLevel(logging.INFO)
# ---------------------------------------------------



# Initialize FastAPI app
app = FastAPI()

origins = ["http://localhost", "http://localhost:5173", "http://127.0.0.1:5173", "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define request and response models
class MessageRequest(BaseModel):
    data: list[dict[str, str]]
    id: str


class ExplainationRequest(BaseModel):
    data: dict[str, list[float]]
    id: str
    file: str


class Image(BaseModel):
    image: str
    name: str


class MessageResponse(BaseModel):
    content: str
    images: list[Image] = []
    index: int
    id: str


def ChatModelCompletion(
    messages: list[dict[str, str]], msg_id: str, images: list[str] = None, seed: int = 0, model: str = "gpt-4o"
):
    # Set temperature based on the model
    temperature = 0 if (model != "o1-preview" and model != "o1-mini") else 1  # o1-preview only supports temperature=1

    # Filter out 'system' role messages if using 'o1-preview' model
    if model == "o1-preview" or model == "o1-mini":
        messages = [msg for msg in messages if msg['role'] != 'system']

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        temperature=temperature,
        seed=seed,
    )
    index = 0
    for chunk in response:
        if chunk.choices[0].delta.content:
            response_text = chunk.choices[0].delta.content
            response_data = {
                "index": index,
                "content": response_text,
                "id": msg_id,
                "images": images if index == 0 and images else [],
            }
            yield f"data: {json.dumps(response_data)}\n\n"
            index += 1


def get_full_response(messages: list[dict[str, str]], model: str = "gpt-4o", seed: int = 0):
    temperature = 0 if (model != "o1-preview" and model != "o1-mini") else 1
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        seed=seed,
    )
    full_response = ""
    for choice in response.choices:
        full_response += choice.message.content
    return full_response


import os
import pandas as pd

def generate_feature_comparison(request_data, file_path):
    """
    Build a compact "Top 6 Contributing Features (Fault vs Normal)" comparison string
    for the Multi‑LLM view. Uses the latest value from request_data and compares to
    the precomputed normal means/std in stats/features_mean_std.csv.

    Returns a string like:
      Top 6 Contributing Features (Fault vs Normal):
      1. Reactor Temperature: Fault=120.45 | Normal=120.40 | Δ=0.05 (0.04%) | z=2.10
    """
    try:
        # Load normal baseline
        current_dir = os.path.dirname(os.path.abspath(__file__))
        stats_file_path = os.path.join(current_dir, "stats", "features_mean_std.csv")
        normal_df = pd.read_csv(stats_file_path).set_index("feature")

        # Extract last values from request_data
        rows = []
        for feature, series in (request_data or {}).items():
            try:
                if series is None or len(series) == 0:
                    continue
                last_val = float(series[-1])
                rows.append((feature, last_val))
            except Exception:
                continue

        if not rows:
            return "Top 6 Contributing Features (Fault vs Normal):\n(no features provided)"

        # Compute deltas vs normal mean for features present in baseline
        scored = []
        for feat, val in rows:
            if feat in normal_df.index:
                norm_mean = float(normal_df.loc[feat, "mean"]) if "mean" in normal_df.columns else 0.0
                norm_std = float(normal_df.loc[feat, "std"]) if "std" in normal_df.columns else 0.0
                delta = val - norm_mean
                denom = norm_mean if abs(norm_mean) > 1e-9 else 1e-9
                pct = (delta / denom) * 100.0
                z = delta / (norm_std if norm_std > 1e-12 else 1e9)
                score = abs(pct)  # rank by magnitude of percent change
                scored.append((feat, val, norm_mean, delta, pct, z, score))
            else:
                # Keep but mark missing baseline
                scored.append((feat, val, None, None, None, None, -1))

        # Select top 6 by score (>=0); fall back to any 6 if baseline missing
        with_scores = [s for s in scored if s[-1] >= 0]
        top = sorted(with_scores, key=lambda x: x[-1], reverse=True)[:6]
        if len(top) < 6:
            # pad with remaining entries (baseline unknown)
            remain = [s for s in scored if s not in top]
            top += remain[: 6 - len(top)]

        lines = ["Top 6 Contributing Features (Fault vs Normal):"]
        idx = 1
        for feat, val, norm_mean, delta, pct, z, _ in top:
            if norm_mean is not None:
                lines.append(f"{idx}. {feat}: Fault={val:.3f} | Normal={norm_mean:.3f} | Δ={delta:.3f} ({pct:.2f}%) | z={z:.2f}")
            else:
                lines.append(f"{idx}. {feat}: Fault={val:.3f} | Normal=NA (baseline not loaded)")
            idx += 1
        return "\n".join(lines)
    except Exception as e:
        # Fail safe: minimal message so LLMs still get some context
        return f"Top 6 Contributing Features (Fault vs Normal):\n(error building comparison: {e})"
# === Live ingestion endpoints ===
class IngestRequest(BaseModel):
    data_point: Dict[str, float]  # keys must include FEATURE_COLUMNS subset; may include time/step
    id: Optional[str] = None

@app.post("/ingest")
async def ingest_live_point(req: IngestRequest):
    global _consecutive_anomalies, _last_analysis_result, _recent_raw_rows, _aggregated_count, _last_llm_trigger_time, _last_llm_top_features
    try:
        # Keep only required feature columns for PCA
        raw_row = {k: float(v) for k, v in req.data_point.items() if k in FEATURE_COLUMNS}
        if len(raw_row) != len(FEATURE_COLUMNS):
            ingest_logger.info("ignored missing_features present=%s", list(raw_row.keys()))
            return {"status": "ignored", "reason": "missing_features", "present": list(raw_row.keys())}

        # Decimation/aggregation: collect raw rows and every N rows compute their mean
        _recent_raw_rows.append(raw_row)
        ingest_logger.info("row have=%d need=%d", len(_recent_raw_rows), decimation_N)
        if len(_recent_raw_rows) < max(1, decimation_N):
            # Not enough for an aggregated point yet
            return {"status": "ok", "aggregating": True, "have": len(_recent_raw_rows), "need": decimation_N}

        import numpy as _np
        import pandas as _pd3
        arr = _np.array([[r[c] for c in FEATURE_COLUMNS] for r in list(_recent_raw_rows)])
        mean_vec = arr.mean(axis=0)
        row = {c: float(v) for c, v in zip(FEATURE_COLUMNS, mean_vec)}
        _recent_raw_rows.clear()  # reset for next aggregation window
        _aggregated_count += 1

        df = _pd3.DataFrame([row])
        t2, is_anom = pca_model.process_data_point(df)

        # Maintain live buffer for context (store t2/anomaly too for streaming)
        row_with_stats = {**row,
                           "t2_stat": float(t2),
                           "anomaly": bool(is_anom),
                           "time": _aggregated_count,
                           "threshold": float(pca_model.t2_threshold)}
        live_buffer.append(row_with_stats)

        # Count consecutive anomalies
        if is_anom:
            _consecutive_anomalies += 1
        else:
            _consecutive_anomalies = 0

        result: Dict[str, Any] = {
            "t2_stat": t2,
            "anomaly": bool(is_anom),
            "threshold": float(pca_model.t2_threshold),
            "consecutive_anomalies": _consecutive_anomalies,
            "aggregated_index": _aggregated_count,
        }
        ingest_logger.info("aggregated idx=%d t2=%.4f anomaly=%s", _aggregated_count, t2, bool(is_anom))

        # LLM trigger gating: need enough anomalies, enough context, and respect min interval
        import time as _time
        can_rate_limit = (_time.time() - _last_llm_trigger_time) >= llm_min_interval_seconds
        enough_context = len(live_buffer) >= max(5, int(LIVE_WINDOW_SIZE/2))  # relax for quicker triggers
        if is_anom and _consecutive_anomalies >= min(1, consecutive_anomalies_required) and enough_context and can_rate_limit:
            buf_df = _pd3.DataFrame(list(live_buffer))
            deltas = (buf_df.iloc[-1][FEATURE_COLUMNS] - buf_df[FEATURE_COLUMNS].mean()).abs().sort_values(ascending=False)
            topk = int(config.get("topkfeatures", 6))
            top_features = list(deltas.index[:topk])

            # Feature-shift retrigger criteria: compare with last trigger's top features
            def jaccard(a: list[str], b: list[str]) -> float:
                sa, sb = set(a), set(b)
                return len(sa & sb) / max(1, len(sa | sb))

            now = _time.time()
            elapsed = now - _last_llm_trigger_time
            allow_feature_shift = (
                elapsed >= feature_shift_min_interval_seconds and
                (not _last_llm_top_features or jaccard(top_features, _last_llm_top_features) < feature_shift_jaccard_threshold)
            )

            if not can_rate_limit and not allow_feature_shift:
                result["llm"] = {"status": "not_triggered"}
            else:
                feature_series = {feat: buf_df[feat].tail(LIVE_WINDOW_SIZE).tolist() for feat in top_features}
                comparison = build_live_feature_comparison(feature_series)
                user_prompt = f"{PROMPT_SELECT}\n\nHere are the top six features with values during the fault and normal operation:\n{comparison}"

                # 🔧 FIX: Run LLM analysis in background to avoid blocking /stream endpoint
                import asyncio
                async def background_llm_analysis():
                    try:
                        logger.info("🤖 Starting background LLM analysis...")
                        llm_results = await multi_llm_client.get_analysis_from_all_models(
                            system_message=SYSTEM_MESSAGE,
                            user_prompt=user_prompt,
                        )
                        formatted = multi_llm_client.format_comparative_results(results=llm_results, feature_comparison=comparison)
                        global _last_analysis_result
                        _last_analysis_result = formatted

                        # build a snapshot with an id for persistence
                        import time as _time
                        snap = {"id": int(_time.time()*1000), "time": now, **formatted}
                        _analysis_history.append(snap)
                        # persist to JSONL
                        try:
                            with open(_history_file, 'a') as f:
                                import json as _json
                                f.write(_json.dumps(snap) + "\n")
                            # also write Markdown lines (append to cumulative + daily file)
                            try:
                                import time as _time
                                ts = snap.get("timestamp") or _time.strftime("%Y-%m-%d %H:%M:%S")
                                md = f"\n## {ts} (id: {snap.get('id')})\n\n" + (snap.get("feature_analysis") or "") + "\n"
                                with open(_history_md_file, 'a') as mf:
                                    mf.write(md)
                                day_name = _time.strftime("%Y-%m-%d")
                                day_path = os.path.join(_history_days_dir, f"{day_name}.md")
                                with open(day_path, 'a') as df:
                                    df.write(md)
                            except Exception as _em:
                                logger.warning("failed to append md history: %s", _em)
                        except Exception as _e:
                            logger.warning("failed to append history file: %s", _e)
                        logger.info("✅ Background LLM analysis completed")
                    except Exception as e:
                        logger.error("❌ Background LLM analysis failed: %s", e)

                # Start background task without waiting
                asyncio.create_task(background_llm_analysis())

                result["llm"] = {"status": "triggered", "top_features": top_features}
                _consecutive_anomalies = 0
                _last_llm_trigger_time = now
                _last_llm_top_features = top_features
        else:
            result["llm"] = {"status": "not_triggered"}

        return result
    except Exception as e:
        logger.exception("ingest error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stream")
async def stream_live_points():
    """Server-Sent Events stream of the latest aggregated live point.
    Previous implementation yielded only when len(live_buffer) grew, which stalls
    once the deque reaches its maxlen. Here we track the 'time' field of the last
    row (which equals aggregated_count) and emit whenever it changes.
    """
    async def event_generator():
        import asyncio as _asyncio
        last_time_seen = None
        sse_logger.info("client connected")
        try:
            while True:
                try:
                    if live_buffer:
                        row = live_buffer[-1]  # has t2_stat, anomaly, threshold, time
                        current_time_val = row.get("time")
                        if current_time_val != last_time_seen:
                            payload = json.dumps(row)
                            sse_logger.info("emit time=%s t2=%.4f anomaly=%s", current_time_val, row.get("t2_stat"), row.get("anomaly"))
                            yield f"data: {payload}\n\n"
                            last_time_seen = current_time_val
                    await _asyncio.sleep(0.5)
                except Exception as e:
                    sse_logger.warning("generator loop error: %s", e)
                    break
        finally:
            sse_logger.info("client disconnected")
    # Add SSE-friendly headers (and CORS for dev)
    resp = StreamingResponse(event_generator(), media_type="text/event-stream")
    resp.headers["Cache-Control"] = "no-cache"
    resp.headers["X-Accel-Buffering"] = "no"
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


@app.post("/config/runtime")
async def update_runtime_config(payload: Dict[str, Any] = Body(...)):
    global LIVE_WINDOW_SIZE, consecutive_anomalies_required, decimation_N, llm_min_interval_seconds, live_buffer, _recent_raw_rows, feature_shift_min_interval_seconds, feature_shift_jaccard_threshold
    changes = {}
    # Update PCA window size and resize live buffer conservatively (preserve latest data)
    if "pca_window_size" in payload:
        LIVE_WINDOW_SIZE = int(payload["pca_window_size"])
        # Rebuild live_buffer to reflect new window size while preserving content
        try:
            prev = list(live_buffer)
        except Exception:
            prev = []
        live_buffer = deque(prev[-LIVE_WINDOW_SIZE:], maxlen=LIVE_WINDOW_SIZE)
        changes["pca_window_size"] = LIVE_WINDOW_SIZE
    # Update consecutive anomalies threshold
    if "fault_trigger_consecutive_step" in payload:
        consecutive_anomalies_required = int(payload["fault_trigger_consecutive_step"])
        changes["fault_trigger_consecutive_step"] = consecutive_anomalies_required
    # Update decimation and resize recent raw rows buffer to avoid starvation when N>1
    if "decimation_N" in payload:
        decimation_N = max(1, int(payload["decimation_N"]))
        try:
            prev_raw = list(_recent_raw_rows)
        except Exception:
            prev_raw = []
        _recent_raw_rows = deque(prev_raw[-decimation_N+1 if decimation_N>1 else 0:], maxlen=decimation_N)
        changes["decimation_N"] = decimation_N
    # Update LLM rate limit
    if "llm_min_interval_seconds" in payload:
        llm_min_interval_seconds = max(0, int(payload["llm_min_interval_seconds"]))
        changes["llm_min_interval_seconds"] = llm_min_interval_seconds
    # Feature shift trigger knobs
    if "feature_shift_jaccard_threshold" in payload:
        feature_shift_jaccard_threshold = float(payload["feature_shift_jaccard_threshold"])
        changes["feature_shift_jaccard_threshold"] = feature_shift_jaccard_threshold
    if "feature_shift_min_interval_seconds" in payload:
        feature_shift_min_interval_seconds = int(payload["feature_shift_min_interval_seconds"])
        changes["feature_shift_min_interval_seconds"] = feature_shift_min_interval_seconds
    return {"status": "ok", "updated": changes}

@app.post("/config/baseline/reload")

@app.get("/config/baseline/reload")
async def reload_baseline_get():
    # Convenience GET to avoid Body disturbed errors from double-read clients
    return await reload_baseline(payload=None)

async def reload_baseline(payload: Dict[str, Any] = Body(None)):
    """Reload baseline means/std from stats/features_mean_std.csv (optionally a specific file).
    Returns the number of features loaded. Does not require server restart.
    """
    try:
        global _normal_stats
        stats_name = None
        if payload and isinstance(payload, dict):
            stats_name = payload.get("filename")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "stats", stats_name) if stats_name else os.path.join(base_dir, "stats", "features_mean_std.csv")
        df = _pd2.read_csv(path).set_index("feature")
        _normal_stats = df
        return {"status": "ok", "filename": os.path.basename(path), "features": int(len(_normal_stats))}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/metrics")
def metrics():
    return {
        "aggregated_count": _aggregated_count,
        "live_buffer": len(live_buffer),
        "decimation_N": decimation_N,
        "pca_window": LIVE_WINDOW_SIZE,
        "consecutive_anomalies_required": consecutive_anomalies_required,
        "llm_min_interval_seconds": llm_min_interval_seconds,
        "baseline_features": (int(len(_normal_stats)) if _normal_stats is not None else 0),
    }

@app.get("/preview/top6")
async def preview_top6():
    """Compute a quick top-6 comparison from the current live_buffer without triggering LLM.
    Returns { text, features } where text is the Top 6... block.
    """
    try:
        import pandas as _pd3
        if len(live_buffer) == 0:
            return {"status":"empty","text":"Top 6 Contributing Features (Fault vs Normal):\n(no live data)","features":[]}
        buf_df = _pd3.DataFrame(list(live_buffer))
        deltas = (buf_df.iloc[-1][FEATURE_COLUMNS] - buf_df[FEATURE_COLUMNS].mean()).abs().sort_values(ascending=False)
        topk = int(config.get("topkfeatures", 6))
        top_features = list(deltas.index[:topk])
        series = {feat: buf_df[feat].tail(LIVE_WINDOW_SIZE).tolist() for feat in top_features}
        text = build_live_feature_comparison(series)
        return {"status":"ok","text": text, "features": top_features}
    except Exception as e:
        return {"status":"error","error": str(e)}


@app.post("/config/alpha")
async def update_alpha(payload: Dict[str, Any] = Body(...)):
    # Update anomaly_threshold (alpha) and recompute T2 threshold without retrain
    try:
        new_alpha = float(payload.get("anomaly_threshold"))
        if not (0 < new_alpha < 1):
            raise ValueError("alpha must be between 0 and 1")
        pca_model.alpha = new_alpha
        pca_model.set_t2_threshold()
        return {"status": "ok", "alpha": new_alpha, "t2_threshold": float(pca_model.t2_threshold)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/retrain")
async def retrain_pca(payload: Dict[str, Any] = Body(...)):
    """Retrain PCA model with new training data."""
    try:
        import pandas as pd
        from model import FaultDetectionModel

        # Get training file path
        training_file = payload.get("training_file", "live_fault0.csv")
        training_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", training_file)

        if not os.path.exists(training_path):
            raise ValueError(f"Training file not found: {training_path}")

        # Load new training data
        train_df = pd.read_csv(training_path)
        if "time" in train_df.columns:
            train_df = train_df.drop(columns=["time"])

        # Validate columns
        missing_cols = [c for c in FEATURE_COLUMNS if c not in train_df.columns]
        if missing_cols:
            raise ValueError(f"Training data missing expected columns: {missing_cols}")

        train_df = train_df[FEATURE_COLUMNS]

        # Create new PCA model
        global pca_model
        new_pca_model = FaultDetectionModel(n_components=0.9, alpha=config.get("anomaly_threshold", 0.01))
        new_pca_model.fit(train_df)

        # Replace global model
        pca_model = new_pca_model

        print(f"✅ PCA model retrained with {len(train_df)} data points from {training_file}")

        return {
            "status": "success",
            "message": f"PCA model retrained with {len(train_df)} data points",
            "n_components": int(pca_model.pca.n_components_),
            "t2_threshold": float(pca_model.t2_threshold),
            "training_file": training_file
        }

    except Exception as e:
        print(f"❌ PCA retrain failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/status")
def status():
    return {"running": True}

@app.get("/analysis/history")
def analysis_history(limit: int = 10):
    """Return last N items (from disk if available, else memory)."""
    items = []
    try:
        if os.path.exists(_history_file):
            # read the last N lines efficiently
            import io
            with open(_history_file, 'rb') as f:
                f.seek(0, os.SEEK_END)
                size = f.tell()
                block = 4096
                buf = b""
                lines = []
                while size > 0 and len(lines) <= limit:
                    step = block if size - block > 0 else size
                    size -= step
                    f.seek(size)
                    buf = f.read(step) + buf
                    lines = buf.split(b"\n")
                raw = [x for x in lines if x.strip()]
                import json as _json
                items = [_json.loads(line) for line in raw[-limit:]]
        else:
            items = list(_analysis_history)[-limit:]
    except Exception as e:
        return {"status":"error","error":str(e),"items":list(_analysis_history)[-limit:]}
    return {"items": items}

@app.get("/analysis/item/{item_id}")
def analysis_item(item_id: int):
    try:
        # first check memory
        for it in reversed(_analysis_history):
            if int(it.get("id", 0)) == int(item_id):
                return it
        # then scan file
        if os.path.exists(_history_file):
            import json as _json
            with open(_history_file, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    obj = _json.loads(line)
                    if int(obj.get("id",0)) == int(item_id):
                        return obj
    except Exception as e:
        return {"status":"error","error":str(e)}
    return {"status":"not_found"}

    return {
        "running": True,
        "aggregated_count": _aggregated_count,
        "live_buffer": len(live_buffer),
        "t2_threshold": float(pca_model.t2_threshold),
        "models": multi_llm_client.enabled_models,
    }

@app.get("/last_analysis")
def last_analysis():
    if _last_analysis_result is None:
        return {"status": "none"}
    return _last_analysis_result

# === Model Control Endpoints ===

@app.post("/models/toggle")
async def toggle_model(payload: dict):
    """Toggle a model on/off at runtime"""
    try:
        model_name = payload.get("model_name")
        enabled = payload.get("enabled", False)

        if not model_name:
            raise HTTPException(status_code=400, detail="model_name is required")

        result = multi_llm_client.toggle_model(model_name, enabled)

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except Exception as e:
        logger.exception("Model toggle error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models/status")
def get_model_status():
    """Get detailed status of all models"""
    try:
        return multi_llm_client.get_model_status()
    except Exception as e:
        logger.exception("Model status error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/models/reset_usage")
def reset_usage_stats():
    """Reset usage statistics"""
    try:
        return multi_llm_client.reset_usage_stats()
    except Exception as e:
        logger.exception("Reset usage error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

# === Cost Protection Endpoints ===

@app.get("/session/status")
def get_session_status():
    """Get current premium session status and remaining time"""
    try:
        return multi_llm_client.get_session_status()
    except Exception as e:
        logger.exception("Session status error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/session/extend")
async def extend_session(payload: dict):
    """Extend premium session by additional minutes"""
    try:
        additional_minutes = payload.get("additional_minutes", 30)
        result = multi_llm_client.extend_premium_session(additional_minutes)

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except Exception as e:
        logger.exception("Session extend error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/session/shutdown")
def force_shutdown_premium():
    """Manually force shutdown of premium models"""
    try:
        return multi_llm_client.force_shutdown_premium()
    except Exception as e:
        logger.exception("Force shutdown error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/session/cancel_auto_shutdown")
def cancel_auto_shutdown():
    """Cancel the auto-shutdown timer"""
    try:
        multi_llm_client.cancel_auto_shutdown()
        return {"success": True, "message": "Auto-shutdown cancelled"}
    except Exception as e:
        logger.exception("Cancel auto-shutdown error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/session/set_auto_shutdown")
async def set_auto_shutdown(payload: dict):
    """Enable or disable auto-shutdown feature"""
    try:
        enabled = payload.get("enabled", True)
        multi_llm_client.set_auto_shutdown_enabled(enabled)
        return {"success": True, "auto_shutdown_enabled": enabled}
    except Exception as e:
        logger.exception("Set auto-shutdown error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/simulation/auto_stop_status")
def get_simulation_auto_stop_status():
    """Check if simulation should be auto-stopped due to cost protection"""
    global _simulation_auto_stopped
    return {
        "auto_stopped": _simulation_auto_stopped,
        "message": "Simulation auto-stopped due to premium model shutdown" if _simulation_auto_stopped else "Simulation running normally"
    }

@app.post("/simulation/reset_auto_stop")
def reset_simulation_auto_stop():
    """Reset the simulation auto-stop flag"""
    global _simulation_auto_stopped
    _simulation_auto_stopped = False
    return {"success": True, "message": "Auto-stop flag reset"}


    # Combine all results into a single string
    return "The top feature changes are\n" + "\n".join(comparison_results)


# Health check endpoints
@app.get("/")
def read_root():
    return {"message": "FaultExplainer Multi-LLM API", "status": "running"}

@app.get("/health/lmstudio")
async def check_lmstudio_health():
    """Check LMStudio health status"""
    try:
        import requests

        # Quick connection test
        response = requests.get("http://127.0.0.1:1234/v1/models", timeout=5)
        if response.status_code == 200:
            models = response.json().get("data", [])
            return {
                "status": "healthy",
                "models_available": len(models),
                "models": [m["id"] for m in models[:3]]  # Show first 3 models
            }
        else:
            return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}

    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.post("/restart/lmstudio")
async def restart_lmstudio_suggestion():
    """Provide LMStudio restart suggestions"""
    return {
        "message": "LMStudio restart required",
        "steps": [
            "1. Open LMStudio application",
            "2. Go to Server tab",
            "3. Stop current server if running",
            "4. Select model and click 'Start Server'",
            "5. Ensure server runs on 127.0.0.1:1234"
        ],
        "health_check_url": "/health/lmstudio"
    }

@app.post("/explain", response_model=None)
async def explain(request: ExplainationRequest):
    try:
        logger.info(f"explain start id=%s file=%s models=%s", request.id, request.file, multi_llm_client.enabled_models)

        # Generate feature comparison
        comparison_result = generate_feature_comparison(request.data, request.file)
        user_prompt = f"{PROMPT_SELECT}\n{comparison_result}"

        logger.info("feature comparison prepared")

        # Extract fault features for RAG enhancement
        fault_features = []
        fault_data = {"file": request.file, "id": request.id}

        # Try to extract feature names from the comparison result
        try:
            # Simple extraction of feature names from comparison text
            import re
            feature_matches = re.findall(r'Feature:\s*([^,\n]+)', comparison_result)
            fault_features = [f.strip() for f in feature_matches[:6]]  # Top 6 features
        except Exception as e:
            logger.warning(f"Could not extract fault features: {str(e)}")

        # Get analysis from all enabled models with RAG enhancement
        llm_results = await multi_llm_client.get_analysis_from_all_models(
            system_message=SYSTEM_MESSAGE,
            user_prompt=user_prompt,
            fault_features=fault_features,
            fault_data=fault_data
        )

        # Format comparative results
        formatted_results = multi_llm_client.format_comparative_results(
            results=llm_results,
            feature_comparison=comparison_result
        )

        logger.info("multi-llm analysis completed id=%s", request.id)

        # Return JSON response instead of streaming for comparative display
        return JSONResponse(content=formatted_results)

    except Exception as e:
        logger.exception("explain endpoint error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/send_message", response_model=MessageResponse)
async def send_message(request: MessageRequest):
    try:
        return StreamingResponse(
            ChatModelCompletion(messages=request.data, msg_id=f"reply-{request.id}"),
            media_type="text/event-stream",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# RAG Knowledge Base Management Endpoints

@app.post("/rag/initialize")
async def initialize_rag_knowledge_base(force_reindex: bool = False):
    """Initialize or update the RAG knowledge base"""
    try:
        result = multi_llm_client.initialize_knowledge_base(force_reindex=force_reindex)
        return result
    except Exception as e:
        logger.exception("RAG initialization error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rag/status")
async def get_rag_status():
    """Get RAG system status and statistics"""
    try:
        status = multi_llm_client.get_rag_status()
        return status
    except Exception as e:
        logger.exception("RAG status error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rag/search")
async def search_knowledge_base(query: str, n_results: int = 5):
    """Search the knowledge base for relevant information"""
    try:
        results = multi_llm_client.search_knowledge_base(query, n_results=n_results)
        return results
    except Exception as e:
        logger.exception("RAG search error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("🚀 Starting FastAPI server...")
    try:
        import uvicorn
        print("📡 Uvicorn imported successfully")
        print("🌐 Starting server on http://0.0.0.0:8001 (Integration System)")
        uvicorn.run(app, host="0.0.0.0", port=8001)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()