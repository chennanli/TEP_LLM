#!/usr/bin/env python3
"""
Test FaultExplainer LLM Integration
==================================

Quick test to see if we can get LLM explanations from your live TEP data.
"""

import requests
import json
import pandas as pd
import time
import os

def test_faultexplainer_backend():
    """Test if FaultExplainer backend is running."""
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        return response.status_code == 200
    except:
        return False

def send_fault_data_for_analysis():
    """Send your live fault data to FaultExplainer for LLM analysis."""
    
    # Check if we have live fault data
    data_dir = 'external_repos/FaultExplainer-MultiLLM/backend/data'
    fault_files = [f for f in os.listdir(data_dir) if f.startswith('live_fault_')]
    
    if not fault_files:
        print("❌ No live fault data found. Run TEP Bridge first.")
        return False
    
    # Use the latest fault file
    latest_fault = sorted(fault_files)[-1]
    fault_path = os.path.join(data_dir, latest_fault)
    
    print(f"📊 Using fault data: {latest_fault}")
    
    # Load the fault data
    try:
        fault_df = pd.read_csv(fault_path)
        print(f"✅ Loaded {len(fault_df)} data points")
        
        # Prepare data for FaultExplainer
        # Get the last few rows for analysis
        recent_data = fault_df.tail(10)
        
        # Convert to the format FaultExplainer expects
        data_dict = {}
        for column in recent_data.columns:
            if column != 'time':
                data_dict[column] = recent_data[column].tolist()
        
        # Send to FaultExplainer
        request_data = {
            "data": data_dict,
            "id": f"test_analysis_{int(time.time())}",
            "file": latest_fault
        }
        
        print("🤖 Sending data to FaultExplainer for LLM analysis...")
        
        response = requests.post(
            'http://localhost:8000/explain',
            json=request_data,
            timeout=60,
            stream=True
        )
        
        if response.status_code == 200:
            print("✅ LLM Analysis Response:")
            print("=" * 50)
            
            # Handle streaming response
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        content = line_str[6:]
                        if content.strip() and content != '[DONE]':
                            print(content, end='', flush=True)
            
            print("\n" + "=" * 50)
            return True
        else:
            print(f"❌ FaultExplainer returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error analyzing fault data: {e}")
        return False

def main():
    print("🧪 Testing FaultExplainer LLM Integration")
    print("=" * 50)
    
    # Test 1: Check if backend is running
    print("🔍 Checking FaultExplainer backend...")
    if test_faultexplainer_backend():
        print("✅ FaultExplainer backend is running")
    else:
        print("❌ FaultExplainer backend not running")
        print("   Start it with: ./start_faultexplainer.sh")
        return
    
    # Test 2: Send fault data for analysis
    print("\n🤖 Testing LLM analysis...")
    if send_fault_data_for_analysis():
        print("✅ LLM analysis successful!")
    else:
        print("❌ LLM analysis failed")
    
    print("\n🎯 Test complete!")

if __name__ == '__main__':
    main()
