#!/usr/bin/env python3
"""
Unified TEP Control Panel - Clean Version v2
Single interface for Dynamic TEP Simulation + FaultExplainer Integration

Features:
- Built-in data bridge (no separate bridge needed)
- Three preset modes: Demo, Balanced, Realistic
- IDV fault injection controls
- Live LLM analysis integration
- Documentation tab with explanations
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
import psutil

# Add current directory to path for tep2py import
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    import tep2py
    print("✅ Real tep2py loaded")
except ImportError as e:
    print(f"❌ Failed to import tep2py: {e}")
    sys.exit(1)


def resolve_venv_python():
    """Get virtual environment Python path."""
    cwd = os.getcwd()
    candidates = [
        os.path.join(cwd, '.venv', 'bin', 'python'),
        os.path.join(cwd, 'tep_env', 'bin', 'python'),
    ] if not sys.platform.startswith('win') else [
        os.path.join(cwd, '.venv', 'Scripts', 'python.exe'),
        os.path.join(cwd, 'tep_env', 'Scripts', 'python.exe'),
    ]
    
    for p in candidates:
        if os.path.exists(p):
            return p
    return sys.executable


class TEPDataBridge:
    """Unified TEP simulation with built-in FaultExplainer bridge."""

    def __init__(self):
        # Simulation state
        self.tep_running = False
        self.simulation_thread = None
        self.current_step = 0
        self.idv_values = np.zeros(20)
        
        # Timing control
        self.step_interval_seconds = 180  # 3 minutes default
        self.speed_mode = 'real'
        
        # Data storage
        self.raw_data_queue = deque(maxlen=100)
        
        # Process management
        self.processes = {}
        self.python_path = resolve_venv_python()
        
        print("✅ TEP Data Bridge initialized")
        print("✅ Timing: TEP(3min) → Anomaly Detection(6min) → LLM(12min)")

    def run_tep_simulation_step(self):
        """Run one TEP simulation step."""
        try:
            result = tep2py.tep(self.idv_values)
            data_point = {
                'step': self.current_step,
                'timestamp': time.time(),
                'idv_values': self.idv_values.tolist(),
                'measurements': np.array(result).flatten().tolist() if hasattr(result, '__iter__') else [float(result)]
            }
            return data_point
        except Exception as e:
            print(f"❌ TEP simulation error: {e}")
            return None

    def save_data_for_faultexplainer(self, data_point):
        """Save data and post to FaultExplainer."""
        try:
            # Save to CSV
            os.makedirs('data', exist_ok=True)
            csv_file = 'data/live_tep_data.csv'
            
            file_exists = os.path.exists(csv_file)
            with open(csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                if not file_exists:
                    header = ['step', 'timestamp'] + [f'idv_{i+1}' for i in range(20)] + [f'measurement_{i+1}' for i in range(len(data_point['measurements']))]
                    writer.writerow(header)
                
                row = [data_point['step'], data_point['timestamp']] + data_point['idv_values'] + data_point['measurements']
                writer.writerow(row)
            
            print(f"💾 Saved data point {data_point['step']} to {csv_file}")
            
            # Post to FaultExplainer (built-in bridge!)
            print("➡️ Posting /ingest...")
            response = requests.post(
                'http://localhost:8000/ingest',
                json=data_point,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                t2_value = result.get('t2_statistic', 0)
                anomaly = result.get('anomaly_detected', False)
                idx = result.get('data_index', 0)
                
                if anomaly:
                    print(f"✅ /ingest OK in {response.elapsed.total_seconds():.2f}s (t2={t2_value}, anomaly={anomaly}, idx={idx})")
                    print("🤖 LLM triggered (live)")
                else:
                    print(f"⏳ /ingest aggregating in {response.elapsed.total_seconds():.2f}s (have={idx+1}, need=4)")
                return True
            else:
                print(f"❌ /ingest failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to save/post data: {e}")
            return False

    def simulation_loop(self):
        """Main simulation loop."""
        print("🚀 Starting TEP simulation loop")
        
        while self.tep_running:
            try:
                print(f"⏱️ Step {self.current_step} start (interval={self.step_interval_seconds}s, mode={self.speed_mode})")
                
                # Run simulation step
                data_point = self.run_tep_simulation_step()
                if data_point:
                    self.raw_data_queue.append(data_point)
                    self.save_data_for_faultexplainer(data_point)
                    self.current_step += 1
                
                # Sleep for next step
                print("💤 Sleeping for next step...")
                time.sleep(self.step_interval_seconds)
                
            except Exception as e:
                print(f"❌ Simulation loop error: {e}")
                time.sleep(10)
        
        print("🛑 TEP simulation loop stopped")

    def start_tep_simulation(self):
        """Start TEP simulation."""
        if self.tep_running:
            return False, "TEP simulation already running"
        
        self.tep_running = True
        self.current_step = 0
        self.simulation_thread = threading.Thread(target=self.simulation_loop, daemon=True)
        self.simulation_thread.start()
        return True, "TEP simulation started"

    def stop_tep_simulation(self):
        """Stop TEP simulation."""
        self.tep_running = False
        if self.simulation_thread:
            self.simulation_thread.join(timeout=5)
        return True, "TEP simulation stopped"

    def set_idv(self, idv_number, value):
        """Set IDV value (1-based indexing)."""
        if 1 <= idv_number <= 20:
            self.idv_values[idv_number - 1] = float(value)
            print(f"🔧 Set IDV_{idv_number} = {value:.2f}")
            return True
        return False

    def start_faultexplainer_backend(self):
        """Start FaultExplainer backend."""
        if self.check_process_status('faultexplainer_backend'):
            return True, 'Backend already running'
        
        try:
            backend_dir = 'external_repos/FaultExplainer-main/backend'
            if not os.path.exists(backend_dir):
                return False, f'Backend directory not found: {backend_dir}'
            
            print(f"🚀 Starting backend: {self.python_path} app.py in {os.path.abspath(backend_dir)}")
            
            process = subprocess.Popen(
                [self.python_path, 'app.py'],
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            self.processes['faultexplainer_backend'] = process
            time.sleep(2)
            
            if process.poll() is None:
                print("✅ Backend process started successfully")
                return True, 'Backend started successfully'
            else:
                return False, 'Backend failed to start'
                
        except Exception as e:
            return False, f'Failed to start backend: {e}'

    def start_faultexplainer_frontend(self):
        """Start FaultExplainer frontend."""
        if self.check_process_status('faultexplainer_frontend'):
            return True, 'Frontend already running'
        
        try:
            frontend_dir = 'external_repos/FaultExplainer-main/frontend'
            npm_cmd = 'npm.cmd' if sys.platform.startswith('win') else 'npm'
            
            process = subprocess.Popen(
                [npm_cmd, 'run', 'dev'],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            self.processes['faultexplainer_frontend'] = process
            time.sleep(3)
            
            if process.poll() is None:
                print("✅ Frontend process started successfully")
                return True, 'Frontend started successfully'
            else:
                return False, 'Frontend failed to start'
                
        except Exception as e:
            return False, f'Failed to start frontend: {e}'

    def check_process_status(self, process_name):
        """Check if a process is running."""
        if process_name not in self.processes:
            return False
        process = self.processes[process_name]
        return process.poll() is None

    def check_port_status(self, port):
        """Check if a port is in use."""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    for conn in proc.connections(kind='inet'):
                        if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except Exception:
            return False

    def stop_all_processes(self):
        """Stop all processes."""
        self.stop_tep_simulation()
        
        for process_name in list(self.processes.keys()):
            try:
                process = self.processes[process_name]
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                del self.processes[process_name]
                print(f"🛑 Stopped {process_name}")
            except Exception as e:
                print(f"⚠️ Error stopping {process_name}: {e}")


class UnifiedControlPanel:
    """Main control panel with clean, modular design."""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.bridge = TEPDataBridge()
        self.setup_routes()
        
        # Cleanup handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("✅ Unified Control Panel initialized")

    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\n🛑 Received signal {signum}, shutting down...")
        self.bridge.stop_all_processes()
        sys.exit(0)

    def setup_routes(self):
        """Setup all Flask routes."""
        
        @self.app.route('/')
        def index():
            from web_interface import get_main_html_template
            return get_main_html_template()

        @self.app.route('/static/<path:filename>')
        def serve_static(filename):
            return send_from_directory('static', filename)

        # Status API
        @self.app.route('/api/status')
        def get_status():
            return jsonify({
                'tep_running': self.bridge.tep_running,
                'backend_running': self.bridge.check_port_status(8000),
                'frontend_running': self.bridge.check_port_status(5173) or self.bridge.check_port_status(5174),
                'bridge_running': self.bridge.tep_running,  # Built-in bridge
                'idv_values': self.bridge.idv_values.tolist(),
                'current_step': self.bridge.current_step,
                'simulation_mode': self.bridge.speed_mode,
                'simulation_interval': self.bridge.step_interval_seconds
            })

        # Control APIs
        @self.app.route('/api/tep/start', methods=['POST'])
        def start_tep():
            success, message = self.bridge.start_tep_simulation()
            return jsonify({'success': success, 'message': message})

        @self.app.route('/api/tep/stop', methods=['POST'])
        def stop_tep():
            success, message = self.bridge.stop_tep_simulation()
            return jsonify({'success': success, 'message': message})

        @self.app.route('/api/faultexplainer/backend/start', methods=['POST'])
        def start_backend():
            success, message = self.bridge.start_faultexplainer_backend()
            return jsonify({'success': success, 'message': message})

        @self.app.route('/api/faultexplainer/frontend/start', methods=['POST'])
        def start_frontend():
            success, message = self.bridge.start_faultexplainer_frontend()
            return jsonify({'success': success, 'message': message})

        @self.app.route('/api/stop/all', methods=['POST'])
        def stop_all():
            self.bridge.stop_all_processes()
            return jsonify({'success': True, 'message': 'All processes stopped'})

        @self.app.route('/api/idv/set', methods=['POST'])
        def set_idv():
            data = request.get_json() or {}
            idv_num = data.get('idv_num')
            value = data.get('value')
            success = self.bridge.set_idv(idv_num, value)
            return jsonify({'success': success})

        @self.app.route('/api/speed', methods=['POST'])
        def set_speed():
            data = request.get_json() or {}
            interval = data.get('interval', 4)
            self.bridge.step_interval_seconds = int(interval)
            return jsonify({'success': True, 'interval': interval})

        # Backend proxy for configuration
        @self.app.route('/api/backend/config/runtime', methods=['POST'])
        def proxy_backend_runtime_config():
            try:
                payload = request.get_json() or {}
                r = requests.post('http://localhost:8000/config/runtime', json=payload, timeout=5)
                return jsonify(r.json()), r.status_code
            except Exception as e:
                return jsonify({'status': 'error', 'error': str(e)}), 500

        # Backend proxy for analysis history
        @self.app.route('/api/backend/analysis/history', methods=['GET'])
        def proxy_backend_analysis_history():
            try:
                limit = request.args.get('limit', '5')
                r = requests.get(f'http://localhost:8000/analysis/history?limit={limit}', timeout=10)
                return jsonify(r.json()), r.status_code
            except Exception as e:
                return jsonify({'status': 'error', 'error': str(e)}), 500

    def run(self, host='127.0.0.1', port=9001):
        """Run the control panel."""
        print(f"🚀 Starting Unified TEP Control Panel on http://{host}:{port}")
        print("✅ Built-in data bridge - no separate bridge needed!")
        print("✅ Documentation tab included")
        print("✅ Clean modular code")
        
        try:
            self.app.run(host=host, port=port, debug=False, threaded=True)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
        finally:
            self.bridge.stop_all_processes()


if __name__ == "__main__":
    panel = UnifiedControlPanel()
    panel.run()
