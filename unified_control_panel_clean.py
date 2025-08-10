#!/usr/bin/env python3
"""
Unified TEP Control Panel - Clean Version
Main orchestrator for TEP simulation and FaultExplainer integration.

Modular structure:
- tep_bridge.py: TEP simulation and data flow
- process_manager.py: Process lifecycle management  
- api_routes.py: Flask API endpoints
- web_interface.py: HTML templates and UI
"""

import os
import sys
import signal
import atexit
from flask import Flask, send_from_directory

# Import our modules
from tep_bridge import TEPDataBridge
from process_manager import ProcessManager
from api_routes import APIRoutes
from web_interface import get_main_html_template


class UnifiedControlPanel:
    """Main control panel orchestrator."""
    
    def __init__(self, port=9001):
        self.port = port
        self.app = Flask(__name__)
        
        # Initialize components
        self.bridge = TEPDataBridge()
        self.process_manager = ProcessManager()
        
        # Setup routes
        self.api_routes = APIRoutes(self.app, self.bridge, self.process_manager)
        self.setup_main_routes()
        
        # Setup cleanup
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("✅ Unified Control Panel initialized")

    def setup_main_routes(self):
        """Setup main web interface routes."""
        
        @self.app.route('/')
        def index():
            return get_main_html_template()

        @self.app.route('/static/<path:filename>')
        def serve_static(filename):
            return send_from_directory('static', filename)

    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\n🛑 Received signal {signum}, shutting down...")
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        """Cleanup resources on shutdown."""
        print("🧹 Cleaning up...")
        try:
            self.bridge.stop_simulation()
            self.process_manager.stop_all_processes()
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")

    def run(self):
        """Start the control panel server."""
        print(f"🚀 Starting Unified TEP Control Panel on port {self.port}")
        print(f"🌐 Access at: http://127.0.0.1:{self.port}")
        print("📋 Features:")
        print("   • TEP Simulation Control")
        print("   • FaultExplainer Integration") 
        print("   • Live Data Bridge")
        print("   • IDV Fault Injection")
        print("   • LLM Analysis Management")
        print("\n🎯 Quick Start:")
        print("   1. Click 'Start TEP' (orange)")
        print("   2. Click 'Start Backend' (blue)")
        print("   3. Click 'Start Frontend' (purple)")
        print("   4. Click 'Start Bridge' (orange)")
        print("   5. Adjust IDV sliders to inject faults")
        print("\n⏱️ Timing: TEP(3min) → Anomaly(6min) → LLM(12min)")
        print("🔒 Use freeze toggle in FaultExplainer UI to read analysis")
        print("\n" + "="*60)
        
        try:
            self.app.run(
                host='127.0.0.1',
                port=self.port,
                debug=False,
                use_reloader=False,
                threaded=True
            )
        except KeyboardInterrupt:
            print("\n🛑 Keyboard interrupt received")
        except Exception as e:
            print(f"❌ Server error: {e}")
        finally:
            self.cleanup()


def main():
    """Main entry point."""
    try:
        panel = UnifiedControlPanel()
        panel.run()
    except Exception as e:
        print(f"❌ Failed to start control panel: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
