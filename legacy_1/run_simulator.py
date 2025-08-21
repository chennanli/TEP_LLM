#!/usr/bin/env python3
"""
TEP Simulator Launcher
=====================

Simple launcher for TEP simulators with organized file structure.
"""

import subprocess
import sys
import os

def check_environment():
    """Check if virtual environment is activated."""
    if 'tep_env' not in sys.executable:
        print("⚠️  WARNING: Virtual environment not detected!")
        print("   Please run: source tep_env/bin/activate")
        print("   Then run this script again.")
        return False
    return True

def main():
    """Main launcher function."""
    print("🎛️ TEP Simulator Launcher")
    print("="*40)
    
    if not check_environment():
        return
    
    print("Choose a simulator:")
    print("1️⃣  Qt Desktop Simulator")
    print("    • Professional desktop app")
    print("    • Native macOS interface")
    print("    • Comprehensive monitoring")
    print()
    print("2️⃣  Enhanced Web Simulator")
    print("    • Multiple product flows")
    print("    • Product compositions")
    print("    • http://localhost:8082")
    print()
    print("3️⃣  Check/Clean Background Processes")
    print("    • Find running simulators")
    print("    • Clean up orphaned processes")
    print()
    print("0️⃣  Exit")
    print()
    
    while True:
        try:
            choice = input("Select option (1-3, 0 to exit): ").strip()

            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                print("🎛️ Starting Qt Desktop Simulator...")
                subprocess.run([sys.executable, "simulators/live/clean_qt_tep_simulator.py"])
                break
            elif choice == "2":
                print("🏭 Starting Enhanced Web Simulator...")
                # Change to the correct directory for the enhanced simulator
                import os
                original_dir = os.getcwd()
                try:
                    os.chdir("simulators/live")
                    subprocess.run([sys.executable, "improved_tep_simulator.py"])
                finally:
                    os.chdir(original_dir)
                break
            elif choice == "3":
                print("🔍 Checking Background Processes...")
                subprocess.run([sys.executable, "scripts/utilities/check_simulators.py"])
            else:
                print("❌ Invalid choice. Please select 1, 2, 3, or 0.")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()
