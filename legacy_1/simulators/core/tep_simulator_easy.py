#!/usr/bin/env python3
"""
Tennessee Eastman Process (TEP) Simulator - Easy Interface
===========================================================

This script provides a simplified interface to run TEP simulations.
Users can easily modify parameters to test different scenarios and faults.

Requirements:
- Virtual environment activated (source tep_env/bin/activate)
- Compiled Fortran module (temain_mod.cpython-39-darwin.so)

Author: Augment Agent
Date: 2025-06-29
"""

import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Add the tep2py directory to Python path
sys.path.append('external_repos/tep2py-master')

try:
    from tep2py import tep2py
    print("✅ TEP simulator loaded successfully!")
except ImportError as e:
    print(f"❌ Error importing TEP simulator: {e}")
    print("Make sure you're in the correct directory and the virtual environment is activated.")
    sys.exit(1)


class TEPSimulatorEasy:
    """
    Simplified interface for Tennessee Eastman Process simulation.
    """
    
    def __init__(self):
        """Initialize the TEP simulator."""
        self.fault_descriptions = {
            0: "Normal operation (no fault)",
            1: "A/C feed ratio, B composition constant (Stream 4)",
            2: "B composition, A/C ratio constant (Stream 4)", 
            3: "D feed temperature (Stream 2)",
            4: "Reactor cooling water inlet temperature",
            5: "Condenser cooling water inlet temperature",
            6: "A feed loss (Stream 1)",
            7: "C header pressure loss-reduced availability (Stream 4)",
            8: "A, B, C feed composition (Stream 4)",
            9: "D feed temperature (Stream 2)",
            10: "C feed temperature (Stream 4)",
            11: "Reactor cooling water inlet temperature",
            12: "Condenser cooling water inlet temperature",
            13: "Reaction kinetics",
            14: "Reactor cooling water valve",
            15: "Condenser cooling water valve",
            16: "Unknown",
            17: "Unknown",
            18: "Unknown",
            19: "Unknown",
            20: "Unknown"
        }
    
    def run_simulation(self, duration_hours=8, fault_type=0, fault_start_hour=1, save_results=True, plot_results=True):
        """
        Run a TEP simulation with specified parameters.
        
        Parameters:
        -----------
        duration_hours : int
            Total simulation duration in hours (default: 8)
        fault_type : int
            Fault type (0-20, where 0 = no fault, default: 0)
        fault_start_hour : float
            When to introduce the fault in hours (default: 1)
        save_results : bool
            Whether to save results to CSV file (default: True)
        plot_results : bool
            Whether to generate plots (default: True)
            
        Returns:
        --------
        pandas.DataFrame
            Simulation results with process measurements and manipulated variables
        """
        
        print(f"\n🚀 Starting TEP Simulation")
        print(f"   Duration: {duration_hours} hours")
        print(f"   Fault: {fault_type} - {self.fault_descriptions.get(fault_type, 'Unknown')}")
        if fault_type > 0:
            print(f"   Fault starts at: {fault_start_hour} hours")
        print("-" * 60)
        
        # Calculate simulation parameters
        # TEP simulator: 1 sample every 3 minutes (180 seconds)
        samples_per_hour = 20  # 60 minutes / 3 minutes per sample
        total_samples = int(duration_hours * samples_per_hour)
        fault_start_sample = int(fault_start_hour * samples_per_hour)
        
        # Initialize disturbance matrix (samples x 20 disturbances)
        idata = np.zeros((total_samples, 20))
        
        # Set fault if specified
        if fault_type > 0 and fault_type <= 20:
            if fault_start_sample < total_samples:
                idata[fault_start_sample:, fault_type-1] = 1
                print(f"   Fault {fault_type} activated at sample {fault_start_sample}")
        
        # Run simulation
        print("   Running simulation... ⏳")
        tep = tep2py(idata)
        tep.simulate()
        
        # Get results
        results = tep.process_data.copy()
        
        # Add time column in hours for easier interpretation
        results['Time_Hours'] = np.arange(0, duration_hours, duration_hours/len(results))
        
        print(f"✅ Simulation completed! Generated {len(results)} data points")
        
        # Save results
        if save_results:
            filename = f"tep_simulation_fault_{fault_type}_{duration_hours}h.csv"
            results.to_csv(filename)
            print(f"💾 Results saved to: {filename}")
        
        # Generate plots
        if plot_results:
            self._plot_results(results, fault_type, fault_start_hour)
        
        return results
    
    def _plot_results(self, results, fault_type, fault_start_hour):
        """Generate plots for simulation results."""
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'TEP Simulation Results - Fault {fault_type}', fontsize=16)
        
        time_hours = results['Time_Hours']
        
        # Plot 1: Reactor pressure and temperature
        axes[0,0].plot(time_hours, results['XMEAS(7)'], 'b-', label='Reactor Pressure')
        axes[0,0].set_ylabel('Reactor Pressure (kPa)', color='b')
        axes[0,0].tick_params(axis='y', labelcolor='b')
        ax2 = axes[0,0].twinx()
        ax2.plot(time_hours, results['XMEAS(9)'], 'r-', label='Reactor Temperature')
        ax2.set_ylabel('Reactor Temperature (°C)', color='r')
        ax2.tick_params(axis='y', labelcolor='r')
        axes[0,0].set_title('Reactor Conditions')
        axes[0,0].set_xlabel('Time (hours)')
        if fault_type > 0:
            axes[0,0].axvline(x=fault_start_hour, color='k', linestyle='--', alpha=0.7, label='Fault Start')
        
        # Plot 2: Product flow rates
        axes[0,1].plot(time_hours, results['XMEAS(11)'], label='Product Sep Flow')
        axes[0,1].plot(time_hours, results['XMEAS(17)'], label='Stripper Steam Flow')
        axes[0,1].set_title('Product Flows')
        axes[0,1].set_xlabel('Time (hours)')
        axes[0,1].set_ylabel('Flow Rate')
        axes[0,1].legend()
        if fault_type > 0:
            axes[0,1].axvline(x=fault_start_hour, color='k', linestyle='--', alpha=0.7)
        
        # Plot 3: Reactor levels
        axes[1,0].plot(time_hours, results['XMEAS(12)'], label='Reactor Level')
        axes[1,0].plot(time_hours, results['XMEAS(13)'], label='Separator Level')
        axes[1,0].set_title('Process Levels')
        axes[1,0].set_xlabel('Time (hours)')
        axes[1,0].set_ylabel('Level (%)')
        axes[1,0].legend()
        if fault_type > 0:
            axes[1,0].axvline(x=fault_start_hour, color='k', linestyle='--', alpha=0.7)
        
        # Plot 4: Manipulated variables (first few)
        axes[1,1].plot(time_hours, results['XMV(1)'], label='D Feed Flow')
        axes[1,1].plot(time_hours, results['XMV(2)'], label='E Feed Flow')
        axes[1,1].plot(time_hours, results['XMV(3)'], label='A Feed Flow')
        axes[1,1].set_title('Feed Flow Rates')
        axes[1,1].set_xlabel('Time (hours)')
        axes[1,1].set_ylabel('Flow Rate (%)')
        axes[1,1].legend()
        if fault_type > 0:
            axes[1,1].axvline(x=fault_start_hour, color='k', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        
        # Save plot
        plot_filename = f"tep_simulation_fault_{fault_type}_plot.png"
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        print(f"📊 Plot saved to: {plot_filename}")
        
        plt.show()
    
    def list_faults(self):
        """Display available fault types."""
        print("\n🔧 Available TEP Fault Types:")
        print("=" * 50)
        for fault_id, description in self.fault_descriptions.items():
            print(f"Fault {fault_id:2d}: {description}")
        print("=" * 50)


def main():
    """Main function with example usage."""
    
    # Create simulator instance
    simulator = TEPSimulatorEasy()
    
    # Show available faults
    simulator.list_faults()
    
    print("\n" + "="*60)
    print("🎯 EXAMPLE SIMULATIONS")
    print("="*60)
    
    # Example 1: Normal operation
    print("\n1️⃣  Running normal operation (no fault)...")
    results_normal = simulator.run_simulation(
        duration_hours=4,
        fault_type=0,
        save_results=True,
        plot_results=False  # Set to True to see plots
    )
    
    # Example 2: Fault simulation
    print("\n2️⃣  Running simulation with Fault 1 (A/C feed ratio)...")
    results_fault = simulator.run_simulation(
        duration_hours=6,
        fault_type=1,
        fault_start_hour=2,
        save_results=True,
        plot_results=False  # Set to True to see plots
    )
    
    print("\n" + "="*60)
    print("✅ SIMULATION COMPLETE!")
    print("="*60)
    print("📁 Check the generated CSV files and plots in the current directory.")
    print("🔧 Modify the parameters above to test different scenarios.")
    print("📊 Set plot_results=True to see real-time plots.")


if __name__ == "__main__":
    main()
