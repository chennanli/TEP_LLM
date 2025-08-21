#!/usr/bin/env python3
"""
Real TEP Simulator using actual tep2py
Replaces the fake SimpleTEPSimulator with real physics-based simulation
"""

import os
import sys
import numpy as np
import pandas as pd
from collections import deque
import threading
import time

class RealTEPSimulator:
    """Real-time TEP simulator using actual tep2py physics."""
    
    def __init__(self):
        self.setup_tep2py()
        
        # Simulation state
        self.current_step = 0
        self.is_running = False
        self.simulation_thread = None
        
        # IDV values (20 disturbances)
        self.idv_values = np.zeros(20)
        
        # Data storage
        self.xmeas_data = deque(maxlen=1000)  # Process measurements (41 variables)
        self.xmv_data = deque(maxlen=1000)    # Manipulated variables (11 variables)
        self.time_data = deque(maxlen=1000)   # Time stamps
        
        # Current values
        self.current_xmeas = np.zeros(41)
        self.current_xmv = np.zeros(11)
        
        # Simulation parameters
        self.sample_time = 3.0  # 3 minutes per sample (TEP standard)
        self.points_per_sample = 180  # 180 seconds = 3 minutes
        
        print("✅ Real TEP Simulator initialized")
    
    def setup_tep2py(self):
        """Setup tep2py module."""
        try:
            # Add TEP path
            tep_path = os.path.join(os.getcwd(), 'external_repos', 'tep2py-master')
            if tep_path not in sys.path:
                sys.path.insert(0, tep_path)
            
            # Import tep2py
            import tep2py
            self.tep2py = tep2py
            print("✅ tep2py module loaded successfully")
            
        except Exception as e:
            print(f"❌ Failed to load tep2py: {e}")
            raise
    
    def set_idv(self, idv_num, value):
        """Set IDV (disturbance) value."""
        if 1 <= idv_num <= 20:
            self.idv_values[idv_num - 1] = value
            print(f"🔧 Set IDV_{idv_num} = {value}")
    
    def run_simulation_batch(self, num_samples=10):
        """Run a batch of TEP simulation."""
        try:
            # Create disturbance matrix for batch simulation
            # Each row is one sample (3 minutes), columns are IDV_1 to IDV_20
            idata = np.tile(self.idv_values, (num_samples, 1))

            # Run TEP simulation using correct API
            tep_sim = self.tep2py.tep2py(idata)
            tep_sim.simulate()  # This populates tep_sim.process_data

            # Extract results
            if hasattr(tep_sim, 'process_data') and isinstance(tep_sim.process_data, pd.DataFrame):
                result = tep_sim.process_data

                # Get the last sample (most recent)
                latest_sample = result.iloc[-1]

                # Extract XMEAS (process measurements) and XMV (manipulated variables)
                xmeas_cols = [col for col in result.columns if 'XMEAS' in col]
                xmv_cols = [col for col in result.columns if 'XMV' in col]

                self.current_xmeas = latest_sample[xmeas_cols].values
                self.current_xmv = latest_sample[xmv_cols].values

                return True
            else:
                print(f"❌ No process_data found or wrong type: {type(getattr(tep_sim, 'process_data', None))}")
                return False

        except Exception as e:
            print(f"❌ TEP simulation error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def simulation_loop(self):
        """Main simulation loop."""
        print("🚀 Starting real TEP simulation loop")
        
        while self.is_running:
            try:
                # Run simulation batch
                success = self.run_simulation_batch(num_samples=1)
                
                if success:
                    # Store data
                    self.xmeas_data.append(self.current_xmeas.copy())
                    self.xmv_data.append(self.current_xmv.copy())
                    self.time_data.append(time.time())
                    
                    self.current_step += 1
                    
                    if self.current_step % 5 == 0:
                        print(f"📊 Real TEP Step {self.current_step}: {len(self.xmeas_data)} data points")
                
                # Wait for next sample (real-time simulation)
                time.sleep(self.sample_time)
                
            except Exception as e:
                print(f"❌ Simulation loop error: {e}")
                time.sleep(1)
        
        print("🛑 Real TEP simulation stopped")
    
    def start(self):
        """Start real-time simulation."""
        if self.is_running:
            return False, "Simulation already running"
        
        self.is_running = True
        self.simulation_thread = threading.Thread(target=self.simulation_loop, daemon=True)
        self.simulation_thread.start()
        
        return True, "Real TEP simulation started"
    
    def stop(self):
        """Stop simulation."""
        self.is_running = False
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=5)
        
        return True, "Real TEP simulation stopped"
    
    def get_current_data(self):
        """Get current simulation data."""
        if len(self.xmeas_data) == 0:
            return None
        
        # Create data dictionary compatible with dashboard
        data = {}
        
        # Add XMEAS variables
        for i in range(41):
            if i < len(self.current_xmeas):
                data[f'XMEAS_{i+1}'] = self.current_xmeas[i]
        
        # Add XMV variables  
        for i in range(11):
            if i < len(self.current_xmv):
                data[f'XMV_{i+1}'] = self.current_xmv[i]
        
        return data
    
    def get_time_series_data(self, max_points=50):
        """Get time series data for plotting."""
        if len(self.xmeas_data) == 0:
            return {}, []
        
        # Get recent data
        recent_xmeas = list(self.xmeas_data)[-max_points:]
        recent_xmv = list(self.xmv_data)[-max_points:]
        recent_times = list(self.time_data)[-max_points:]
        
        # Convert to relative time (seconds from start)
        if len(recent_times) > 0:
            start_time = recent_times[0]
            relative_times = [(t - start_time) for t in recent_times]
        else:
            relative_times = []
        
        # Create time series dictionary
        time_series = {}
        
        # Add XMEAS time series
        for i in range(41):
            values = [sample[i] if i < len(sample) else 0 for sample in recent_xmeas]
            time_series[f'XMEAS_{i+1}'] = values
        
        # Add XMV time series
        for i in range(11):
            values = [sample[i] if i < len(sample) else 0 for sample in recent_xmv]
            time_series[f'XMV_{i+1}'] = values
        
        return time_series, relative_times

if __name__ == "__main__":
    # Test the real simulator
    sim = RealTEPSimulator()
    
    print("Testing real TEP simulator...")
    success, msg = sim.start()
    print(f"Start result: {msg}")
    
    if success:
        # Let it run for a bit
        time.sleep(10)
        
        # Test IDV change
        sim.set_idv(1, 1.0)
        time.sleep(10)
        
        # Get data
        data = sim.get_current_data()
        print(f"Current data keys: {list(data.keys()) if data else 'None'}")
        
        # Stop
        sim.stop()
