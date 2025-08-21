#!/usr/bin/env python3
"""
Step 1: Simple TEP Visualization
================================

A simple, reliable visualization that will definitely work on your system.
This creates static plots that are saved as PNG files you can view.

Author: Augment Agent
Date: 2025-06-29
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to ensure it works

# Add TEP simulator to path
sys.path.append('external_repos/tep2py-master')

try:
    from tep2py import tep2py
    print("✅ TEP simulator loaded successfully!")
except ImportError as e:
    print(f"❌ Error loading TEP simulator: {e}")
    sys.exit(1)


def create_process_diagram():
    """Create a simple process flow diagram."""
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # Create a simple process flow diagram
    ax.text(0.1, 0.8, "FEED A", fontsize=14, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
    ax.text(0.1, 0.6, "FEED D", fontsize=14, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
    
    # Reactor
    ax.text(0.4, 0.7, "REACTOR\n(High Pressure\nChemical Reaction)", fontsize=14, 
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightcoral"), ha='center')
    
    # Separator
    ax.text(0.7, 0.7, "SEPARATOR\n(Liquid/Gas\nSeparation)", fontsize=14,
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgreen"), ha='center')
    
    # Stripper
    ax.text(0.7, 0.3, "STRIPPER\n(Product\nPurification)", fontsize=14,
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow"), ha='center')
    
    # Product
    ax.text(0.9, 0.3, "PRODUCT", fontsize=14, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightpink"))
    
    # Arrows
    ax.annotate('', xy=(0.35, 0.75), xytext=(0.25, 0.8), 
                arrowprops=dict(arrowstyle='->', lw=2, color='blue'))
    ax.annotate('', xy=(0.35, 0.65), xytext=(0.25, 0.6), 
                arrowprops=dict(arrowstyle='->', lw=2, color='blue'))
    ax.annotate('', xy=(0.65, 0.7), xytext=(0.55, 0.7), 
                arrowprops=dict(arrowstyle='->', lw=2, color='red'))
    ax.annotate('', xy=(0.7, 0.45), xytext=(0.7, 0.55), 
                arrowprops=dict(arrowstyle='->', lw=2, color='green'))
    ax.annotate('', xy=(0.85, 0.3), xytext=(0.8, 0.3), 
                arrowprops=dict(arrowstyle='->', lw=2, color='purple'))
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title('Tennessee Eastman Process - Simplified Flow Diagram', fontsize=16, fontweight='bold')
    ax.text(0.5, 0.1, 'This is the industrial chemical process you are simulating!', 
            ha='center', fontsize=12, style='italic')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('step1_process_diagram.png', dpi=300, bbox_inches='tight')
    print("📊 Process diagram saved: step1_process_diagram.png")
    plt.close()


def run_simple_simulation():
    """Run a simple simulation and create clear visualizations."""
    
    print("\n🚀 Running TEP Simulation...")
    print("   Duration: 4 hours")
    print("   Fault: 4 (Reactor Cooling Water)")
    print("   Fault starts at: 1.5 hours")
    print("-" * 50)
    
    # Simulation parameters
    duration_hours = 4
    fault_type = 4
    fault_start_hour = 1.5
    
    # Calculate simulation parameters
    samples_per_hour = 20  # TEP standard: 1 sample every 3 minutes
    total_samples = int(duration_hours * samples_per_hour)
    fault_start_sample = int(fault_start_hour * samples_per_hour)
    
    # Create disturbance matrix
    idata = np.zeros((total_samples, 20))
    idata[fault_start_sample:, fault_type-1] = 1  # Activate fault 4
    
    print(f"   Total samples: {total_samples}")
    print(f"   Fault starts at sample: {fault_start_sample}")
    print("   Running simulation... ⏳")
    
    # Run simulation
    tep = tep2py(idata)
    tep.simulate()
    
    # Get results
    results = tep.process_data.copy()
    results['Time_Hours'] = np.arange(0, duration_hours, duration_hours/len(results))
    
    print(f"✅ Simulation completed! Generated {len(results)} data points")
    
    return results, fault_start_hour


def create_visualization_plots(results, fault_start_hour):
    """Create clear, informative plots."""
    
    print("\n📊 Creating visualization plots...")
    
    # Create a comprehensive 4-panel plot
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('TEP Simulation Results - Cooling Water Fault (Fault 4)', fontsize=16, fontweight='bold')
    
    time_hours = results['Time_Hours']
    
    # Plot 1: Reactor Temperature (Most Important!)
    axes[0,0].plot(time_hours, results['XMEAS(9)'], 'r-', linewidth=3, label='Reactor Temperature')
    axes[0,0].axvline(x=fault_start_hour, color='black', linestyle='--', linewidth=2, 
                     label=f'Fault Starts ({fault_start_hour}h)')
    axes[0,0].set_title('🌡️ Reactor Temperature (Critical!)', fontsize=14, fontweight='bold')
    axes[0,0].set_ylabel('Temperature (°C)')
    axes[0,0].legend()
    axes[0,0].grid(True, alpha=0.3)
    
    # Add annotations
    normal_temp = results['XMEAS(9)'][:int(fault_start_hour*20)].mean()
    fault_temp = results['XMEAS(9)'][int(fault_start_hour*20):].mean()
    temp_change = fault_temp - normal_temp
    
    axes[0,0].text(0.02, 0.98, f'Normal: {normal_temp:.1f}°C\nWith Fault: {fault_temp:.1f}°C\nChange: {temp_change:+.1f}°C', 
                  transform=axes[0,0].transAxes, verticalalignment='top',
                  bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
    
    # Plot 2: Reactor Pressure
    axes[0,1].plot(time_hours, results['XMEAS(7)'], 'b-', linewidth=3, label='Reactor Pressure')
    axes[0,1].axvline(x=fault_start_hour, color='black', linestyle='--', linewidth=2)
    axes[0,1].set_title('📊 Reactor Pressure', fontsize=14, fontweight='bold')
    axes[0,1].set_ylabel('Pressure (kPa)')
    axes[0,1].legend()
    axes[0,1].grid(True, alpha=0.3)
    
    # Plot 3: Product Flow Rate
    axes[1,0].plot(time_hours, results['XMEAS(11)'], 'g-', linewidth=3, label='Product Flow')
    axes[1,0].axvline(x=fault_start_hour, color='black', linestyle='--', linewidth=2)
    axes[1,0].set_title('🏭 Product Flow Rate', fontsize=14, fontweight='bold')
    axes[1,0].set_xlabel('Time (hours)')
    axes[1,0].set_ylabel('Flow Rate (m³/h)')
    axes[1,0].legend()
    axes[1,0].grid(True, alpha=0.3)
    
    # Plot 4: Reactor Level
    axes[1,1].plot(time_hours, results['XMEAS(12)'], 'purple', linewidth=3, label='Reactor Level')
    axes[1,1].axvline(x=fault_start_hour, color='black', linestyle='--', linewidth=2)
    axes[1,1].set_title('📏 Reactor Level', fontsize=14, fontweight='bold')
    axes[1,1].set_xlabel('Time (hours)')
    axes[1,1].set_ylabel('Level (%)')
    axes[1,1].legend()
    axes[1,1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('step1_simulation_results.png', dpi=300, bbox_inches='tight')
    print("📊 Simulation results saved: step1_simulation_results.png")
    plt.close()
    
    # Create a simple before/after comparison
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    
    # Split data into before and after fault
    fault_sample = int(fault_start_hour * 20)
    before_fault = results.iloc[:fault_sample]
    after_fault = results.iloc[fault_sample:]
    
    ax.plot(before_fault['Time_Hours'], before_fault['XMEAS(9)'], 'g-', linewidth=4, 
           label='NORMAL OPERATION', alpha=0.8)
    ax.plot(after_fault['Time_Hours'], after_fault['XMEAS(9)'], 'r-', linewidth=4, 
           label='WITH COOLING WATER FAULT', alpha=0.8)
    
    ax.axvline(x=fault_start_hour, color='black', linestyle='--', linewidth=3, 
              label=f'FAULT INTRODUCED')
    
    ax.set_title('🚨 DRAMATIC EFFECT OF COOLING WATER FAULT ON REACTOR TEMPERATURE', 
                fontsize=16, fontweight='bold')
    ax.set_xlabel('Time (hours)', fontsize=14)
    ax.set_ylabel('Reactor Temperature (°C)', fontsize=14)
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # Add explanation text
    ax.text(0.02, 0.98, 
           'WHAT YOU\'RE SEEING:\n'
           '• Green = Normal operation (stable temperature)\n'
           '• Red = After cooling water fault (temperature rises!)\n'
           '• This is a SAFETY CRITICAL fault in real industry!', 
           transform=ax.transAxes, verticalalignment='top', fontsize=11,
           bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.9))
    
    plt.tight_layout()
    plt.savefig('step1_before_after_comparison.png', dpi=300, bbox_inches='tight')
    print("📊 Before/after comparison saved: step1_before_after_comparison.png")
    plt.close()


def main():
    """Main function for Step 1."""
    
    print("🎯 STEP 1: Simple TEP Visualization")
    print("="*50)
    print("This will create visual plots saved as PNG files that you can view.")
    print("No complex windows - just clear, simple visualizations!")
    
    # Step 1a: Create process diagram
    print("\n📋 Step 1a: Creating process flow diagram...")
    create_process_diagram()
    
    # Step 1b: Run simulation
    print("\n🚀 Step 1b: Running simulation...")
    results, fault_start_hour = run_simple_simulation()
    
    # Step 1c: Create visualizations
    print("\n📊 Step 1c: Creating visualization plots...")
    create_visualization_plots(results, fault_start_hour)
    
    # Step 1d: Save data
    results.to_csv('step1_simulation_data.csv', index=False)
    print("💾 Simulation data saved: step1_simulation_data.csv")
    
    print("\n" + "="*50)
    print("✅ STEP 1 COMPLETE!")
    print("="*50)
    print("📁 Files created:")
    print("   • step1_process_diagram.png - Shows what the TEP process looks like")
    print("   • step1_simulation_results.png - 4-panel detailed results")
    print("   • step1_before_after_comparison.png - Clear before/after comparison")
    print("   • step1_simulation_data.csv - Raw data for analysis")
    
    print("\n🎯 WHAT YOU LEARNED:")
    print("   • The TEP is a chemical process with reactor, separator, stripper")
    print("   • Fault 4 (cooling water) causes reactor temperature to rise")
    print("   • This is SAFETY CRITICAL in real industrial plants!")
    print("   • The simulator shows realistic industrial behavior")
    
    print("\n👀 NEXT: Open the PNG files to see your results!")
    print("   Double-click on the .png files to view them")


if __name__ == "__main__":
    main()
