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
from flask import Flask, render_template_string, jsonify, request, redirect, url_for
import requests

# --- Helpers: resolve tools cross-platform and venv-aware ---

def resolve_venv_python():
    """Prefer .venv over tep_env. Return absolute python path for current OS."""
    cwd = os.getcwd()
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
        self.setup_tep2py()

        # Simulation state
        self.tep_running = False
        self.current_step = 0
        self.idv_values = np.zeros(20)  # 20 IDV inputs (0.0 to 1.0 range)
        # Maintain a time-series of IDV rows so the simulator advances over time
        # Rather than simulating a single step repeatedly (which yields a constant output)
        from collections import deque as _deque
        self.idv_history = _deque(maxlen=1200)  # ~1 day of 3-min steps

        # Data queues with proper timing
        self.raw_data_queue = deque(maxlen=1000)  # Every 3 minutes (raw TEP)
        self.pca_data_queue = deque(maxlen=500)   # Every 6 minutes (half speed)
        self.llm_data_queue = deque(maxlen=250)   # Every 12 minutes (quarter speed)

        # Timing control
        self.last_pca_time = 0
        self.last_llm_time = 0
        self.pca_interval = 6 * 60  # 6 minutes in seconds
        self.llm_interval = 12 * 60  # 12 minutes in seconds
        # Simulation step interval (default: real-time 3 minutes)
        self.step_interval_seconds = 180
        self.speed_mode = 'real'  # 'demo' or 'real'
        self.current_preset = None  # 'demo' or 'real'

        # Process management
        self.processes = {}

        # Heartbeat and CSV stats
        self.last_loop_at = 0
        self.last_ingest_at = 0
        self.last_ingest_ok = False
        self.csv_rows = 0
        self.csv_bytes = 0
        # Diagnostics
        self.last_error = ""
        self.last_ingest_info = {}

        print("✅ TEP Data Bridge initialized")
        print("✅ Timing: TEP(3min) → Anomaly Detection(6min) → LLM(12min)")

    def setup_tep2py(self):
        """Setup real tep2py simulator."""
        try:
            tep_path = os.path.join(os.getcwd(), 'external_repos', 'tep2py-master')
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


    def set_idv(self, idv_num, value):
        """Set IDV value (1-20, range 0.0-1.0)."""
        if 1 <= idv_num <= 20 and 0.0 <= value <= 1.0:
            self.idv_values[idv_num - 1] = value
            print(f"🔧 Set IDV_{idv_num} = {value:.2f}")
            return True
        return False

    def run_tep_simulation_step(self):
        """Run one TEP simulation step (3 minutes)."""
        try:
            if not self.tep2py:
                return None

            # Append current IDV to history and build matrix up to 'now'
            self.idv_history.append(self.idv_values.copy())
            import numpy as _np2
            idv_matrix = _np2.array(list(self.idv_history)).reshape(-1, 20)

            # Run TEP simulation for the whole history and take the latest row
            tep_sim = self.tep2py.tep2py(idv_matrix)
            tep_sim.simulate()

            if hasattr(tep_sim, 'process_data'):
                # Get latest data point
                latest = tep_sim.process_data.iloc[-1]

                # Extract XMEAS and XMV
                xmeas_cols = [col for col in tep_sim.process_data.columns if 'XMEAS' in col]
                xmv_cols = [col for col in tep_sim.process_data.columns if 'XMV' in col]

                # Create data point
                data_point = {
                    'timestamp': time.time(),
                    'step': self.current_step,
                    'idv_values': self.idv_values.copy(),
                }

                # Add XMEAS data
                for i, col in enumerate(xmeas_cols):
                    data_point[f'XMEAS_{i+1}'] = latest[col]

                # Add XMV data
                for i, col in enumerate(xmv_cols):
                    data_point[f'XMV_{i+1}'] = latest[col]

                return data_point

        except Exception as e:
            print(f"❌ TEP simulation step failed: {e}")
            return None

    def save_data_for_faultexplainer(self, data_point):
        """Save data in FaultExplainer format."""
        try:
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

            # Update simple CSV stats
            try:
                self.csv_rows += 1
                self.csv_bytes = os.path.getsize(csv_path)
            except Exception:
                pass

            print(f"💾 Saved data point {data_point['step']} to {csv_path}")
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

                    # Also send to live /ingest for real-time PCA+LLM
                    print("➡️ Posting /ingest...")
                    self.send_to_ingest(data_point)

                    # Check if time for PCA analysis (every 6 minutes)
                    current_time = time.time()
                    if current_time - self.last_pca_time >= self.pca_interval:
                        self.pca_data_queue.append(data_point)
                        self.last_pca_time = current_time
                        print(f"📊 PCA data point added (step {self.current_step})")

                        # Check if time for LLM analysis (every 12 minutes)
                        if current_time - self.last_llm_time >= self.llm_interval:
                            self.llm_data_queue.append(data_point)
                            self.last_llm_time = current_time
                            print(f"🤖 LLM data point added (step {self.current_step})")

                    self.current_step += 1

                # Wait for next step (demo or real-time)
                print("💤 Sleeping for next step...")
                time.sleep(self.step_interval_seconds)

            except Exception as e:
                self.last_error = f"loop: {e}"
                print(f"❌ Simulation loop error: {e}")
                time.sleep(10)

        print("🛑 TEP simulation loop stopped")

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
            self.last_pca_time = 0
            self.last_llm_time = 0
            self.last_loop_at = 0
            self.last_ingest_at = 0
            self.last_ingest_ok = False
            self.csv_rows = 0
            self.csv_bytes = 0
            # Start fresh
            self.tep_running = True
            self.simulation_thread = threading.Thread(target=self.simulation_loop, daemon=True)
            self.simulation_thread.start()
            return True, "TEP simulation restarted"
        except Exception as e:
            return False, f"Failed to restart TEP: {e}"

        return True, "TEP simulation started"

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
            backend_path = os.path.join(os.getcwd(), 'external_repos', 'FaultExplainer-main', 'backend')

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
            backend_path = os.path.join(os.getcwd(), 'external_repos', 'FaultExplainer-main', 'backend')
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
            frontend_path = os.path.join(os.getcwd(), 'external_repos', 'FaultExplainer-main', 'frontend')

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
        """Stop all running processes."""
        for name, process in self.processes.items():
            try:
                process.terminate()
                print(f"🛑 Stopped {name}")
            except:
                pass
        self.processes.clear()

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

class UnifiedControlPanel:
    """Unified control panel for TEP system."""

    def __init__(self):
        self.app = Flask(__name__)
        self.bridge = TEPDataBridge()
        self.setup_routes()
        print("✅ Unified Control Panel initialized")

    def setup_routes(self):
        """Setup Flask routes."""

        @self.app.route('/')
        def index():
            return render_template_string(CONTROL_PANEL_HTML)

        @self.app.route('/api/status')
        def get_status():
            return jsonify(self.bridge.get_status())

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

        @self.app.route('/api/idv/set', methods=['POST'])
        def set_idv():
            data = request.get_json()
            idv_num = data.get('idv_num')
            value = data.get('value')

            success = self.bridge.set_idv(idv_num, value)
            return jsonify({'success': success})

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
            bdir = os.path.join(os.getcwd(), 'external_repos','FaultExplainer-main','backend','diagnostics')
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
            diag_dir = os.path.join(os.getcwd(), 'external_repos','FaultExplainer-main','backend','diagnostics')
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
            diag_dir = os.path.join(os.getcwd(), 'external_repos','FaultExplainer-main','backend','diagnostics','analysis_history')
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
                    process = subprocess.Popen([os.path.join(os.getcwd(), 'tep_env','bin','python'), 'tep_faultexplainer_bridge.py'],
                                               cwd=os.getcwd(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
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
                    payload = request.get_json(silent=True) or {}
                    import requests
                    r = requests.post('http://localhost:8000/config/baseline/reload', json=payload, timeout=5)
                    return jsonify(r.json()), r.status_code
                except Exception as e:
                    return jsonify({'status':'error','error':str(e)}), 500


        @self.app.route('/api/backend/config/alpha', methods=['POST'])
        def proxy_backend_alpha():
            try:
                payload = request.get_json() or {}
                r = requests.post('http://localhost:8000/config/alpha', json=payload, timeout=5)
                return jsonify(r.json()), r.status_code
            except Exception as e:
                return jsonify({'status':'error','error':str(e)}), 500

        @self.app.route('/api/stop/all', methods=['POST'])
        def stop_all():
            self.bridge.stop_tep_simulation()
            self.bridge.stop_all_processes()
            return jsonify({'success': True, 'message': 'All processes stopped'})

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
        .idv-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .idv-control { padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        .slider { width: 100%; margin: 8px 0; }
        .data-flow { background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 10px 0; }
        .timing-info { background: #1976d2; color: white; padding: 10px; border-radius: 5px; font-size: 14px; font-weight: bold; }
        #status { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .btn-active { background: #4CAF50 !important; color: #fff !important; }

        .correct-badge { background: #4CAF50; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; }
        .live-badge { display:inline-block; padding:4px 10px; border-radius:12px; font-weight:700; font-size:12px; margin-left:8px; }
        .live-ok { background:#4CAF50; color:#fff; }
        .live-bad { background:#f44336; color:#fff; }
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
        </div>

        <div id="status"></div>

        <!-- Status Display for Form Actions -->
        <div id="form-status" style="display: none; padding: 15px; margin: 10px; border-radius: 8px; font-weight: bold;"></div>

        <!-- EMERGENCY FALLBACK: Form-based controls -->
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

        <!-- System Status -->
        <div class="section">
            <h3>📊 System Status</h3>
            <div class="status-grid" id="status-grid">
                <div class="status-card status-stopped">
                    <h4>🏭 TEP Simulation</h4>
                    <p id="tep-status">Stopped</p>
                    <p>Step: <span id="tep-step">0</span></p>
                </div>
                    <p>Speed: <span id="speed-mode">Real (180s)</span></p>
                    <p>Preset: <span id="preset-mode">None</span></p>

                <div class="status-card status-stopped">
                    <h4>🔍 FaultExplainer Backend</h4>
                    <p id="backend-status">Stopped</p>
                </div>
                <div class="status-card status-stopped">
                    <h4>🖥️ FaultExplainer Frontend</h4>
                    <p id="frontend-status">Stopped</p>
                </div>
                <div class="status-card">
                    <h4>📈 Data Points</h4>
                    <p>Raw: <span id="raw-count">0</span></p>
                    <p>Anomaly Detection: <span id="pca-count">0</span></p>
                    <p>LLM: <span id="llm-count">0</span></p>
                </div>
            </div>
        </div>

        <!-- Main Controls -->
        <div class="section">
            <h3>🎛️ Main Controls</h3>
            <div class="control-card">
                <h4>🔌 Ingestion Source</h4>
                <p>Select one source for live data. CSV Bridge is only for external CSV producer.</p>
                <div>
                    <button id="btn-ingest-internal" class="btn btn-active" onclick="setIngestion('internal')">Internal Simulator</button>
                    <button id="btn-ingest-csv" class="btn" onclick="setIngestion('csv')">CSV Bridge (optional)</button>
                </div>
                <p id="ingest-hint" style="font-size:12px;color:#666;">Using Internal Simulator. Bridge controls disabled.</p>
            </div>

            <div class="controls-grid">
                <div class="control-card">
                    <h4>🏭 TEP Dynamic Simulation</h4>
                    <p>Real tep2py physics simulation with 3-minute intervals</p>
                    <button class="btn btn-success" onclick="startTEP()">▶️ Start TEP Simulation</button>
                    <button class="btn btn-danger" onclick="stopTEP()">⏹️ Stop TEP Simulation</button>
                        <div style="margin-top:10px;">
                            <span>Speed:</span>
                            <button id="btn-speed-demo" class="btn" onclick="setSpeed('demo')">Demo (1s)</button>
                            <button id="btn-speed-real" class="btn" onclick="setSpeed('real')">Real (3min)</button>
                            <div style="margin-top:8px">
                                <label>Demo interval: <span id="demo-interval">1</span>s</label>
                                <input type="range" min="1" max="10" step="1" value="1" class="slider" id="demo-interval-slider" onchange="setDemoInterval(this.value)">
                            </div>
                        </div>
                        <div style="margin-top:10px;">
                            <button id="btn-preset-demo" class="btn" onclick="setPreset('demo')">Set Backend Preset: Demo</button>
                            <button id="btn-preset-balanced" class="btn" onclick="setPreset('balanced')">Set Backend Preset: Balanced</button>
                            <button id="btn-preset-real" class="btn" onclick="setPreset('real')">Set Backend Preset: Realistic</button>
                        </div>

                </div>

                <div class="control-card">
                    <h4>🔍 FaultExplainer Backend</h4>
                    <p>Analysis engine with correct threshold (0.01)</p>
                    <button class="btn btn-primary" onclick="startBackend()">▶️ Start Backend</button>
                        <div style="margin-top:6px">
                            <button class="btn" onclick="checkBaselineStatus()">🔎 Check Baseline Status</button>
                        </div>

                    <p style="font-size: 12px; color: #666;">Port: 8000</p>
                        <div style="margin-top:6px">
                            <button class="btn btn-warning" onclick="restartTEP()">⟳ Restart TEP</button>
                        </div>
                        <div style="margin-top:8px">
                            <label>LLM min interval: <span id="llm-interval-label">20</span>s</label>
                            <input type="range" min="10" max="120" step="5" value="20" class="slider" id="llm-interval-slider" onchange="setLLMInterval(this.value)">
                        </div>

                                <div style="display:flex; gap:8px; align-items:center; margin-top:6px">
                                    <label style="font-size:12px; color:#666">Select date</label>
                                    <input type="date" id="history-date" class="btn" style="padding:6px;">
                                    <button class="btn" onclick="downloadAnalysisByDate()">⬇ Download MD by date</button>
                                </div>
                                <p style="margin-top:6px; font-size:12px; color:#666">Logs auto-saved at backend/diagnostics/analysis_history/YYYY-MM-DD.md</p>

                        <div style="margin-top:6px">
                            <button id="btn-reload-baseline" class="btn" onclick="reloadBaseline()">⟳ Reload Baseline</button>
                        </div>
                        <div style="margin-top:6px">
                            <button id="btn-stability-defaults" class="btn" onclick="applyStabilityDefaults()">✔ Apply Stability Defaults</button>
                        </div>

                            <div style="display:flex; gap:8px; align-items:center; margin-top:6px">
                                <label style="font-size:12px; color:#666">Show last</label>
                                <select id="history-limit" class="btn">
                                    <option>5</option>
                                    <option>10</option>
                                    <option>20</option>
                                </select>
                                <button class="btn" onclick="showAnalysisHistory()">🔄 Refresh</button>
                                <button class="btn" onclick="copyAnalysisHistory()">📋 Copy</button>
                                <button class="btn" onclick="downloadAnalysis('jsonl')">⬇ Download JSONL</button>
                                <button class="btn" onclick="downloadAnalysis('md')">⬇ Download MD</button>
                            </div>


                            <div style="margin-top:6px">
                                <button class="btn" onclick="showAnalysisHistory()">🕘 Show Last 5 Analyses</button>
                            </div>





                </div>

                <div class="control-card">
                    <h4>🖥️ FaultExplainer Frontend</h4>
                    <p>React interface for visualization and control</p>
                <div class="control-card">
                    <h4>🌉 TEP→FaultExplainer Bridge</h4>
                    <p>Connect live CSV to backend /ingest</p>
                    <button id="btn-bridge-start" class="btn" onclick="startBridge()">▶️ Start Bridge</button>
                    <button class="btn btn-danger" onclick="stopBridge()">⏹️ Stop Bridge</button>
                    <p style="font-size: 12px; color: #666;">Monitors: data/live_tep_data.csv</p>
                </div>

                    <button class="btn btn-primary" onclick="startFrontend()">▶️ Start Frontend</button>
                    <p style="font-size: 12px; color: #666;">Port: 5173</p>
                </div>

                <div class="control-card">
                    <h4>🛑 Emergency Stop</h4>
                    <p>Stop all running processes</p>
                    <button class="btn btn-danger" onclick="stopAll()">🛑 Stop Everything</button>
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

        <!-- IDV Fault Controls -->
        <div class="section">
            <h3>🔧 Fault Injection (IDV Controls)</h3>
            <p><span class="correct-badge">CORRECTED</span> Range: 0.0 to 1.0 (standard TEP values)</p>
            <div class="idv-grid">
                <div class="idv-control">
                    <label><strong>IDV_1:</strong> A/C Feed Ratio</label>
                    <input type="range" class="slider" min="0" max="1" step="0.1" value="0"
                           onchange="setIDV(1, this.value)" id="idv1">
                    <div>Value: <span id="idv1-value">0.0</span></div>
                </div>

                <div class="idv-control">
                    <label><strong>IDV_4:</strong> Reactor Cooling</label>
                    <input type="range" class="slider" min="0" max="1" step="0.1" value="0"
                           onchange="setIDV(4, this.value)" id="idv4">
                    <div>Value: <span id="idv4-value">0.0</span></div>
                </div>

                <div class="idv-control">
                    <label><strong>IDV_6:</strong> A Feed Loss</label>
                    <input type="range" class="slider" min="0" max="1" step="0.1" value="0"
                           onchange="setIDV(6, this.value)" id="idv6">
                    <div>Value: <span id="idv6-value">0.0</span></div>
                </div>

                <div class="idv-control">
                    <label><strong>IDV_8:</strong> A,B,C Composition</label>
                    <input type="range" class="slider" min="0" max="1" step="0.1" value="0"
                           onchange="setIDV(8, this.value)" id="idv8">
                    <div>Value: <span id="idv8-value">0.0</span></div>
                </div>

                <div class="idv-control">
                    <label><strong>IDV_13:</strong> Reaction Kinetics</label>
                    <input type="range" class="slider" min="0" max="1" step="0.1" value="0"
                           onchange="setIDV(13, this.value)" id="idv13">
                    <div>Value: <span id="idv13-value">0.0</span></div>
                </div>
            </div>
        </div>

        <!-- Quick Links -->
        <div class="section">
            <h3>🔗 Quick Access</h3>
            <p>Once started, access components directly:</p>
            <button class="btn btn-primary" onclick="window.open('http://localhost:5173', '_blank')">
                🖥️ Open FaultExplainer UI
            </button>
            <button class="btn btn-primary" onclick="window.open('http://localhost:8000', '_blank')">
                🔍 Open Backend API
            </button>
        </div>
    </div>

    <script>
        console.log('Control Panel JS loading...');
        console.log('JavaScript is working - Control Panel loaded!');
        console.log('User Agent:', navigator.userAgent);
        console.log('Safari detected:', navigator.userAgent.indexOf('Safari') > -1);

        // Safari compatibility polyfills
        if (!Array.prototype.forEach) {
            Array.prototype.forEach = function(callback, thisArg) {
                for (var i = 0; i < this.length; i++) {
                    callback.call(thisArg, this[i], i, this);
                }
            };
        }

        // Test if JavaScript is working - Safari compatible
        try {
            var statusEl = document.getElementById('status');
            if (statusEl) {
                statusEl.innerHTML = '<div style="background: green; color: white; padding: 10px; margin: 10px;">✅ JavaScript is WORKING!</div>';
            }
            var debugEl = document.getElementById('js-status');
            if (debugEl) {
                debugEl.textContent = 'JavaScript loaded successfully - Safari compatible';
                debugEl.parentNode.style.background = '#c8e6c9';
            }
            console.log('✅ JavaScript test passed');
        } catch(e) {
            console.error('❌ JavaScript test failed:', e);
            alert('JavaScript Error: ' + e.message);
        }

        function testFunction() {
            console.log('testFunction() executed');
            alert('Test function works!');
            showMessage('Test function works!', 'success');
        }

        // Add a simple test button that should definitely work
        function simpleTest() {
            alert('Simple test button clicked!');
            console.log('Simple test button clicked!');
            var statusEl = document.getElementById('status');
            if (statusEl) {
                statusEl.innerHTML = '<div style="background: blue; color: white; padding: 10px;">Button clicked at ' + new Date().toLocaleTimeString() + '</div>';
            }
        }

        function updateStatusCardColor(statusId, isRunning) {
            const statusElement = document.getElementById(statusId);
            const card = statusElement.closest('.status-card');
            if (card) {
                card.className = isRunning ? 'status-card status-running' : 'status-card status-stopped';
            }
        }

        function updateStatus() {
            console.log('updateStatus() called');
            fetch('/api/status')
                .then(function(response) { return response.json(); })
                .then(function(data) {
                    console.log('Status data received:', data);
                    // Update TEP status
                    document.getElementById('tep-status').textContent = data.tep_running ? 'Running' : 'Stopped';
                    document.getElementById('tep-step').textContent = data.current_step;

                    // Update backend/frontend/bridge status
                    document.getElementById('backend-status').textContent = data.backend_running ? 'Running' : 'Stopped';
                    document.getElementById('frontend-status').textContent = data.frontend_running ? 'Running' : 'Stopped';

                    // Update speed/preset/bridge button badges
                    if (data.step_interval_seconds !== undefined) {
                        document.getElementById('speed-mode').textContent = (data.speed_mode === 'demo') ? 'Demo (' + data.step_interval_seconds + 's)' : 'Real (180s)';
                            const di = document.getElementById('demo-interval'); if (di) di.textContent = data.step_interval_seconds;
                            const ds = document.getElementById('demo-interval-slider'); if (ds && data.speed_mode==='demo') ds.value = data.step_interval_seconds;
                        document.getElementById('btn-speed-demo').classList.toggle('btn-active', data.speed_mode==='demo');
                        document.getElementById('btn-speed-real').classList.toggle('btn-active', data.speed_mode!=='demo');
                    }
                    if (data.current_preset) {
                        const label = (data.current_preset === 'demo') ? 'Demo' : (data.current_preset === 'balanced') ? 'Balanced' : 'Realistic';
                        document.getElementById('preset-mode').textContent = label;
                        document.getElementById('btn-preset-demo').classList.toggle('btn-active', data.current_preset==='demo');
                        const bp = document.getElementById('btn-preset-balanced'); if (bp) bp.classList.toggle('btn-active', data.current_preset==='balanced');
                        document.getElementById('btn-preset-real').classList.toggle('btn-active', data.current_preset==='real');
                    }
                    // Bridge button shows green when running
                    const hasBridgeBtn = document.getElementById('btn-bridge-start');
                    if (hasBridgeBtn) {
                        document.getElementById('btn-bridge-start').classList.toggle('btn-active', !!data.bridge_running);
                    }

                    // Update status card colors
                    updateStatusCardColor('tep-status', data.tep_running);
                    updateStatusCardColor('backend-status', data.backend_running);
                    updateStatusCardColor('frontend-status', data.frontend_running);

                    // Update data counts
                    document.getElementById('raw-count').textContent = data.raw_data_points;
                    document.getElementById('pca-count').textContent = data.pca_data_points;
                    document.getElementById('llm-count').textContent = data.llm_data_points;

                    // Live connection badge from backend counters
                    const liveBadge = document.getElementById('live-connection');
                    const liveCount = document.getElementById('live-count');
                    if (data.backend_aggregated_count !== null && data.backend_aggregated_count !== undefined) {
                        liveCount.textContent = 'Received: ' + data.backend_aggregated_count;
                        const connected = data.backend_aggregated_count > 1 || (data.last_ingest_ok && data.backend_aggregated_count >= 1);
                        liveBadge.textContent = connected ? 'Live: Connected' : 'Live: Disconnected';
                        liveBadge.className = connected ? 'live-badge live-ok' : 'live-badge live-bad';
                    }

                    // Update IDV values
                    for (let i = 0; i < data.idv_values.length; i++) {
                        const idvNum = i + 1;
                        if ([1, 4, 6, 8, 13].includes(idvNum)) {
                            const slider = document.getElementById('idv' + idvNum);
                            const valueSpan = document.getElementById('idv' + idvNum + '-value');
                            if (slider && valueSpan) {
                                slider.value = data.idv_values[i];
                                valueSpan.textContent = data.idv_values[i].toFixed(1);
                            }
                        }
                    }
                })
                .catch(function(error) { console.error('Status update failed:', error); });
        }

        function showMessage(message, type = 'info') {
            console.log('showMessage:', message, type);
            const statusDiv = document.getElementById('status');
            if (!statusDiv) {
                console.error('Status div not found!');
                alert(message); // Fallback
                return;
            }
            statusDiv.textContent = message;
            statusDiv.className = type === 'success' ? 'btn-success' :
                                 type === 'error' ? 'btn-danger' : 'btn-primary';
            statusDiv.style.display = 'block';
            statusDiv.style.padding = '15px';
            statusDiv.style.borderRadius = '8px';
            statusDiv.style.marginBottom = '20px';
            statusDiv.style.fontWeight = 'bold';

            // Auto-hide after 5 seconds
            setTimeout(function() {
                statusDiv.style.display = 'none';
            }, 5000);
        }

        function startTEP() {
            const btns = document.querySelectorAll("button[onclick*='startTEP']");
            btns.forEach(function(b) { if (b) b.disabled = true; });
            fetch('/api/tep/start', {method: 'POST'})
                .then(function(response) { return response.json(); })
                .then(function(data) {
                    showMessage(data.message, data.success ? 'success' : 'error');
                    if (data.success) {
                        btns.forEach(function(b) {
                            b.classList.add('btn-success');
                            setTimeout(function() { b.classList.remove('btn-success'); }, 800);
                        });
                    }
                })
                .catch(function(e) { showMessage('Start TEP failed: ' + e,'error'); })
                .finally(function() { btns.forEach(function(b) { if (b) b.disabled = false; }); });
        }

            function loadLog(name){
              fetch(`/api/logs/${name}`).then(r=>r.json()).then(d=>{
                const el = document.getElementById('log-view');
                el.textContent = (d.lines||[]).join('');
                el.scrollTop = el.scrollHeight;
              }).catch(e=>{
                showMessage('Failed to load log: ' + e,'error');
              });
            }
            function clearLog(){
              const el = document.getElementById('log-view');
              el.textContent = '';
            }

        function stopTEP() {
            var btns = document.querySelectorAll("button[onclick*='stopTEP']");
            btns.forEach(function(b) { if (b) b.disabled = true; });
            fetch('/api/tep/stop', {method: 'POST'})
                .then(function(response) { return response.json(); })
                .then(function(data) {
                    showMessage(data.message, data.success ? 'success' : 'error');
                    if (data.success) {
                        btns.forEach(function(b) {
                            b.classList.add('btn-success');
                            setTimeout(function() { b.classList.remove('btn-success'); }, 800);
                        });
                    }
                })
                .catch(function(e) { showMessage('Stop TEP failed: ' + e,'error'); })
                .finally(function() { btns.forEach(function(b) { if (b) b.disabled = false; }); });
        }

        function startBackend() {
            console.log('startBackend() called');
            const btns = document.querySelectorAll("button[onclick*='startBackend']");
            console.log('Found buttons:', btns.length);
            btns.forEach(function(b) { if (b) b.disabled = true; });

            fetch('/api/faultexplainer/backend/start', {method: 'POST'})
                .then(function(response) {
                    console.log('Backend response:', response.status);
                    return response.json();
                })
                .then(function(data) {
                    console.log('Backend data:', data);
                    showMessage(data.message, data.success ? 'success' : 'error');
                    if (data.success) {
                        btns.forEach(function(b) {
                            b.classList.add('btn-success');
                            setTimeout(function() { b.classList.remove('btn-success'); }, 800);
                        });
                    }
                    // Force status update
                    setTimeout(updateStatus, 1000);
                })
                .catch(function(e) {
                    console.error('Backend error:', e);
                    showMessage('Backend start failed: ' + e, 'error');
                })
                .finally(function() { btns.forEach(function(b) { if (b) b.disabled = false; }); });
        }
        function startBridge(){
            fetch('/api/bridge/start', {method: 'POST'})
              .then(function(r) { return r.json(); })
              .then(function(d) { showMessage(d.message, d.success? 'success':'error'); })
              .catch(function(e) { showMessage('Bridge start failed: ' + e, 'error'); });
        }
        function stopBridge(){
            fetch('/api/bridge/stop', {method: 'POST'})
              .then(r=>r.json())
              .then(d=>showMessage(d.message, d.success? 'success':'error'))
              .catch(e=>showMessage('Bridge stop failed: ' + e, 'error'));
        }


        function restartTEP(){
            fetch('/api/tep/restart',{method:'POST'})
              .then(r=>r.json())
              .then(d=>showMessage(d.message, d.success? 'success':'error'))
              .catch(e=>showMessage('Restart failed: ' + e,'error'));
        }

        function startFrontend() {
            var btns = document.querySelectorAll("button[onclick*='startFrontend']");
            btns.forEach(function(b) { if (b) b.disabled = true; });
            fetch('/api/faultexplainer/frontend/start', {method: 'POST'})
                .then(function(response) { return response.json(); })
                .then(function(data) {
                    showMessage(data.message, data.success ? 'success' : 'error');
                    if (data.success) {
                        btns.forEach(function(b) {
                            b.classList.add('btn-success');
                            setTimeout(function() { b.classList.remove('btn-success'); }, 800);
                        });
                    }
                })
                .catch(function(e) { showMessage('Frontend start failed: ' + e, 'error'); })
                .finally(function() { btns.forEach(function(b) { if (b) b.disabled = false; }); });
        }


        function setSpeed(mode) {
            fetch('/api/speed', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({mode: mode})
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                showMessage('Speed set to ' + data.mode + ' (' + data.step_interval_seconds + 's/step)', 'success');
                document.getElementById('speed-mode').textContent = data.mode === 'demo' ? 'Demo (' + data.step_interval_seconds + 's)' : 'Real (180s)';
                var di = document.getElementById('demo-interval');
                if (di) di.textContent = data.step_interval_seconds;
                var ds = document.getElementById('demo-interval-slider');
                if (ds && data.mode==='demo') ds.value = data.step_interval_seconds;
                document.getElementById('btn-speed-demo').classList.toggle('btn-active', data.mode==='demo');
                document.getElementById('btn-speed-real').classList.toggle('btn-active', data.mode!=='demo');
            })
            .catch(function(e) { showMessage('Speed update failed: ' + e, 'error'); });
        }

        function setPreset(mode){
            var demo = {
                pca_window_size: 8,
                fault_trigger_consecutive_step: 3,
                decimation_N: 1,
                llm_min_interval_seconds: 0
            };
            var balanced = {
                // Balanced demo: readable and responsive
                decimation_N: 4,
                pca_window_size: 12,
                fault_trigger_consecutive_step: 2,
                llm_min_interval_seconds: 20,
                feature_shift_min_interval_seconds: 60,
                feature_shift_jaccard_threshold: 0.8
            };
            var real = {
                pca_window_size: 20,
                fault_trigger_consecutive_step: 6,
                decimation_N: 1,
                llm_min_interval_seconds: 300
            };
            var cfg = mode==='demo' ? demo : (mode==='balanced' ? balanced : real);
            // Add preset to config object
            cfg.preset = mode;
            fetch('/api/backend/config/runtime',{
                method:'POST', headers:{'Content-Type':'application/json'},
                body: JSON.stringify(cfg)
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                showMessage('Backend runtime config updated: ' + JSON.stringify(data.updated),'success');
                var label = mode==='demo' ? 'Demo' : (mode==='balanced' ? 'Balanced' : 'Realistic');
                document.getElementById('preset-mode').textContent = label;
                document.getElementById('btn-preset-demo').classList.toggle('btn-active', mode==='demo');
                var bp = document.getElementById('btn-preset-balanced');
                if (bp) bp.classList.toggle('btn-active', mode==='balanced');
                document.getElementById('btn-preset-real').classList.toggle('btn-active', mode==='real');
            })
            .catch(function(e) { showMessage('Config update failed: ' + e,'error'); });
        }

        function setDemoInterval(sec){
            var seconds = parseInt(sec);
            fetch('/api/speed',{
                method:'POST', headers:{'Content-Type':'application/json'},
                body: JSON.stringify({mode:'demo', seconds: seconds})
            })
            .then(function(r) { return r.json(); })
            .then(function(d) {
                document.getElementById('demo-interval').textContent = d.step_interval_seconds;
                document.getElementById('speed-mode').textContent = 'Demo (' + d.step_interval_seconds + 's)';
                showMessage('Demo interval set to ' + d.step_interval_seconds + 's', 'success');
            })
            .catch(function(e) { showMessage('Failed to set interval: ' + e,'error'); });
        }

        function setLLMInterval(sec){
            var seconds = parseInt(sec);
            fetch('/api/backend/config/runtime',{
                method:'POST', headers:{'Content-Type':'application/json'},
                body: JSON.stringify({ llm_min_interval_seconds: seconds })
            })
            .then(function(r) { return r.json(); })
            .then(function(_) {
                var lab = document.getElementById('llm-interval-label');
                if (lab) lab.textContent = seconds;
                showMessage('LLM refresh interval set to ' + seconds + 's', 'success');
            })
            .catch(function(e) { showMessage('Failed to set LLM interval: ' + e,'error'); });
        }

            function applyStabilityDefaults(){
                const payload = {
                    llm_min_interval_seconds: 70,
                    feature_shift_min_interval_seconds: 999,
                    feature_shift_jaccard_threshold: 1.0
                };
                const btn = document.getElementById('btn-stability-defaults');
                if (btn) { btn.disabled = true; btn.classList.add('btn-active'); }
                fetch('/api/backend/config/runtime',{
                    method:'POST', headers:{'Content-Type':'application/json'},
                    body: JSON.stringify(payload)
                }).then(async r=>{ try { return await r.json(); } catch(e){ const t=await r.text(); throw new Error(`Non-JSON (${r.status}): ${t.slice(0,160)}`);} })
                .then(_=>{
                    showMessage(`Stability defaults applied`, 'success');
                    if (btn) { btn.classList.add('btn-success'); setTimeout(()=>btn.classList.remove('btn-success'), 1200); }
                })
                .catch(e=>showMessage(`Failed to apply defaults: ${e}`,'error'))
                .finally(()=>{ if (btn) { btn.disabled = false; btn.classList.remove('btn-active'); }});
            }

            async function checkBaselineStatus(){
                try{
                    const r = await fetch('http://localhost:8000/metrics');
                    const data = await r.json();
                    showMessage(`Backend ok. live_buffer=${data.live_buffer}, window=${data.pca_window}, baseline_features=${data.baseline_features}`, 'success');
                }catch(e){
                    showMessage(`Metrics check failed: ${e}`, 'error');
                }
            }

            function setIngestion(mode){
                const internal = mode==='internal';
                document.getElementById('btn-ingest-internal').classList.toggle('btn-active', internal);
                document.getElementById('btn-ingest-csv').classList.toggle('btn-active', !internal);
                const hint = document.getElementById('ingest-hint');
                hint.textContent = internal ? 'Using Internal Simulator. Bridge controls disabled.' : 'Using CSV Bridge. Internal Simulator controls disabled.';
                const simButtons = [
                    ...document.querySelectorAll("button[onclick*='startTEP'], button[onclick*='stopTEP']")
                ];
                const bridgeButtons = [
                    document.getElementById('btn-bridge-start'),
                    ...document.querySelectorAll("button[onclick*='stopBridge']")
                ];
                simButtons.forEach(b=>{ if (b) b.disabled = !internal; });
                bridgeButtons.forEach(b=>{ if (b) b && (b.disabled = internal); });
            }

            function reloadBaseline(){
                const btn = document.getElementById('btn-reload-baseline');
                if (btn) { btn.disabled = true; btn.classList.add('btn-active'); }
                fetch('/api/backend/config/baseline/reload',{
                    method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({})
                }).then(async r=>{ const t = await r.text(); try { return JSON.parse(t); } catch(e){ return {status:'error', error:`Non-JSON (${r.status}): ${t.slice(0,160)}`}; } })
                .then(data=>{
                    if(data.status==='ok') {
                        showMessage(`Baseline reloaded (${data.features} features)`, 'success');
                        if (btn) { btn.classList.add('btn-success'); setTimeout(()=>btn.classList.remove('btn-success'), 1200); }
                    } else {
                        showMessage(`Baseline reload error: ${data.error}`, 'error');

            function downloadAnalysisByDate(){
                const inp = document.getElementById('history-date');
                if (!inp || !inp.value){
                    showMessage('Please select a date','error');
                    return;
                }
                const ds = inp.value; // YYYY-MM-DD
                window.location = `/api/analysis/history/download/bydate/${ds}`;
            }

                    }
                }).catch(e=>showMessage(`Baseline reload failed: ${e}`,'error'))
                .finally(()=>{ if (btn) { btn.disabled = false; btn.classList.remove('btn-active'); }});
            }

            async function showAnalysisHistory(){
                try{
                    const limitSel = document.getElementById('history-limit');
                    const limit = limitSel ? parseInt(limitSel.value) : 5;
                    const r = await fetch(`http://localhost:8000/analysis/history?limit=${limit}`);
                    const data = await r.json();
                    const box = document.getElementById('analysis-history');
                    if (!box) return;
                    if (!data.items || !data.items.length){
                        box.textContent = '(no history yet)';
                    } else {
                        const lines = data.items.map((it, idx)=>{
                            const ts = it.timestamp || new Date((it.time||0)*1000).toLocaleTimeString();
                            const header = `#${idx+1} — ${ts}`;
                            const summary = it.performance_summary ? JSON.stringify(it.performance_summary) : '';
                            return `${header}\n${it.feature_analysis || ''}\n${summary}\n`;
                        });
                        box.textContent = lines.join('\n-------------------------------------\n');
                    }
                    box.style.display = 'block';
                }catch(e){
                    showMessage(`Failed to load analysis history: ${e}`, 'error');
                }
            }

            async function copyAnalysisHistory(){
                try{
                    const limitSel = document.getElementById('history-limit');
                    const limit = limitSel ? parseInt(limitSel.value) : 5;
                    const r = await fetch(`http://localhost:8000/analysis/history?limit=${limit}`);
                    const data = await r.json();
                    const lines = (data.items||[]).map((it, idx)=>{
                        const ts = it.timestamp || new Date((it.time||0)*1000).toLocaleTimeString();
                        const header = `#${idx+1} — ${ts}`;
                        return `${header}\n${it.feature_analysis || ''}`;
                    }).join('\n\n');
                    await navigator.clipboard.writeText(lines);
                    showMessage('Copied analysis history to clipboard','success');
                }catch(e){ showMessage(`Copy failed: ${e}`,'error'); }
            }

            function downloadAnalysis(fmt){
                window.location = `/api/analysis/history/download/${fmt}`;
            }


        function stopAll() {
            fetch('/api/stop/all', {method: 'POST'})
                .then(function(response) { return response.json(); })
                .then(function(data) { showMessage(data.message, 'success'); });
        }

        function setIDV(idvNum, value) {
            document.getElementById('idv' + idvNum + '-value').textContent = parseFloat(value).toFixed(1);

            fetch('/api/idv/set', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({idv_num: idvNum, value: parseFloat(value)})
            })
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data.success) {
                    showMessage('IDV_' + idvNum + ' set to ' + value, 'success');
                }
            });
        }

        // Initialize after all functions are defined
        console.log('Control Panel JS loaded - initializing...');

        // Auto-refresh status every 5 seconds
        setInterval(updateStatus, 5000);
        updateStatus(); // Initial load

        console.log('Status updates started');
    </script>
</body>
</html>
'''

if __name__ == "__main__":
    panel = UnifiedControlPanel()
    panel.run(debug=False)
