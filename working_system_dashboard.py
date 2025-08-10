#!/usr/bin/env python3
"""
Working TEP System Dashboard
Shows the complete data flow and system status
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import time
import os
import requests
import tkinter as tk
from tkinter import ttk
import threading

class TEPSystemDashboard:
    """Dashboard showing TEP → FaultExplainer data flow"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TEP System Dashboard - Live Data Flow")
        self.root.geometry("800x600")
        
        self.live_data_file = "data/live_tep_data.csv"
        self.faultexplainer_url = "http://localhost:8000"
        
        self.setup_ui()
        self.running = False
        
    def setup_ui(self):
        """Setup the dashboard UI"""
        
        # Title
        title_label = tk.Label(self.root, text="🏭 TEP System Dashboard", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Status frame
        status_frame = ttk.LabelFrame(self.root, text="System Status", padding=10)
        status_frame.pack(fill="x", padx=10, pady=5)
        
        self.tep_status = tk.Label(status_frame, text="TEP Simulation: ❌ Not Running", 
                                  font=("Arial", 12))
        self.tep_status.pack(anchor="w")
        
        self.backend_status = tk.Label(status_frame, text="FaultExplainer Backend: ❌ Not Running", 
                                      font=("Arial", 12))
        self.backend_status.pack(anchor="w")
        
        self.bridge_status = tk.Label(status_frame, text="Data Bridge: ❌ Not Running", 
                                     font=("Arial", 12))
        self.bridge_status.pack(anchor="w")
        
        # Data info frame
        data_frame = ttk.LabelFrame(self.root, text="Live Data", padding=10)
        data_frame.pack(fill="x", padx=10, pady=5)
        
        self.data_points_label = tk.Label(data_frame, text="Data Points: 0", 
                                         font=("Arial", 12))
        self.data_points_label.pack(anchor="w")
        
        self.last_update_label = tk.Label(data_frame, text="Last Update: Never", 
                                         font=("Arial", 12))
        self.last_update_label.pack(anchor="w")
        
        # Key variables frame
        vars_frame = ttk.LabelFrame(self.root, text="Key Process Variables", padding=10)
        vars_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create text widget for variables
        self.vars_text = tk.Text(vars_frame, height=15, font=("Courier", 10))
        scrollbar = ttk.Scrollbar(vars_frame, orient="vertical", command=self.vars_text.yview)
        self.vars_text.configure(yscrollcommand=scrollbar.set)
        
        self.vars_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Control buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        self.start_button = tk.Button(button_frame, text="🚀 Start Monitoring", 
                                     command=self.start_monitoring, bg="green", fg="white")
        self.start_button.pack(side="left", padx=5)
        
        self.stop_button = tk.Button(button_frame, text="🛑 Stop Monitoring", 
                                    command=self.stop_monitoring, bg="red", fg="white")
        self.stop_button.pack(side="left", padx=5)
        
        self.refresh_button = tk.Button(button_frame, text="🔄 Refresh", 
                                       command=self.update_display)
        self.refresh_button.pack(side="left", padx=5)
        
        # Instructions
        instructions = """
📋 INSTRUCTIONS:
1. Start TEP simulation: python real_tep_simulator.py
2. Start FaultExplainer backend: cd external_repos/FaultExplainer-main/backend && python app.py  
3. Start FaultExplainer frontend: cd external_repos/FaultExplainer-main/frontend && npm run dev
4. Click 'Start Monitoring' to see live data flow
5. Access FaultExplainer UI at: http://localhost:5173
        """
        
        instructions_label = tk.Label(self.root, text=instructions, 
                                     font=("Arial", 9), justify="left", bg="lightyellow")
        instructions_label.pack(fill="x", padx=10, pady=5)
    
    def check_tep_status(self):
        """Check if TEP simulation is generating data"""
        try:
            if os.path.exists(self.live_data_file):
                df = pd.read_csv(self.live_data_file)
                if not df.empty:
                    # Check if data is recent (within last 5 minutes)
                    latest_time = df['timestamp'].max()
                    current_time = time.time()
                    if current_time - latest_time < 300:  # 5 minutes
                        return True, len(df)
            return False, 0
        except:
            return False, 0
    
    def check_backend_status(self):
        """Check if FaultExplainer backend is running"""
        try:
            response = requests.get(f"{self.faultexplainer_url}/", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def get_latest_data(self):
        """Get latest TEP data"""
        try:
            if os.path.exists(self.live_data_file):
                df = pd.read_csv(self.live_data_file)
                if not df.empty:
                    latest = df.iloc[-1]
                    return latest.to_dict()
            return None
        except:
            return None
    
    def update_display(self):
        """Update the dashboard display"""
        # Check system status
        tep_running, data_count = self.check_tep_status()
        backend_running = self.check_backend_status()
        
        # Update status labels
        if tep_running:
            self.tep_status.config(text="TEP Simulation: ✅ Running", fg="green")
        else:
            self.tep_status.config(text="TEP Simulation: ❌ Not Running", fg="red")
        
        if backend_running:
            self.backend_status.config(text="FaultExplainer Backend: ✅ Running", fg="green")
        else:
            self.backend_status.config(text="FaultExplainer Backend: ❌ Not Running", fg="red")
        
        if self.running:
            self.bridge_status.config(text="Data Bridge: ✅ Monitoring", fg="green")
        else:
            self.bridge_status.config(text="Data Bridge: ❌ Not Running", fg="red")
        
        # Update data info
        self.data_points_label.config(text=f"Data Points: {data_count}")
        self.last_update_label.config(text=f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
        
        # Update variables display
        latest_data = self.get_latest_data()
        if latest_data:
            self.vars_text.delete(1.0, tk.END)
            
            # Show key process variables
            key_vars = [
                ('XMEAS_1', 'A Feed Flow'),
                ('XMEAS_2', 'D Feed Flow'),
                ('XMEAS_7', 'Reactor Pressure'),
                ('XMEAS_8', 'Reactor Level'),
                ('XMEAS_9', 'Reactor Temperature'),
                ('XMEAS_11', 'Product Sep Temp'),
                ('XMEAS_13', 'Product Sep Pressure'),
                ('XMEAS_15', 'Stripper Level'),
                ('XMEAS_17', 'Stripper Underflow'),
                ('IDV_1', 'A/C Feed Ratio Fault')
            ]
            
            output = f"📊 LIVE TEP DATA (Step {latest_data.get('step', 'N/A')})\n"
            output += "=" * 50 + "\n\n"
            
            for var_name, description in key_vars:
                if var_name in latest_data:
                    value = latest_data[var_name]
                    output += f"{description:25}: {value:10.3f}\n"
            
            output += "\n" + "=" * 50 + "\n"
            output += f"Timestamp: {datetime.fromtimestamp(latest_data.get('timestamp', 0))}\n"
            
            # Show fault status
            fault_active = any(latest_data.get(f'IDV_{i}', 0) > 0 for i in range(1, 21))
            if fault_active:
                output += "🚨 FAULT DETECTED - Check FaultExplainer UI\n"
            else:
                output += "✅ Normal Operation\n"
            
            self.vars_text.insert(1.0, output)
    
    def start_monitoring(self):
        """Start monitoring the system"""
        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
    
    def stop_monitoring(self):
        """Stop monitoring the system"""
        self.running = False
        
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
    
    def monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                self.update_display()
                time.sleep(2)  # Update every 2 seconds
            except:
                break
    
    def run(self):
        """Run the dashboard"""
        self.update_display()  # Initial update
        self.root.mainloop()

def main():
    """Run the dashboard"""
    print("🏭 Starting TEP System Dashboard...")
    dashboard = TEPSystemDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
