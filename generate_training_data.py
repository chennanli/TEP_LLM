#!/usr/bin/env python3
"""
TEP Training Data Generator
==========================

Generate training datasets for deep learning studies.
No GUI - just pure data generation with configurable parameters.
"""

import sys
import numpy as np
import pandas as pd
import time
from datetime import datetime
import os

# Add TEP simulator to path
sys.path.append('external_repos/tep2py-master')

try:
    from tep2py import tep2py
    print("✅ TEP simulator loaded successfully!")
except ImportError as e:
    print(f"❌ Error loading TEP simulator: {e}")
    sys.exit(1)

class TEPDataGenerator:
    """Generate training data for machine learning models."""
    
    def __init__(self):
        self.fault_types = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        self.variable_names = [
            'XMEAS(1)', 'XMEAS(2)', 'XMEAS(3)', 'XMEAS(4)', 'XMEAS(5)', 'XMEAS(6)',
            'XMEAS(7)', 'XMEAS(8)', 'XMEAS(9)', 'XMEAS(10)', 'XMEAS(11)', 'XMEAS(12)',
            'XMEAS(13)', 'XMEAS(14)', 'XMEAS(15)', 'XMEAS(16)', 'XMEAS(17)', 'XMEAS(18)',
            'XMEAS(19)', 'XMEAS(20)', 'XMEAS(21)', 'XMEAS(22)', 'XMEAS(23)', 'XMEAS(24)',
            'XMEAS(25)', 'XMEAS(26)', 'XMEAS(27)', 'XMEAS(28)', 'XMEAS(29)', 'XMEAS(30)',
            'XMEAS(31)', 'XMEAS(32)', 'XMEAS(33)', 'XMEAS(34)', 'XMEAS(35)', 'XMEAS(36)',
            'XMEAS(37)', 'XMEAS(38)', 'XMEAS(39)', 'XMEAS(40)', 'XMEAS(41)',
            'XMV(1)', 'XMV(2)', 'XMV(3)', 'XMV(4)', 'XMV(5)', 'XMV(6)',
            'XMV(7)', 'XMV(8)', 'XMV(9)', 'XMV(10)', 'XMV(11)'
        ]
    
    def generate_fault_data(self, fault_type, duration_hours=8, intensity=1.0, samples_per_hour=60):
        """
        Generate data for a specific fault type.
        
        Args:
            fault_type (int): Fault number (0-20, 0=normal)
            duration_hours (float): Simulation duration in hours
            intensity (float): Fault intensity (0.5-2.0)
            samples_per_hour (int): Sampling frequency
        
        Returns:
            pandas.DataFrame: Simulation data with timestamps
        """
        print(f"🔄 Generating fault {fault_type} data...")
        print(f"   Duration: {duration_hours}h, Intensity: {intensity}, Samples/h: {samples_per_hour}")
        
        total_samples = int(duration_hours * samples_per_hour)
        all_data = []
        
        for i in range(total_samples):
            # Create fault input vector
            idata = np.zeros((1, 20))
            if fault_type > 0:
                idata[0, fault_type-1] = intensity
            
            # Run simulation
            tep = tep2py(idata)
            tep.simulate()
            data = tep.process_data
            
            if len(data) > 0:
                latest = data.iloc[-1].copy()
                latest['timestamp'] = i * (60 / samples_per_hour)  # minutes
                latest['fault_type'] = fault_type
                latest['fault_intensity'] = intensity if fault_type > 0 else 0.0
                all_data.append(latest)
            
            # Progress indicator
            if (i + 1) % (samples_per_hour * 2) == 0:  # Every 2 hours
                progress = (i + 1) / total_samples * 100
                print(f"   Progress: {progress:.1f}%")
        
        df = pd.DataFrame(all_data)
        print(f"✅ Generated {len(df)} samples for fault {fault_type}")
        return df
    
    def generate_mixed_dataset(self, output_dir="data/training_datasets"):
        """Generate a comprehensive dataset with all fault types."""
        print("🚀 Generating comprehensive training dataset...")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        all_datasets = []
        
        # Generate normal operation data (longer duration)
        normal_data = self.generate_fault_data(0, duration_hours=12, intensity=0.0)
        all_datasets.append(normal_data)
        
        # Generate fault data for each fault type
        for fault in range(1, 21):
            fault_data = self.generate_fault_data(fault, duration_hours=8, intensity=1.5)
            all_datasets.append(fault_data)
        
        # Combine all data
        combined_df = pd.concat(all_datasets, ignore_index=True)
        
        # Add additional features
        combined_df['hour'] = combined_df['timestamp'] / 60
        combined_df['is_fault'] = (combined_df['fault_type'] > 0).astype(int)
        
        # Save datasets
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Full dataset
        full_path = f"{output_dir}/tep_full_dataset_{timestamp}.csv"
        combined_df.to_csv(full_path, index=False)
        print(f"💾 Saved full dataset: {full_path}")
        
        # Training/validation split (80/20)
        train_size = int(0.8 * len(combined_df))
        train_df = combined_df.iloc[:train_size]
        val_df = combined_df.iloc[train_size:]
        
        train_path = f"{output_dir}/tep_train_{timestamp}.csv"
        val_path = f"{output_dir}/tep_validation_{timestamp}.csv"
        
        train_df.to_csv(train_path, index=False)
        val_df.to_csv(val_path, index=False)
        
        print(f"💾 Saved training set: {train_path} ({len(train_df)} samples)")
        print(f"💾 Saved validation set: {val_path} ({len(val_df)} samples)")
        
        # Generate summary
        summary = {
            'total_samples': len(combined_df),
            'normal_samples': len(combined_df[combined_df['fault_type'] == 0]),
            'fault_samples': len(combined_df[combined_df['fault_type'] > 0]),
            'fault_distribution': combined_df['fault_type'].value_counts().to_dict(),
            'variables': list(combined_df.columns),
            'generation_time': timestamp
        }
        
        summary_path = f"{output_dir}/dataset_summary_{timestamp}.txt"
        with open(summary_path, 'w') as f:
            for key, value in summary.items():
                f.write(f"{key}: {value}\n")
        
        print(f"📋 Saved summary: {summary_path}")
        print("✅ Dataset generation complete!")
        
        return combined_df
    
    def generate_specific_faults(self, fault_list, output_dir="data/training_datasets"):
        """Generate data for specific fault types only."""
        print(f"🎯 Generating data for specific faults: {fault_list}")
        
        os.makedirs(output_dir, exist_ok=True)
        all_datasets = []
        
        # Always include normal operation
        if 0 not in fault_list:
            fault_list = [0] + fault_list
        
        for fault in fault_list:
            duration = 12 if fault == 0 else 8
            intensity = 0.0 if fault == 0 else 1.5
            fault_data = self.generate_fault_data(fault, duration_hours=duration, intensity=intensity)
            all_datasets.append(fault_data)
        
        combined_df = pd.concat(all_datasets, ignore_index=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"{output_dir}/tep_specific_faults_{timestamp}.csv"
        combined_df.to_csv(output_path, index=False)
        
        print(f"💾 Saved specific faults dataset: {output_path}")
        return combined_df

def main():
    """Main function with user options."""
    print("🎛️ TEP Training Data Generator")
    print("="*50)
    
    generator = TEPDataGenerator()
    
    print("Choose generation mode:")
    print("1️⃣  Full dataset (all 20 faults + normal)")
    print("2️⃣  Specific faults only")
    print("3️⃣  Single fault analysis")
    print("0️⃣  Exit")
    
    choice = input("\nSelect option (1-3, 0 to exit): ").strip()
    
    if choice == "1":
        print("\n🚀 Generating full dataset...")
        generator.generate_mixed_dataset()
        
    elif choice == "2":
        print("\n🎯 Specify fault numbers (comma-separated, e.g., 1,4,13):")
        fault_input = input("Faults: ").strip()
        try:
            fault_list = [int(x.strip()) for x in fault_input.split(',')]
            generator.generate_specific_faults(fault_list)
        except ValueError:
            print("❌ Invalid input. Please use numbers separated by commas.")
            
    elif choice == "3":
        print("\n🔍 Single fault analysis")
        try:
            fault_num = int(input("Fault number (0-20): "))
            intensity = float(input("Intensity (0.5-2.0): "))
            duration = float(input("Duration (hours): "))
            
            data = generator.generate_fault_data(fault_num, duration, intensity)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"data/training_datasets/tep_fault_{fault_num}_{timestamp}.csv"
            os.makedirs("data/training_datasets", exist_ok=True)
            data.to_csv(output_path, index=False)
            print(f"💾 Saved: {output_path}")
            
        except ValueError:
            print("❌ Invalid input.")
            
    elif choice == "0":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice.")

if __name__ == "__main__":
    main()
