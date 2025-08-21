#!/usr/bin/env python3
"""
TEP Simulator Demo with Plots
=============================

This script demonstrates the TEP simulator with visualization.
Run this to see the simulator in action with real-time plots.

Author: Augment Agent
Date: 2025-06-29
"""

from tep_simulator_easy import TEPSimulatorEasy
import matplotlib.pyplot as plt

def main():
    """Run demonstration with plots."""
    
    print("🎬 TEP Simulator Demo with Visualization")
    print("="*50)
    
    # Create simulator
    simulator = TEPSimulatorEasy()
    
    # Demo 1: Normal operation
    print("\n📊 Demo 1: Normal Operation (4 hours)")
    print("-" * 40)
    
    results_normal = simulator.run_simulation(
        duration_hours=4,
        fault_type=0,
        save_results=True,
        plot_results=True  # Enable plots
    )
    
    print(f"✅ Normal operation completed: {len(results_normal)} data points")
    
    # Demo 2: Fault simulation
    print("\n📊 Demo 2: Fault Simulation (6 hours)")
    print("-" * 40)
    
    results_fault = simulator.run_simulation(
        duration_hours=6,
        fault_type=3,  # D feed temperature fault
        fault_start_hour=2,
        save_results=True,
        plot_results=True  # Enable plots
    )
    
    print(f"✅ Fault simulation completed: {len(results_fault)} data points")
    
    # Demo 3: Comparison plot
    print("\n📊 Demo 3: Comparison Analysis")
    print("-" * 40)
    
    # Create comparison plot
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    fig.suptitle('TEP Simulation Comparison: Normal vs Fault', fontsize=16)
    
    # Plot reactor temperature comparison
    time_normal = results_normal['Time_Hours']
    time_fault = results_fault['Time_Hours']
    
    axes[0].plot(time_normal, results_normal['XMEAS(9)'], 'b-', 
                label='Normal Operation', linewidth=2)
    axes[0].plot(time_fault, results_fault['XMEAS(9)'], 'r-', 
                label='With Fault 3', linewidth=2)
    axes[0].axvline(x=2, color='k', linestyle='--', alpha=0.7, label='Fault Start')
    axes[0].set_title('Reactor Temperature Comparison')
    axes[0].set_ylabel('Temperature (°C)')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Plot reactor pressure comparison
    axes[1].plot(time_normal, results_normal['XMEAS(7)'], 'b-', 
                label='Normal Operation', linewidth=2)
    axes[1].plot(time_fault, results_fault['XMEAS(7)'], 'r-', 
                label='With Fault 3', linewidth=2)
    axes[1].axvline(x=2, color='k', linestyle='--', alpha=0.7, label='Fault Start')
    axes[1].set_title('Reactor Pressure Comparison')
    axes[1].set_xlabel('Time (hours)')
    axes[1].set_ylabel('Pressure (kPa)')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('tep_comparison_demo.png', dpi=300, bbox_inches='tight')
    print("📊 Comparison plot saved: tep_comparison_demo.png")
    plt.show()
    
    # Summary statistics
    print("\n📈 Summary Statistics")
    print("-" * 40)
    
    print("Normal Operation:")
    print(f"  Reactor Temp: {results_normal['XMEAS(9)'].mean():.2f} ± {results_normal['XMEAS(9)'].std():.2f} °C")
    print(f"  Reactor Press: {results_normal['XMEAS(7)'].mean():.2f} ± {results_normal['XMEAS(7)'].std():.2f} kPa")
    
    print("\nWith Fault 3:")
    print(f"  Reactor Temp: {results_fault['XMEAS(9)'].mean():.2f} ± {results_fault['XMEAS(9)'].std():.2f} °C")
    print(f"  Reactor Press: {results_fault['XMEAS(7)'].mean():.2f} ± {results_fault['XMEAS(7)'].std():.2f} kPa")
    
    print("\n" + "="*50)
    print("🎉 DEMO COMPLETE!")
    print("="*50)
    print("📁 Generated files:")
    print("   • tep_simulation_fault_0_4h.csv")
    print("   • tep_simulation_fault_3_6h.csv")
    print("   • tep_simulation_fault_0_plot.png")
    print("   • tep_simulation_fault_3_plot.png")
    print("   • tep_comparison_demo.png")
    print("\n🔧 Try modifying the fault types and parameters!")


if __name__ == "__main__":
    main()
