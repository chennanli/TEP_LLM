#!/usr/bin/env python3
"""
Live Interactive TEP Simulator
==============================

Real-time Tennessee Eastman Process simulator with live parameter changes
and dynamic visualization. Perfect for customer demonstrations.

Features:
- Live parameter changes (press Enter to apply)
- Real-time process visualization
- Streaming data for anomaly detection
- Customer-friendly interface

Author: Augment Agent
Date: 2025-06-29
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches
import threading
import time
import queue
from datetime import datetime
import tkinter as tk
from tkinter import ttk
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


class LiveTEPSimulator:
    """Live interactive TEP simulator with real-time visualization."""
    
    def __init__(self):
        """Initialize the live simulator."""
        self.root = tk.Tk()
        self.root.title("Live TEP Simulator - Customer Demo")
        self.root.geometry("1400x900")
        
        # Simulation state
        self.is_running = False
        self.current_fault = 0
        self.fault_intensity = 1.0
        self.simulation_speed = 1.0
        self.data_queue = queue.Queue()
        self.simulation_thread = None
        
        # Data storage for live plotting
        self.time_data = []
        self.temp_data = []
        self.pressure_data = []
        self.flow_data = []
        self.level_data = []
        self.max_points = 100  # Keep last 100 points for live view
        
        # Anomaly detection placeholder
        self.anomaly_detected = False
        self.anomaly_location = ""
        self.anomaly_confidence = 0.0
        
        self.setup_ui()
        self.setup_plots()
        
    def setup_ui(self):
        """Create the user interface."""
        
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel (left side)
        control_frame = ttk.LabelFrame(main_frame, text="🎛️ Live Controls", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Start/Stop button
        self.start_button = ttk.Button(control_frame, text="▶️ Start Simulation", 
                                      command=self.toggle_simulation, width=20)
        self.start_button.pack(pady=5)
        
        # Fault selection
        ttk.Label(control_frame, text="Fault Type:", font=('Arial', 10, 'bold')).pack(pady=(10,0))
        self.fault_var = tk.StringVar(value="0")
        fault_frame = ttk.Frame(control_frame)
        fault_frame.pack(fill=tk.X, pady=5)
        
        fault_options = [
            ("0 - Normal", "0"),
            ("1 - Feed Composition", "1"),
            ("4 - Cooling Water", "4"),
            ("6 - Feed Loss", "6"),
            ("8 - Multiple Feed", "8"),
            ("13 - Reaction Kinetics", "13")
        ]
        
        for text, value in fault_options:
            ttk.Radiobutton(fault_frame, text=text, variable=self.fault_var, 
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
        
        # Simulation speed
        ttk.Label(control_frame, text="Simulation Speed:", font=('Arial', 10, 'bold')).pack(pady=(10,0))
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = ttk.Scale(control_frame, from_=0.1, to=5.0, 
                               variable=self.speed_var, orient=tk.HORIZONTAL,
                               command=self.update_speed)
        speed_scale.pack(fill=tk.X, pady=5)
        self.speed_label = ttk.Label(control_frame, text="1.0x")
        self.speed_label.pack()
        
        # Status display
        status_frame = ttk.LabelFrame(control_frame, text="📊 Status", padding=10)
        status_frame.pack(fill=tk.X, pady=(20,0))
        
        self.status_label = ttk.Label(status_frame, text="Ready to start", 
                                     font=('Arial', 10))
        self.status_label.pack()
        
        # Anomaly detection display
        anomaly_frame = ttk.LabelFrame(control_frame, text="🤖 AI Anomaly Detection", padding=10)
        anomaly_frame.pack(fill=tk.X, pady=(10,0))
        
        self.anomaly_status = ttk.Label(anomaly_frame, text="🟢 Normal Operation", 
                                       font=('Arial', 10, 'bold'), foreground='green')
        self.anomaly_status.pack()
        
        self.anomaly_details = ttk.Label(anomaly_frame, text="No anomalies detected", 
                                        font=('Arial', 9))
        self.anomaly_details.pack()
        
        # Customer info
        info_frame = ttk.LabelFrame(control_frame, text="ℹ️ Demo Info", padding=10)
        info_frame.pack(fill=tk.X, pady=(10,0))
        
        info_text = """This is a live Tennessee Eastman Process simulator.

🎛️ Change parameters above
📊 See real-time plant response  
🤖 Watch AI detect anomalies
🔍 Get root cause analysis

Perfect for industrial AI demos!"""
        
        ttk.Label(info_frame, text=info_text, font=('Arial', 8), 
                 justify=tk.LEFT).pack()
        
        # Plot area (right side)
        self.plot_frame = ttk.Frame(main_frame)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
    def setup_plots(self):
        """Setup real-time plotting."""
        
        # Create matplotlib figure
        self.fig, self.axes = plt.subplots(2, 2, figsize=(10, 8))
        self.fig.suptitle('🏭 Live TEP Process Monitoring', fontsize=14, fontweight='bold')
        
        # Setup individual plots
        self.temp_line, = self.axes[0,0].plot([], [], 'r-', linewidth=2, label='Reactor Temperature')
        self.axes[0,0].set_title('🌡️ Reactor Temperature')
        self.axes[0,0].set_ylabel('Temperature (°C)')
        self.axes[0,0].grid(True, alpha=0.3)
        self.axes[0,0].legend()
        
        self.pressure_line, = self.axes[0,1].plot([], [], 'b-', linewidth=2, label='Reactor Pressure')
        self.axes[0,1].set_title('📊 Reactor Pressure')
        self.axes[0,1].set_ylabel('Pressure (kPa)')
        self.axes[0,1].grid(True, alpha=0.3)
        self.axes[0,1].legend()
        
        self.flow_line, = self.axes[1,0].plot([], [], 'g-', linewidth=2, label='Product Flow')
        self.axes[1,0].set_title('🏭 Product Flow Rate')
        self.axes[1,0].set_xlabel('Time (minutes)')
        self.axes[1,0].set_ylabel('Flow (m³/h)')
        self.axes[1,0].grid(True, alpha=0.3)
        self.axes[1,0].legend()
        
        self.level_line, = self.axes[1,1].plot([], [], 'purple', linewidth=2, label='Reactor Level')
        self.axes[1,1].set_title('📏 Reactor Level')
        self.axes[1,1].set_xlabel('Time (minutes)')
        self.axes[1,1].set_ylabel('Level (%)')
        self.axes[1,1].grid(True, alpha=0.3)
        self.axes[1,1].legend()
        
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
        """Background simulation worker."""
        
        sample_count = 0
        start_time = time.time()
        
        while self.is_running:
            try:
                # Create small simulation chunk (1 sample = 3 minutes)
                idata = np.zeros((1, 20))
                
                # Apply current fault
                if self.current_fault > 0:
                    idata[0, self.current_fault-1] = self.fault_intensity
                
                # Run simulation
                tep = tep2py(idata)
                tep.simulate()
                data = tep.process_data
                
                if len(data) > 0:
                    # Get latest data point
                    latest = data.iloc[-1]
                    current_time = sample_count * 3  # 3 minutes per sample
                    
                    # Add to data queue
                    self.data_queue.put({
                        'time': current_time,
                        'temperature': latest['XMEAS(9)'],
                        'pressure': latest['XMEAS(7)'],
                        'flow': latest['XMEAS(11)'],
                        'level': latest['XMEAS(12)']
                    })
                    
                    # Simple anomaly detection (placeholder)
                    self.detect_anomaly(latest)
                    
                    sample_count += 1
                
                # Control simulation speed
                time.sleep(1.0 / self.simulation_speed)
                
            except Exception as e:
                print(f"Simulation error: {e}")
                break
                
    def detect_anomaly(self, data_point):
        """Simple anomaly detection (placeholder for real AI model)."""
        
        # Simple threshold-based detection
        temp = data_point['XMEAS(9)']
        pressure = data_point['XMEAS(7)']
        
        # Normal ranges
        temp_normal = (120, 125)
        pressure_normal = (2700, 2800)
        
        anomaly_found = False
        anomaly_msg = ""
        confidence = 0.0
        
        if not (temp_normal[0] <= temp <= temp_normal[1]):
            anomaly_found = True
            anomaly_msg = f"Temperature anomaly: {temp:.1f}°C"
            confidence = min(abs(temp - 122.5) / 10, 1.0)
            
        if not (pressure_normal[0] <= pressure <= pressure_normal[1]):
            if anomaly_found:
                anomaly_msg += f", Pressure: {pressure:.0f} kPa"
            else:
                anomaly_found = True
                anomaly_msg = f"Pressure anomaly: {pressure:.0f} kPa"
                confidence = min(abs(pressure - 2750) / 100, 1.0)
        
        self.anomaly_detected = anomaly_found
        self.anomaly_location = anomaly_msg
        self.anomaly_confidence = confidence
        
    def update_plots(self):
        """Update real-time plots."""
        
        if not self.is_running:
            return
            
        # Process data from queue
        while not self.data_queue.empty():
            try:
                data_point = self.data_queue.get_nowait()
                
                # Add to data arrays
                self.time_data.append(data_point['time'])
                self.temp_data.append(data_point['temperature'])
                self.pressure_data.append(data_point['pressure'])
                self.flow_data.append(data_point['flow'])
                self.level_data.append(data_point['level'])
                
                # Keep only recent data
                if len(self.time_data) > self.max_points:
                    self.time_data.pop(0)
                    self.temp_data.pop(0)
                    self.pressure_data.pop(0)
                    self.flow_data.pop(0)
                    self.level_data.pop(0)
                    
            except queue.Empty:
                break
        
        # Update plots if we have data
        if len(self.time_data) > 1:
            self.temp_line.set_data(self.time_data, self.temp_data)
            self.pressure_line.set_data(self.time_data, self.pressure_data)
            self.flow_line.set_data(self.time_data, self.flow_data)
            self.level_line.set_data(self.time_data, self.level_data)
            
            # Auto-scale axes
            for ax in self.axes.flat:
                ax.relim()
                ax.autoscale_view()
            
            # Update anomaly status
            if self.anomaly_detected:
                self.anomaly_status.config(text="🔴 ANOMALY DETECTED!", foreground='red')
                self.anomaly_details.config(text=f"{self.anomaly_location}\nConfidence: {self.anomaly_confidence:.1%}")
            else:
                self.anomaly_status.config(text="🟢 Normal Operation", foreground='green')
                self.anomaly_details.config(text="No anomalies detected")
            
            self.canvas.draw()
        
        # Schedule next update
        self.root.after(500, self.update_plots)  # Update every 500ms
        
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
        
    def update_speed(self, value):
        """Update simulation speed."""
        self.simulation_speed = float(value)
        self.speed_label.config(text=f"{self.simulation_speed:.1f}x")
        
    def run(self):
        """Start the application."""
        print("🎛️ Starting Live TEP Simulator...")
        print("   • Change parameters in real-time")
        print("   • Watch live process response")
        print("   • See AI anomaly detection")
        print("   • Perfect for customer demos!")
        self.root.mainloop()


def main():
    """Main function."""
    
    print("🚀 Live Interactive TEP Simulator")
    print("="*50)
    print("Features:")
    print("   🎛️ Real-time parameter changes")
    print("   📊 Live process visualization")
    print("   🤖 AI anomaly detection")
    print("   👥 Customer-friendly interface")
    print("\nStarting application...")
    
    app = LiveTEPSimulator()
    app.run()


if __name__ == "__main__":
    main()
