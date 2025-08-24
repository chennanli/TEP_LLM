#!/usr/bin/env python3
"""
TEP Data Bridge Module
- Handles TEP simulation execution
- Manages data flow to FaultExplainer
- Controls timing and anomaly detection
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
import requests

# Add tep2py path for integration system (now using integration's own copy)
tep2py_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../external_repos/tep2py-master'))
if tep2py_path not in sys.path:
    sys.path.insert(0, tep2py_path)
    print(f"✅ Added tep2py path (integration): {tep2py_path}")


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
        self.simulation_thread = None
        self.stop_simulation = False
        self.current_step = 0
        self.idv_values = np.zeros(20)  # IDV_1 to IDV_20 (disturbance variables)
        self.xmv_values = np.array([63.0, 53.0, 24.0, 61.0, 22.0, 40.0, 38.0, 46.0, 47.0, 41.0, 18.0])  # XMV_1 to XMV_11 (manipulated variables)
        self.simulation_mode = 'real'  # 'demo', 'balanced', 'real'
        self.simulation_interval = 180  # seconds (3 minutes default)

        # Data storage
        self.recent_data = deque(maxlen=100)

        print("✅ TEP Data Bridge initialized with XMV/IDV support")
        print("✅ Timing: TEP(3min) → Anomaly Detection(6min) → LLM(12min)")
        print(f"🎛️ Default XMV values: {self.xmv_values}")
        print(f"🔧 Default IDV values: {self.idv_values}")

    def setup_tep2py(self):
        """Load the TEP simulation module."""
        try:
            # Add the current directory to Python path for tep2py import
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            
            import tep2py
            self.tep = tep2py
            print("✅ Real tep2py loaded")
        except ImportError as e:
            print(f"❌ Failed to import tep2py: {e}")
            print("📁 Current directory:", os.getcwd())
            print("📁 Python path:", sys.path[:3])
            raise

    def set_xmv(self, xmv_number, value):
        """Set XMV value (1-based indexing)."""
        if 1 <= xmv_number <= 11:
            self.xmv_values[xmv_number - 1] = float(value)
            print(f"🎛️ Set XMV_{xmv_number} = {value:.2f}%")
            return True
        return False

    def set_idv(self, idv_number, value):
        """Set IDV value (1-based indexing)."""
        if 1 <= idv_number <= 20:
            self.idv_values[idv_number - 1] = float(value)
            print(f"🔧 Set IDV_{idv_number} = {value:.3f}")
            return True
        return False

    def get_simulation_data(self):
        """Run one step of TEP simulation with REAL Fortran physics."""
        try:
            # Create IDV matrix for simulation (1 time step)
            idv_matrix = self.idv_values.reshape(1, -1)

            print(f"🎛️ Running TEP simulation with XMV: {self.xmv_values}")
            print(f"🔧 IDV disturbances: {self.idv_values}")

            # Create tep2py instance with current XMV values
            tep_sim = self.tep.tep2py(idv_matrix, speed_factor=1.0, user_xmv=self.xmv_values)

            # Run REAL Fortran simulation
            tep_sim.simulate()

            # Extract the latest data point
            if hasattr(tep_sim, 'process_data') and not tep_sim.process_data.empty:
                # Get the last row of data (most recent simulation step)
                latest_data = tep_sim.process_data.iloc[-1].values

                # Create data record
                record = {
                    'step': self.current_step,
                    'timestamp': time.time(),
                    'idv_values': self.idv_values.tolist(),
                    'xmv_values': self.xmv_values.tolist(),
                    'measurements': latest_data.tolist(),
                    'mode': self.simulation_mode
                }

                self.recent_data.append(record)
                print(f"✅ TEP simulation step {self.current_step} complete - REAL Fortran physics!")
                return record
            else:
                print("❌ No simulation data generated")
                return None

        except Exception as e:
            print(f"❌ Simulation error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def save_data_point(self, data_point):
        """Save data point to CSV file."""
        try:
            os.makedirs('data', exist_ok=True)
            csv_file = 'data/live_tep_data.csv'
            
            # Create header if file doesn't exist
            file_exists = os.path.exists(csv_file)
            
            with open(csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                
                if not file_exists:
                    # Write header
                    header = ['step', 'timestamp', 'mode'] + [f'idv_{i+1}' for i in range(20)] + [f'measurement_{i+1}' for i in range(len(data_point['measurements']))]
                    writer.writerow(header)
                
                # Write data
                row = [data_point['step'], data_point['timestamp'], data_point['mode']] + data_point['idv_values'] + data_point['measurements']
                writer.writerow(row)
                
            print(f"💾 Saved data point {data_point['step']} to {csv_file}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save data: {e}")
            return False

    def post_to_faultexplainer(self, data_point):
        """Post data to FaultExplainer backend."""
        try:
            # Prepare data in FaultExplainer format
            payload = {
                'timestamp': data_point['timestamp'],
                'measurements': data_point['measurements'],
                'idv_values': data_point['idv_values'],
                'step': data_point['step']
            }
            
            print("➡️ Posting /ingest...")
            response = requests.post(
                'http://localhost:8001/ingest',  # Integration backend port
                json=payload,
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
            print(f"❌ Failed to post to FaultExplainer: {e}")
            return False

    def simulation_loop(self):
        """Main simulation loop."""
        print("🚀 Starting TEP simulation loop")
        
        while not self.stop_simulation:
            try:
                print(f"⏱️ Step {self.current_step} start (interval={self.simulation_interval}s, mode={self.simulation_mode})")
                
                # Run simulation
                data_point = self.get_simulation_data()
                if data_point:
                    # Save to CSV
                    self.save_data_point(data_point)
                    
                    # Post to FaultExplainer
                    self.post_to_faultexplainer(data_point)
                    
                    self.current_step += 1
                
                # Sleep for next iteration
                print("💤 Sleeping for next step...")
                for i in range(self.simulation_interval):
                    if self.stop_simulation:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                print(f"❌ Simulation loop error: {e}")
                time.sleep(5)  # Brief pause before retry

    def start_simulation(self):
        """Start the simulation in a background thread."""
        if self.simulation_thread and self.simulation_thread.is_alive():
            print("⚠️ Simulation already running")
            return False
            
        self.stop_simulation = False
        self.current_step = 0
        self.simulation_thread = threading.Thread(target=self.simulation_loop, daemon=True)
        self.simulation_thread.start()
        print("✅ TEP simulation started")
        return True

    def stop_simulation(self):
        """Stop the simulation."""
        self.stop_simulation = True
        if self.simulation_thread:
            self.simulation_thread.join(timeout=5)
        print("🛑 TEP simulation loop stopped")
        return True

    def get_status(self):
        """Get current simulation status."""
        return {
            'running': self.simulation_thread and self.simulation_thread.is_alive() and not self.stop_simulation,
            'current_step': self.current_step,
            'mode': self.simulation_mode,
            'interval': self.simulation_interval,
            'idv_values': self.idv_values.tolist(),
            'recent_data_count': len(self.recent_data)
        }

    def set_simulation_mode(self, mode):
        """Set simulation mode and corresponding interval."""
        mode_intervals = {
            'demo': 4,      # 4 seconds for demo
            'balanced': 60, # 1 minute for balanced
            'real': 180     # 3 minutes for real
        }
        
        if mode in mode_intervals:
            self.simulation_mode = mode
            self.simulation_interval = mode_intervals[mode]
            print(f"🎛️ Set simulation mode: {mode} (interval: {self.simulation_interval}s)")
            return True
        return False
