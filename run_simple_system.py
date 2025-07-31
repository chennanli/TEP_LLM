#!/usr/bin/env python3
"""
Simple TEP System with LLM Fault Diagnosis
==========================================

Launches:
1. Your existing TEP simulator (Qt5 or Web)
2. FaultExplainer backend only (no complex frontend setup)
3. Simple web interface to test LLM analysis

Author: Augment Agent
Date: 2025-07-23
"""

import sys
import os
import subprocess
import time
import webbrowser
import threading
import signal
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class SimpleSystemLauncher:
    def __init__(self):
        self.processes = []
        self.running = True
    
    def check_environment(self):
        """Check if environment is ready."""
        print("🔍 Checking environment...")
        
        # Check virtual environment
        if 'tep_env' not in sys.executable:
            print("❌ Please activate virtual environment:")
            print("   source tep_env/bin/activate")
            print("   python run_simple_system.py")
            return False
        
        # Check required packages for FaultExplainer backend
        required = ['fastapi', 'uvicorn', 'pandas', 'numpy', 'matplotlib', 'requests', 'python-dotenv']
        missing = []
        
        for package in required:
            try:
                if package == 'python-dotenv':
                    import dotenv
                else:
                    __import__(package)
            except ImportError:
                missing.append(package)
        
        if missing:
            print(f"📦 Installing missing packages: {', '.join(missing)}")
            for package in missing:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print("✅ Packages installed")
        
        # Check FaultExplainer backend exists
        if not os.path.exists('external_repos/FaultExplainer-MultiLLM/backend/app.py'):
            print("❌ FaultExplainer backend not found")
            return False
        
        print("✅ Environment ready!")
        return True
    
    def setup_api_keys(self):
        """Setup API keys for FaultExplainer."""
        print("🔑 Setting up API keys...")
        
        # Check if API keys are set
        anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')
        google_key = os.getenv('GOOGLE_API_KEY', '')
        openai_key = os.getenv('OPENAI_API_KEY', '')
        
        if not anthropic_key and not google_key and not openai_key:
            print("⚠️  WARNING: No API keys found in environment!")
            print("   Please create a .env file with your API keys.")
            print("   See .env.template for the format.")
            print("   You can still use LMStudio without API keys.")
        
        # Create .env file for FaultExplainer backend
        env_content = f"""# API Keys for FaultExplainer
ANTHROPIC_API_KEY={anthropic_key}
GOOGLE_API_KEY={google_key}
OPENAI_API_KEY={openai_key}
LMSTUDIO_URL={os.getenv('LMSTUDIO_URL', 'http://127.0.0.1:1234')}
"""
        
        env_path = 'external_repos/FaultExplainer-MultiLLM/backend/.env'
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print("✅ API keys configured")
    
    def launch_tep_simulator(self, sim_type):
        """Launch TEP simulator."""
        print(f"🎛️ Launching {sim_type} TEP simulator...")
        
        try:
            if sim_type == "qt5":
                cmd = [sys.executable, "simulators/live/clean_qt_tep_simulator.py"]
                process = subprocess.Popen(cmd)
                self.processes.append(('TEP Qt5 Simulator', process))
                print("✅ Qt5 TEP Simulator launched")
                return True
                
            elif sim_type == "web":
                cmd = [sys.executable, "simulators/live/improved_tep_simulator.py"]
                process = subprocess.Popen(cmd)
                self.processes.append(('TEP Web Simulator', process))
                print("✅ Web TEP Simulator launched at http://localhost:8082")
                time.sleep(3)  # Give web server time to start
                webbrowser.open('http://localhost:8082')
                return True
                
        except Exception as e:
            print(f"❌ Error launching TEP simulator: {e}")
            return False
    
    def launch_faultexplainer_backend(self):
        """Launch FaultExplainer backend."""
        print("🤖 Launching FaultExplainer backend...")
        
        try:
            backend_dir = 'external_repos/FaultExplainer-MultiLLM/backend'
            cmd = [sys.executable, '-m', 'uvicorn', 'app:app', '--host', '0.0.0.0', '--port', '8000']
            process = subprocess.Popen(cmd, cwd=backend_dir)
            self.processes.append(('FaultExplainer Backend', process))
            
            # Wait for backend to start
            print("⏳ Waiting for backend to start...")
            for i in range(15):
                try:
                    response = requests.get('http://localhost:8000/docs', timeout=2)
                    if response.status_code == 200:
                        print("✅ FaultExplainer backend ready at http://localhost:8000")
                        return True
                except:
                    time.sleep(1)
            
            print("⚠️  Backend started but may still be initializing")
            return True
            
        except Exception as e:
            print(f"❌ Error launching FaultExplainer backend: {e}")
            return False
    
    def test_llm_analysis(self):
        """Test LLM analysis with sample data."""
        print("🧪 Testing LLM analysis...")
        
        try:
            # Test with sample fault data
            test_data = {
                "fault_type": 1,
                "data": [
                    {"XMEAS(1)": 0.25, "XMEAS(2)": 3664, "XMEAS(3)": 4509, "XMEAS(4)": 9.35, "XMEAS(5)": 26.9},
                    {"XMEAS(1)": 0.26, "XMEAS(2)": 3665, "XMEAS(3)": 4510, "XMEAS(4)": 9.36, "XMEAS(5)": 27.0}
                ]
            }
            
            # Test LMStudio first
            response = requests.post(
                'http://localhost:8000/explain',
                json=test_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ LLM analysis working!")
                print("🤖 Sample analysis:")
                print(result.get('explanation', 'No explanation returned'))
                return True
            else:
                print(f"❌ Backend returned status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing LLM: {e}")
            return False
    
    def cleanup(self):
        """Clean up all processes."""
        print("\n🧹 Cleaning up processes...")
        for name, process in self.processes:
            try:
                print(f"   Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass
        print("✅ Cleanup complete")
    
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully."""
        print("\n🛑 Received interrupt signal...")
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def run(self):
        """Main run function."""
        # Setup signal handler
        signal.signal(signal.SIGINT, self.signal_handler)
        
        print("🎛️ Simple TEP System with LLM Fault Diagnosis")
        print("=" * 50)
        
        if not self.check_environment():
            return
        
        self.setup_api_keys()
        
        print("\n🚀 Choose TEP Simulator:")
        print("1. Qt5 Desktop Simulator")
        print("2. Web Browser Simulator")
        print("0. Exit")
        
        while True:
            choice = input("\nSelect option (1-2, 0 to exit): ").strip()
            
            if choice == "0":
                return
            elif choice == "1":
                sim_type = "qt5"
                break
            elif choice == "2":
                sim_type = "web"
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 0.")
        
        print(f"\n🚀 Starting system with {sim_type.upper()} simulator...")
        print("=" * 50)
        
        # Launch components
        if not self.launch_tep_simulator(sim_type):
            return
        
        if not self.launch_faultexplainer_backend():
            return
        
        # Test LLM analysis
        time.sleep(3)
        self.test_llm_analysis()
        
        print("\n🎉 System launched successfully!")
        print("=" * 50)
        print("📋 Your System:")
        print(f"🎛️  TEP Simulator: {sim_type.upper()}")
        if sim_type == "web":
            print("    http://localhost:8082")
        print("🤖 FaultExplainer Backend: http://localhost:8000")
        print("📖 API Documentation: http://localhost:8000/docs")
        print("\n🎯 How to use:")
        print("1. Use TEP simulator to trigger faults")
        print("2. Visit http://localhost:8000/docs to test API")
        print("3. Send fault data to /explain endpoint")
        print("4. Get LLM analysis results!")
        print("\n🔧 API Example:")
        print("POST http://localhost:8000/explain")
        print('{"fault_type": 1, "data": [...]}')
        print("\n⚠️  Press Ctrl+C to stop all services")
        print("=" * 50)
        
        # Open API docs
        time.sleep(2)
        webbrowser.open('http://localhost:8000/docs')
        
        # Keep running until interrupted
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        
        self.cleanup()

def main():
    launcher = SimpleSystemLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
