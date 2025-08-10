# Unified TEP + FaultExplainer Addendum (Run/Tuning Guide)

This addendum documents how to run the unified Control Panel with the FaultExplainer backend/frontend, how to tune sensitivity for demo, and how to troubleshoot.

## 1) Environment

- Always activate the local virtual environment first
  - macOS/Linux: `source tep_env/bin/activate`
- Then start the control panel: `python unified_tep_control_panel.py`
- Open: http://localhost:9001

## 2) Start order and verification

1. Start Backend → should show green banner; verify http://localhost:8000 loads
2. Start Frontend → should show green banner and auto-open http://localhost:5173
3. Click Demo (1s) → banner shows “Speed set to demo (1s/step)”
4. Click Set Backend Preset: Demo → banner confirms updated runtime params
5. Start TEP Simulation → System Status shows “Running”, Step increments every second

Quick checks:
- http://localhost:9001/api/status shows `step_interval_seconds: 1`, `speed_mode: "demo"`, and `current_preset: "demo"`
- http://localhost:8000/stream shows SSE lines appending
- http://localhost:8000/last_analysis returns the latest LLM result (if triggered)

## 3) Sensitivity presets (runtime)

The backend computes PCA T² thresholds at confidence (1−alpha). Lower alpha → stricter threshold; higher alpha → more sensitive.

- Demo Sensitive (fast feedback):
  - POST /config/runtime: `{ "pca_window_size": 6, "fault_trigger_consecutive_step": 1, "decimation_N": 1, "llm_min_interval_seconds": 20 }`
  - POST /config/alpha: `{ "anomaly_threshold": 0.05 }`
- Realistic:
  - POST /config/runtime: `{ "pca_window_size": 20, "fault_trigger_consecutive_step": 6, "decimation_N": 4, "llm_min_interval_seconds": 300 }`
  - POST /config/alpha: `{ "anomaly_threshold": 0.01 }`

You can apply these using the control panel buttons or via curl/Postman.

## 4) Fault injection and expectations

- Use the IDV sliders in the Control Panel (not the FE UI). Example demo test:
  - IDV_1 = 1.0, IDV_4 = 0.9
- With “Demo Sensitive” preset you should see:
  - /stream: anomaly becomes true intermittently; t2_stat rises above threshold
  - /last_analysis: an LLM result within ~10–30 seconds

## 5) Troubleshooting

- Control Panel shows Running but FE chart is flat:
  - Hard refresh FE (Cmd+Shift+R)
  - Verify /stream emits data continuously
- Buttons show no change:
  - Hard refresh Control Panel (Cmd+Shift+R)
  - Check http://localhost:9001/api/status for `speed_mode` and `current_preset`
- Backend not responding:
  - Restart from Control Panel → Stop All → Start Backend

## 6) Restart behavior

- Use the “Restart TEP” action to ensure the old loop stops and buffers reset before a new run. This avoids duplicate loops and stale counters.

## 7) Notes on dynamics vs. anomalies

- The TEP physics will show variable-level changes immediately when IDVs change, but PCA T² anomalies depend on:
  - Windowed statistics (using the selected feature subset and decimation)
  - Threshold strictness (alpha)
  - Consecutive anomaly gating (to avoid noise-triggered LLM spam)
- For demo, the “Demo Sensitive” preset reduces friction so you can quickly see detection and LLM analysis.

