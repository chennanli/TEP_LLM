#!/usr/bin/env python3
"""
Simple TEP Test - Minimal Working Version
=========================================

Just to test if the basic components work.
"""

import os
import sys
import threading
import time
from flask import Flask, render_template_string, jsonify
from collections import deque
import numpy as np

class SimpleTEPTest:
    def __init__(self):
        self.app = Flask(__name__)
        
        # Simple state
        self.tep_running = False
        self.data_points = 0
        self.time_data = deque(maxlen=100)
        
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.route('/')
        def dashboard():
            return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Simple TEP Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .status { padding: 20px; margin: 10px; border: 2px solid #ddd; border-radius: 8px; }
        .running { background-color: #d4edda; border-color: #28a745; }
        .stopped { background-color: #f8d7da; border-color: #dc3545; }
        button { padding: 10px 20px; margin: 5px; cursor: pointer; border: none; border-radius: 5px; }
        .start-btn { background-color: #28a745; color: white; }
        .stop-btn { background-color: #dc3545; color: white; }
    </style>
</head>
<body>
    <h1>🧪 Simple TEP Test</h1>
    
    <div class="status" id="tep-status">
        <h3>TEP Simulation</h3>
        <p id="tep-indicator">❌ Not Running</p>
        <p>Data Points: <span id="data-count">0</span></p>
        <button class="start-btn" onclick="startTEP()">Start TEP</button>
        <button class="stop-btn" onclick="stopTEP()">Stop TEP</button>
    </div>
    
    <div id="message"></div>
    
    <script>
        function showMessage(msg) {
            document.getElementById('message').innerHTML = '<p>' + msg + '</p>';
        }
        
        function startTEP() {
            fetch('/start', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    showMessage(data.message);
                    updateStatus();
                });
        }
        
        function stopTEP() {
            fetch('/stop', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    showMessage(data.message);
                    updateStatus();
                });
        }
        
        function updateStatus() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('tep-indicator').textContent = 
                        data.running ? '✅ Running' : '❌ Not Running';
                    document.getElementById('tep-status').className = 
                        'status ' + (data.running ? 'running' : 'stopped');
                    document.getElementById('data-count').textContent = data.data_points;
                });
        }
        
        // Update every 2 seconds
        setInterval(updateStatus, 2000);
        updateStatus();
    </script>
</body>
</html>
            ''')
        
        @self.app.route('/status')
        def get_status():
            return jsonify({
                'running': self.tep_running,
                'data_points': self.data_points
            })
        
        @self.app.route('/start', methods=['POST'])
        def start_tep():
            if self.tep_running:
                return jsonify({'success': False, 'message': '⚠️ Already running'})
            
            print("🔧 Starting simple TEP test...")
            self.tep_running = True
            self.data_points = 0
            
            # Start simple simulation thread
            thread = threading.Thread(target=self.run_simulation, daemon=True)
            thread.start()
            
            return jsonify({'success': True, 'message': '✅ TEP test started'})
        
        @self.app.route('/stop', methods=['POST'])
        def stop_tep():
            print("🛑 Stopping TEP test...")
            self.tep_running = False
            return jsonify({'success': True, 'message': '✅ TEP test stopped'})
    
    def run_simulation(self):
        """Simple simulation loop."""
        print("🚀 Simple simulation started")
        
        while self.tep_running:
            try:
                # Simple data generation
                self.data_points += 1
                current_time = self.data_points * 3
                self.time_data.append(current_time)
                
                print(f"📊 Step {self.data_points}: Generated data point")
                
                time.sleep(3)  # 3-second intervals
                
            except Exception as e:
                print(f"❌ Simulation error: {e}")
                break
        
        print("🛑 Simple simulation stopped")

def main():
    print("🧪 Simple TEP Test")
    print("=" * 20)
    
    test = SimpleTEPTest()
    
    print("🚀 Starting on http://localhost:8081")
    test.app.run(host='0.0.0.0', port=8081, debug=False)

if __name__ == '__main__':
    main()
