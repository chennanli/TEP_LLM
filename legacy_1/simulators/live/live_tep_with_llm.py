#!/usr/bin/env python3
"""
Live TEP Simulator with LLM Root Cause Analysis
===============================================

Enhanced version of the live simulator that integrates with FaultExplainer
for real-time LLM-based root cause analysis and operator suggestions.

Features:
- Live parameter changes with immediate plant response
- Real-time anomaly detection
- LLM-powered root cause analysis
- Natural language explanations and suggestions

Author: Augment Agent
Date: 2025-06-29
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import threading
import time
import queue
import requests
import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Add TEP simulator to path
sys.path.append('external_repos/tep2py-master')

try:
    from tep2py import tep2py
    print("✅ TEP simulator loaded successfully!")
except ImportError as e:
    print(f"❌ Error loading TEP simulator: {e}")
    sys.exit(1)


class FaultExplainerClient:
    """Client to communicate with FaultExplainer backend."""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def analyze_fault(self, process_data, fault_info):
        """Send process data to FaultExplainer for LLM analysis."""
        try:
            # Prepare data for FaultExplainer
            payload = {
                "process_data": process_data.to_dict('records'),
                "fault_type": fault_info.get('fault_type', 0),
                "fault_intensity": fault_info.get('intensity', 1.0),
                "timestamp": datetime.now().isoformat()
            }
            
            response = self.session.post(
                f"{self.base_url}/analyze_fault",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API error: {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            return {"error": f"Connection error: {str(e)}"}
    
    def get_suggestions(self, fault_analysis):
        """Get operator suggestions based on fault analysis."""
        try:
            response = self.session.post(
                f"{self.base_url}/get_suggestions",
                json=fault_analysis,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"suggestions": ["Unable to get suggestions at this time."]}
                
        except requests.exceptions.RequestException as e:
            return {"suggestions": [f"Error getting suggestions: {str(e)}"]}


class LiveTEPWithLLM:
    """Live TEP simulator with integrated LLM root cause analysis."""
    
    def __init__(self):
        """Initialize the enhanced simulator."""
        self.root = tk.Tk()
        self.root.title("Live TEP Simulator with AI Root Cause Analysis")
        self.root.geometry("1600x1000")
        
        # Simulation state
        self.is_running = False
        self.current_fault = 0
        self.fault_intensity = 1.0
        self.simulation_speed = 1.0
        self.data_queue = queue.Queue()
        self.simulation_thread = None
        
        # Data storage
        self.time_data = []
        self.temp_data = []
        self.pressure_data = []
        self.flow_data = []
        self.level_data = []
        self.max_points = 100
        
        # LLM integration
        self.fault_explainer = FaultExplainerClient()
        self.llm_analysis_queue = queue.Queue()
        self.last_analysis_time = 0
        self.analysis_interval = 30  # Analyze every 30 seconds
        
        # Anomaly detection
        self.anomaly_detected = False
        self.anomaly_confidence = 0.0
        self.current_analysis = None
        
        self.setup_ui()
        self.setup_plots()
        
    def setup_ui(self):
        """Create the enhanced user interface."""
        
        # Main container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel: Controls + LLM Analysis
        left_panel = ttk.Frame(main_container)
        main_container.add(left_panel, weight=1)
        
        # Right panel: Plots
        right_panel = ttk.Frame(main_container)
        main_container.add(right_panel, weight=2)
        
        # === LEFT PANEL ===
        
        # Control section
        control_frame = ttk.LabelFrame(left_panel, text="🎛️ Live Controls", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Start/Stop button
        self.start_button = ttk.Button(control_frame, text="▶️ Start Simulation", 
                                      command=self.toggle_simulation, width=20)
        self.start_button.pack(pady=5)
        
        # Fault selection
        ttk.Label(control_frame, text="Fault Type:", font=('Arial', 10, 'bold')).pack(pady=(10,0))
        self.fault_var = tk.StringVar(value="0")
        
        fault_options = [
            ("0 - Normal", "0"),
            ("1 - Feed Composition", "1"),
            ("4 - Cooling Water", "4"),
            ("6 - Feed Loss", "6"),
            ("8 - Multiple Feed", "8"),
            ("13 - Reaction Kinetics", "13")
        ]
        
        for text, value in fault_options:
            ttk.Radiobutton(control_frame, text=text, variable=self.fault_var, 
                           value=value, command=self.update_fault).pack(anchor=tk.W)
        
        # Fault intensity
        ttk.Label(control_frame, text="Fault Intensity:", font=('Arial', 10, 'bold')).pack(pady=(10,0))
        self.intensity_var = tk.DoubleVar(value=1.0)
        intensity_scale = ttk.Scale(control_frame, from_=0.1, to=2.0, 
                                   variable=self.intensity_var, orient=tk.HORIZONTAL,
                                   command=self.update_intensity)
        intensity_scale.pack(fill=tk.X, pady=5)
        self.intensity_label = ttk.Label(control_frame, text="1.0x")
        self.intensity_label.pack()
        
        # Status
        status_frame = ttk.LabelFrame(left_panel, text="📊 System Status", padding=10)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="Ready to start", font=('Arial', 10))
        self.status_label.pack()
        
        self.anomaly_status = ttk.Label(status_frame, text="🟢 Normal Operation", 
                                       font=('Arial', 10, 'bold'), foreground='green')
        self.anomaly_status.pack(pady=(5, 0))
        
        # LLM Analysis section
        llm_frame = ttk.LabelFrame(left_panel, text="🤖 AI Root Cause Analysis", padding=10)
        llm_frame.pack(fill=tk.BOTH, expand=True)
        
        # Analysis status
        self.analysis_status = ttk.Label(llm_frame, text="Waiting for anomaly...", 
                                        font=('Arial', 10, 'italic'))
        self.analysis_status.pack(pady=(0, 10))
        
        # Analysis text area
        self.analysis_text = scrolledtext.ScrolledText(llm_frame, height=15, width=50,
                                                      wrap=tk.WORD, font=('Arial', 9))
        self.analysis_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Suggestions area
        ttk.Label(llm_frame, text="💡 Operator Suggestions:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.suggestions_text = scrolledtext.ScrolledText(llm_frame, height=8, width=50,
                                                         wrap=tk.WORD, font=('Arial', 9))
        self.suggestions_text.pack(fill=tk.BOTH, expand=True)
        
        # === RIGHT PANEL ===
        self.plot_frame = right_panel
        
    def setup_plots(self):
        """Setup real-time plotting."""
        
        # Create matplotlib figure
        self.fig, self.axes = plt.subplots(2, 2, figsize=(12, 8))
        self.fig.suptitle('🏭 Live TEP Process Monitoring', fontsize=14, fontweight='bold')
        
        # Setup individual plots
        self.temp_line, = self.axes[0,0].plot([], [], 'r-', linewidth=2)
        self.axes[0,0].set_title('🌡️ Reactor Temperature')
        self.axes[0,0].set_ylabel('Temperature (°C)')
        self.axes[0,0].grid(True, alpha=0.3)
        
        self.pressure_line, = self.axes[0,1].plot([], [], 'b-', linewidth=2)
        self.axes[0,1].set_title('📊 Reactor Pressure')
        self.axes[0,1].set_ylabel('Pressure (kPa)')
        self.axes[0,1].grid(True, alpha=0.3)
        
        self.flow_line, = self.axes[1,0].plot([], [], 'g-', linewidth=2)
        self.axes[1,0].set_title('🏭 Product Flow Rate')
        self.axes[1,0].set_xlabel('Time (minutes)')
        self.axes[1,0].set_ylabel('Flow (m³/h)')
        self.axes[1,0].grid(True, alpha=0.3)
        
        self.level_line, = self.axes[1,1].plot([], [], 'purple', linewidth=2)
        self.axes[1,1].set_title('📏 Reactor Level')
        self.axes[1,1].set_xlabel('Time (minutes)')
        self.axes[1,1].set_ylabel('Level (%)')
        self.axes[1,1].grid(True, alpha=0.3)
        
        # Embed plot in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        plt.tight_layout()
        
    def toggle_simulation(self):
        """Start or stop the simulation."""
        if not self.is_running:
            self.start_simulation()
        else:
            self.stop_simulation()
            
    def start_simulation(self):
        """Start the live simulation."""
        self.is_running = True
        self.start_button.config(text="⏹️ Stop Simulation")
        self.status_label.config(text="🚀 Simulation running...")
        
        # Clear previous data
        self.time_data.clear()
        self.temp_data.clear()
        self.pressure_data.clear()
        self.flow_data.clear()
        self.level_data.clear()
        
        # Start simulation thread
        self.simulation_thread = threading.Thread(target=self.simulation_worker, daemon=True)
        self.simulation_thread.start()
        
        # Start plot update timer
        self.update_plots()
        
    def stop_simulation(self):
        """Stop the simulation."""
        self.is_running = False
        self.start_button.config(text="▶️ Start Simulation")
        self.status_label.config(text="⏹️ Simulation stopped")
        
    def simulation_worker(self):
        """Background simulation worker with LLM integration."""
        sample_count = 0
        process_data_buffer = []
        
        while self.is_running:
            try:
                # Create simulation chunk
                idata = np.zeros((1, 20))
                if self.current_fault > 0:
                    idata[0, self.current_fault-1] = self.fault_intensity
                
                # Run simulation
                tep = tep2py(idata)
                tep.simulate()
                data = tep.process_data
                
                if len(data) > 0:
                    latest = data.iloc[-1]
                    current_time = sample_count * 3
                    
                    # Add to data queue for plotting
                    self.data_queue.put({
                        'time': current_time,
                        'temperature': latest['XMEAS(9)'],
                        'pressure': latest['XMEAS(7)'],
                        'flow': latest['XMEAS(11)'],
                        'level': latest['XMEAS(12)']
                    })
                    
                    # Buffer data for LLM analysis
                    process_data_buffer.append(latest)
                    
                    # Detect anomaly
                    self.detect_anomaly(latest)
                    
                    # Trigger LLM analysis if anomaly detected and enough time passed
                    current_time_sec = time.time()
                    if (self.anomaly_detected and 
                        current_time_sec - self.last_analysis_time > self.analysis_interval and
                        len(process_data_buffer) >= 10):  # Need some data for analysis
                        
                        self.trigger_llm_analysis(process_data_buffer[-10:])  # Last 10 samples
                        self.last_analysis_time = current_time_sec
                    
                    sample_count += 1
                
                time.sleep(1.0 / self.simulation_speed)
                
            except Exception as e:
                print(f"Simulation error: {e}")
                break
                
    def detect_anomaly(self, data_point):
        """Enhanced anomaly detection."""
        temp = data_point['XMEAS(9)']
        pressure = data_point['XMEAS(7)']
        
        # Normal ranges
        temp_normal = (120, 125)
        pressure_normal = (2700, 2800)
        
        anomaly_found = False
        confidence = 0.0
        
        if not (temp_normal[0] <= temp <= temp_normal[1]):
            anomaly_found = True
            confidence = max(confidence, min(abs(temp - 122.5) / 10, 1.0))
            
        if not (pressure_normal[0] <= pressure <= pressure_normal[1]):
            anomaly_found = True
            confidence = max(confidence, min(abs(pressure - 2750) / 100, 1.0))
        
        self.anomaly_detected = anomaly_found
        self.anomaly_confidence = confidence
        
    def trigger_llm_analysis(self, recent_data):
        """Trigger LLM analysis in background thread."""
        def analyze():
            try:
                # Prepare data for analysis
                df = pd.DataFrame(recent_data)
                fault_info = {
                    'fault_type': self.current_fault,
                    'intensity': self.fault_intensity
                }
                
                # Get LLM analysis
                analysis = self.fault_explainer.analyze_fault(df, fault_info)
                
                # Queue the result for UI update
                self.llm_analysis_queue.put(analysis)
                
            except Exception as e:
                error_analysis = {"error": f"Analysis failed: {str(e)}"}
                self.llm_analysis_queue.put(error_analysis)
        
        # Run analysis in background
        analysis_thread = threading.Thread(target=analyze, daemon=True)
        analysis_thread.start()
        
    def update_plots(self):
        """Update real-time plots and LLM analysis."""
        if not self.is_running:
            return
            
        # Process simulation data
        while not self.data_queue.empty():
            try:
                data_point = self.data_queue.get_nowait()
                
                self.time_data.append(data_point['time'])
                self.temp_data.append(data_point['temperature'])
                self.pressure_data.append(data_point['pressure'])
                self.flow_data.append(data_point['flow'])
                self.level_data.append(data_point['level'])
                
                if len(self.time_data) > self.max_points:
                    self.time_data.pop(0)
                    self.temp_data.pop(0)
                    self.pressure_data.pop(0)
                    self.flow_data.pop(0)
                    self.level_data.pop(0)
                    
            except queue.Empty:
                break
        
        # Process LLM analysis results
        while not self.llm_analysis_queue.empty():
            try:
                analysis = self.llm_analysis_queue.get_nowait()
                self.update_llm_display(analysis)
            except queue.Empty:
                break
        
        # Update plots
        if len(self.time_data) > 1:
            self.temp_line.set_data(self.time_data, self.temp_data)
            self.pressure_line.set_data(self.time_data, self.pressure_data)
            self.flow_line.set_data(self.time_data, self.flow_data)
            self.level_line.set_data(self.time_data, self.level_data)
            
            for ax in self.axes.flat:
                ax.relim()
                ax.autoscale_view()
            
            # Update anomaly status
            if self.anomaly_detected:
                self.anomaly_status.config(text="🔴 ANOMALY DETECTED!", foreground='red')
            else:
                self.anomaly_status.config(text="🟢 Normal Operation", foreground='green')
            
            self.canvas.draw()
        
        # Schedule next update
        self.root.after(500, self.update_plots)
        
    def update_llm_display(self, analysis):
        """Update the LLM analysis display."""
        if "error" in analysis:
            self.analysis_status.config(text="❌ Analysis Error")
            self.analysis_text.delete(1.0, tk.END)
            self.analysis_text.insert(tk.END, f"Error: {analysis['error']}")
        else:
            self.analysis_status.config(text="✅ Analysis Complete")
            
            # Display analysis
            self.analysis_text.delete(1.0, tk.END)
            analysis_content = f"""🔍 ROOT CAUSE ANALYSIS
Time: {datetime.now().strftime('%H:%M:%S')}

Fault Type: {self.current_fault}
Confidence: {self.anomaly_confidence:.1%}

Analysis: {analysis.get('explanation', 'No explanation available')}

Key Variables Affected:
{analysis.get('affected_variables', 'Not specified')}

Potential Causes:
{analysis.get('root_causes', 'Not specified')}
"""
            self.analysis_text.insert(tk.END, analysis_content)
            
            # Get and display suggestions
            suggestions = self.fault_explainer.get_suggestions(analysis)
            self.suggestions_text.delete(1.0, tk.END)
            
            suggestions_content = "💡 OPERATOR RECOMMENDATIONS:\n\n"
            for i, suggestion in enumerate(suggestions.get('suggestions', []), 1):
                suggestions_content += f"{i}. {suggestion}\n\n"
            
            self.suggestions_text.insert(tk.END, suggestions_content)
        
    def update_fault(self):
        """Update fault type."""
        self.current_fault = int(self.fault_var.get())
        fault_names = {0: "Normal", 1: "Feed Composition", 4: "Cooling Water", 
                      6: "Feed Loss", 8: "Multiple Feed", 13: "Reaction Kinetics"}
        fault_name = fault_names.get(self.current_fault, "Unknown")
        self.status_label.config(text=f"Fault: {fault_name}")
        
    def update_intensity(self, value):
        """Update fault intensity."""
        self.fault_intensity = float(value)
        self.intensity_label.config(text=f"{self.fault_intensity:.1f}x")
        
    def run(self):
        """Start the application."""
        print("🤖 Starting Live TEP Simulator with LLM Integration...")
        print("   • Real-time parameter changes")
        print("   • Live anomaly detection")
        print("   • LLM root cause analysis")
        print("   • Natural language explanations")
        self.root.mainloop()


def main():
    """Main function."""
    print("🚀 Live TEP Simulator with AI Root Cause Analysis")
    print("="*60)
    print("Features:")
    print("   🎛️ Real-time parameter control")
    print("   📊 Live process visualization")
    print("   🤖 AI anomaly detection")
    print("   🧠 LLM root cause analysis")
    print("   💡 Operator suggestions")
    print("\nNote: Make sure FaultExplainer backend is running!")
    print("      cd external_repos/FaultExplainer-MultiLLM/backend")
    print("      fastapi dev app.py")
    
    app = LiveTEPWithLLM()
    app.run()


if __name__ == "__main__":
    main()
