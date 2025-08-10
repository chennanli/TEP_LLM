#!/usr/bin/env python3
"""
SIMPLE WORKING SOLUTION - No complex process management
Just start the components manually in separate terminals
"""

import os
import sys

def print_instructions():
    """Print simple, clear instructions."""
    
    print("=" * 60)
    print("🚀 SIMPLE TEP SYSTEM STARTUP GUIDE")
    print("=" * 60)
    print()
    
    print("📁 Current directory:", os.getcwd())
    print()
    
    print("🔥 STEP 1: Start Backend (Terminal 1)")
    print("-" * 40)
    print("cd external_repos/FaultExplainer-main/backend")
    print("source ../../../tep_env/bin/activate")
    print("python app.py")
    print("✅ Should show: 'Uvicorn running on http://0.0.0.0:8000'")
    print()
    
    print("🔥 STEP 2: Start Frontend (Terminal 2)")
    print("-" * 40)
    print("cd external_repos/FaultExplainer-main/frontend")
    print("npm run dev")
    print("✅ Should show: 'Local: http://localhost:5173/'")
    print()
    
    print("🔥 STEP 3: Start TEP Simulation (Terminal 3)")
    print("-" * 40)
    print("source tep_env/bin/activate")
    print("python real_tep_simulator.py")
    print("✅ Should start generating TEP data")
    print()
    
    print("🌐 ACCESS POINTS:")
    print("-" * 40)
    print("• FaultExplainer UI: http://localhost:5173")
    print("• Backend API: http://localhost:8000")
    print("• TEP Data: data/live_tep_data.csv")
    print()
    
    print("💡 TIPS:")
    print("-" * 40)
    print("• Use 3 separate terminal windows")
    print("• Start backend first, then frontend, then TEP")
    print("• Check each component starts successfully before next")
    print("• Use Ctrl+C to stop each component")
    print()
    
    print("=" * 60)

def check_files():
    """Check if required files exist."""
    
    print("🔍 CHECKING REQUIRED FILES...")
    print("-" * 40)
    
    files_to_check = [
        "external_repos/FaultExplainer-main/backend/app.py",
        "external_repos/FaultExplainer-main/frontend/package.json",
        "real_tep_simulator.py",
        "tep_env/bin/activate"
    ]
    
    all_good = True
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING!")
            all_good = False
    
    print()
    
    if all_good:
        print("🎉 All required files found!")
    else:
        print("💥 Some files are missing - check your setup")
    
    print()
    return all_good

if __name__ == "__main__":
    print()
    check_files()
    print_instructions()
    
    print("🚀 Ready to start? Follow the steps above in 3 terminals!")
    print()
