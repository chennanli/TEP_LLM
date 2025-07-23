#!/usr/bin/env python3
"""
Setup LLM Integration for TEP Simulator
=======================================

This script helps you set up the FaultExplainer backend and SensorSCAN
for complete LLM-powered root cause analysis.

Author: Augment Agent
Date: 2025-06-29
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path


def check_openai_key():
    """Check if OpenAI API key is available."""
    
    print("🔑 Checking OpenAI API Key...")
    
    # Check environment variable
    if os.getenv('OPENAI_API_KEY'):
        print("   ✅ Found OPENAI_API_KEY in environment")
        return True
    
    # Check .env file
    env_file = Path('Other_Repo/FaultExplainer-main/backend/.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            if 'OPENAI_API_KEY' in content and '=' in content:
                print("   ✅ Found OPENAI_API_KEY in .env file")
                return True
    
    print("   ❌ OpenAI API key not found!")
    print("\n💡 To set up OpenAI API key:")
    print("   1. Get API key from: https://platform.openai.com/api-keys")
    print("   2. Create file: Other_Repo/FaultExplainer-main/backend/.env")
    print("   3. Add line: OPENAI_API_KEY=your_key_here")
    
    return False


def setup_faultexplainer():
    """Setup FaultExplainer backend."""
    
    print("\n🤖 Setting up FaultExplainer (LLM Root Cause Analysis)...")
    
    backend_dir = Path('Other_Repo/FaultExplainer-main/backend')
    
    if not backend_dir.exists():
        print("   ❌ FaultExplainer backend directory not found!")
        return False
    
    # Check if requirements.txt exists
    requirements_file = backend_dir / 'requirements.txt'
    if not requirements_file.exists():
        print("   ❌ requirements.txt not found in FaultExplainer backend!")
        return False
    
    print("   📦 Installing FaultExplainer dependencies...")
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
        ], capture_output=True, text=True, cwd=str(backend_dir))
        
        if result.returncode == 0:
            print("   ✅ FaultExplainer dependencies installed successfully")
        else:
            print(f"   ❌ Failed to install dependencies: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error installing dependencies: {e}")
        return False
    
    return True


def setup_sensorscan():
    """Setup SensorSCAN for advanced anomaly detection."""
    
    print("\n🧠 Setting up SensorSCAN (Advanced Anomaly Detection)...")
    
    sensorscan_dir = Path('Other_Repo/sensorscan-main')
    
    if not sensorscan_dir.exists():
        print("   ❌ SensorSCAN directory not found!")
        return False
    
    requirements_file = sensorscan_dir / 'requirements.txt'
    if not requirements_file.exists():
        print("   ❌ requirements.txt not found in SensorSCAN!")
        return False
    
    print("   📦 Installing SensorSCAN dependencies...")
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
        ], capture_output=True, text=True, cwd=str(sensorscan_dir))
        
        if result.returncode == 0:
            print("   ✅ SensorSCAN dependencies installed successfully")
        else:
            print(f"   ❌ Failed to install dependencies: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error installing dependencies: {e}")
        return False
    
    return True


def test_faultexplainer_backend():
    """Test if FaultExplainer backend is running."""
    
    print("\n🧪 Testing FaultExplainer backend connection...")
    
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("   ✅ FaultExplainer backend is running!")
            return True
        else:
            print(f"   ❌ Backend responded with status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException:
        print("   ❌ FaultExplainer backend is not running")
        print("\n💡 To start the backend:")
        print("   cd Other_Repo/FaultExplainer-main/backend")
        print("   fastapi dev app.py")
        return False


def create_startup_script():
    """Create a convenient startup script."""
    
    print("\n📝 Creating startup scripts...")
    
    # Backend startup script
    backend_script = """#!/bin/bash
echo "🚀 Starting FaultExplainer Backend..."
cd Other_Repo/FaultExplainer-main/backend
source ../../../tep_env/bin/activate
fastapi dev app.py
"""
    
    with open('start_faultexplainer.sh', 'w') as f:
        f.write(backend_script)
    
    os.chmod('start_faultexplainer.sh', 0o755)
    print("   ✅ Created start_faultexplainer.sh")
    
    # Complete system startup script
    complete_script = """#!/bin/bash
echo "🎯 Starting Complete TEP System with LLM Integration..."

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Activating virtual environment..."
    source tep_env/bin/activate
fi

echo "🤖 Starting FaultExplainer backend in background..."
cd Other_Repo/FaultExplainer-main/backend
fastapi dev app.py &
BACKEND_PID=$!

echo "⏳ Waiting for backend to start..."
sleep 5

echo "🎛️ Starting Live TEP Simulator with LLM..."
cd ../../..
python live_tep_with_llm.py

# Cleanup
echo "🧹 Stopping backend..."
kill $BACKEND_PID
"""
    
    with open('start_complete_system.sh', 'w') as f:
        f.write(complete_script)
    
    os.chmod('start_complete_system.sh', 0o755)
    print("   ✅ Created start_complete_system.sh")


def main():
    """Main setup function."""
    
    print("🎯 TEP Simulator LLM Integration Setup")
    print("="*50)
    print("This will set up:")
    print("   🤖 FaultExplainer (LLM root cause analysis)")
    print("   🧠 SensorSCAN (advanced anomaly detection)")
    print("   🎛️ Enhanced live simulator")
    
    success_count = 0
    total_steps = 4
    
    # Step 1: Check OpenAI API key
    if check_openai_key():
        success_count += 1
    
    # Step 2: Setup FaultExplainer
    if setup_faultexplainer():
        success_count += 1
    
    # Step 3: Setup SensorSCAN
    if setup_sensorscan():
        success_count += 1
    
    # Step 4: Create startup scripts
    create_startup_script()
    success_count += 1
    
    print("\n" + "="*50)
    print("📊 SETUP SUMMARY")
    print("="*50)
    print(f"Completed: {success_count}/{total_steps} steps")
    
    if success_count == total_steps:
        print("🎉 SETUP COMPLETE!")
        print("\n🚀 Next Steps:")
        print("   1. Start FaultExplainer backend:")
        print("      ./start_faultexplainer.sh")
        print("   2. In new terminal, start complete system:")
        print("      python live_tep_with_llm.py")
        print("   3. Or use the all-in-one script:")
        print("      ./start_complete_system.sh")
        
        print("\n🎛️ How to Use:")
        print("   • Change fault parameters in the UI")
        print("   • Watch real-time plant response")
        print("   • See AI detect anomalies")
        print("   • Get LLM root cause analysis")
        print("   • Receive operator suggestions")
        
    else:
        print("⚠️  SETUP INCOMPLETE")
        print("Please fix the issues above and run again.")
    
    print("\n💡 Remember:")
    print("   • You need an OpenAI API key for LLM analysis")
    print("   • FaultExplainer backend must be running")
    print("   • Virtual environment should be activated")


if __name__ == "__main__":
    main()
