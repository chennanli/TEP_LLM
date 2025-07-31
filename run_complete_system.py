#!/usr/bin/env python3
"""
Complete TEP System with LLM Fault Diagnosis
============================================

Launches:
1. Your existing TEP simulator (Qt5 or Web)
2. FaultExplainer backend (with your API keys)
3. FaultExplainer frontend (professional UI)

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
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class SystemLauncher:
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
            print("   python run_complete_system.py")
            return False
        
        # Check required packages for FaultExplainer
        required = ['fastapi', 'uvicorn', 'pandas', 'numpy', 'matplotlib', 'requests']
        missing = []
        
        for package in required:
            try:
                __import__(package)
            except ImportError:
                missing.append(package)
        
        if missing:
            print(f"📦 Installing missing packages: {', '.join(missing)}")
            for package in missing:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print("✅ Packages installed")
        
        # Check FaultExplainer exists
        if not os.path.exists('external_repos/FaultExplainer-MultiLLM/backend/app.py'):
            print("❌ FaultExplainer backend not found")
            return False
        
        if not os.path.exists('external_repos/FaultExplainer-MultiLLM/frontend/package.json'):
            print("❌ FaultExplainer frontend not found")
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
    
    def install_frontend_deps(self):
        """Install frontend dependencies if needed."""
        frontend_dir = 'external_repos/FaultExplainer-MultiLLM/frontend'
        
        if not os.path.exists(os.path.join(frontend_dir, 'node_modules')):
            print("📦 Installing frontend dependencies...")
            try:
                # Try yarn first, then npm
                result = subprocess.run(['yarn', '--version'], capture_output=True)
                if result.returncode == 0:
                    subprocess.run(['yarn'], cwd=frontend_dir, check=True)
                else:
                    subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True)
                print("✅ Frontend dependencies installed")
            except subprocess.CalledProcessError:
                print("❌ Failed to install frontend dependencies")
                print("   Please install Node.js and yarn/npm")
                return False
        
        return True
    
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
            for i in range(10):
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
    
    def launch_faultexplainer_frontend(self):
        """Launch FaultExplainer frontend."""
        print("🌐 Launching FaultExplainer frontend...")
        
        try:
            frontend_dir = 'external_repos/FaultExplainer-MultiLLM/frontend'
            
            # Try yarn first, then npm
            try:
                cmd = ['yarn', 'dev']
                process = subprocess.Popen(cmd, cwd=frontend_dir)
            except FileNotFoundError:
                cmd = ['npm', 'run', 'dev']
                process = subprocess.Popen(cmd, cwd=frontend_dir)
            
            self.processes.append(('FaultExplainer Frontend', process))
            
            # Wait a bit then open browser
            time.sleep(5)
            print("✅ FaultExplainer frontend launching...")
            print("🌐 Frontend will be available at http://localhost:5173")
            webbrowser.open('http://localhost:5173')
            return True
            
        except Exception as e:
            print(f"❌ Error launching FaultExplainer frontend: {e}")
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
        
        print("🎛️ Complete TEP System with LLM Fault Diagnosis")
        print("=" * 55)
        
        if not self.check_environment():
            return
        
        self.setup_api_keys()
        
        if not self.install_frontend_deps():
            return
        
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
        
        print(f"\n🚀 Starting complete system with {sim_type.upper()} simulator...")
        print("=" * 55)
        
        # Launch components
        if not self.launch_tep_simulator(sim_type):
            return
        
        if not self.launch_faultexplainer_backend():
            return
        
        if not self.launch_faultexplainer_frontend():
            return
        
        print("\n🎉 Complete system launched successfully!")
        print("=" * 55)
        print("📋 Your System:")
        print(f"🎛️  TEP Simulator: {sim_type.upper()}")
        if sim_type == "web":
            print("    http://localhost:8082")
        print("🤖 FaultExplainer Backend: http://localhost:8000")
        print("🌐 FaultExplainer Frontend: http://localhost:5173")
        print("\n🎯 How to use:")
        print("1. Use TEP simulator to trigger faults")
        print("2. Upload fault data to FaultExplainer")
        print("3. Get multi-LLM analysis and explanations")
        print("4. Compare different AI perspectives!")
        print("\n⚠️  Press Ctrl+C to stop all services")
        print("=" * 55)
        
        # Keep running until interrupted
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        
        self.cleanup()

def main():
    launcher = SystemLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
