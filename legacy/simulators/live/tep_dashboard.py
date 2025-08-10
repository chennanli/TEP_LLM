#!/usr/bin/env python3
"""
TEP Simulator Interactive Dashboard
==================================

A visual interface for the Tennessee Eastman Process simulator
that provides real-time monitoring and easy parameter control.

Author: Augment Agent
Date: 2025-06-29
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches
from datetime import datetime
import threading
import time

# Add TEP simulator to path
sys.path.append('Other_Repo/tep2py-master')

try:
    from tep2py import tep2py
    print("✅ TEP Dashboard: Simulator loaded successfully!")
except ImportError as e:
    print(f"❌ Error loading TEP simulator: {e}")
    sys.exit(1)


class TEPDashboard:
    """Interactive dashboard for TEP simulation monitoring."""
    
    def __init__(self):
        """Initialize the dashboard."""
        self.current_data = None
        self.simulation_running = False
        self.fault_active = False
        self.fault_descriptions = {
            0: "Normal Operation",
            1: "A/C Feed Ratio Fault",
            2: "B Composition Fault", 
            3: "D Feed Temperature Fault",
            4: "Reactor Cooling Water Fault",
            5: "Condenser Cooling Water Fault",
            6: "A Feed Loss Fault",
            7: "C Header Pressure Loss",
            8: "A,B,C Feed Composition Fault",
            13: "Reaction Kinetics Fault",
            14: "Reactor Cooling Water Valve",
            15: "Condenser Cooling Water Valve"
        }
        
    def create_process_diagram(self, ax):
        """Create a simplified process flow diagram."""
        ax.clear()
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 8)
        ax.set_aspect('equal')
        
        # Reactor
        reactor = patches.Circle((3, 4), 1, linewidth=2, 
                               edgecolor='blue', facecolor='lightblue', alpha=0.7)
        ax.add_patch(reactor)
        ax.text(3, 4, 'REACTOR', ha='center', va='center', fontweight='bold')
        
        # Separator
        separator = patches.Rectangle((6, 3), 1.5, 2, linewidth=2,
                                    edgecolor='green', facecolor='lightgreen', alpha=0.7)
        ax.add_patch(separator)
        ax.text(6.75, 4, 'SEP', ha='center', va='center', fontweight='bold')
        
        # Stripper
        stripper = patches.Rectangle((6, 0.5), 1.5, 1.5, linewidth=2,
                                   edgecolor='orange', facecolor='lightyellow', alpha=0.7)
        ax.add_patch(stripper)
        ax.text(6.75, 1.25, 'STRIP', ha='center', va='center', fontweight='bold')
        
        # Feed streams
        ax.arrow(0.5, 6, 2, -1.5, head_width=0.1, head_length=0.1, fc='red', ec='red')
        ax.text(0.5, 6.5, 'Feed A', fontsize=10)
        
        ax.arrow(0.5, 2, 2, 1.5, head_width=0.1, head_length=0.1, fc='red', ec='red')
        ax.text(0.5, 1.5, 'Feed D', fontsize=10)
        
        # Product stream
        ax.arrow(8, 1.25, 1, 0, head_width=0.1, head_length=0.1, fc='purple', ec='purple')
        ax.text(8.5, 1.5, 'Product', fontsize=10)
        
        # Connections
        ax.plot([4, 6], [4, 4], 'k-', linewidth=2)  # Reactor to Separator
        ax.plot([6.75, 6.75], [3, 2], 'k-', linewidth=2)  # Separator to Stripper
        
        ax.set_title('Tennessee Eastman Process Flow Diagram', fontsize=14, fontweight='bold')
        ax.axis('off')
        
    def update_process_status(self, ax, data_row):
        """Update process status indicators."""
        ax.clear()
        
        if data_row is None:
            ax.text(0.5, 0.5, 'No Data Available', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=16)
            return
            
        # Key process variables
        reactor_temp = data_row.get('XMEAS(9)', 0)
        reactor_pressure = data_row.get('XMEAS(7)', 0)
        reactor_level = data_row.get('XMEAS(12)', 0)
        product_flow = data_row.get('XMEAS(11)', 0)
        
        # Status indicators
        status_data = [
            ('Reactor Temperature', f'{reactor_temp:.1f} °C', 
             'green' if 120 <= reactor_temp <= 125 else 'red'),
            ('Reactor Pressure', f'{reactor_pressure:.0f} kPa', 
             'green' if 2700 <= reactor_pressure <= 2800 else 'red'),
            ('Reactor Level', f'{reactor_level:.1f} %', 
             'green' if 50 <= reactor_level <= 80 else 'red'),
            ('Product Flow', f'{product_flow:.1f} m³/h', 
             'green' if 22 <= product_flow <= 26 else 'red'),
        ]
        
        y_positions = [0.8, 0.6, 0.4, 0.2]
        
        for i, (name, value, color) in enumerate(status_data):
            # Status indicator circle
            circle = patches.Circle((0.1, y_positions[i]), 0.03, 
                                  facecolor=color, transform=ax.transAxes)
            ax.add_patch(circle)
            
            # Text
            ax.text(0.2, y_positions[i], f'{name}: {value}', 
                   transform=ax.transAxes, fontsize=12, va='center')
        
        ax.set_title('Process Status', fontsize=14, fontweight='bold')
        ax.axis('off')
        
    def run_simulation_thread(self, duration_hours, fault_type, fault_start_hour):
        """Run simulation in background thread."""
        try:
            self.simulation_running = True
            
            # Calculate parameters
            samples_per_hour = 20
            total_samples = int(duration_hours * samples_per_hour)
            fault_start_sample = int(fault_start_hour * samples_per_hour)
            
            # Create disturbance matrix
            idata = np.zeros((total_samples, 20))
            if fault_type > 0:
                idata[fault_start_sample:, fault_type-1] = 1
                
            # Run simulation
            tep = tep2py(idata)
            tep.simulate()
            
            # Store results
            self.current_data = tep.process_data.copy()
            self.current_data['Time_Hours'] = np.arange(0, duration_hours, duration_hours/len(self.current_data))
            
            print(f"✅ Simulation completed: {len(self.current_data)} data points")
            
        except Exception as e:
            print(f"❌ Simulation error: {e}")
        finally:
            self.simulation_running = False
    
    def create_dashboard(self, duration_hours=8, fault_type=0, fault_start_hour=2):
        """Create and display the interactive dashboard."""
        
        print(f"\n🚀 Starting TEP Dashboard")
        print(f"   Duration: {duration_hours} hours")
        print(f"   Fault: {fault_type} - {self.fault_descriptions.get(fault_type, 'Unknown')}")
        if fault_type > 0:
            print(f"   Fault starts at: {fault_start_hour} hours")
        print("-" * 60)
        
        # Start simulation in background
        sim_thread = threading.Thread(
            target=self.run_simulation_thread, 
            args=(duration_hours, fault_type, fault_start_hour)
        )
        sim_thread.daemon = True
        sim_thread.start()
        
        # Create dashboard layout
        fig = plt.figure(figsize=(16, 10))
        fig.suptitle('Tennessee Eastman Process - Live Dashboard', fontsize=16, fontweight='bold')
        
        # Layout: 2x3 grid
        ax_diagram = plt.subplot(2, 3, 1)      # Process diagram
        ax_status = plt.subplot(2, 3, 2)       # Status indicators  
        ax_trends = plt.subplot(2, 3, 3)       # Trend plots
        ax_temp = plt.subplot(2, 3, 4)         # Temperature trend
        ax_pressure = plt.subplot(2, 3, 5)     # Pressure trend
        ax_flow = plt.subplot(2, 3, 6)         # Flow trend
        
        # Initialize plots
        self.create_process_diagram(ax_diagram)
        
        def update_dashboard(frame):
            """Update dashboard with latest data."""
            
            if self.current_data is None:
                # Show loading message
                for ax in [ax_status, ax_trends, ax_temp, ax_pressure, ax_flow]:
                    ax.clear()
                    ax.text(0.5, 0.5, 'Loading Simulation...', 
                           ha='center', va='center', transform=ax.transAxes)
                return
            
            # Get current data point (simulate real-time)
            current_idx = min(frame, len(self.current_data) - 1)
            current_row = self.current_data.iloc[current_idx]
            
            # Update status
            self.update_process_status(ax_status, current_row)
            
            # Update trend plots
            time_data = self.current_data['Time_Hours'][:current_idx+1]
            
            # Temperature trend
            ax_temp.clear()
            ax_temp.plot(time_data, self.current_data['XMEAS(9)'][:current_idx+1], 'r-', linewidth=2)
            ax_temp.set_title('Reactor Temperature')
            ax_temp.set_ylabel('Temperature (°C)')
            ax_temp.grid(True, alpha=0.3)
            if fault_type > 0:
                ax_temp.axvline(x=fault_start_hour, color='k', linestyle='--', alpha=0.7)
            
            # Pressure trend
            ax_pressure.clear()
            ax_pressure.plot(time_data, self.current_data['XMEAS(7)'][:current_idx+1], 'b-', linewidth=2)
            ax_pressure.set_title('Reactor Pressure')
            ax_pressure.set_ylabel('Pressure (kPa)')
            ax_pressure.grid(True, alpha=0.3)
            if fault_type > 0:
                ax_pressure.axvline(x=fault_start_hour, color='k', linestyle='--', alpha=0.7)
            
            # Flow trend
            ax_flow.clear()
            ax_flow.plot(time_data, self.current_data['XMEAS(11)'][:current_idx+1], 'g-', linewidth=2)
            ax_flow.set_title('Product Flow Rate')
            ax_flow.set_xlabel('Time (hours)')
            ax_flow.set_ylabel('Flow (m³/h)')
            ax_flow.grid(True, alpha=0.3)
            if fault_type > 0:
                ax_flow.axvline(x=fault_start_hour, color='k', linestyle='--', alpha=0.7)
            
            # Overview trends
            ax_trends.clear()
            if len(time_data) > 1:
                ax_trends.plot(time_data, self.current_data['XMEAS(9)'][:current_idx+1], 'r-', label='Temperature', alpha=0.7)
                ax_trends2 = ax_trends.twinx()
                ax_trends2.plot(time_data, self.current_data['XMEAS(7)'][:current_idx+1], 'b-', label='Pressure', alpha=0.7)
                ax_trends.set_title('Process Overview')
                ax_trends.set_ylabel('Temperature (°C)', color='r')
                ax_trends2.set_ylabel('Pressure (kPa)', color='b')
                ax_trends.grid(True, alpha=0.3)
                if fault_type > 0:
                    ax_trends.axvline(x=fault_start_hour, color='k', linestyle='--', alpha=0.7)
        
        # Create animation
        anim = FuncAnimation(fig, update_dashboard, interval=500, cache_frame_data=False)
        
        plt.tight_layout()
        plt.show()
        
        return anim


def main():
    """Main dashboard application."""
    
    print("🎛️ TEP Interactive Dashboard")
    print("="*50)
    
    dashboard = TEPDashboard()
    
    # Get user input
    print("\n📋 Dashboard Configuration:")
    print("Available faults: 0=Normal, 1=Feed Ratio, 4=Cooling Water, 6=Feed Loss, 13=Reaction")
    
    try:
        duration = float(input("Simulation duration (hours) [default: 6]: ") or "6")
        fault_type = int(input("Fault type (0-20) [default: 1]: ") or "1")
        fault_start = float(input("Fault start time (hours) [default: 2]: ") or "2")
    except ValueError:
        print("Using default values...")
        duration, fault_type, fault_start = 6, 1, 2
    
    print(f"\n🚀 Starting dashboard with:")
    print(f"   Duration: {duration} hours")
    print(f"   Fault: {fault_type}")
    print(f"   Fault start: {fault_start} hours")
    print("\n💡 Close the plot window to exit the dashboard")
    
    # Create and run dashboard
    anim = dashboard.create_dashboard(duration, fault_type, fault_start)
    
    print("\n✅ Dashboard session completed!")


if __name__ == "__main__":
    main()
