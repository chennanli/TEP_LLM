# Live Stream Integration Issue – Summary and Hand‑off Prompt

Date: 2025-08-09
Environment: macOS, Python venv `tep_env`
Project root: /Users/chennanli/Desktop/LLM_Project/TE

## TL;DR
- Backend (FastAPI) is up and healthy. `/` and `/status` respond.
- Frontend (Vite React) runs; Monitoring set to “Live (stream)”. Charts appear but do not move.
- SSE stream `/stream` yields exactly one event, then no more (while the user expects 1s cadence in Demo mode).
- `/status` shows `aggregated_count: 1`, `live_buffer: 1` even after minutes.
- Unified Control Panel shows Demo (1s), Preset Demo, all components Running, but its Data Points counters are also stuck at 1 (Raw:1 / PCA:1 / LLM:1).
- LLM never triggers: `/last_analysis` returns `{"status":"none"}`. Backend log file remains empty (it only logs explain events).
- User changed IDV‑1 and IDV‑4 to 1.0, but still no continuous data arrival.

Conclusion: The data producer loop is not continuously feeding the backend; only a single point reaches `/ingest`. Likely the unified control panel’s simulation loop is stuck at step 1 (exception, blocking call, or thread not progressing).

## What was run (key commands and outputs)

- venv active: `source tep_env/bin/activate`
- Backend: `python external_repos/FaultExplainer-main/backend/app.py`
  - `/` → `{ "message":"FaultExplainer Multi-LLM API", "status":"running" }`
  - `/status` → `{ running:true, aggregated_count:0→1, live_buffer:0→1, t2_threshold:26.088..., models:["claude"] }`
- Frontend dev: `npm run dev` in `external_repos/FaultExplainer-main/frontend`; UI reachable at http://localhost:5173
- Stream sanity: `curl -N http://localhost:8000/stream` → one line like:
  - `data: { ..., "t2_stat": 10.7051, "anomaly": false, "time": 1, "threshold": 26.0881 }`
- Unified Control Panel: `python unified_tep_control_panel.py` at http://localhost:9001
  - UI shows: Speed Demo (1s), Preset Demo, TEP/Backend/Frontend Running, Data Points Raw:1, PCA:1, LLM:1
- Backend runtime lowered for fast triggers:
  - `POST /config/runtime` with `{pca_window_size:5, decimation_N:1, fault_trigger_consecutive_step:1, llm_min_interval_seconds:0, feature_shift_min_interval_seconds:0}` → status ok
  - `POST /config/alpha` with `{anomaly_threshold:0.1}` → status ok, new `t2_threshold` returned
- `/last_analysis` → `{ "status":"none" }`
- Backend logs: `tail -f external_repos/FaultExplainer-main/backend/logs/backend.log` → empty (expected until first LLM run)

## Symptoms
- Monitoring page shows static plots in Live mode. No continuous updates.
- Backend aggregated_count does not increase beyond 1.
- SSE `/stream` emits exactly one event, then stalls.
- Unified control panel step counter/data counters stuck at 1 despite Demo (1s) speed.
- Changing IDV‑1 and IDV‑4 to 1.0 did not make data arrive continuously nor trigger LLM.

## What we changed earlier (relevant)
- Frontend: fixed Live anomaly boolean/string mismatch; lowered `postFaultThreshold` to 2.
- Backend: added `/status`, rotating logs, relaxed gating; made runtime config adjustable at `/config/runtime` and `/config/alpha`.
- None of these affect whether the simulator produces continuous points—only how backend reacts when points arrive.

## Hypotheses for why data is stuck at 1
1) Unified simulator thread not progressing (simulation_loop stuck) due to an exception in `setup_tep2py()` or `simulation_step()`; control panel UI still shows Running but loop isn’t iterating.
2) `send_to_ingest()` blocking on `requests.post(..., timeout=60)` causing long stalls; but even after minutes, aggregates stayed at 1.
3) Speed switch to Demo not applied to the running bridge instance (should set `step_interval_seconds=1`); UI shows Demo, but actual loop value might differ.
4) CSV isn’t updating (no writes to `data/live_tep_data.csv`) — indicates loop not running.

## High‑signal places in code
- `unified_tep_control_panel.py`:
  - `TEPDataBridge.simulation_loop` (sends to `/ingest`, then `time.sleep(self.step_interval_seconds)`).
  - `send_to_ingest()` posts to backend.
  - `setup_tep2py()` may fail and set `self.tep2py=None`.
  - `/api/speed` handler sets `self.bridge.step_interval_seconds = 1` for demo.
- Backend: `/ingest` aggregates and streams via `/stream`; `/status` exposes `aggregated_count`.

## Concrete next debug steps (suggested to the next AI)
1) Inspect unified panel process logs (where it runs). Look for "❌ TEP simulation step failed" lines or tracebacks. Add prints in `simulation_loop` before and after `send_to_ingest` to verify loop iterations.
2) Query panel status: `curl http://localhost:9001/api/status` to see `current_step` and `step_interval_seconds`. Does `current_step` increase?
3) CSV growth check: `ls -l data/live_tep_data.csv` and `tail -f data/live_tep_data.csv`. Is the file growing?
4) Directly run the simple bridge path to bypass unified panel logic:
   - Terminal A: `python real_tep_simulator.py` (producer)
   - Terminal B: `python tep_faultexplainer_bridge.py` (posts to `/ingest`)
   - Confirm `/status` aggregated_count climbs and `/stream` emits continuously.
5) Validate tep2py import: `python -c "import sys; sys.path.insert(0,'external_repos/tep2py-master'); import tep2py; print('ok')"`
6) If `requests.post` is blocking, reduce timeout and log each POST; or post asynchronously.

---

# Hand‑off Prompt for Another AI

You are helping diagnose a live data pipeline issue between a dynamic TEP simulator and a FaultExplainer backend/frontend.

Context:
- OS: macOS. Python venv: `tep_env`.
- Backend: FastAPI at http://localhost:8000 (healthy). SSE `/stream` and `/status` available.
- Frontend: React (Vite) at http://localhost:5173. Monitoring page set to “Live (stream)”.
- Unified control panel at http://localhost:9001 starts a TEP loop and posts to `/ingest` each step.

Observed behavior:
- `/status` returns `aggregated_count: 1`, `live_buffer: 1` and stays there even after many minutes.
- `/stream` emits exactly one event (with `time:1`) then no further events.
- Frontend Monitoring charts do not update in Live mode.
- Unified control panel shows Speed: Demo (1s), Preset: Demo, components Running, but its Data Points counters are stuck at Raw:1 / PCA:1 / LLM:1.
- IDV‑1 and IDV‑4 were set to 1.0; no effect on continuous data arrival.
- `/last_analysis` is `{"status":"none"}` (no LLM triggered).
- Backend runtime was relaxed (`pca_window_size=5`, `decimation_N=1`, `fault_trigger_consecutive_step=1`, `llm_min_interval_seconds=0`, `feature_shift_min_interval_seconds=0`) and alpha increased to 0.1 — confirmed via API responses.

Key code (unified_tep_control_panel.py):
- `TEPDataBridge.simulation_loop` generates data, calls `save_data_for_faultexplainer`, then `send_to_ingest`, then sleeps `step_interval_seconds`.
- `/api/speed` sets `self.bridge.step_interval_seconds=1` in Demo.
- `setup_tep2py()` loads `external_repos/tep2py-master`; on failure sets `self.tep2py=None`.

Goal:
- Determine why `simulation_loop` is not producing more than one data point (step stuck at 1), resulting in no continuous stream to `/ingest` and static Monitoring charts.

Please:
1) Run `curl http://localhost:9001/api/status` and report `current_step` and `step_interval_seconds`. Is `current_step` increasing?
2) Check the console logs of `unified_tep_control_panel.py` for exceptions (look for "❌ TEP simulation step failed"). If missing, instrument the loop with prints to confirm iterations.
3) Verify whether `data/live_tep_data.csv` is growing: `tail -f data/live_tep_data.csv`.
4) Confirm tep2py import works: `python -c "import sys; sys.path.insert(0,'external_repos/tep2py-master'); import tep2py; print('ok')"`.
5) Temporarily bypass unified panel and test the simpler path:
   - `python real_tep_simulator.py` and `python tep_faultexplainer_bridge.py` in separate venv terminals.
   - Expect `/status.aggregated_count` to increment and `/stream` to emit continuously.
6) If `/ingest` POSTs are blocking, reduce timeout to 5s and log before/after each POST to confirm loop progress.
7) Once continuous ingestion is confirmed, re-check `/last_analysis` and the Multi‑LLM page.

Deliverables:
- Root cause of why only a single point reaches the backend (stuck sim loop vs blocked POST vs tep2py failure).
- Minimal fix (code or config) to restore continuous data generation and ingestion.
- Verification: `aggregated_count` increases steadily; Monitoring charts update; at least one LLM analysis runs (non-"none" `/last_analysis`).



## Update – 2025-08-09 (later)

Observed by user:
- Sometimes backend not running (curl /status empty; lsof -i :8000 empty)
- When backend is up: /status stays {aggregated_count:1, live_buffer:1}; /stream only first row (time:1)
- Control Panel /api/status: current_step increases in other runs (e.g., 1→8→103) with last_ingest_ok:true and csv_rows increasing; but backend counters remain 1
- Frontend on Live shows flat plots

Interpretation:
- Simulator loop is iterating and posting; backend is either down or accepting posts but not aggregating (returns HTTP 200 with status:"ignored" or aggregating:true). That keeps aggregated_count stuck at 1, so /stream never advances.

Minimal working recipe to verify:
1) Terminal A (venv):
   - source tep_env/bin/activate
   - cd external_repos/FaultExplainer-main/backend
   - python app.py
   - Verify: curl -s http://localhost:8000/status | python -m json.tool → aggregated_count:0
2) Terminal B (venv):
   - python unified_tep_control_panel.py
   - Browser http://localhost:9001 → Start TEP Simulation → Demo (1s) (do NOT Start Bridge)
3) Check:
   - curl -s http://localhost:9001/api/status | python -m json.tool → current_step increases
   - curl -s http://localhost:8000/status | python -m json.tool → aggregated_count increases

If aggregated_count stays 1:
- Force runtime: POST /config/runtime with {pca_window_size:5, decimation_N:1, fault_trigger_consecutive_step:1, llm_min_interval_seconds:0, feature_shift_min_interval_seconds:0}
- Capture one /ingest response (panel prints JSON). If {status:"ignored"}, fix mapper names to match all 22 FEATURE_COLUMNS exactly; if {aggregating:true}, ensure decimation_N=1.

Hand-off prompt (compressed):
Diagnose why backend aggregated_count stays at 1 while the panel’s TEP loop runs. Backend code at backend/app.py requires 22 exact feature names for /ingest (FEATURE_COLUMNS). Confirm backend is running, set decimation_N=1, and verify a single POST /ingest returns t2_stat (accepted). If it returns status:"ignored", correct the mapper in unified_tep_control_panel.py to use those 22 names; if aggregating:true, persist decimation_N=1. Verify /status increments and /stream emits at 1s cadence in Demo mode.
