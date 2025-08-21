#!/usr/bin/env python3
"""
Run Academic Benchmark - All TEP Faults
=======================================

This script runs the standard academic benchmark used in research papers.
You can choose to run all faults or just a subset for learning.

Author: Augment Agent
Date: 2025-06-29
"""

import sys
import os
import time
from datetime import datetime

# Add TEP simulator to path
sys.path.append('external_repos/tep2py-master')

try:
    from tep_simulator_easy import TEPSimulatorEasy
    print("✅ TEP simulator loaded successfully!")
except ImportError as e:
    print(f"❌ Error loading TEP simulator: {e}")
    sys.exit(1)


def run_beginner_benchmark():
    """Run a beginner-friendly subset of faults."""
    
    print("🎯 BEGINNER'S BENCHMARK")
    print("="*50)
    print("Running 5 most important faults for learning:")
    
    simulator = TEPSimulatorEasy()
    
    # 5 most educational faults
    beginner_faults = [
        (1, "Feed Composition - Easy to see"),
        (4, "Cooling Water - Safety critical"),
        (6, "Feed Loss - Production impact"),
        (8, "Multiple Feed Issues - Complex"),
        (13, "Reaction Kinetics - Subtle/Advanced")
    ]
    
    print("\nFaults to run:")
    for fault_id, description in beginner_faults:
        print(f"   • Fault {fault_id}: {description}")
    
    print(f"\nThis will create {len(beginner_faults)} CSV files and {len(beginner_faults)} plot files.")
    
    # Run each fault
    for i, (fault_id, description) in enumerate(beginner_faults, 1):
        print(f"\n[{i}/{len(beginner_faults)}] Running Fault {fault_id}: {description}")
        
        try:
            simulator.run_simulation(
                duration_hours=6,
                fault_type=fault_id,
                fault_start_hour=1.5,
                save_results=True,
                plot_results=True
            )
            print(f"   ✅ Fault {fault_id} completed")
        except Exception as e:
            print(f"   ❌ Fault {fault_id} failed: {e}")
    
    print("\n🎉 Beginner's benchmark complete!")
    return len(beginner_faults)


def run_standard_benchmark():
    """Run the full academic benchmark (faults 1-15)."""
    
    print("🎓 STANDARD ACADEMIC BENCHMARK")
    print("="*50)
    print("Running faults 1-15 (standard research protocol)")
    print("Duration: 8 hours each, Fault starts: 1 hour")
    print("This is the same benchmark used in 100+ research papers!")
    
    simulator = TEPSimulatorEasy()
    
    # Standard academic faults (skip 16-20 as they're unknown)
    standard_faults = list(range(1, 16))  # Faults 1-15
    
    print(f"\nThis will run {len(standard_faults)} fault simulations.")
    print("Each simulation takes about 30-60 seconds.")
    print(f"Estimated total time: {len(standard_faults) * 1} minutes")
    
    confirm = input("\nProceed with full benchmark? (y/n): ").lower().strip()
    if confirm != 'y':
        print("Benchmark cancelled.")
        return 0
    
    successful_runs = 0
    start_time = time.time()
    
    # Run each fault
    for i, fault_id in enumerate(standard_faults, 1):
        print(f"\n[{i}/{len(standard_faults)}] Running Fault {fault_id}...")
        
        try:
            simulator.run_simulation(
                duration_hours=8,
                fault_type=fault_id,
                fault_start_hour=1,
                save_results=True,
                plot_results=False  # Skip plots for speed
            )
            successful_runs += 1
            print(f"   ✅ Fault {fault_id} completed")
        except Exception as e:
            print(f"   ❌ Fault {fault_id} failed: {e}")
    
    # Also run normal operation for comparison
    print(f"\n[{len(standard_faults)+1}/{len(standard_faults)+1}] Running Normal Operation...")
    try:
        simulator.run_simulation(
            duration_hours=8,
            fault_type=0,
            fault_start_hour=1,
            save_results=True,
            plot_results=False
        )
        successful_runs += 1
        print("   ✅ Normal operation completed")
    except Exception as e:
        print(f"   ❌ Normal operation failed: {e}")
    
    elapsed_time = time.time() - start_time
    print(f"\n🎉 Standard benchmark complete!")
    print(f"   Successful runs: {successful_runs}/{len(standard_faults)+1}")
    print(f"   Total time: {elapsed_time/60:.1f} minutes")
    
    return successful_runs


def run_custom_benchmark():
    """Run a custom set of faults chosen by the user."""
    
    print("🎛️ CUSTOM BENCHMARK")
    print("="*50)
    print("Choose which faults to run:")
    print("\nEasy faults (good for learning): 1, 2, 3, 4, 5, 6, 9")
    print("Medium faults (intermediate): 7, 8, 10, 11, 12")
    print("Hard faults (advanced): 13, 14, 15")
    
    fault_input = input("\nEnter fault numbers (comma-separated, e.g., 1,4,6,13): ").strip()
    
    try:
        fault_list = [int(x.strip()) for x in fault_input.split(',')]
        fault_list = [f for f in fault_list if 1 <= f <= 20]  # Validate range
        
        if not fault_list:
            print("No valid faults specified.")
            return 0
            
    except ValueError:
        print("Invalid input format.")
        return 0
    
    duration = input("Duration in hours (default: 6): ").strip()
    try:
        duration = float(duration) if duration else 6
    except ValueError:
        duration = 6
    
    fault_start = input("Fault start time in hours (default: 1.5): ").strip()
    try:
        fault_start = float(fault_start) if fault_start else 1.5
    except ValueError:
        fault_start = 1.5
    
    create_plots = input("Create plots? (y/n, default: y): ").strip().lower()
    create_plots = create_plots != 'n'
    
    print(f"\nRunning {len(fault_list)} faults: {fault_list}")
    print(f"Duration: {duration} hours, Fault start: {fault_start} hours")
    print(f"Plots: {'Yes' if create_plots else 'No'}")
    
    simulator = TEPSimulatorEasy()
    successful_runs = 0
    
    for i, fault_id in enumerate(fault_list, 1):
        print(f"\n[{i}/{len(fault_list)}] Running Fault {fault_id}...")
        
        try:
            simulator.run_simulation(
                duration_hours=duration,
                fault_type=fault_id,
                fault_start_hour=fault_start,
                save_results=True,
                plot_results=create_plots
            )
            successful_runs += 1
            print(f"   ✅ Fault {fault_id} completed")
        except Exception as e:
            print(f"   ❌ Fault {fault_id} failed: {e}")
    
    print(f"\n🎉 Custom benchmark complete!")
    print(f"   Successful runs: {successful_runs}/{len(fault_list)}")
    
    return successful_runs


def show_csv_info():
    """Show information about generated CSV files."""
    
    print("\n📊 CSV FILES INFORMATION")
    print("="*50)
    
    # Count CSV files
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv') and 'tep_simulation' in f]
    
    if not csv_files:
        print("No TEP simulation CSV files found.")
        return
    
    print(f"Found {len(csv_files)} simulation CSV files:")
    
    total_size = 0
    for csv_file in sorted(csv_files):
        size = os.path.getsize(csv_file)
        total_size += size
        print(f"   • {csv_file} ({size/1024:.1f} KB)")
    
    print(f"\nTotal size: {total_size/1024:.1f} KB")
    
    print("\n📋 Each CSV file contains:")
    print("   • 41 XMEAS variables (process measurements)")
    print("   • 11 XMV variables (manipulated variables)")
    print("   • Time_Hours column")
    print("   • One row per sample (20 samples/hour)")
    
    print("\n💡 To analyze the data:")
    print("   • Open in Excel/Google Sheets")
    print("   • Use pandas in Python: pd.read_csv('filename.csv')")
    print("   • Plot with matplotlib or other tools")


def main():
    """Main function."""
    
    print("🎓 TEP Academic Benchmark Runner")
    print("="*50)
    print("Choose your benchmark type:")
    print("1. Beginner's Benchmark (5 key faults, with plots)")
    print("2. Standard Academic Benchmark (faults 1-15, research standard)")
    print("3. Custom Benchmark (choose your own faults)")
    print("4. Show CSV file information")
    print("5. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            runs = run_beginner_benchmark()
            show_csv_info()
            break
        elif choice == '2':
            runs = run_standard_benchmark()
            show_csv_info()
            break
        elif choice == '3':
            runs = run_custom_benchmark()
            show_csv_info()
            break
        elif choice == '4':
            show_csv_info()
            break
        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-5.")


if __name__ == "__main__":
    main()
