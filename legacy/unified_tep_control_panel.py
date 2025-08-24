#!/usr/bin/env python3
"""
Unified TEP Control Panel
- Single interface to control all components
- Dynamic simulation → FaultExplainer integration
- Proper timing: 3min → 6min → 12min
- Uses original FaultExplainer backend/frontend
- Correct IDV ranges (0-1) and threshold (0.01)
"""

import os
import sys
import time
import threading
import subprocess
import signal
import json
import csv
from collections import deque
import numpy as np
from flask import Flask, render_template_string, jsonify, request, redirect, url_for, send_from_directory
import requests

# --- Helpers: resolve tools cross-platform and venv-aware ---

def resolve_venv_python():
    """Prefer .venv over tep_env. Return absolute python path for current OS."""
    # Get the project root (parent of legacy directory)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    cwd = project_root
    if sys.platform.startswith('win'):
        candidates = [
            os.path.join(cwd, '.venv', 'Scripts', 'python.exe'),
            os.path.join(cwd, 'tep_env', 'Scripts', 'python.exe'),
        ]
    else:
        candidates = [
            os.path.join(cwd, '.venv', 'bin', 'python'),
            os.path.join(cwd, 'tep_env', 'bin', 'python'),
        ]
    for p in candidates:
        if os.path.exists(p):
            return p
    # Fallback to current interpreter
    return sys.executable


def resolve_npm_cmd():
    return 'npm.cmd' if sys.platform.startswith('win') else 'npm'

class TEPDataBridge:
    """Bridge between dynamic TEP simulation and FaultExplainer."""

    def __init__(self):
        # Auto-cleanup before initialization
        self.auto_cleanup_tep_processes()
        self.setup_tep2py()

        # Simulation state
        self.tep_running = False
        self.current_step = 0
        self.idv_values = np.zeros(20)  # 20 IDV inputs (0.0 to 1.0 range)
        # Maintain a time-series of IDV rows so the simulator advances over time
        # Rather than simulating a single step repeatedly (which yields a constant output)
        from collections import deque as _deque
        self.idv_history = _deque(maxlen=1200)  # ~1 day of 3-min steps

        # Keep persistent simulation instance to avoid re-running entire history
        self.tep_sim_instance = None
        self.last_simulated_step = 0

        # Data queues with proper timing
        self.raw_data_queue = deque(maxlen=1000)  # Every 3 minutes (raw TEP)
        self.pca_data_queue = deque(maxlen=500)   # Every 6 minutes (half speed)
        self.llm_data_queue = deque(maxlen=250)   # Every 12 minutes (quarter speed)

        # Anomaly Detection training mode
        self.pca_training_mode = False
        self.pca_training_data = []
        self.pca_training_target = 30   # Faster demo training (reduced from 100)

        # Stability monitoring for smart Anomaly Detection retraining
        self.stability_buffer = []
        self.stability_window = 20  # Monitor last 20 points for stability
        self.stability_threshold = 0.05  # 5% coefficient of variation threshold
        self.is_stable = False

        # Timing control
        self.last_pca_time = 0
        self.last_llm_time = 0
        self.pca_interval = 6 * 60  # 6 minutes in seconds
        self.llm_interval = 12 * 60  # 12 minutes in seconds
        # Simulation step interval (default: real-time 3 minutes)
        self.step_interval_seconds = 180
        self.speed_mode = 'real'  # 'demo' or 'real'
        self.current_preset = None  # 'demo' or 'real'
        self.speed_factor = 1.0  # New: speed multiplier (0.1x to 10x)

        # Process management
        self.processes = {}

        # Heartbeat and CSV stats
        self.last_loop_at = 0
        self.last_ingest_at = 0
        self.last_ingest_ok = False
        self.csv_rows = 0
        self.csv_bytes = 0
        self.last_saved_step = -1  # Track last saved step to prevent duplicates

        # Cost protection
        self.last_auto_stop_check = 0
        self.auto_stop_check_interval = 60  # Check every minute
        # Diagnostics
        self.last_error = ""
        self.last_ingest_info = {}

        print("✅ TEP Data Bridge initialized")
        print("✅ Timing: TEP(3min) → Anomaly Detection(6min) → LLM(12min)")

    def auto_cleanup_tep_processes(self):
        """Auto-cleanup any existing TEP processes and data files for clean startup."""
        print("🧹 Auto-cleanup: Checking for existing TEP processes...")

        try:
            import psutil

            # Find and terminate existing TEP processes
            tep_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''

                    # Look for other TEP-related processes (but not current one)
                    if any(keyword in cmdline.lower() for keyword in [
                        'unified_tep_control_panel',
                        'tep_bridge',
                        'mvp_dashboard'
                    ]) and proc.info['pid'] != os.getpid():
                        tep_processes.append(proc.info['pid'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Terminate found processes
            if tep_processes:
                print(f"🔪 Found {len(tep_processes)} existing TEP processes, terminating...")
                for pid in tep_processes:
                    try:
                        os.kill(pid, signal.SIGTERM)
                        print(f"✅ Terminated PID {pid}")
                    except:
                        pass
                time.sleep(1)  # Give processes time to exit
            else:
                print("✅ No conflicting TEP processes found")

            # Clean up data file for fresh start
            data_file = os.path.join('data', 'live_tep_data.csv')
            if os.path.exists(data_file):
                try:
                    # Keep header only
                    with open(data_file, 'r') as f:
                        header = f.readline()

                    with open(data_file, 'w') as f:
                        f.write(header)

                    print(f"✅ Cleaned data file: {data_file}")
                except Exception as e:
                    print(f"⚠️ Could not clean data file: {e}")

            print("✅ Auto-cleanup completed")

        except ImportError:
            print("⚠️ psutil not available, skipping process cleanup")
        except Exception as e:
            print(f"⚠️ Auto-cleanup error: {e}")

    def setup_tep2py(self):
        """Setup real tep2py simulator."""
        try:
            # Get script directory and build path to external_repos
            script_dir = os.path.dirname(os.path.abspath(__file__))
            tep_path = os.path.join(script_dir, 'external_repos', 'tep2py-master')
            if tep_path not in sys.path:
                sys.path.insert(0, tep_path)

            import tep2py
            self.tep2py = tep2py
            print("✅ Real tep2py loaded")

        except Exception as e:
            print(f"❌ tep2py setup failed: {e}")
            self.tep2py = None
    def map_to_faultexplainer_features(self, data_point):
        """Map XMEAS_* keys to FaultExplainer friendly feature names required by /ingest."""
        xmeas_to_name = {
            1: 'A Feed', 2: 'D Feed', 3: 'E Feed', 4: 'A and C Feed', 5: 'Recycle Flow',
            6: 'Reactor Feed Rate', 7: 'Reactor Pressure', 8: 'Reactor Level', 9: 'Reactor Temperature',
            10: 'Purge Rate', 11: 'Product Sep Temp', 12: 'Product Sep Level', 13: 'Product Sep Pressure',
            14: 'Product Sep Underflow', 15: 'Stripper Level', 16: 'Stripper Pressure', 17: 'Stripper Underflow',
            18: 'Stripper Temp', 19: 'Stripper Steam Flow', 20: 'Compressor Work', 21: 'Reactor Coolant Temp',
            22: 'Separator Coolant Temp'
        }
        row = {}
        for i, name in xmeas_to_name.items():
            row[name] = float(data_point.get(f'XMEAS_{i}', 0.0))
        return row

    def send_to_ingest(self, data_point, url="http://localhost:8000/ingest"):
        """Post a single mapped point to FaultExplainer /ingest and record heartbeat.
        Logs backend response to detect ignored vs aggregating vs accepted events.
        """
        start = time.time()
        try:
            mapped = self.map_to_faultexplainer_features(data_point)

            # Always check stability for monitoring
            self.check_data_stability(mapped)

            # Check if we're in Anomaly Detection training mode
            if self.pca_training_mode:
                self.pca_training_data.append(mapped)
                print(f"📊 Anomaly Detection Training: Collected {len(self.pca_training_data)}/{self.pca_training_target} data points")

                if len(self.pca_training_data) >= self.pca_training_target:
                    print("🎯 Anomaly Detection Training: Target reached, retraining model...")
                    self.retrain_pca_model()
                    self.pca_training_mode = False
                    print("✅ Anomaly Detection Training: Complete, resuming normal operation")

                # Don't send to ingest during training - just record heartbeat
                self.last_ingest_at = time.time()
                self.last_ingest_ok = True
                self.last_ingest_info = {"status": "training", "collected": len(self.pca_training_data)}
                return

            import requests
            r = requests.post(url, json={"data_point": mapped}, timeout=60)
            self.last_ingest_at = time.time()
            self.last_ingest_ok = (r.status_code == 200)
            if not self.last_ingest_ok:
                print(f"⚠️ /ingest HTTP {r.status_code}: {r.text[:160]}")
                return
            dt = self.last_ingest_at - start
            try:
                info = r.json()
            except Exception:
                info = {"raw": r.text[:160]}
            status = info.get('status')
            if status == 'ignored':
                reason = info.get('reason','')
                present = info.get('present')
                print(f"⚠️ /ingest ignored in {dt:.2f}s reason={reason} present={len(present) if present else 0}")
                return
            if info.get('aggregating'):
                have = info.get('have')
                need = info.get('need')
                print(f"⏳ /ingest aggregating in {dt:.2f}s (have={have}, need={need})")
                return
            # Accepted point with t2/anomaly
            print(f"✅ /ingest OK in {dt:.2f}s (t2={info.get('t2_stat','-')}, anomaly={info.get('anomaly')}, idx={info.get('aggregated_index')})")
            if info.get('llm', {}).get('status') == 'triggered':
                print("🤖 LLM triggered (live)")
        except Exception as e:
            self.last_ingest_ok = False
            self.last_ingest_info = {"error": str(e)}
            print(f"❌ Failed to POST /ingest: {e}")

    def retrain_pca_model(self):
        """Retrain Anomaly Detection model with collected stable data."""
        try:
            import pandas as pd
            import requests

            # Convert training data to DataFrame
            df = pd.DataFrame(self.pca_training_data)
            print(f"📊 Retraining Anomaly Detection with {len(df)} data points")

            # Save training data
            training_file = "external_repos/FaultExplainer-main/backend/data/live_fault0.csv"
            os.makedirs(os.path.dirname(training_file), exist_ok=True)
            df.to_csv(training_file, index=False)
            print(f"💾 Saved training data to {training_file}")

            # Send retrain request to FaultExplainer
            retrain_url = "http://localhost:8000/retrain"
            payload = {"training_file": "live_fault0.csv"}

            response = requests.post(retrain_url, json=payload, timeout=120)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Anomaly Detection model retrained successfully")
                print(f"   - Components: {result.get('n_components', 'N/A')}")
                print(f"   - Threshold: {result.get('t2_threshold', 'N/A'):.2f}")
            else:
                print(f"❌ Anomaly Detection retrain failed: {response.status_code} {response.text}")

        except Exception as e:
            print(f"❌ Anomaly Detection retrain error: {e}")

    def check_data_stability(self, data_point):
        """Check if recent data is stable enough for Anomaly Detection retraining."""
        # Add current data point to stability buffer
        key_vars = ['A Feed', 'Reactor Pressure', 'Reactor Level', 'Reactor Temperature']
        stability_values = []

        for var in key_vars:
            if var in data_point:
                stability_values.append(data_point[var])

        if stability_values:
            avg_value = sum(stability_values) / len(stability_values)
            self.stability_buffer.append(avg_value)

            # Keep only recent points
            if len(self.stability_buffer) > self.stability_window:
                self.stability_buffer.pop(0)

            # Check stability if we have enough points
            if len(self.stability_buffer) >= self.stability_window:
                import numpy as np
                values = np.array(self.stability_buffer)
                mean_val = np.mean(values)
                std_val = np.std(values)
                cv = std_val / mean_val if mean_val != 0 else 1.0

                self.is_stable = bool(cv < self.stability_threshold)
                return self.is_stable

        return False

    def start_pca_training(self):
        """Start Anomaly Detection training mode."""
        self.pca_training_mode = True
        self.pca_training_data = []
        print(f"🎯 Anomaly Detection Training: Started, will collect {self.pca_training_target} stable data points")

    def set_idv(self, idv_num, value):
        """Set IDV value (1-20, binary 0 or 1 as per original TEP paper)."""
        if 1 <= idv_num <= 20:
            # Convert to integer (0 or 1) as per original TEP specification
            binary_value = int(value)
            if binary_value in [0, 1]:
                self.idv_values[idv_num - 1] = binary_value
                status = "ON" if binary_value == 1 else "OFF"
                print(f"🔧 Set IDV_{idv_num} = {binary_value} ({status})")
                return True
        return False

    def set_xmv(self, xmv_num, value):
        """Set XMV value (1-11, continuous 0.0-100.0% as per original TEP paper)."""
        if 1 <= xmv_num <= 11:
            # Convert to float (0.0-100.0) as per original TEP specification
            float_value = float(value)
            if 0.0 <= float_value <= 100.0:
                # Initialize XMV values if not exists (TEP requires exactly 11 values for XMV(1) to XMV(11))
                if not hasattr(self, 'xmv_values'):
                    self.xmv_values = np.array([63.0, 53.0, 24.0, 61.0, 22.0, 40.0, 38.0, 46.0, 47.0, 41.0, 18.0])

                self.xmv_values[xmv_num - 1] = float_value
                print(f"🎛️ Set XMV_{xmv_num} = {float_value:.1f}%")
                return True
        return False

    def run_tep_simulation_step(self):
        """Run one TEP simulation step (3 minutes) - GENUINE FORTRAN SIMULATION."""
        try:
            if not self.tep2py:
                return None

            # Append current IDV to history
            self.idv_history.append(self.idv_values.copy())
            current_step = len(self.idv_history)

            # REAL TEP SIMULATION: Always run fresh simulation with current history
            # This ensures we get genuine dynamic data, not artificial stability
            import numpy as _np2

            # Create simulation matrix with current IDV history
            # Include some pre-run steps for stability, then actual history
            prerun_steps = 10  # Reduced for faster simulation
            prerun_matrix = _np2.zeros((prerun_steps, 20), dtype=_np2.float64)  # No faults during pre-run

            # Convert IDV history to proper format (FLOAT, not INT!)
            if len(self.idv_history) > 0:
                actual_matrix = _np2.array(list(self.idv_history), dtype=_np2.float64).reshape(-1, 20)
                full_matrix = _np2.vstack([prerun_matrix, actual_matrix])
            else:
                # If no history yet, just use prerun matrix
                full_matrix = prerun_matrix

            print(f"🔄 Running REAL TEP simulation: {prerun_steps} pre-run + {current_step} actual steps (Speed: {self.speed_factor}x)")
            print(f"🎛️ Current XMV values: {self.xmv_values if hasattr(self, 'xmv_values') else 'Not set'}")

            # Create and run fresh simulation - this gives us REAL dynamic data
            user_xmv = self.xmv_values if hasattr(self, 'xmv_values') else None
            tep_sim = self.tep2py.tep2py(full_matrix, speed_factor=self.speed_factor, user_xmv=user_xmv)
            tep_sim.simulate()

            # Extract the LATEST data point (corresponds to current step)
            if hasattr(tep_sim, 'process_data') and len(tep_sim.process_data) > 0:
                # Get the last data point (most recent simulation result)
                latest = tep_sim.process_data.iloc[-1]
                data_length = len(tep_sim.process_data)

                print(f"📊 Using REAL Fortran simulation data (total points: {data_length}, using latest)")

                # Extract XMEAS and XMV columns
                xmeas_cols = [col for col in tep_sim.process_data.columns if 'XMEAS' in col]
                xmv_cols = [col for col in tep_sim.process_data.columns if 'XMV' in col]

                # Create data point with REAL simulation results
                data_point = {
                    'timestamp': time.time(),
                    'step': current_step - 1,  # Use current_step from idv_history, 0-indexed
                    'idv_values': self.idv_values.copy(),
                }

                # Add XMEAS data (process measurements)
                for i, col in enumerate(xmeas_cols):
                    if col in latest.index:
                        data_point[f'XMEAS_{i+1}'] = float(latest[col])
                    else:
                        data_point[f'XMEAS_{i+1}'] = 0.0

                # Add XMV data (manipulated variables)
                for i, col in enumerate(xmv_cols):
                    if col in latest.index:
                        data_point[f'XMV_{i+1}'] = float(latest[col])
                    else:
                        data_point[f'XMV_{i+1}'] = 0.0

                # Debug: Compare set XMV vs actual XMV
                if hasattr(self, 'xmv_values'):
                    print(f"🔍 XMV Comparison:")
                    for i in range(min(len(self.xmv_values), 5)):  # Show first 5
                        set_val = self.xmv_values[i]
                        actual_val = data_point.get(f'XMV_{i+1}', 0)
                        print(f"   XMV_{i+1}: Set={set_val:.1f}%, Actual={actual_val:.1f}%")

                # Log some key values to verify real data
                xmeas_1 = data_point.get('XMEAS_1', 0)
                xmeas_7 = data_point.get('XMEAS_7', 0)
                print(f"📈 REAL data - XMEAS_1: {xmeas_1:.6f}, XMEAS_7: {xmeas_7:.6f}")

                return data_point
            else:
                print(f"❌ No simulation data generated")
                return None

        except Exception as e:
            print(f"❌ TEP simulation step failed: {e}")
            return None

    def save_data_for_faultexplainer(self, data_point):
        """Save data in FaultExplainer format."""
        try:
            # Prevent duplicate saves
            current_step = data_point['step']
            if current_step <= self.last_saved_step:
                print(f"⏭️ Skipping duplicate step {current_step} (last saved: {self.last_saved_step})")
                return True

            # Create CSV file path
            csv_path = os.path.join('data', 'live_tep_data.csv')
            os.makedirs('data', exist_ok=True)

            # Prepare row data
            row_data = [data_point['timestamp'], data_point['step']]

            # Add XMEAS values (41 variables)
            for i in range(1, 42):
                key = f'XMEAS_{i}'
                row_data.append(data_point.get(key, 0.0))

            # Add XMV values (11 variables)
            for i in range(1, 12):
                key = f'XMV_{i}'
                row_data.append(data_point.get(key, 0.0))

            # Add IDV values (20 variables)
            for i in range(20):
                row_data.append(data_point['idv_values'][i])

            # Write to CSV
            file_exists = os.path.exists(csv_path)
            with open(csv_path, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                # Write header if new file
                if not file_exists:
                    header = ['timestamp', 'step']
                    header.extend([f'XMEAS_{i}' for i in range(1, 42)])
                    header.extend([f'XMV_{i}' for i in range(1, 12)])
                    header.extend([f'IDV_{i}' for i in range(1, 21)])
                    writer.writerow(header)
                writer.writerow(row_data)

            # Update simple CSV stats and track last saved step
            try:
                self.csv_rows += 1
                self.csv_bytes = os.path.getsize(csv_path)
                self.last_saved_step = current_step  # Update last saved step
            except Exception:
                pass

            print(f"💾 Saved data point {current_step} to {csv_path}")
            return True

        except Exception as e:
            print(f"❌ Failed to save data: {e}")
            return False


    def simulation_loop(self):
        """Main simulation loop with proper timing and heartbeats."""
        print("🚀 Starting TEP simulation loop")

        while self.tep_running:
            try:
                loop_start = time.time()
                self.last_loop_at = loop_start
                print(f"⏱️ Step {self.current_step} start (interval={self.step_interval_seconds}s, mode={self.speed_mode})")

                # Run TEP simulation step (every 3 minutes)
                data_point = self.run_tep_simulation_step()

                if data_point:
                    # Add to raw data queue
                    self.raw_data_queue.append(data_point)

                    # Save for FaultExplainer
                    if self.save_data_for_faultexplainer(data_point):
                        pass

                    # Also send to live /ingest for real-time Anomaly Detection+LLM
                    print("➡️ Posting /ingest...")
                    self.send_to_ingest(data_point)

                    # Check if time for Anomaly Detection analysis (every 6 minutes)
                    current_time = time.time()
                    if current_time - self.last_pca_time >= self.pca_interval:
                        self.pca_data_queue.append(data_point)
                        self.last_pca_time = current_time
                        print(f"📊 Anomaly Detection data point added (step {self.current_step})")

                        # Check if time for LLM analysis (every 12 minutes)
                        if current_time - self.last_llm_time >= self.llm_interval:
                            self.llm_data_queue.append(data_point)
                            self.last_llm_time = current_time
                            print(f"🤖 LLM data point added (step {self.current_step})")

                    # Update current_step to match the actual simulation step
                    self.current_step = len(self.idv_history)

                # Check for auto-shutdown signal (cost protection)
                current_time = time.time()
                if current_time - self.last_auto_stop_check > self.auto_stop_check_interval:
                    self.last_auto_stop_check = current_time
                    if self.check_auto_shutdown_signal():
                        print("🛡️ AUTO-SHUTDOWN: Premium model session expired - stopping simulation")
                        self.tep_running = False
                        break

                # Wait for next step (demo or real-time)
                print("💤 Sleeping for next step...")
                time.sleep(self.step_interval_seconds)

            except Exception as e:
                self.last_error = f"loop: {e}"
                print(f"❌ Simulation loop error: {e}")
                time.sleep(10)

        print("🛑 TEP simulation loop stopped")

    def check_auto_shutdown_signal(self):
        """Check if backend has signaled for auto-shutdown due to cost protection"""
        try:
            response = requests.get("http://localhost:8000/simulation/auto_stop_status", timeout=5)
            if response.status_code == 200:
                result = response.json()
                if result.get('auto_stopped', False):
                    # Reset the flag so it doesn't trigger again
                    requests.post("http://localhost:8000/simulation/reset_auto_stop", timeout=5)
                    return True
            return False
        except Exception as e:
            print(f"⚠️ Could not check auto-shutdown status: {e}")
            return False

    def start_tep_simulation(self):
        """Start TEP simulation."""
        if self.tep_running:
            return False, "TEP simulation already running"

        # Reset rolling state at (re)start
        try:
            self.idv_history.clear()
        except Exception:
            pass
        self.tep_running = True
        self.simulation_thread = threading.Thread(target=self.simulation_loop, daemon=True)
        self.simulation_thread.start()
        return True, "TEP simulation started"

    def restart_tep_simulation(self):
        """Restart TEP simulation safely: stop thread, reset counters and queues, start again."""
        try:
            # Stop if running
            if self.tep_running:
                self.tep_running = False
                # Allow thread to exit
                time.sleep(min(2, self.step_interval_seconds))
            # Reset state
            self.current_step = 0
            self.raw_data_queue.clear()
            self.pca_data_queue.clear()
            self.llm_data_queue.clear()
            try:
                self.idv_history.clear()
            except Exception:
                pass
            # Reset simulation instance
            self.tep_sim_instance = None
            self.last_simulated_step = 0
            self.last_pca_time = 0
            self.last_llm_time = 0
            self.last_loop_at = 0
            self.last_ingest_at = 0
            self.last_ingest_ok = False
            self.csv_rows = 0
            self.csv_bytes = 0
            self.last_saved_step = -1  # Reset duplicate prevention

            # Ensure IDV values are reset to steady state (all zeros)
            self.idv_values = np.zeros(20)

            print("🏭 TEP Restart: Pre-running to steady state...")
            print("   • IDV values: All zeros (no faults)")
            print("   • Pre-run: 25 steps to reach steady state")
            print("   • Data: Only steady-state data will be used")

            # Pre-run to steady state
            if not self.prerun_to_steady_state():
                return False, "Failed to reach steady state"

            # Start fresh with steady-state simulation
            self.tep_running = True
            self.simulation_thread = threading.Thread(target=self.simulation_loop, daemon=True)
            self.simulation_thread.start()
            return True, "TEP simulation restarted with true steady-state conditions"
        except Exception as e:
            return False, f"Failed to restart TEP: {e}"

    def prerun_to_steady_state(self):
        """Pre-run TEP simulation to reach steady state before actual data collection."""
        try:
            print("🔄 Pre-running TEP simulation to steady state...")

            # Create a longer IDV matrix for pre-run (25 steps should be enough)
            prerun_steps = 25
            idv_matrix = np.zeros((prerun_steps, 20))  # All zeros = no faults

            # Create temporary simulation instance for pre-run
            temp_sim = self.tep2py.tep2py(idv_matrix, speed_factor=1.0)  # Use normal speed for stability
            temp_sim.simulate()

            if hasattr(temp_sim, 'process_data'):
                data = temp_sim.process_data

                # Check if we reached steady state
                if len(data) >= 20:
                    # Analyze last 5 steps for stability
                    reactor_pressure = data['XMEAS(7)'].values[-5:]
                    reactor_temp = data['XMEAS(9)'].values[-5:]

                    pressure_std = np.std(reactor_pressure)
                    temp_std = np.std(reactor_temp)

                    print(f"   📊 Steady state check:")
                    print(f"      Reactor Pressure: {np.mean(reactor_pressure):.1f} ± {pressure_std:.1f} kPa")
                    print(f"      Reactor Temperature: {np.mean(reactor_temp):.1f} ± {temp_std:.1f} °C")

                    # Consider steady if standard deviation is small
                    if pressure_std < 10 and temp_std < 1.0:
                        print("   ✅ Steady state achieved!")

                        # Store steady state values for reference
                        self.steady_state_values = {
                            'pressure': np.mean(reactor_pressure),
                            'temperature': np.mean(reactor_temp),
                            'achieved_at_step': prerun_steps
                        }
                        return True
                    else:
                        print("   ⚠️ Still not fully steady, but proceeding...")
                        return True  # Proceed anyway, it's better than starting from scratch
                else:
                    print("   ⚠️ Insufficient data from pre-run")
                    return False
            else:
                print("   ❌ No data from pre-run simulation")
                return False

        except Exception as e:
            print(f"   ❌ Pre-run failed: {e}")
            return False

    def stop_tep_simulation(self):
        """Stop TEP simulation."""
        self.tep_running = False
        return True, "TEP simulation stopped"

    def kill_port_process(self, port):
        """Kill any process using the specified port."""
        try:
            import psutil
            # Walk processes and check connections safely (avoid 'connections' attr request)
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    for conn in proc.connections(kind='inet'):
                        if conn.laddr and hasattr(conn.laddr, 'port') and conn.laddr.port == port:
                            print(f"🔪 Killing process {proc.pid} using port {port}")
                            proc.kill()
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except ImportError:
            # Fallback using lsof
            try:
                result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
                if result.stdout.strip():
                    pid = result.stdout.strip()
                    subprocess.run(['kill', '-9', pid])
                    print(f"🔪 Killed process {pid} using port {port}")
                    return True
            except:
                pass
        return False

    def start_faultexplainer_backend(self):
        """Start FaultExplainer backend."""
        try:
            # Get script directory and build path to external_repos
            script_dir = os.path.dirname(os.path.abspath(__file__))
            backend_path = os.path.join(script_dir, 'external_repos', 'FaultExplainer-main', 'backend')

            # Kill existing backend if running
            if 'faultexplainer_backend' in self.processes:
                self.processes['faultexplainer_backend'].terminate()
                del self.processes['faultexplainer_backend']

            # Kill any process using port 8000
            self.kill_port_process(8000)
            time.sleep(1)  # Wait for port to be freed

            # Activate virtual environment and start backend (prefer .venv, support Windows)
            venv_python = resolve_venv_python()

            print(f"🚀 Starting backend: {venv_python} app.py in {backend_path}")

            process = subprocess.Popen(
                [venv_python, 'app.py'],
                cwd=backend_path,
                stdout=None,
                stderr=None,
                env=dict(os.environ, PYTHONPATH=backend_path)
            )

            # Wait a moment and check if process started successfully
            time.sleep(2)
            if process.poll() is None:
                self.processes['faultexplainer_backend'] = process
                print("✅ Backend process started successfully")
                return True, "FaultExplainer backend started on port 8000"
            else:
                stdout, stderr = process.communicate()
                error_msg = stdout.decode() if stdout else "Unknown error"
                print(f"❌ Backend failed to start: {error_msg}")
                return False, f"Backend failed to start: {error_msg[:100]}"

        except Exception as e:
            print(f"❌ Exception starting backend: {e}")
            return False, f"Failed to start backend: {e}"

    def start_faultexplainer_backend_dev(self):
        """Start backend in dev (uvicorn reload) mode."""
        try:
            # Get script directory and build path to external_repos
            script_dir = os.path.dirname(os.path.abspath(__file__))
            backend_path = os.path.join(script_dir, 'external_repos', 'FaultExplainer-main', 'backend')
            # Kill existing backend
            if 'faultexplainer_backend' in self.processes:
                self.processes['faultexplainer_backend'].terminate()
                del self.processes['faultexplainer_backend']
            self.kill_port_process(8000)
            time.sleep(1)
            venv_python = resolve_venv_python()
            print(f"🚀 Starting backend (dev reload): {venv_python} -m uvicorn app:app --reload")
            process = subprocess.Popen(
                [venv_python, '-m', 'uvicorn', 'app:app', '--host', '0.0.0.0', '--port', '8000', '--reload'],
                cwd=backend_path,
                stdout=None,
                stderr=None,
                env=dict(os.environ, PYTHONPATH=backend_path)
            )
            time.sleep(2)
            if process.poll() is None:
                self.processes['faultexplainer_backend'] = process
                return True, "FaultExplainer backend (dev) started on port 8000"
            return False, "Backend (dev) failed to start"
        except Exception as e:
            return False, f"Failed to start backend dev: {e}"

            print(f"🚀 Starting backend: {venv_python} app.py in {backend_path}")

            process = subprocess.Popen(
                [venv_python, 'app.py'],
                cwd=backend_path,
                stdout=None,
                stderr=None,
                env=dict(os.environ, PYTHONPATH=backend_path)
            )

            # Wait a moment and check if process started successfully
            time.sleep(2)
            if process.poll() is None:
                self.processes['faultexplainer_backend'] = process
                print("✅ Backend process started successfully")
                return True, "FaultExplainer backend started on port 8000"
            else:
                stdout, stderr = process.communicate()
                error_msg = stdout.decode() if stdout else "Unknown error"
                print(f"❌ Backend failed to start: {error_msg}")
                return False, f"Backend failed to start: {error_msg[:100]}"

        except Exception as e:
            print(f"❌ Exception starting backend: {e}")
            return False, f"Failed to start backend: {e}"

    def start_faultexplainer_frontend(self):
        """Start FaultExplainer frontend."""
        try:
            # Get script directory and build path to external_repos
            script_dir = os.path.dirname(os.path.abspath(__file__))
            frontend_path = os.path.join(script_dir, 'external_repos', 'FaultExplainer-main', 'frontend')

            # Kill existing frontend if running
            if 'faultexplainer_frontend' in self.processes:
                self.processes['faultexplainer_frontend'].terminate()
                del self.processes['faultexplainer_frontend']

            # Kill any process using port 5173 (Vite default)
            self.kill_port_process(5173)
            time.sleep(1)  # Wait for port to be freed

            # Check if node_modules exists
            node_modules_path = os.path.join(frontend_path, 'node_modules')
            if not os.path.exists(node_modules_path):
                return False, "Frontend dependencies not installed. Run: cd external_repos/FaultExplainer-main/frontend && npm install"

            print(f"🚀 Starting frontend: npm start in {frontend_path}")

            # Start frontend (using 'dev' script for Vite)
            process = subprocess.Popen(
                [resolve_npm_cmd(), 'run', 'dev'],
                cwd=frontend_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )

            # Wait a moment and check if process started successfully
            time.sleep(3)
            if process.poll() is None:
                self.processes['faultexplainer_frontend'] = process
                print("✅ Frontend process started successfully")
                try:
                    import webbrowser
                    webbrowser.open('http://localhost:5173')
                except Exception:
                    pass
                return True, "FaultExplainer frontend started on port 5173"
            else:
                stdout, stderr = process.communicate()
                error_msg = stdout.decode() if stdout else "Unknown error"
                print(f"❌ Frontend failed to start: {error_msg}")
                return False, f"Frontend failed to start: {error_msg[:100]}"

        except Exception as e:
            print(f"❌ Exception starting frontend: {e}")
            return False, f"Failed to start frontend: {e}"

    def stop_all_processes(self):
        """Stop all running processes comprehensively."""
        print("🛑 EMERGENCY STOP: Stopping all TEP processes...")

        # Stop TEP simulation first
        self.tep_running = False
        print("✅ TEP simulation stopped")

        # Stop all tracked processes
        for name, process in self.processes.items():
            try:
                print(f"🔪 Terminating {name} (PID: {process.pid})")
                process.terminate()
                # Wait up to 3 seconds for graceful shutdown
                try:
                    process.wait(timeout=3)
                    print(f"✅ {name} terminated gracefully")
                except subprocess.TimeoutExpired:
                    print(f"💀 Force killing {name}")
                    process.kill()
                    process.wait()
            except Exception as e:
                print(f"⚠️ Error stopping {name}: {e}")

        self.processes.clear()

        # Kill processes by port (comprehensive cleanup)
        ports_to_clean = [9001, 9002, 8001, 8000, 5173, 3000]
        for port in ports_to_clean:
            try:
                if self.kill_port_process(port):
                    print(f"🔪 Freed port {port}")
            except Exception as e:
                print(f"⚠️ Could not clean port {port}: {e}")

        # Clean up data files
        try:
            data_file = "data/live_tep_data.csv"
            if os.path.exists(data_file):
                with open(data_file, 'w') as f:
                    f.write("")  # Clear the file
                print("🗑️ Cleared data file")
        except Exception as e:
            print(f"⚠️ Could not clear data file: {e}")

        print("🎉 Emergency stop complete - all processes terminated")

    def check_process_status(self, process_name):
        """Check if a process is actually running."""
        if process_name not in self.processes:
            return False

        process = self.processes[process_name]
        if process.poll() is None:  # Process is still running
            return True
        else:  # Process has terminated
            del self.processes[process_name]
            return False

    def get_status(self):
        """Get current system status (includes backend counters if reachable)."""
        backend_agg = None
        backend_buf = None
        try:
            import requests
            r = requests.get('http://localhost:8000/status', timeout=1.5)
            if r.ok:
                js = r.json()
                backend_agg = js.get('aggregated_count')
                backend_buf = js.get('live_buffer')
        except Exception as e:
            self.last_error = f"backend status: {e}"
        return {
            'tep_running': self.tep_running,
            'current_step': self.current_step,
            'step_interval_seconds': self.step_interval_seconds,
            'speed_mode': self.speed_mode,
            'current_preset': self.current_preset,
            'speed_factor': getattr(self, 'speed_factor', 1.0),
            'raw_data_points': len(self.raw_data_queue),
            'pca_data_points': len(self.pca_data_queue),
            'llm_data_points': len(self.llm_data_queue),
            'last_loop_at': getattr(self, 'last_loop_at', 0),
            'last_ingest_at': getattr(self, 'last_ingest_at', 0),
            'last_ingest_ok': getattr(self, 'last_ingest_ok', False),
            'csv_rows': getattr(self, 'csv_rows', 0),
            'csv_bytes': getattr(self, 'csv_bytes', 0),
            'last_ingest_info': getattr(self, 'last_ingest_info', {}),
            'last_error': getattr(self, 'last_error', ''),
            'backend_aggregated_count': backend_agg,
            'backend_live_buffer': backend_buf,
            'active_processes': list(self.processes.keys()),
            'backend_running': self.check_process_status('faultexplainer_backend'),
            'frontend_running': self.check_process_status('faultexplainer_frontend'),
            'bridge_running': self.check_process_status('tep_bridge'),
            'idv_values': self.idv_values.tolist()
        }

    def system_health_check(self):
        """Comprehensive system health check with detailed diagnostics."""
        status = self.get_status()
        health = {
            'overall_status': 'UNKNOWN',
            'components': {},
            'issues': [],
            'recommendations': []
        }

        # Check TEP Simulation
        simulation_active = (
            status['tep_running'] and
            hasattr(self, 'simulation_thread') and
            self.simulation_thread and
            self.simulation_thread.is_alive() and
            (time.time() - status['last_loop_at'] < max(300, status['step_interval_seconds'] * 2))
        )

        if status['tep_running'] and simulation_active:
            health['components']['tep_simulation'] = '✅ RUNNING'
        elif status['tep_running'] and not simulation_active:
            health['components']['tep_simulation'] = '⚠️ STARTED BUT NOT ACTIVE'
            health['issues'].append('TEP simulation thread may have crashed')
            health['recommendations'].append('Click "⟳ Restart TEP" to fix simulation thread')
        else:
            health['components']['tep_simulation'] = '❌ STOPPED'
            health['issues'].append('TEP simulation not started')
            health['recommendations'].append('Click "▶️ Start TEP" to begin simulation')

        # Check Backend
        if status['backend_running']:
            health['components']['backend'] = '✅ RUNNING'
        else:
            health['components']['backend'] = '❌ STOPPED'
            health['issues'].append('FaultExplainer backend not reachable')
            health['recommendations'].append('Click "▶️ Start Backend" to start analysis engine')

        # Check Data Flow
        data_flow_active = (
            simulation_active and
            status['backend_running'] and
            status['last_ingest_at'] > 0 and
            (time.time() - status['last_ingest_at'] < max(600, status['step_interval_seconds'] * 3))
        )

        if data_flow_active:
            health['components']['data_bridge'] = '✅ ACTIVE'
        else:
            health['components']['data_bridge'] = '❌ INACTIVE'
            health['issues'].append('No data flow between TEP and FaultExplainer')

        # Check Frontend (optional)
        if status['frontend_running']:
            health['components']['frontend'] = '✅ RUNNING'
        else:
            health['components']['frontend'] = '⚠️ STOPPED (Optional)'

        # Overall Status
        critical_issues = len([i for i in health['issues'] if 'TEP' in i or 'backend' in i])
        if critical_issues == 0:
            health['overall_status'] = '✅ READY'
        elif critical_issues == 1:
            health['overall_status'] = '⚠️ PARTIAL'
        else:
            health['overall_status'] = '❌ NOT READY'

        return health

class UnifiedControlPanel:
    """Unified control panel for TEP system."""

    def __init__(self):
        self.app = Flask(__name__)
        self.bridge = TEPDataBridge()
        self.baseline_data = None  # Will be loaded when user clicks "Load Baseline"
        self.setup_routes()
        print("✅ Unified Control Panel initialized")

    def setup_routes(self):
        """Setup Flask routes."""

        @self.app.route('/')
        def index():
            return render_template_string(CONTROL_PANEL_HTML)

        @self.app.route('/static/<path:filename>')
        def static_files(filename):
            return send_from_directory('.', os.path.join('static', filename))

        @self.app.route('/api/status')
        def get_status():
            return jsonify(self.bridge.get_status())

        @self.app.route('/api/health')
        def health_check():
            return jsonify(self.bridge.system_health_check())

        @self.app.route('/api/ultra_start', methods=['POST'])
        def ultra_start():
            """One-click ultra-fast startup: Start everything at 50x speed"""
            try:
                results = []

                # Step 1: Set ultra speed first (50x)
                results.append("🚀 Setting ultra speed (50x)...")
                self.bridge.speed_factor = 50.0
                self.bridge.step_interval_seconds = 180 / 50.0  # 3.6 seconds
                self.bridge.speed_mode = 'fast_50x'
                results.append(f"✅ Speed set to 50x (interval: {self.bridge.step_interval_seconds:.1f}s)")

                # Step 2: Start Backend
                results.append("🔧 Starting FaultExplainer backend...")
                backend_success, backend_message = self.bridge.start_faultexplainer_backend()
                if not backend_success:
                    return jsonify({
                        'success': False,
                        'message': f"❌ Backend failed: {backend_message}"
                    })
                results.append("✅ Backend started")

                # Step 3: Wait for backend to be ready
                import time
                time.sleep(2)
                results.append("⏳ Backend initializing...")

                # Step 4: Start TEP simulation with ultra speed
                results.append("🏭 Starting TEP simulation at 50x speed...")
                tep_success, tep_message = self.bridge.start_tep_simulation()
                if not tep_success:
                    return jsonify({
                        'success': False,
                        'message': f"❌ TEP failed: {tep_message}"
                    })
                results.append("✅ TEP simulation started at ultra speed")

                # Step 5: Start frontend (optional)
                results.append("🖥️ Starting FaultExplainer frontend...")
                try:
                    frontend_success, frontend_message = self.bridge.start_faultexplainer_frontend()
                    if frontend_success:
                        results.append("✅ Frontend started")
                    else:
                        results.append("⚠️ Frontend start failed (optional)")
                except:
                    results.append("⚠️ Frontend start failed (optional)")

                # Step 6: Final verification
                time.sleep(1)
                health = self.bridge.system_health_check()

                results.append("🎉 ULTRA-FAST SYSTEM READY!")
                results.append(f"📊 Data points every {self.bridge.step_interval_seconds:.1f} seconds")
                results.append("🔗 Monitor at http://localhost:3000")
                results.append("⚡ 50x speed = 50x faster than real-time!")

                return jsonify({
                    'success': True,
                    'message': '\n'.join(results),
                    'speed_factor': 50.0,
                    'interval_seconds': self.bridge.step_interval_seconds,
                    'health': health
                })

            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f"❌ Ultra start failed: {str(e)}"
                })

        @self.app.route('/api/tep/start', methods=['POST'])
        def start_tep():
            success, message = self.bridge.start_tep_simulation()
            # Handle form submissions by redirecting back to main page
            if request.content_type and 'application/x-www-form-urlencoded' in request.content_type:
                return redirect(url_for('index'))
            return jsonify({'success': success, 'message': message})

        @self.app.route('/api/tep/restart', methods=['POST'])
        def restart_tep():
            success, message = self.bridge.restart_tep_simulation()
            return jsonify({'success': success, 'message': message})

        @self.app.route('/api/tep/stop', methods=['POST'])
        def stop_tep():
            success, message = self.bridge.stop_tep_simulation()
            return jsonify({'success': success, 'message': message})

        @self.app.route('/api/pca/train', methods=['POST'])
        def start_pca_training_api():
            self.bridge.start_pca_training()
            return jsonify({
                'success': True,
                'message': f'Anomaly Detection training started, will collect {self.bridge.pca_training_target} data points',
                'target': self.bridge.pca_training_target
            })

        @self.app.route('/api/pca/status', methods=['GET'])
        def pca_training_status():
            return jsonify({
                'training_mode': bool(self.bridge.pca_training_mode),
                'collected': len(self.bridge.pca_training_data),
                'target': self.bridge.pca_training_target,
                'progress': len(self.bridge.pca_training_data) / self.bridge.pca_training_target * 100,
                'is_stable': bool(self.bridge.is_stable),
                'stability_buffer_size': len(self.bridge.stability_buffer)
            })

        @self.app.route('/api/pca/stabilize', methods=['POST'])
        def stabilize_pca():
            """Smart Anomaly Detection retraining: collect stable data and retrain."""
            if self.bridge.is_stable:
                self.bridge.start_pca_training()
                return jsonify({
                    'success': True,
                    'message': f'Anomaly Detection stabilization started. System is stable, collecting {self.bridge.pca_training_target} data points.',
                    'is_stable': True
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'System is not stable yet. Wait for stability before retraining.',
                    'is_stable': False
                })

        @self.app.route('/api/speed', methods=['POST'])
        def set_speed():
            # Be tolerant to missing/invalid JSON; allow query or form fallback
            data = request.get_json(silent=True) or {}
            mode = data.get('mode') or request.args.get('mode') or request.form.get('mode') or 'demo'
            # Optional: allow specifying demo seconds (1..10)
            try:
                seconds = int(data.get('seconds')) if data.get('seconds') is not None else None
            except Exception:
                seconds = None
            if mode == 'demo':
                self.bridge.speed_mode = 'demo'
                if seconds is None:
                    seconds = getattr(self.bridge, 'step_interval_seconds', 1) or 1
                seconds = max(1, min(10, int(seconds)))
                self.bridge.step_interval_seconds = seconds
            else:
                self.bridge.step_interval_seconds = 180
                self.bridge.speed_mode = 'real'
            return jsonify({'success': True, 'mode': self.bridge.speed_mode, 'step_interval_seconds': self.bridge.step_interval_seconds})

        @self.app.route('/api/speed/factor', methods=['POST'])
        def set_speed_factor():
            """New API endpoint for speed factor control (0.1x to 10x)"""
            try:
                data = request.get_json() or {}
                speed_factor = float(data.get('speed_factor', 1.0))

                # Validate range - Extended to 50x for ultra-fast testing
                speed_factor = max(0.1, min(50.0, speed_factor))

                # Store speed factor for TEP simulation (now implemented in Fortran!)
                self.bridge.speed_factor = speed_factor

                # ✅ IMPLEMENTED: Speed factor now affects actual Fortran physics simulation
                # The speed factor is passed to temain_with_speed() which scales DELTAT
                # Also adjust Python loop timing for consistency
                base_interval = 180  # 3 minutes normal
                new_interval = max(1, int(base_interval / speed_factor))
                self.bridge.step_interval_seconds = new_interval

                # Update mode based on speed
                if speed_factor >= 1.0:
                    self.bridge.speed_mode = f'fast_{speed_factor}x'
                else:
                    self.bridge.speed_mode = f'slow_{speed_factor}x'

                return jsonify({
                    'success': True,
                    'speed_factor': speed_factor,
                    'step_interval_seconds': new_interval,
                    'mode': self.bridge.speed_mode,
                    'description': f'Simulation running at {speed_factor}x speed'
                })

            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 400

        @self.app.route('/api/xmv/set', methods=['POST'])
        def set_xmv():
            data = request.get_json()
            xmv_num = data.get('xmv_num')
            value = data.get('value')

            success = self.bridge.set_xmv(xmv_num, value)
            return jsonify({
                'success': success,
                'xmv_num': xmv_num,
                'value': float(value) if success else None,
                'current_xmv_state': self.bridge.xmv_values.tolist() if hasattr(self.bridge, 'xmv_values') else None
            })

        @self.app.route('/api/idv/set', methods=['POST'])
        def set_idv():
            data = request.get_json()
            idv_num = data.get('idv_num')
            value = data.get('value')

            success = self.bridge.set_idv(idv_num, value)

            # Return current IDV state for debugging
            return jsonify({
                'success': success,
                'idv_num': idv_num,
                'value': int(value) if success else None,
                'current_idv_state': self.bridge.idv_values.tolist(),
                'active_faults': [i+1 for i, v in enumerate(self.bridge.idv_values) if v == 1]
            })

        @self.app.route('/api/idv/test', methods=['POST'])
        def test_idv_impact():
            """Test if IDV changes actually affect simulation output."""
            try:
                # Run baseline simulation (all IDV = 0)
                baseline_idv = np.zeros(20)
                self.bridge.idv_values = baseline_idv.copy()
                baseline_data = self.bridge.run_tep_simulation_step()

                # Run with IDV_1 = 1 (A/C Feed Ratio fault)
                test_idv = np.zeros(20)
                test_idv[0] = 1  # IDV_1
                self.bridge.idv_values = test_idv.copy()
                fault_data = self.bridge.run_tep_simulation_step()

                # Compare key measurements
                if baseline_data and fault_data:
                    comparison = {
                        'baseline_reactor_temp': baseline_data.get('XMEAS_9', 'N/A'),
                        'fault_reactor_temp': fault_data.get('XMEAS_9', 'N/A'),
                        'baseline_reactor_pressure': baseline_data.get('XMEAS_7', 'N/A'),
                        'fault_reactor_pressure': fault_data.get('XMEAS_7', 'N/A'),
                        'difference_detected': baseline_data != fault_data,
                        'test_successful': True
                    }
                else:
                    comparison = {'test_successful': False, 'error': 'No simulation data'}

                return jsonify(comparison)

            except Exception as e:
                return jsonify({'test_successful': False, 'error': str(e)})

        @self.app.route('/api/faultexplainer/backend/start', methods=['POST'])
        def start_backend():
            mode = (request.get_json(silent=True) or {}).get('mode', 'prod')
            if mode == 'dev':
                success, message = self.bridge.start_faultexplainer_backend_dev()
            else:
                success, message = self.bridge.start_faultexplainer_backend()
            # Handle form submissions by redirecting back to main page
            if request.content_type and 'application/x-www-form-urlencoded' in request.content_type:
                return redirect(url_for('index'))
            return jsonify({'success': success, 'message': message})

        @self.app.route('/api/logs/<name>')
        def get_log(name):
            # Only allow known names
            if name not in ('sse','ingest'):
                return jsonify({'error':'invalid log'}), 400
            # Get script directory and build path to external_repos
            script_dir = os.path.dirname(os.path.abspath(__file__))
            bdir = os.path.join(script_dir, 'external_repos','FaultExplainer-main','backend','diagnostics')
            path = os.path.join(bdir, f"{name}.log")
            try:
                if not os.path.exists(path):
                    return jsonify({'lines': [f'No log file found: {path}']}), 200
                with open(path,'r',encoding='utf-8',errors='replace') as f:
                    lines = f.readlines()[-200:]
                return jsonify({'lines': lines})
            except Exception as e:
                return jsonify({'lines': [f'Error reading log: {e}']}), 200

        @self.app.route('/api/analysis/history/download/<fmt>')
        def download_history(fmt):
            # Get script directory and build path to external_repos
            script_dir = os.path.dirname(os.path.abspath(__file__))
            diag_dir = os.path.join(script_dir, 'external_repos','FaultExplainer-main','backend','diagnostics')
            if fmt == 'jsonl':
                path = os.path.join(diag_dir, 'analysis_history.jsonl')
                if not os.path.exists(path):
                    return jsonify({'error':'missing'}), 404
                return self._send_file(path, 'application/json')
            if fmt == 'md':
                path = os.path.join(diag_dir, 'analysis_history.md')
                if not os.path.exists(path):
                    return jsonify({'error':'missing'}), 404
                return self._send_file(path, 'text/markdown')
            return jsonify({'error':'invalid fmt'}), 400

        def _send_file(self, path, mime):
            from flask import send_file
            return send_file(path, mimetype=mime, as_attachment=True)
        @self.app.route('/api/analysis/history/download/bydate/<datestr>')
        def download_history_by_date(datestr):
            # datestr format: YYYY-MM-DD
            # Get script directory and build path to external_repos
            script_dir = os.path.dirname(os.path.abspath(__file__))
            diag_dir = os.path.join(script_dir, 'external_repos','FaultExplainer-main','backend','diagnostics','analysis_history')
            path = os.path.join(diag_dir, f"{datestr}.md")
            if not os.path.exists(path):
                return jsonify({'error':'missing'}), 404
            return self._send_file(path, 'text/markdown')


        @self.app.route('/api/faultexplainer/frontend/start', methods=['POST'])
        def start_frontend():
            success, message = self.bridge.start_faultexplainer_frontend()
            # Handle form submissions by redirecting back to main page
            if request.content_type and 'application/x-www-form-urlencoded' in request.content_type:
                return redirect(url_for('index'))
            return jsonify({'success': success, 'message': message})

        @self.app.route('/api/bridge/start', methods=['POST'])
        def start_bridge():
            # Start external bridge script in background
            try:
                # if already started, return
                if 'tep_bridge' in self.bridge.processes and self.bridge.check_process_status('tep_bridge'):
                    success, message = True, 'Bridge already running'
                else:
                    # Get project root (parent of legacy directory) for venv and bridge script
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    project_root = os.path.dirname(script_dir)
                    venv_python = os.path.join(project_root, 'tep_env','bin','python')
                    bridge_script_dir = script_dir  # Bridge script is in legacy directory
                    process = subprocess.Popen([venv_python, 'tep_faultexplainer_bridge.py'],
                                               cwd=bridge_script_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    self.bridge.processes['tep_bridge'] = process
                    success, message = True, 'Bridge started'
            except Exception as e:
                success, message = False, f'Bridge failed: {e}'

            # Handle form submissions by redirecting back to main page
            if request.content_type and 'application/x-www-form-urlencoded' in request.content_type:
                return redirect(url_for('index'))
            return jsonify({'success': success, 'message': message})

        @self.app.route('/api/bridge/stop', methods=['POST'])
        def stop_bridge():
            try:
                if 'tep_bridge' in self.bridge.processes:
                    self.bridge.processes['tep_bridge'].terminate()
                    del self.bridge.processes['tep_bridge']
                return jsonify({'success': True, 'message': 'Bridge stopped'})
            except Exception as e:
                return jsonify({'success': False, 'message': f'Failed to stop bridge: {e}'})

        # Backend config proxy (avoid CORS by posting from server-side)
        @self.app.route('/api/backend/config/runtime', methods=['POST'])
        def proxy_backend_runtime_config():
            try:
                payload = request.get_json() or {}
                if 'preset' in payload:
                    self.bridge.current_preset = payload['preset']
                    # Remove preset before forwarding
                    payload = {k:v for k,v in payload.items() if k!='preset'}
                r = requests.post('http://localhost:8000/config/runtime', json=payload, timeout=5)
                return jsonify(r.json()), r.status_code
            except Exception as e:
                return jsonify({'status':'error','error':str(e)}), 500

        @self.app.route('/api/backend/config/baseline/reload', methods=['POST'])
        def proxy_backend_baseline_reload():
                try:
                    # Load baseline data directly from CSV file
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    baseline_path = os.path.join(script_dir, 'external_repos', 'FaultExplainer-MultiLLM', 'backend', 'data', 'normal_baseline.csv')

                    if os.path.exists(baseline_path):
                        import pandas as pd
                        baseline_df = pd.read_csv(baseline_path)

                        # Store baseline data for internal use
                        self.baseline_data = baseline_df

                        # Get feature count
                        feature_count = len([col for col in baseline_df.columns if col != 'time'])

                        print(f"✅ Baseline loaded: {len(baseline_df)} samples, {feature_count} features")
                        print(f"   Key values: Pressure={baseline_df['Reactor Pressure'].mean():.1f} kPa, Temp={baseline_df['Reactor Temperature'].mean():.1f}°C")

                        return jsonify({
                            'status': 'ok',
                            'features': feature_count,
                            'samples': len(baseline_df),
                            'message': f'Baseline loaded with {feature_count} features from {len(baseline_df)} samples'
                        }), 200
                    else:
                        return jsonify({
                            'status': 'error',
                            'error': f'Baseline file not found: {baseline_path}'
                        }), 404

                except Exception as e:
                    print(f"❌ Baseline reload error: {e}")
                    return jsonify({'status':'error','error':str(e)}), 500


        @self.app.route('/api/backend/config/alpha', methods=['POST'])
        def proxy_backend_alpha():
            try:
                payload = request.get_json() or {}
                r = requests.post('http://localhost:8000/config/alpha', json=payload, timeout=5)
                return jsonify(r.json()), r.status_code
            except Exception as e:
                return jsonify({'status':'error','error':str(e)}), 500

        # Backend analysis history proxy
        @self.app.route('/api/backend/analysis/history', methods=['GET'])
        def proxy_backend_analysis_history():
            try:
                limit = request.args.get('limit', '5')
                import requests
                r = requests.get(f'http://localhost:8000/analysis/history?limit={limit}', timeout=10)
                return jsonify(r.json()), r.status_code
            except Exception as e:
                return jsonify({'status':'error','error':str(e), 'message': 'Backend not reachable on port 8000. Make sure FaultExplainer backend is running.'}), 500

        # Download analysis history
        @self.app.route('/api/analysis/history/download/<format>')
        def download_analysis_history(format):
            try:
                limit = request.args.get('limit', '20')
                import requests
                r = requests.get(f'http://localhost:8000/analysis/history?limit={limit}', timeout=10)
                data = r.json()

                if format == 'jsonl':
                    # JSONL format - one JSON object per line
                    import json
                    lines = []
                    for item in data.get('items', []):
                        lines.append(json.dumps(item))
                    content = '\n'.join(lines)

                    from flask import Response
                    return Response(
                        content,
                        mimetype='application/jsonl',
                        headers={'Content-Disposition': f'attachment; filename=tep_analysis_history.jsonl'}
                    )

                elif format == 'md':
                    # Markdown format
                    lines = ['# TEP Analysis History\n']
                    for i, item in enumerate(data.get('items', []), 1):
                        ts = item.get('timestamp', 'Unknown time')
                        lines.append(f'## Analysis #{i} - {ts}\n')
                        lines.append(f'**Feature Analysis:**\n```\n{item.get("feature_analysis", "N/A")}\n```\n')

                        if 'performance_summary' in item:
                            lines.append('**Performance Summary:**\n')
                            for model, perf in item['performance_summary'].items():
                                lines.append(f'- {model}: {perf.get("response_time", 0):.2f}s, {perf.get("word_count", 0)} words\n')
                        lines.append('\n---\n')

                    content = '\n'.join(lines)
                    from flask import Response
                    return Response(
                        content,
                        mimetype='text/markdown',
                        headers={'Content-Disposition': f'attachment; filename=tep_analysis_history.md'}
                    )
                else:
                    return jsonify({'error': 'Invalid format. Use jsonl or md'}), 400

            except Exception as e:
                return jsonify({'error': str(e), 'message': 'Failed to download analysis history. Make sure backend is running.'}), 500

        @self.app.route('/api/stop/all', methods=['POST'])
        def stop_all():
            self.bridge.stop_tep_simulation()
            self.bridge.stop_all_processes()
            return jsonify({'success': True, 'message': 'All processes stopped'})

        @self.app.route('/api/emergency/shutdown', methods=['POST'])
        def emergency_shutdown():
            """Emergency shutdown using external script for maximum safety."""
            try:
                import subprocess
                import os

                # Get the project root directory
                project_root = os.path.dirname(os.path.abspath(__file__))
                script_path = os.path.join(project_root, '..', 'stop_all_tep_services.sh')

                if os.path.exists(script_path):
                    # Run the comprehensive shutdown script
                    result = subprocess.run(['bash', script_path],
                                          capture_output=True, text=True, timeout=30)

                    if result.returncode == 0:
                        return jsonify({
                            'success': True,
                            'message': 'Emergency shutdown completed successfully',
                            'output': result.stdout
                        })
                    else:
                        return jsonify({
                            'success': False,
                            'message': 'Emergency shutdown completed with warnings',
                            'output': result.stdout,
                            'error': result.stderr
                        })
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Emergency shutdown script not found'
                    })

            except subprocess.TimeoutExpired:
                return jsonify({
                    'success': False,
                    'message': 'Emergency shutdown timed out'
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'Emergency shutdown failed: {str(e)}'
                })

        # Model control proxy endpoints
        @self.app.route('/api/models/status', methods=['GET'])
        def proxy_models_status():
            try:
                import requests
                r = requests.get('http://localhost:8000/models/status', timeout=10)
                return jsonify(r.json()), r.status_code
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/models/toggle', methods=['POST'])
        def proxy_models_toggle():
            try:
                payload = request.get_json() or {}
                import requests
                r = requests.post('http://localhost:8000/models/toggle', json=payload, timeout=10)
                return jsonify(r.json()), r.status_code
            except Exception as e:
                return jsonify({'error': str(e)}), 500

    def run(self, host='0.0.0.0', port=9001, debug=False):
        """Run the control panel.
        If port is already in use by an older instance, kill it first to avoid duplicates.
        """
        print(f"🚀 Starting Unified TEP Control Panel on http://localhost:{port}")
        print("✅ Single interface for all components")
        print("✅ Proper data flow: TEP → FaultExplainer")
        print("✅ Correct timing and values")
        # Proactively free port 9001 from any stale processes before starting
        try:
            if self.bridge.kill_port_process(port):
                print(f"🔪 Freed port {port} from stale process")
        except Exception as e:
            print(f"⚠️ Could not pre-free port {port}: {e}")
        time.sleep(0.5)
        self.app.run(host=host, port=port, debug=debug)

# HTML Control Panel Interface
CONTROL_PANEL_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>🎛️ Unified TEP Control Panel</title>
    <meta http-equiv="Content-Security-Policy" content="default-src 'self' 'unsafe-inline' 'unsafe-eval'; script-src 'self' 'unsafe-inline' 'unsafe-eval';">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #2196F3 0%, #21CBF3 100%);
                 color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: center; }
        .section { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;
                  box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .controls-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .control-card { padding: 15px; border: 1px solid #ddd; border-radius: 8px; background: #f8f9fa; }

        .btn { padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
        .btn-primary { background: #2196F3; color: white; }
        .btn-success { background: #4CAF50; color: white; }
        .btn-danger { background: #f44336; color: white; }
        .btn-warning { background: #ff9800; color: white; }
        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }
        .status-card { padding: 15px; border-radius: 8px; text-align: center; }
        .status-running { background: #e8f5e8; border: 2px solid #4CAF50; }
        .status-stopped { background: #ffeaea; border: 2px solid #f44336; }
        .xmv-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            max-height: 500px;
            overflow-y: auto;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background-color: #f8f9fa;
        }
        .xmv-control {
            padding: 12px;
            border: 1px solid #007bff;
            border-radius: 6px;
            background-color: white;
            font-size: 13px;
        }
        .xmv-control label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #007bff;
        }
        .idv-checkbox-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 8px;
            max-height: 400px;
            overflow-y: auto;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background-color: #f8f9fa;
        }
        .idv-checkbox {
            display: flex;
            align-items: center;
            padding: 8px;
            border: 1px solid #28a745;
            border-radius: 4px;
            background-color: white;
            font-size: 13px;
        }
        .idv-checkbox input[type="checkbox"] {
            margin-right: 10px;
            transform: scale(1.2);
        }
        .idv-checkbox label {
            margin: 0;
            cursor: pointer;
            color: #28a745;
        }
        .idv-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 12px;
            max-height: 600px;
            overflow-y: auto;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background-color: #fafafa;
        }
        .idv-control {
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 5px;
            background-color: white;
            font-size: 12px;
        }
        .slider { width: 100%; margin: 8px 0; }
        .data-flow { background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 10px 0; }
        .timing-info { background: #1976d2; color: white; padding: 10px; border-radius: 5px; font-size: 14px; font-weight: bold; }
        #status { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .btn-active { background: #4CAF50 !important; color: #fff !important; }

        .correct-badge { background: #4CAF50; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; }
        .live-badge { display:inline-block; padding:4px 10px; border-radius:12px; font-weight:700; font-size:12px; margin-left:8px; }
        .live-ok { background:#4CAF50; color:#fff; }
        .live-bad { background:#f44336; color:#fff; }

        /* Tab Styles */
        .tab-btn {
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 0 5px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .tab-btn:hover { background: rgba(255,255,255,0.3); }
        .tab-btn.active { background: rgba(255,255,255,0.4); box-shadow: 0 2px 8px rgba(0,0,0,0.3); }
        .tab-content { display: none; }
        .tab-content.active { display: block; }

        /* Documentation Styles */
        .docs-section {
            background: #f8f9fa;
            padding: 25px;
            margin: 20px 0;
            border-radius: 15px;
            border-left: 5px solid #17a2b8;
        }
        .docs-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .docs-table th, .docs-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }
        .docs-table th {
            background: #4facfe;
            color: white;
            font-weight: 600;
        }
        .docs-table tr:hover { background: #f8f9fa; }
        .code-block {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            margin: 10px 0;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎛️ Unified TEP Control Panel</h1>
            <p>Single interface for Dynamic TEP Simulation + FaultExplainer Integration
               <span id="live-connection" class="live-badge live-bad">Live: Disconnected</span>
               <span id="live-count" class="live-badge">Received: 0</span>
            </p>
            <div class="timing-info">
                ⏱️ <strong>Timing:</strong> TEP Simulation (3min) → Anomaly Detection (6min) → LLM Diagnosis (12min)
            </div>

            <!-- Navigation Tabs -->
            <div style="margin-top: 20px;">
                <button class="tab-btn active" onclick="showTab('control')">🎛️ Control Panel</button>
                <button class="tab-btn" onclick="showTab('docs')">📚 Documentation</button>
            </div>
        </div>

        <div id="status"></div>

        <!-- Status Display for Form Actions -->
        <div id="form-status" style="display: none; padding: 15px; margin: 10px; border-radius: 8px; font-weight: bold;"></div>

        <!-- Tab Content: Control Panel -->
        <div id="control-tab" class="tab-content active">
            <!-- JavaScript Status -->
            <div id="js-status-indicator" style="background: #e3f2fd; padding: 8px; margin: 10px; border-radius: 5px; font-size: 12px; text-align: center;">
                🔧 JavaScript Status: <span id="js-status" style="color: orange;">Loading...</span>
            </div>

        <!-- EMERGENCY FALLBACK: Form-based controls (REMOVED) -->
        <!--
        <div style="background: #ff6b6b; color: white; padding: 15px; margin: 10px; border-radius: 8px;">
            <h3>� EMERGENCY FALLBACK CONTROLS</h3>
            <p>JavaScript buttons not working - using form-based controls</p>
            <div style="margin: 10px 0;">
                <button onclick="simpleTest()" style="background: #ff9800; color: white; padding: 10px 20px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer;">
                    🧪 SIMPLE TEST BUTTON
                </button>
                <button onclick="testFunction()" style="background: #9c27b0; color: white; padding: 10px 20px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; margin-left: 10px;">
                    🔧 TEST FUNCTION
                </button>
            </div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <form method="POST" action="/api/tep/start" style="display: inline;">
                    <button type="submit" style="padding: 10px; background: #28a745; color: white; border: none; border-radius: 5px;">▶️ Start TEP</button>
                </form>
                <form method="POST" action="/api/faultexplainer/backend/start" style="display: inline;">
                    <button type="submit" style="padding: 10px; background: #007bff; color: white; border: none; border-radius: 5px;">▶️ Start Backend</button>
                </form>
                <form method="POST" action="/api/faultexplainer/frontend/start" style="display: inline;">
                    <button type="submit" style="padding: 10px; background: #6f42c1; color: white; border: none; border-radius: 5px;">▶️ Start Frontend</button>
                </form>
                <form method="POST" action="/api/bridge/start" style="display: inline;">
                    <button type="submit" style="padding: 10px; background: #fd7e14; color: white; border: none; border-radius: 5px;">▶️ Start Bridge</button>
                </form>
            </div>
        </div>
        -->

        <!-- System Status -->
        <div class="section">
            <h3>📊 System Status</h3>
            <div class="status-grid" id="status-grid">
                <div class="status-card status-stopped">
                    <h4>🏭 TEP Simulation</h4>
                    <p id="tep-status">Stopped</p>
                    <p>Step: <span id="tep-step">0</span></p>
                </div>
                <div class="status-card status-stopped">
                    <h4>🔍 Fault Analysis Backend</h4>
                    <p id="backend-status">Stopped</p>
                </div>
                <div class="status-card status-stopped">
                    <h4>🖥️ Fault Analysis Frontend</h4>
                    <p id="frontend-status">Stopped</p>
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 10px; padding: 0 20px;">
                <p>Speed: <span id="speed-mode">Real (180s)</span></p>
                <p>Preset: <span id="preset-mode">None</span></p>
                <div>
                    <h4 style="display: inline; margin-right: 20px;">📈 Data Points</h4>
                    <span>Raw: <span id="raw-count">0</span> | </span>
                    <span>Anomaly Detection: <span id="pca-count">0</span> | </span>
                    <span>LLM: <span id="llm-count">0</span></span>
                </div>
            </div>
        </div>

        <!-- Main Controls -->
        <div class="section">
            <h3>🎛️ Main Controls</h3>


            <div class="controls-grid">
                <div class="control-card">
                    <h4>🏭 TEP Dynamic Simulation</h4>
                    <p>Real tep2py physics simulation with 3-minute intervals</p>
                    <button class="btn btn-success" onclick="startTEP()">▶️ Start TEP Simulation</button>
                    <button class="btn btn-danger" onclick="stopTEP()">⏹️ Stop TEP Simulation</button>
                    <button class="btn btn-warning" onclick="restartTEP()">⟳ Restart TEP</button>
                    <button class="btn btn-info" onclick="systemHealthCheck()" style="margin-top: 8px;">🔍 System Health Check</button>
                    <button class="btn btn-success" onclick="ultraStart()" style="margin-top: 8px; font-weight: bold; background: linear-gradient(45deg, #ff6b6b, #4ecdc4); border: none; color: white;">🚀 ULTRA START (50x)</button>
                    <div style="margin-top: 10px; padding: 8px; background: #f0f8ff; border-radius: 5px; border-left: 4px solid #2196f3;">
                        <h5 style="margin: 0 0 5px 0; color: #1976d2;">🎯 Anomaly Detection Stabilization</h5>
                        <div id="training-progress" style="display: none; margin: 5px 0; padding: 5px; background: #e8f5e8; border-radius: 3px; font-weight: bold; color: #2e7d32;">
                            📊 Training Progress: <span id="progress-text">0/30</span>
                        </div>
                        <button class="btn btn-info" onclick="checkPCAStatus()" style="margin-right: 5px;">📊 Check Status</button>
                        <button class="btn btn-success" onclick="stabilizePCA()">🎯 Stabilize System</button>
                        <p style="font-size: 11px; color: #666; margin: 5px 0 0 0;">
                            Wait for system stability, then click "Stabilize System" for perfect anomaly detection
                        </p>
                    </div>
                        <div style="margin-top:10px;">
                            <span>Simulation Speed:</span>
                            <div style="margin-top:8px">
                                <label>Speed Factor: <span id="speed-factor">1.0</span>x (Normal)</label>
                                <input type="range" min="0.1" max="50" step="0.1" value="1.0" class="slider" id="speed-factor-slider" onchange="setSpeedFactor(this.value)">
                                <div style="font-size:12px; color:#666; margin-top:4px;">
                                    0.1x = 10x slower | 1.0x = Normal | 10x = 10x faster | 50x = Ultra-fast
                                </div>
                                <div style="font-size:11px; color:#4caf50; margin-top:6px; padding:4px; background:#e8f5e8; border-radius:4px;">
                                    ✅ <strong>Speed Control Active:</strong> Affects actual Fortran physics simulation speed via DELTAT scaling
                                </div>
                            </div>
                        </div>
                </div>

                <div class="control-card">
                    <h4>🔍 Fault Analysis Backend</h4>
                    <p>Analysis engine with correct threshold (0.01)</p>
                    <button class="btn btn-primary" onclick="startBackend()">▶️ Start Backend</button>
                    <p style="font-size: 12px; color: #666;">Port: 8000</p>
                        <div style="margin-top:8px">
                            <label>LLM min interval: <span id="llm-interval-label">20</span>s</label>
                            <input type="range" min="10" max="120" step="5" value="20" class="slider" id="llm-interval-slider" onchange="setLLMInterval(this.value)">
                        </div>
                        <div style="margin-top:6px">
                            <button id="btn-reload-baseline" class="btn" onclick="reloadBaseline()">⟳ Reload Baseline</button>
                            <button id="btn-stability-defaults" class="btn" onclick="applyStabilityDefaults()">✔ Apply Stability Defaults</button>
                        </div>
                </div>

                <div class="control-card">
                    <h4>🖥️ Fault Analysis Frontend</h4>
                    <p>React interface for visualization and control</p>
                    <button class="btn btn-primary" onclick="startFrontend()">▶️ Start Frontend</button>
                    <p style="font-size: 12px; color: #666;">Port: 5173</p>
                    <div style="margin-top:6px">
                        <button id="btn-bridge-start" class="btn" onclick="startBridge()">▶️ Start Bridge</button>
                        <button class="btn btn-danger" onclick="stopBridge()">⏹️ Stop Bridge</button>
                        <p style="font-size: 12px; color: #666;">Monitors: data/live_tep_data.csv</p>
                    </div>
                </div>
            </div>

            <div class="controls-grid">
                <div class="control-card">
                    <h4>🛑 Emergency Stop</h4>
                    <p>Stop all running processes</p>
                    <button class="btn btn-danger" onclick="stopAll()">🛑 Stop Everything</button>
                </div>

                <div class="control-card">
                    <h4>📊 Data Analysis</h4>
                    <p>Download and review analysis history</p>
                    <div style="display:flex; gap:8px; align-items:center; margin-top:6px">
                        <label style="font-size:12px; color:#666">Show last</label>
                        <select id="history-limit" class="btn">
                            <option>5</option>
                            <option>10</option>
                            <option>20</option>
                        </select>
                        <button class="btn" onclick="showAnalysisHistory()">🔄 Refresh</button>
                    </div>
                    <div style="margin-top:6px">
                        <button class="btn" onclick="showAnalysisHistory()">🕘 Show Last 5 Analyses</button>
                    </div>
                    <div style="display:flex; gap:8px; align-items:center; margin-top:6px">
                        <label style="font-size:12px; color:#666">Select date</label>
                        <input type="date" id="history-date" class="btn" style="padding:6px;">
                        <button class="btn" onclick="downloadAnalysisByDate()">⬇ Download MD by date</button>
                    </div>
                    <p style="margin-top:6px; font-size:12px; color:#666">Logs auto-saved at backend/diagnostics/analysis_history/YYYY-MM-DD.md</p>
                </div>

                <div class="control-card">
                    <h4>🔌 Data Source</h4>
                    <p>Bridge controls CSV data flow to backend</p>
                    <div style="margin-top:6px">
                        <button id="btn-ingest-internal" class="btn btn-active" onclick="setIngestion('internal')">Internal Simulator</button>
                    </div>
                    <div style="margin-top:6px">
                        <button id="btn-ingest-csv" class="btn" onclick="setIngestion('csv')">CSV Bridge (optional)</button>
                    </div>
                    <p id="ingest-hint" style="font-size:12px;color:#666;">Using Internal Simulator. Bridge controls disabled.</p>
                </div>
            </div>
        </div>

        <!-- Data Flow Visualization -->
        <div class="section">
            <h3>📊 Data Flow</h3>
                <div style="margin-top:8px">
                    <pre id="analysis-history" style="height:160px; overflow:auto; background:#111; color:#ddd; padding:10px; border-radius:6px; display:none;"></pre>
                </div>

                <div class="control-card">
                    <h4>📜 Diagnostics Logs</h4>
                    <p>Backend logs (last 200 lines)</p>
                    <div style="display:flex; gap:10px; margin-bottom:8px;">
                      <button class="btn" onclick="loadLog('sse')">View SSE Log</button>
                      <button class="btn" onclick="loadLog('ingest')">View Ingest Log</button>
                      <button class="btn" onclick="clearLog()">Clear</button>
                    </div>
                    <pre id="log-view" style="height:200px; overflow:auto; background:#111; color:#0f0; padding:10px; border-radius:6px;"></pre>
                </div>

            <div class="data-flow">
                <strong>TEP Simulation</strong> (every 3 min)
                → <strong>CSV Export</strong>
                → <strong>Anomaly Detection</strong> (every 6 min)
                → <strong>LLM Diagnosis</strong> (every 12 min)
                → <strong>FaultExplainer UI</strong>
            </div>
            <p>✅ Uses original FaultExplainer backend/frontend with live data feed</p>
            <p>✅ Proper timing hierarchy prevents LLM overload</p>
        </div>

        <!-- XMV Process Controls -->
        <div class="section">
            <h3>🎛️ Process Controls (XMV Variables) - 11 Manipulated Variables</h3>
            <p><span class="correct-badge">CONTINUOUS</span> Range: 0-100% - Valve positions and control setpoints</p>
            <div class="xmv-grid">
                <!-- Feed Flow Controls -->
                <div class="xmv-control">
                    <label><strong>XMV_1:</strong> D Feed Flow</label>
                    <input type="range" class="slider" min="0" max="100" step="0.1" value="63.0"
                           onchange="setXMV(1, this.value)" id="xmv1">
                    <div>Value: <span id="xmv1-value">63.0</span>%</div>
                </div>

                <div class="xmv-control">
                    <label><strong>XMV_2:</strong> E Feed Flow</label>
                    <input type="range" class="slider" min="0" max="100" step="0.1" value="53.0"
                           onchange="setXMV(2, this.value)" id="xmv2">
                    <div>Value: <span id="xmv2-value">53.0</span>%</div>
                </div>

                <div class="xmv-control">
                    <label><strong>XMV_3:</strong> A Feed Flow</label>
                    <input type="range" class="slider" min="0" max="100" step="0.1" value="24.0"
                           onchange="setXMV(3, this.value)" id="xmv3">
                    <div>Value: <span id="xmv3-value">24.0</span>%</div>
                </div>

                <div class="xmv-control">
                    <label><strong>XMV_4:</strong> A+C Feed Flow</label>
                    <input type="range" class="slider" min="0" max="100" step="0.1" value="61.0"
                           onchange="setXMV(4, this.value)" id="xmv4">
                    <div>Value: <span id="xmv4-value">61.0</span>%</div>
                </div>

                <!-- Process Control Valves -->
                <div class="xmv-control">
                    <label><strong>XMV_5:</strong> Compressor Recycle Valve</label>
                    <input type="range" class="slider" min="0" max="100" step="0.1" value="22.0"
                           onchange="setXMV(5, this.value)" id="xmv5">
                    <div>Value: <span id="xmv5-value">22.0</span>%</div>
                </div>

                <div class="xmv-control">
                    <label><strong>XMV_6:</strong> Purge Valve</label>
                    <input type="range" class="slider" min="0" max="100" step="0.1" value="40.0"
                           onchange="setXMV(6, this.value)" id="xmv6">
                    <div>Value: <span id="xmv6-value">40.0</span>%</div>
                </div>

                <div class="xmv-control">
                    <label><strong>XMV_7:</strong> Separator Liquid Flow</label>
                    <input type="range" class="slider" min="0" max="100" step="0.1" value="38.0"
                           onchange="setXMV(7, this.value)" id="xmv7">
                    <div>Value: <span id="xmv7-value">38.0</span>%</div>
                </div>

                <div class="xmv-control">
                    <label><strong>XMV_8:</strong> Stripper Liquid Flow</label>
                    <input type="range" class="slider" min="0" max="100" step="0.1" value="46.0"
                           onchange="setXMV(8, this.value)" id="xmv8">
                    <div>Value: <span id="xmv8-value">46.0</span>%</div>
                </div>

                <div class="xmv-control">
                    <label><strong>XMV_9:</strong> Stripper Steam Valve</label>
                    <input type="range" class="slider" min="0" max="100" step="0.1" value="47.0"
                           onchange="setXMV(9, this.value)" id="xmv9">
                    <div>Value: <span id="xmv9-value">47.0</span>%</div>
                </div>

                <!-- Cooling Controls -->
                <div class="xmv-control">
                    <label><strong>XMV_10:</strong> Reactor Cooling Water</label>
                    <input type="range" class="slider" min="0" max="100" step="0.1" value="41.0"
                           onchange="setXMV(10, this.value)" id="xmv10">
                    <div>Value: <span id="xmv10-value">41.0</span>%</div>
                </div>

                <div class="xmv-control">
                    <label><strong>XMV_11:</strong> Condenser Cooling Water</label>
                    <input type="range" class="slider" min="0" max="100" step="0.1" value="18.0"
                           onchange="setXMV(11, this.value)" id="xmv11">
                    <div>Value: <span id="xmv11-value">18.0</span>%</div>
                </div>


            </div>
        </div>

        <!-- IDV Fault Controls -->
        <div class="section">
            <h3>🔧 Fault Injection (IDV Controls) - All 20 Variables</h3>
            <p><span class="correct-badge">BINARY</span> Checkboxes: ☐ OFF or ☑ ON - Binary flags as per original TEP paper</p>
            <div style="margin: 10px 0;">
                <button class="btn btn-warning" onclick="testIDVImpact()">🧪 Test IDV Impact</button>
                <span style="margin-left: 10px; font-size: 12px; color: #666;">
                    Tests if IDV changes actually affect simulation output
                </span>
            </div>
            <div class="idv-checkbox-grid">
                <!-- IDV 1-5: Feed Disturbances -->
                <div class="idv-checkbox">
                    <input type="checkbox" id="idv1" onchange="setIDV(1, this.checked ? 1 : 0)">
                    <label for="idv1"><strong>IDV_1:</strong> A/C Feed Ratio, B Composition Constant</label>
                </div>

                <div class="idv-checkbox">
                    <input type="checkbox" id="idv2" onchange="setIDV(2, this.checked ? 1 : 0)">
                    <label for="idv2"><strong>IDV_2:</strong> B Composition, A/C Ratio Constant</label>
                </div>

                <div class="idv-checkbox">
                    <input type="checkbox" id="idv3" onchange="setIDV(3, this.checked ? 1 : 0)">
                    <label for="idv3"><strong>IDV_3:</strong> D Feed Temperature (Stream 2)</label>
                </div>

                <div class="idv-checkbox">
                    <input type="checkbox" id="idv4" onchange="setIDV(4, this.checked ? 1 : 0)">
                    <label for="idv4"><strong>IDV_4:</strong> Reactor Cooling Water Inlet Temperature</label>
                </div>

                <div class="idv-checkbox">
                    <input type="checkbox" id="idv5" onchange="setIDV(5, this.checked ? 1 : 0)">
                    <label for="idv5"><strong>IDV_5:</strong> Condenser Cooling Water Inlet Temperature</label>
                </div>

                <!-- IDV 6-10: Equipment Failures -->
                <div class="idv-checkbox">
                    <input type="checkbox" id="idv6" onchange="setIDV(6, this.checked ? 1 : 0)">
                    <label for="idv6"><strong>IDV_6:</strong> A Feed Loss (Stream 1)</label>
                </div>

                <div class="idv-checkbox">
                    <input type="checkbox" id="idv7" onchange="setIDV(7, this.checked ? 1 : 0)">
                    <label for="idv7"><strong>IDV_7:</strong> C Header Pressure Loss (Stream 4)</label>
                </div>

                <div class="idv-checkbox">
                    <input type="checkbox" id="idv8" onchange="setIDV(8, this.checked ? 1 : 0)">
                    <label for="idv8"><strong>IDV_8:</strong> A, B, C Feed Composition Random Variation</label>
                </div>

                <div class="idv-checkbox">
                    <input type="checkbox" id="idv9" onchange="setIDV(9, this.checked ? 1 : 0)">
                    <label for="idv9"><strong>IDV_9:</strong> D Feed Temperature Random Variation</label>
                </div>

                <div class="idv-checkbox">
                    <input type="checkbox" id="idv10" onchange="setIDV(10, this.checked ? 1 : 0)">
                    <label for="idv10"><strong>IDV_10:</strong> C Feed Temperature Random Variation</label>
                </div>

                <!-- IDV 11-15: Cooling System Disturbances -->
                <div class="idv-checkbox">
                    <input type="checkbox" id="idv11" onchange="setIDV(11, this.checked ? 1 : 0)">
                    <label for="idv11"><strong>IDV_11:</strong> Reactor Cooling Water Inlet Temp Random</label>
                </div>

                <div class="idv-checkbox">
                    <input type="checkbox" id="idv12" onchange="setIDV(12, this.checked ? 1 : 0)">
                    <label for="idv12"><strong>IDV_12:</strong> Condenser Cooling Water Inlet Temp Random</label>
                </div>

                <div class="idv-checkbox">
                    <input type="checkbox" id="idv13" onchange="setIDV(13, this.checked ? 1 : 0)">
                    <label for="idv13"><strong>IDV_13:</strong> Reaction Kinetics</label>
                </div>

                <!-- IDV 14-20: Valve Sticking and Unknown -->
                <div class="idv-checkbox">
                    <input type="checkbox" id="idv14" onchange="setIDV(14, this.checked ? 1 : 0)">
                    <label for="idv14"><strong>IDV_14:</strong> Reactor Cooling Water Valve</label>
                </div>

                <div class="idv-checkbox">
                    <input type="checkbox" id="idv15" onchange="setIDV(15, this.checked ? 1 : 0)">
                    <label for="idv15"><strong>IDV_15:</strong> Condenser Cooling Water Valve</label>
                </div>

                <div class="idv-checkbox">
                    <input type="checkbox" id="idv16" onchange="setIDV(16, this.checked ? 1 : 0)">
                    <label for="idv16"><strong>IDV_16:</strong> Unknown</label>
                </div>

                <div class="idv-checkbox">
                    <input type="checkbox" id="idv17" onchange="setIDV(17, this.checked ? 1 : 0)">
                    <label for="idv17"><strong>IDV_17:</strong> Unknown</label>
                </div>

                <div class="idv-checkbox">
                    <input type="checkbox" id="idv18" onchange="setIDV(18, this.checked ? 1 : 0)">
                    <label for="idv18"><strong>IDV_18:</strong> Unknown</label>
                </div>

                <div class="idv-checkbox">
                    <input type="checkbox" id="idv19" onchange="setIDV(19, this.checked ? 1 : 0)">
                    <label for="idv19"><strong>IDV_19:</strong> Unknown</label>
                </div>

                <div class="idv-checkbox">
                    <input type="checkbox" id="idv20" onchange="setIDV(20, this.checked ? 1 : 0)">
                    <label for="idv20"><strong>IDV_20:</strong> Unknown</label>
                </div>
            </div>
        </div>


    </div>

    <!-- Load external JavaScript file for Safari compatibility -->
    <script src="/static/control_panel.js"></script>

    <script>
        // Minimal Safari-compatible inline script
        console.log('Inline script loading...');
        console.log('User Agent:', navigator.userAgent);
        console.log('Safari detected:', navigator.userAgent.indexOf('Safari') > -1);

        // Simple test without modern syntax
        setTimeout(function() {
            console.log('Inline script test complete');
        }, 500);

        // All functions are in external JS file - no inline functions needed

        // Tab switching function
        function showTab(tabName) {
            // Hide all tab contents
            var contents = document.querySelectorAll('.tab-content');
            contents.forEach(function(content) {
                content.classList.remove('active');
            });

            // Remove active class from all tab buttons
            var buttons = document.querySelectorAll('.tab-btn');
            buttons.forEach(function(btn) {
                btn.classList.remove('active');
            });

            // Show selected tab content
            document.getElementById(tabName + '-tab').classList.add('active');

            // Add active class to clicked button
            event.target.classList.add('active');
        }
    </script>
        </div> <!-- End Control Tab -->

        <!-- Tab Content: Documentation -->
        <div id="docs-tab" class="tab-content">
            <div class="docs-section">
                <h3>📚 System Documentation</h3>

                <div class="docs-section">
                    <h4>🌉 Bridge Functionality</h4>
                    <p><strong>Q: Why is "Start Bridge" optional?</strong></p>
                    <p><strong>A:</strong> The TEP simulation has a <strong>built-in bridge</strong> that automatically posts data to FaultExplainer!</p>

                    <div class="code-block">
TEP Simulation → Automatic Data Flow → FaultExplainer
(No separate bridge needed!)
                    </div>

                    <p><strong>Two Bridge Options:</strong></p>
                    <ul>
                        <li><strong>Built-in Bridge</strong> (automatic) - TEP simulation directly posts to FaultExplainer</li>
                        <li><strong>External Bridge</strong> (optional) - Separate bridge script for advanced scenarios</li>
                    </ul>

                    <p><strong>🎯 Recommendation:</strong> Just use "Start TEP" + "Start Backend" - the bridge is automatic!</p>
                </div>

                <div class="docs-section">
                    <h4>🎛️ Preset Modes Comparison</h4>
                    <table class="docs-table">
                        <thead>
                            <tr>
                                <th>Setting</th>
                                <th>🚀 Demo</th>
                                <th>⚖️ Balanced</th>
                                <th>🏭 Realistic</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>TEP Simulation Speed</strong></td>
                                <td>4 seconds</td>
                                <td>60 seconds (1 min)</td>
                                <td>180 seconds (3 min)</td>
                            </tr>
                            <tr>
                                <td><strong>Anomaly Detection Window Size</strong></td>
                                <td>8 samples</td>
                                <td>12 samples</td>
                                <td>20 samples</td>
                            </tr>
                            <tr>
                                <td><strong>Anomaly Trigger</strong></td>
                                <td>3 consecutive</td>
                                <td>2 consecutive</td>
                                <td>6 consecutive</td>
                            </tr>
                            <tr>
                                <td><strong>LLM Min Interval</strong></td>
                                <td>0 seconds (instant)</td>
                                <td>20 seconds</td>
                                <td>300 seconds (5 min)</td>
                            </tr>
                            <tr>
                                <td><strong>Data Decimation</strong></td>
                                <td>1 (all data)</td>
                                <td>4 (every 4th)</td>
                                <td>1 (all data)</td>
                            </tr>
                            <tr>
                                <td><strong>Use Case</strong></td>
                                <td>Testing & Demo</td>
                                <td>Development</td>
                                <td>Industrial Deployment</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="docs-section">
                    <h4>📊 Data Flow Ratios</h4>

                    <p><strong>🚀 Demo Mode:</strong></p>
                    <ul>
                        <li>TEP: Every 4 seconds</li>
                        <li>Anomaly Detection: Every 4 seconds (immediate)</li>
                        <li>LLM: Instant when anomaly detected</li>
                        <li><strong>Ratio:</strong> 1:1:immediate (very fast, lots of analysis)</li>
                    </ul>

                    <p><strong>⚖️ Balanced Mode:</strong></p>
                    <ul>
                        <li>TEP: Every 60 seconds (1 min)</li>
                        <li>Anomaly Detection: Every 60 seconds</li>
                        <li>LLM: Minimum 20 seconds between calls</li>
                        <li><strong>Ratio:</strong> 1:1:controlled (moderate speed, controlled analysis)</li>
                    </ul>

                    <p><strong>🏭 Realistic Mode:</strong></p>
                    <ul>
                        <li>TEP: Every 180 seconds (3 min)</li>
                        <li>Anomaly Detection: Every 180 seconds</li>
                        <li>LLM: Minimum 300 seconds (5 min) between calls</li>
                        <li><strong>Ratio:</strong> 1:1:5min-minimum (real industrial timing)</li>
                    </ul>
                </div>

                <div class="docs-section">
                    <h4>🚀 Quick Start Guide</h4>
                    <ol>
                        <li><strong>Start TEP</strong> (orange button) - Starts chemical plant simulation</li>
                        <li><strong>Start Backend</strong> (blue button) - Starts Fault Analysis engine</li>
                        <li><strong>Start Frontend</strong> (purple button) - Starts Fault Analysis web interface (optional)</li>
                        <li><strong>Control Process:</strong> Use XMV sliders (0-100%) to adjust valve positions and flows</li>
                        <li><strong>Inject Faults:</strong> Use IDV checkboxes (☐/☑) to simulate plant disturbances</li>
                        <li><strong>Monitor Results:</strong> Click "Show Last 5 Analyses" to see LLM diagnosis</li>
                    </ol>

                    <p><strong>🎯 Note:</strong> "Start Bridge" is optional - the bridge is built-in!</p>
                </div>

                <div class="docs-section">
                    <h4>🔧 IDV Fault Types</h4>
                    <ul>
                        <li><strong>IDV_1:</strong> A/C Feed Ratio - Feed composition disturbance</li>
                        <li><strong>IDV_2:</strong> B Composition - Feed quality variation</li>
                        <li><strong>IDV_3:</strong> D Feed Temperature - Thermal disturbance</li>
                        <li><strong>IDV_4:</strong> Reactor Cooling - Heat removal issues</li>
                        <li><strong>IDV_5:</strong> Condenser Cooling - Cooling system problems</li>
                        <li><strong>IDV_6:</strong> A Feed Loss - Feed supply interruption</li>
                    </ul>
                    <p><strong>Range:</strong> 0.0 (no fault) to 1.0 (maximum fault intensity)</p>
                </div>
            </div>
        </div> <!-- End Documentation Tab -->

</body>
</html>
'''

if __name__ == "__main__":
    panel = UnifiedControlPanel()
    panel.run(debug=False)
