#!/usr/bin/env python3
"""
Step 3: Compare Different Fault Scenarios
=========================================

This script runs multiple fault scenarios so you can see how different
industrial problems affect the Tennessee Eastman Process.

Author: Augment Agent
Date: 2025-06-29
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

# Add TEP simulator to path
sys.path.append('external_repos/tep2py-master')

try:
    from tep2py import tep2py
    print("✅ TEP simulator loaded successfully!")
except ImportError as e:
    print(f"❌ Error loading TEP simulator: {e}")
    sys.exit(1)


def run_fault_scenario(fault_type, fault_name, duration_hours=4, fault_start_hour=1.5):
    """Run a single fault scenario."""
    
    print(f"\n🚀 Running Fault {fault_type}: {fault_name}")
    print(f"   Duration: {duration_hours} hours, Fault starts: {fault_start_hour} hours")
    
    # Calculate simulation parameters
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
    
    # Get results
    results = tep.process_data.copy()
    results['Time_Hours'] = np.arange(0, duration_hours, duration_hours/len(results))
    results['Fault_Type'] = fault_type
    results['Fault_Name'] = fault_name
    
    print(f"   ✅ Completed: {len(results)} data points")
    
    return results


def create_fault_comparison():
    """Run multiple fault scenarios and create comparison plots."""
    
    print("🎯 STEP 3: Comparing Different Fault Scenarios")
    print("="*60)
    print("We'll run 4 different scenarios to show you the variety of industrial problems:")
    
    # Define scenarios to run
    scenarios = [
        (0, "Normal Operation"),
        (1, "Feed Composition Fault"),
        (4, "Cooling Water Fault"), 
        (6, "Feed Loss Fault")
    ]
    
    all_results = []
    
    # Run each scenario
    for fault_type, fault_name in scenarios:
        results = run_fault_scenario(fault_type, fault_name)
        all_results.append(results)
    
    return all_results


def create_comparison_plots(all_results):
    """Create comprehensive comparison plots."""
    
    print("\n📊 Creating comparison visualizations...")
    
    # Create a large comparison plot
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('TEP Fault Comparison - How Different Industrial Problems Affect the Process', 
                 fontsize=16, fontweight='bold')
    
    colors = ['green', 'blue', 'red', 'orange']
    fault_names = [results['Fault_Name'].iloc[0] for results in all_results]
    
    # Plot 1: Reactor Temperature (Most Important!)
    ax = axes[0, 0]
    for i, results in enumerate(all_results):
        ax.plot(results['Time_Hours'], results['XMEAS(9)'], 
               color=colors[i], linewidth=3, label=fault_names[i], alpha=0.8)
        if i > 0:  # Add fault start line for non-normal cases
            ax.axvline(x=1.5, color=colors[i], linestyle='--', alpha=0.5)
    
    ax.set_title('Reactor Temperature - Safety Critical!', fontsize=14, fontweight='bold')
    ax.set_ylabel('Temperature (°C)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 2: Reactor Pressure
    ax = axes[0, 1]
    for i, results in enumerate(all_results):
        ax.plot(results['Time_Hours'], results['XMEAS(7)'], 
               color=colors[i], linewidth=3, label=fault_names[i], alpha=0.8)
        if i > 0:
            ax.axvline(x=1.5, color=colors[i], linestyle='--', alpha=0.5)
    
    ax.set_title('Reactor Pressure', fontsize=14, fontweight='bold')
    ax.set_ylabel('Pressure (kPa)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 3: Product Flow Rate
    ax = axes[1, 0]
    for i, results in enumerate(all_results):
        ax.plot(results['Time_Hours'], results['XMEAS(11)'], 
               color=colors[i], linewidth=3, label=fault_names[i], alpha=0.8)
        if i > 0:
            ax.axvline(x=1.5, color=colors[i], linestyle='--', alpha=0.5)
    
    ax.set_title('Product Flow Rate - Production Impact', fontsize=14, fontweight='bold')
    ax.set_xlabel('Time (hours)')
    ax.set_ylabel('Flow Rate (m³/h)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 4: Feed Flow Rate
    ax = axes[1, 1]
    for i, results in enumerate(all_results):
        ax.plot(results['Time_Hours'], results['XMEAS(1)'], 
               color=colors[i], linewidth=3, label=fault_names[i], alpha=0.8)
        if i > 0:
            ax.axvline(x=1.5, color=colors[i], linestyle='--', alpha=0.5)
    
    ax.set_title('A Feed Flow Rate', fontsize=14, fontweight='bold')
    ax.set_xlabel('Time (hours)')
    ax.set_ylabel('Flow Rate (kscmh)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('step3_fault_comparison.png', dpi=300, bbox_inches='tight')
    print("📊 Fault comparison saved: step3_fault_comparison.png")
    plt.close()
    
    # Create individual fault effect plots
    create_individual_fault_plots(all_results)


def create_individual_fault_plots(all_results):
    """Create individual plots showing the effect of each fault."""
    
    normal_data = all_results[0]  # Normal operation
    
    for i in range(1, len(all_results)):
        fault_data = all_results[i]
        fault_name = fault_data['Fault_Name'].iloc[0]
        fault_type = fault_data['Fault_Type'].iloc[0]
        
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))
        fig.suptitle(f'Effect of {fault_name} (Fault {fault_type})', fontsize=16, fontweight='bold')
        
        # Temperature comparison
        axes[0].plot(normal_data['Time_Hours'], normal_data['XMEAS(9)'], 
                    'g-', linewidth=3, label='Normal Operation', alpha=0.8)
        axes[0].plot(fault_data['Time_Hours'], fault_data['XMEAS(9)'], 
                    'r-', linewidth=3, label=f'With {fault_name}', alpha=0.8)
        axes[0].axvline(x=1.5, color='black', linestyle='--', linewidth=2, label='Fault Introduced')
        axes[0].set_title('Reactor Temperature Comparison', fontsize=14)
        axes[0].set_ylabel('Temperature (°C)')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Calculate and show the impact
        normal_temp = normal_data['XMEAS(9)'][30:].mean()  # After fault would start
        fault_temp = fault_data['XMEAS(9)'][30:].mean()    # After fault starts
        temp_change = fault_temp - normal_temp
        
        axes[0].text(0.02, 0.98, f'Temperature Impact: {temp_change:+.2f}°C', 
                    transform=axes[0].transAxes, verticalalignment='top',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
        
        # Product flow comparison
        axes[1].plot(normal_data['Time_Hours'], normal_data['XMEAS(11)'], 
                    'g-', linewidth=3, label='Normal Operation', alpha=0.8)
        axes[1].plot(fault_data['Time_Hours'], fault_data['XMEAS(11)'], 
                    'r-', linewidth=3, label=f'With {fault_name}', alpha=0.8)
        axes[1].axvline(x=1.5, color='black', linestyle='--', linewidth=2, label='Fault Introduced')
        axes[1].set_title('Product Flow Rate Comparison', fontsize=14)
        axes[1].set_xlabel('Time (hours)')
        axes[1].set_ylabel('Flow Rate (m³/h)')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        # Calculate production impact
        normal_flow = normal_data['XMEAS(11)'][30:].mean()
        fault_flow = fault_data['XMEAS(11)'][30:].mean()
        flow_change = fault_flow - normal_flow
        
        axes[1].text(0.02, 0.98, f'Production Impact: {flow_change:+.2f} m³/h', 
                    transform=axes[1].transAxes, verticalalignment='top',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))
        
        plt.tight_layout()
        filename = f'step3_fault_{fault_type}_effect.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"📊 Individual fault effect saved: {filename}")
        plt.close()


def create_summary_report(all_results):
    """Create a summary report of all fault effects."""
    
    print("\n📋 Creating summary report...")
    
    normal_data = all_results[0]
    
    summary_data = []
    
    for results in all_results:
        fault_type = results['Fault_Type'].iloc[0]
        fault_name = results['Fault_Name'].iloc[0]
        
        # Calculate average values after fault period
        after_fault = results.iloc[30:]  # After 1.5 hours
        
        avg_temp = after_fault['XMEAS(9)'].mean()
        avg_pressure = after_fault['XMEAS(7)'].mean()
        avg_product_flow = after_fault['XMEAS(11)'].mean()
        
        if fault_type == 0:
            temp_change = 0
            pressure_change = 0
            flow_change = 0
        else:
            normal_after = normal_data.iloc[30:]
            temp_change = avg_temp - normal_after['XMEAS(9)'].mean()
            pressure_change = avg_pressure - normal_after['XMEAS(7)'].mean()
            flow_change = avg_product_flow - normal_after['XMEAS(11)'].mean()
        
        summary_data.append({
            'Fault_Type': fault_type,
            'Fault_Name': fault_name,
            'Avg_Temperature': avg_temp,
            'Temperature_Change': temp_change,
            'Avg_Pressure': avg_pressure,
            'Pressure_Change': pressure_change,
            'Avg_Product_Flow': avg_product_flow,
            'Flow_Change': flow_change
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv('step3_fault_summary.csv', index=False)
    print("📊 Summary report saved: step3_fault_summary.csv")
    
    return summary_df


def main():
    """Main function for Step 3."""
    
    print("🎯 STEP 3: Compare Different Fault Scenarios")
    print("="*60)
    print("This will run 4 different industrial fault scenarios:")
    print("   • Normal Operation (baseline)")
    print("   • Feed Composition Fault (quality issues)")
    print("   • Cooling Water Fault (safety critical)")
    print("   • Feed Loss Fault (production impact)")
    print("\nYou'll see how each affects the process differently!")
    
    # Run all scenarios
    all_results = create_fault_comparison()
    
    # Create visualizations
    create_comparison_plots(all_results)
    
    # Create summary report
    summary_df = create_summary_report(all_results)
    
    print("\n" + "="*60)
    print("✅ STEP 3 COMPLETE!")
    print("="*60)
    print("📁 Files created:")
    print("   • step3_fault_comparison.png - Side-by-side comparison of all faults")
    print("   • step3_fault_1_effect.png - Feed composition fault details")
    print("   • step3_fault_4_effect.png - Cooling water fault details")
    print("   • step3_fault_6_effect.png - Feed loss fault details")
    print("   • step3_fault_summary.csv - Numerical summary of all effects")
    
    print("\n🎯 WHAT YOU LEARNED:")
    print("   • Different faults affect different parts of the process")
    print("   • Cooling water fault (4) has the biggest temperature impact")
    print("   • Feed loss fault (6) reduces production the most")
    print("   • Feed composition fault (1) causes subtle but important changes")
    print("   • Each fault has a unique 'signature' that can be detected")
    
    print("\n📊 KEY INSIGHTS:")
    for _, row in summary_df.iterrows():
        if row['Fault_Type'] > 0:
            print(f"   • {row['Fault_Name']}: "
                  f"Temp {row['Temperature_Change']:+.1f}°C, "
                  f"Flow {row['Flow_Change']:+.1f} m³/h")
    
    print("\n👀 NEXT: Open the PNG files to see the detailed comparisons!")


if __name__ == "__main__":
    main()
