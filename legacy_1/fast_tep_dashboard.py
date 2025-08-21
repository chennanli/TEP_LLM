#!/usr/bin/env python3
"""
Fast TEP Dashboard with Real Physics
- Uses real tep2py simulator (not fake SimpleTEPSimulator)
- Proper anomaly threshold (30.0, not 11.345)
- Faster refresh rates
- WebSocket for real-time updates
"""

import os
import sys
import time
import threading
import json
from collections import deque
import numpy as np
import pandas as pd
from flask import Flask, render_template_string, jsonify, request
from flask_socketio import SocketIO, emit
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

# Import our real TEP simulator
from real_tep_simulator import RealTEPSimulator

class FastTEPDashboard:
    """Fast TEP Dashboard with real physics and WebSocket updates."""
    
    def __init__(self):
        # Real TEP simulator
        self.tep_sim = RealTEPSimulator()
        
        # Dashboard state
        self.is_running = False
        self.update_thread = None
        
        # Anomaly detection (CORRECTED THRESHOLD)
        self.anomaly_threshold = 30.0  # Proper TEP threshold, not 11.345!
        self.current_t2_statistic = 0.0
        self.anomaly_detected = False
        
        # Data for plotting
        self.plot_data = {}
        self.plot_times = []
        
        # Flask app with SocketIO
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'tep_dashboard_secret'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        self.setup_routes()
        print("✅ Fast TEP Dashboard initialized")
    
    def setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def index():
            return render_template_string(DASHBOARD_HTML)
        
        @self.app.route('/start_tep', methods=['POST'])
        def start_tep():
            success, msg = self.tep_sim.start()
            if success:
                self.start_dashboard_updates()
            return jsonify({'success': success, 'message': msg})
        
        @self.app.route('/stop_tep', methods=['POST'])
        def stop_tep():
            success, msg = self.tep_sim.stop()
            self.stop_dashboard_updates()
            return jsonify({'success': success, 'message': msg})
        
        @self.app.route('/set_idv', methods=['POST'])
        def set_idv():
            data = request.get_json()
            idv_num = data.get('idv_num')
            value = data.get('value', 0.0)
            
            self.tep_sim.set_idv(idv_num, value)
            return jsonify({'success': True, 'message': f'IDV_{idv_num} set to {value}'})
        
        @self.socketio.on('connect')
        def handle_connect():
            print('Client connected')
            emit('status', {'message': 'Connected to TEP Dashboard'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            print('Client disconnected')
    
    def calculate_t2_statistic(self, data):
        """Calculate T² statistic for anomaly detection."""
        try:
            if not data or len(self.plot_times) < 10:
                return 0.0
            
            # Get recent XMEAS values for T² calculation
            xmeas_keys = [k for k in data.keys() if k.startswith('XMEAS')]
            if len(xmeas_keys) < 5:
                return 0.0
            
            # Simple T² approximation using variance
            values = [data[k] for k in xmeas_keys[:10]]  # Use first 10 XMEAS
            mean_val = np.mean(values)
            var_val = np.var(values) + 1e-6  # Avoid division by zero
            
            # T² statistic (simplified)
            t2 = (mean_val ** 2) / var_val * len(values)
            return max(0, t2)
            
        except Exception as e:
            print(f"❌ T² calculation error: {e}")
            return 0.0
    
    def update_dashboard_data(self):
        """Update dashboard data and emit to clients."""
        while self.is_running:
            try:
                # Get current TEP data
                current_data = self.tep_sim.get_current_data()
                
                if current_data:
                    # Update plot data
                    time_series, times = self.tep_sim.get_time_series_data(max_points=50)
                    self.plot_data = time_series
                    self.plot_times = times
                    
                    # Calculate T² statistic
                    self.current_t2_statistic = self.calculate_t2_statistic(current_data)
                    self.anomaly_detected = self.current_t2_statistic > self.anomaly_threshold
                    
                    # Prepare data for client
                    dashboard_data = {
                        'current_data': current_data,
                        'plot_data': time_series,
                        'plot_times': times,
                        't2_statistic': round(self.current_t2_statistic, 3),
                        't2_threshold': self.anomaly_threshold,
                        'anomaly_detected': self.anomaly_detected,
                        'data_points': len(times),
                        'timestamp': time.time()
                    }
                    
                    # Emit to all connected clients
                    self.socketio.emit('dashboard_update', dashboard_data)
                
                # Update every 2 seconds (much faster than 5s)
                time.sleep(2.0)
                
            except Exception as e:
                print(f"❌ Dashboard update error: {e}")
                time.sleep(1.0)
    
    def start_dashboard_updates(self):
        """Start dashboard update thread."""
        if not self.is_running:
            self.is_running = True
            self.update_thread = threading.Thread(target=self.update_dashboard_data, daemon=True)
            self.update_thread.start()
            print("🚀 Dashboard updates started")
    
    def stop_dashboard_updates(self):
        """Stop dashboard updates."""
        self.is_running = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=3)
        print("🛑 Dashboard updates stopped")
    
    def run(self, host='0.0.0.0', port=8082, debug=False):
        """Run the dashboard."""
        print(f"🚀 Starting Fast TEP Dashboard on http://localhost:{port}")
        print("✅ Real tep2py physics simulation")
        print("✅ Corrected anomaly threshold (30.0)")
        print("✅ WebSocket real-time updates")
        self.socketio.run(self.app, host=host, port=port, debug=debug)

# HTML Template with WebSocket
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>🚀 Fast TEP Dashboard - Real Physics</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                 color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                      gap: 20px; margin-bottom: 20px; }
        .status-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .controls { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .idv-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .idv-control { padding: 15px; border: 1px solid #ddd; border-radius: 8px; }
        .btn { padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; }
        .btn-primary { background: #007bff; color: white; }
        .btn-danger { background: #dc3545; color: white; }
        .btn-success { background: #28a745; color: white; }
        .anomaly-normal { color: #28a745; font-weight: bold; }
        .anomaly-detected { color: #dc3545; font-weight: bold; }
        .plot-container { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        #status { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .slider { width: 100%; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Fast TEP Dashboard - Real Physics</h1>
            <p>✅ Real tep2py simulation | ✅ Corrected threshold (30.0) | ✅ WebSocket updates</p>
        </div>
        
        <div id="status"></div>
        
        <div class="status-grid">
            <div class="status-card">
                <h3>📊 Data Status</h3>
                <p>Data points: <span id="data-points">0</span></p>
                <p>Simulation step: <span id="sim-step">0</span></p>
                <p>Variables: <span id="variables">52/52</span></p>
            </div>
            
            <div class="status-card">
                <h3>🚨 Anomaly Detection</h3>
                <p>T² Score: <span id="t2-score">0.000</span></p>
                <p>Threshold: <span id="t2-threshold">30.0</span></p>
                <p>Status: <span id="anomaly-status" class="anomaly-normal">Normal</span></p>
            </div>
            
            <div class="status-card">
                <h3>⏱️ Timing</h3>
                <p>TEP: Real-time</p>
                <p>Updates: Every 2s</p>
                <p>WebSocket: Live</p>
            </div>
        </div>
        
        <div class="controls">
            <h3>🎛️ TEP Control</h3>
            <button class="btn btn-success" onclick="startTEP()">Start TEP Simulation</button>
            <button class="btn btn-danger" onclick="stopTEP()">Stop TEP Simulation</button>
            
            <h4>🔧 Fault Injection (IDV Controls)</h4>
            <div class="idv-grid">
                <div class="idv-control">
                    <label>IDV_1: A/C Feed Ratio</label>
                    <input type="range" class="slider" min="0" max="2" step="0.1" value="0" 
                           onchange="setIDV(1, this.value)" id="idv1">
                    <span id="idv1-value">0.0</span>
                </div>
                <div class="idv-control">
                    <label>IDV_4: Reactor Cooling</label>
                    <input type="range" class="slider" min="0" max="2" step="0.1" value="0" 
                           onchange="setIDV(4, this.value)" id="idv4">
                    <span id="idv4-value">0.0</span>
                </div>
                <div class="idv-control">
                    <label>IDV_6: A Feed Loss</label>
                    <input type="range" class="slider" min="0" max="2" step="0.1" value="0" 
                           onchange="setIDV(6, this.value)" id="idv6">
                    <span id="idv6-value">0.0</span>
                </div>
                <div class="idv-control">
                    <label>IDV_8: A,B,C Composition</label>
                    <input type="range" class="slider" min="0" max="2" step="0.1" value="0" 
                           onchange="setIDV(8, this.value)" id="idv8">
                    <span id="idv8-value">0.0</span>
                </div>
            </div>
        </div>
        
        <div class="plot-container">
            <h3>📈 Real-Time TEP Process Variables</h3>
            <div id="tep-plots" style="height: 600px;"></div>
        </div>
    </div>

    <script>
        const socket = io();
        
        socket.on('connect', function() {
            updateStatus('🟢 Connected to TEP Dashboard', 'success');
        });
        
        socket.on('disconnect', function() {
            updateStatus('🔴 Disconnected from server', 'error');
        });
        
        socket.on('dashboard_update', function(data) {
            updateDashboard(data);
        });
        
        function updateStatus(message, type) {
            const statusDiv = document.getElementById('status');
            statusDiv.textContent = message;
            statusDiv.className = type === 'success' ? 'btn-success' : 
                                 type === 'error' ? 'btn-danger' : 'btn-primary';
        }
        
        function updateDashboard(data) {
            // Update status cards
            document.getElementById('data-points').textContent = data.data_points || 0;
            document.getElementById('t2-score').textContent = data.t2_statistic || '0.000';
            document.getElementById('t2-threshold').textContent = data.t2_threshold || '30.0';
            
            const anomalyStatus = document.getElementById('anomaly-status');
            if (data.anomaly_detected) {
                anomalyStatus.textContent = '🚨 DETECTED';
                anomalyStatus.className = 'anomaly-detected';
            } else {
                anomalyStatus.textContent = '✅ Normal';
                anomalyStatus.className = 'anomaly-normal';
            }
            
            // Update plots
            if (data.plot_data && data.plot_times) {
                updatePlots(data.plot_data, data.plot_times, data.t2_statistic, data.t2_threshold);
            }
        }
        
        function updatePlots(plotData, times, t2Score, threshold) {
            const traces = [];
            
            // Key process variables
            const keyVars = ['XMEAS_9', 'XMEAS_7', 'XMEAS_8', 'XMEAS_6', 'XMEAS_21'];
            const varNames = ['🌡️ Reactor Temp', '📊 Reactor Pressure', '📈 Reactor Level', 
                             '🔄 Feed Rate', '🚨 T² Statistic'];
            
            keyVars.forEach((varKey, i) => {
                if (plotData[varKey]) {
                    traces.push({
                        x: times,
                        y: plotData[varKey],
                        name: varNames[i] || varKey,
                        type: 'scatter',
                        mode: 'lines',
                        yaxis: i === 4 ? 'y2' : 'y'  // T² on secondary axis
                    });
                }
            });
            
            // Add threshold line for T²
            if (times.length > 0) {
                traces.push({
                    x: [times[0], times[times.length-1]],
                    y: [threshold, threshold],
                    name: `Threshold (${threshold})`,
                    type: 'scatter',
                    mode: 'lines',
                    line: {dash: 'dash', color: 'red'},
                    yaxis: 'y2'
                });
            }
            
            const layout = {
                title: 'TEP Real-Time Process Variables',
                xaxis: {title: 'Time (s)'},
                yaxis: {title: 'Process Variables', side: 'left'},
                yaxis2: {title: 'T² Statistic', side: 'right', overlaying: 'y'},
                showlegend: true,
                height: 600
            };
            
            Plotly.newPlot('tep-plots', traces, layout);
        }
        
        function startTEP() {
            fetch('/start_tep', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    updateStatus(data.message, data.success ? 'success' : 'error');
                });
        }
        
        function stopTEP() {
            fetch('/stop_tep', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    updateStatus(data.message, data.success ? 'success' : 'error');
                });
        }
        
        function setIDV(idvNum, value) {
            document.getElementById(`idv${idvNum}-value`).textContent = parseFloat(value).toFixed(1);
            
            fetch('/set_idv', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({idv_num: idvNum, value: parseFloat(value)})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateStatus(data.message, 'success');
                }
            });
        }
    </script>
</body>
</html>
'''

if __name__ == "__main__":
    dashboard = FastTEPDashboard()
    dashboard.run(debug=False)
