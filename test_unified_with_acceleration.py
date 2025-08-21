#!/usr/bin/env python3
"""
Quick test launcher for unified interface with acceleration
"""

import os
import sys
import subprocess
import time

def main():
    print("🚀 UNIFIED INTERFACE WITH ACCELERATION TEST")
    print("="*60)
    
    # Check if we're in the right directory
    if not os.path.exists("tep_env"):
        print("❌ Please run this from the TE project root directory")
        print("cd /Users/chennanli/Desktop/LLM_Project/TE")
        return
    
    print("✅ Starting unified interface with acceleration support...")
    print("✅ New features:")
    print("   - True simulation acceleration (1x-10x)")
    print("   - Separate loop speed and simulation speed controls")
    print("   - Real-time speed factor adjustment")
    print()
    
    # Change to the correct directory
    unified_script = "integration/src/backend/services/simulation/unified_tep_control_panel.py"
    
    if not os.path.exists(unified_script):
        print(f"❌ Cannot find {unified_script}")
        return
    
    print(f"Starting: {unified_script}")
    print("🌐 Web interface will be available at: http://localhost:9001")
    print("🎛️ Look for the '🚀 Simulation Acceleration' section")
    print()
    print("Press Ctrl+C to stop")
    print("-" * 60)
    
    try:
        # Activate virtual environment and run
        cmd = [
            "bash", "-c", 
            f"source tep_env/bin/activate && python {unified_script}"
        ]
        
        subprocess.run(cmd, cwd=".")
        
    except KeyboardInterrupt:
        print("\n\n✅ Unified interface stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
