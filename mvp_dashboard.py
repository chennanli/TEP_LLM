#!/usr/bin/env python3
"""
TEP FaultExplainer MVP Dashboard
===============================

Unified interface that connects:
1. TEP Simulator (real-time data generation)
2. Parameter controls (A/C ratio, fault injection)
3. Anomaly detection (simplified PCA)
4. LLM explanations (using your Gemini/Claude APIs)

Author: Augment Agent
Date: 2025-01-30
"""

import sys
import os
import json
import time
import threading
import queue
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request
from flask_socketio import SocketIO, emit
import pandas as pd
import numpy as np
from collections import deque
import requests

# Add TEP simulator to path
sys.path.append('external_repos/tep2py-master')

try:
    from tep2py import tep2py
    print("✅ TEP Simulator loaded successfully!")
except ImportError as e:
    print(f"❌ Error loading TEP simulator: {e}")
    sys.exit(1)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

class MVPDashboard:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'mvp-dashboard-secret'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # TEP Simulator state
        self.tep_simulator = None
        self.is_running = False
        self.current_fault = 0
        self.fault_intensity = 1.0
        self.ac_ratio = 1.0  # A/C feed ratio
        
        # Data storage
        self.data_buffer = deque(maxlen=50)  # Store last 50 data points
        self.pca_window = deque(maxlen=20)   # 20-point window for anomaly detection
        self.anomaly_threshold = 2.0
        self.current_anomaly_score = 0.0
        
        # LLM integration
        self.gemini_api_key = os.getenv('GOOGLE_API_KEY')
        self.claude_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.last_explanation = ""
        self.explanation_history = []
        
        # Setup routes
        self.setup_routes()
        
    def setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def index():
            return render_template_string(HTML_TEMPLATE)
        
        @self.app.route('/start_simulation', methods=['POST'])
        def start_simulation():
            try:
                self.start_tep_simulation()
                return jsonify({'success': True, 'message': '✅ TEP Simulation started'})
            except Exception as e:
                return jsonify({'success': False, 'message': f'❌ Error: {e}'})
        
        @self.app.route('/stop_simulation', methods=['POST'])
        def stop_simulation():
            self.stop_tep_simulation()
            return jsonify({'success': True, 'message': '⏹️ Simulation stopped'})
        
        @self.app.route('/adjust_ratio', methods=['POST'])
        def adjust_ratio():
            try:
                data = request.get_json()
                self.ac_ratio = float(data.get('ratio', 1.0))
                return jsonify({'success': True, 'message': f'✅ A/C ratio set to {self.ac_ratio}'})
            except Exception as e:
                return jsonify({'success': False, 'message': f'❌ Error: {e}'})
        
        @self.app.route('/inject_fault', methods=['POST'])
        def inject_fault():
            try:
                data = request.get_json()
                self.current_fault = int(data.get('fault_type', 0))
                self.fault_intensity = float(data.get('intensity', 1.0))
                return jsonify({'success': True, 'message': f'✅ Fault {self.current_fault} injected'})
            except Exception as e:
                return jsonify({'success': False, 'message': f'❌ Error: {e}'})
        
        @self.app.route('/get_status')
        def get_status():
            return jsonify({
                'running': self.is_running,
                'fault': self.current_fault,
                'ac_ratio': self.ac_ratio,
                'anomaly_score': self.current_anomaly_score,
                'threshold': self.anomaly_threshold,
                'data_points': len(self.data_buffer),
                'last_explanation': self.last_explanation
            })
        
        @self.socketio.on('connect')
        def handle_connect():
            print('🔌 Client connected to dashboard')
            emit('status', {'message': 'Connected to MVP Dashboard'})
    
    def start_tep_simulation(self):
        """Start TEP simulation in background thread."""
        if self.is_running:
            return
        
        self.is_running = True
        self.data_buffer.clear()
        self.pca_window.clear()
        
        # Initialize TEP simulator
        idata = np.zeros((1, 20))
        if self.current_fault > 0:
            idata[0, self.current_fault-1] = self.fault_intensity
        
        self.tep_simulator = tep2py(idata)
        
        # Start simulation thread
        thread = threading.Thread(target=self.simulation_worker, daemon=True)
        thread.start()
        
        print("🚀 TEP simulation started")
    
    def stop_tep_simulation(self):
        """Stop TEP simulation."""
        self.is_running = False
        print("⏹️ TEP simulation stopped")
    
    def simulation_worker(self):
        """Background simulation worker."""
        sample_count = 0
        
        while self.is_running:
            try:
                # Create simulation step
                idata = np.zeros((1, 20))
                if self.current_fault > 0:
                    idata[0, self.current_fault-1] = self.fault_intensity
                
                # Run simulation
                self.tep_simulator = tep2py(idata)
                self.tep_simulator.simulate()
                data = self.tep_simulator.process_data
                
                if len(data) > 0:
                    # Get latest data point
                    latest = data.iloc[-1]
                    
                    # Create data point
                    data_point = {
                        'timestamp': datetime.now().isoformat(),
                        'sample': sample_count,
                        'temperature': float(latest['XMEAS(9)']),
                        'pressure': float(latest['XMEAS(7)']),
                        'flow': float(latest['XMEAS(11)']),
                        'level': float(latest['XMEAS(12)']),
                        'fault': self.current_fault,
                        'ac_ratio': self.ac_ratio
                    }
                    
                    # Add to buffers
                    self.data_buffer.append(data_point)
                    self.pca_window.append(data_point)
                    
                    # Simple anomaly detection
                    self.detect_anomaly()
                    
                    # Emit real-time data
                    self.socketio.emit('data_update', {
                        'data': data_point,
                        'anomaly_score': self.current_anomaly_score,
                        'is_anomaly': self.current_anomaly_score > self.anomaly_threshold
                    })
                    
                    sample_count += 1
                
                # Control simulation speed (1 sample per 2 seconds for demo)
                time.sleep(2.0)
                
            except Exception as e:
                print(f"❌ Simulation error: {e}")
                break
    
    def detect_anomaly(self):
        """Simple anomaly detection using statistical methods."""
        if len(self.pca_window) < 10:
            self.current_anomaly_score = 0.0
            return
        
        # Extract key variables
        temps = [p['temperature'] for p in self.pca_window]
        pressures = [p['pressure'] for p in self.pca_window]
        flows = [p['flow'] for p in self.pca_window]
        
        # Calculate simple anomaly score (standard deviations from mean)
        temp_std = np.std(temps) if len(temps) > 1 else 0
        pressure_std = np.std(pressures) if len(pressures) > 1 else 0
        flow_std = np.std(flows) if len(flows) > 1 else 0
        
        # Combined anomaly score
        self.current_anomaly_score = (temp_std + pressure_std + flow_std) / 3.0
        
        # Trigger LLM analysis if anomaly detected
        if self.current_anomaly_score > self.anomaly_threshold:
            self.trigger_llm_analysis()
    
    def trigger_llm_analysis(self):
        """Trigger LLM analysis in background."""
        if not self.gemini_api_key:
            self.last_explanation = "❌ No API key configured for LLM analysis"
            return
        
        # Run in background thread
        thread = threading.Thread(target=self.get_llm_explanation, daemon=True)
        thread.start()
    
    def get_llm_explanation(self):
        """Get LLM explanation for current anomaly."""
        try:
            # Prepare data for LLM
            recent_data = list(self.pca_window)[-5:]  # Last 5 data points
            
            prompt = f"""
            Analyze this Tennessee Eastman Process anomaly:
            
            Current Status:
            - Fault Type: {self.current_fault}
            - A/C Ratio: {self.ac_ratio}
            - Anomaly Score: {self.current_anomaly_score:.2f}
            
            Recent Data:
            {json.dumps(recent_data, indent=2)}
            
            Provide a brief explanation of what might be causing this anomaly and recommended actions.
            """
            
            # Try Gemini API
            response = self.call_gemini_api(prompt)
            
            if response:
                self.last_explanation = response
                self.explanation_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'explanation': response,
                    'anomaly_score': self.current_anomaly_score
                })
                
                # Emit to frontend
                self.socketio.emit('llm_explanation', {
                    'explanation': response,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                self.last_explanation = "❌ Failed to get LLM explanation"
                
        except Exception as e:
            self.last_explanation = f"❌ LLM analysis error: {e}"
            print(f"❌ LLM error: {e}")
    
    def call_gemini_api(self, prompt):
        """Call Google Gemini API."""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.gemini_api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    return result['candidates'][0]['content']['parts'][0]['text']
            
            return None
            
        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            return None
    
    def run(self, host='0.0.0.0', port=8080):
        """Run the dashboard."""
        print("🎛️ Starting TEP FaultExplainer MVP Dashboard")
        print(f"🌐 Open your browser to: http://localhost:{port}")
        print("📋 Features:")
        print("   • Real-time TEP simulation")
        print("   • Parameter adjustment (A/C ratio, fault injection)")
        print("   • Anomaly detection")
        print("   • LLM explanations")
        
        self.socketio.run(self.app, host=host, port=port, debug=False)

# HTML Template for the dashboard
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>TEP FaultExplainer MVP Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .panel { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .controls { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .control-group { margin-bottom: 15px; }
        .control-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .control-group input, .control-group select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .btn { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #2980b9; }
        .btn.danger { background: #e74c3c; }
        .btn.danger:hover { background: #c0392b; }
        .status { padding: 10px; border-radius: 4px; margin: 10px 0; }
        .status.normal { background: #d4edda; color: #155724; }
        .status.anomaly { background: #f8d7da; color: #721c24; }
        .data-display { font-family: monospace; background: #f8f9fa; padding: 15px; border-radius: 4px; }
        .explanation { background: #e3f2fd; padding: 15px; border-radius: 4px; border-left: 4px solid #2196f3; }
        #chart { height: 300px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎛️ TEP FaultExplainer MVP Dashboard</h1>
            <p>Real-time Tennessee Eastman Process monitoring with AI-powered fault analysis</p>
        </div>
        
        <div class="grid">
            <div class="panel">
                <h3>🎮 Controls</h3>
                <div class="controls">
                    <div class="control-group">
                        <label>A/C Feed Ratio:</label>
                        <input type="range" id="acRatio" min="0.5" max="2.0" step="0.1" value="1.0">
                        <span id="acRatioValue">1.0</span>
                    </div>
                    <div class="control-group">
                        <label>Fault Type:</label>
                        <select id="faultType">
                            <option value="0">No Fault</option>
                            <option value="1">A/C Feed Ratio</option>
                            <option value="4">Cooling Water</option>
                            <option value="6">Feed Loss</option>
                            <option value="8">Feed Composition</option>
                            <option value="13">Reaction Kinetics</option>
                        </select>
                    </div>
                    <div class="control-group">
                        <label>Fault Intensity:</label>
                        <input type="range" id="faultIntensity" min="0.1" max="2.0" step="0.1" value="1.0">
                        <span id="faultIntensityValue">1.0</span>
                    </div>
                </div>
                <button class="btn" onclick="startSimulation()">▶️ Start Simulation</button>
                <button class="btn danger" onclick="stopSimulation()">⏹️ Stop</button>
                <button class="btn" onclick="adjustRatio()">🔧 Adjust A/C Ratio</button>
                <button class="btn" onclick="injectFault()">🚨 Inject Fault</button>
                <div id="controlStatus" class="status normal">Ready to start simulation</div>
            </div>
            
            <div class="panel">
                <h3>📊 Live Process Data</h3>
                <div class="data-display" id="processData">
                    <div>Temperature: -- °C</div>
                    <div>Pressure: -- bar</div>
                    <div>Flow: -- kg/h</div>
                    <div>Level: -- %</div>
                    <div>Samples: --</div>
                </div>
                <div id="anomalyStatus" class="status normal">
                    Anomaly Score: 0.0 (Normal)
                </div>
            </div>
        </div>
        
        <div class="panel" style="margin-top: 20px;">
            <h3>📈 Real-time Chart</h3>
            <div id="chart"></div>
        </div>
        
        <div class="panel" style="margin-top: 20px;">
            <h3>🤖 AI Fault Analysis</h3>
            <div id="llmExplanation" class="explanation">
                Waiting for anomaly detection to trigger AI analysis...
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        let chartData = {
            temperature: [],
            pressure: [],
            flow: [],
            timestamps: []
        };
        
        // Initialize chart
        const layout = {
            title: 'TEP Process Variables',
            xaxis: { title: 'Time' },
            yaxis: { title: 'Value' }
        };
        
        Plotly.newPlot('chart', [], layout);
        
        // Socket event handlers
        socket.on('data_update', function(data) {
            updateProcessData(data);
            updateChart(data);
        });
        
        socket.on('llm_explanation', function(data) {
            updateLLMExplanation(data);
        });
        
        // Control handlers
        document.getElementById('acRatio').addEventListener('input', function() {
            document.getElementById('acRatioValue').textContent = this.value;
        });
        
        document.getElementById('faultIntensity').addEventListener('input', function() {
            document.getElementById('faultIntensityValue').textContent = this.value;
        });
        
        function startSimulation() {
            fetch('/start_simulation', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('controlStatus').textContent = data.message;
                    document.getElementById('controlStatus').className = data.success ? 'status normal' : 'status anomaly';
                });
        }
        
        function stopSimulation() {
            fetch('/stop_simulation', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('controlStatus').textContent = data.message;
                    document.getElementById('controlStatus').className = 'status normal';
                });
        }
        
        function adjustRatio() {
            const ratio = document.getElementById('acRatio').value;
            fetch('/adjust_ratio', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ratio: parseFloat(ratio) })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('controlStatus').textContent = data.message;
            });
        }
        
        function injectFault() {
            const faultType = document.getElementById('faultType').value;
            const intensity = document.getElementById('faultIntensity').value;
            fetch('/inject_fault', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    fault_type: parseInt(faultType),
                    intensity: parseFloat(intensity)
                })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('controlStatus').textContent = data.message;
            });
        }
        
        function updateProcessData(data) {
            const processData = document.getElementById('processData');
            processData.innerHTML = `
                <div>Temperature: ${data.data.temperature.toFixed(1)} °C</div>
                <div>Pressure: ${data.data.pressure.toFixed(2)} bar</div>
                <div>Flow: ${data.data.flow.toFixed(1)} kg/h</div>
                <div>Level: ${data.data.level.toFixed(1)} %</div>
                <div>Samples: ${data.data.sample}</div>
            `;
            
            const anomalyStatus = document.getElementById('anomalyStatus');
            const score = data.anomaly_score.toFixed(2);
            if (data.is_anomaly) {
                anomalyStatus.textContent = `🚨 ANOMALY DETECTED! Score: ${score}`;
                anomalyStatus.className = 'status anomaly';
            } else {
                anomalyStatus.textContent = `✅ Normal Operation - Score: ${score}`;
                anomalyStatus.className = 'status normal';
            }
        }
        
        function updateChart(data) {
            const maxPoints = 50;
            const timestamp = new Date(data.data.timestamp);
            
            chartData.timestamps.push(timestamp);
            chartData.temperature.push(data.data.temperature);
            chartData.pressure.push(data.data.pressure * 10); // Scale for visibility
            chartData.flow.push(data.data.flow);
            
            // Keep only last 50 points
            if (chartData.timestamps.length > maxPoints) {
                chartData.timestamps.shift();
                chartData.temperature.shift();
                chartData.pressure.shift();
                chartData.flow.shift();
            }
            
            const traces = [
                {
                    x: chartData.timestamps,
                    y: chartData.temperature,
                    name: 'Temperature (°C)',
                    type: 'scatter'
                },
                {
                    x: chartData.timestamps,
                    y: chartData.pressure,
                    name: 'Pressure (×10 bar)',
                    type: 'scatter'
                },
                {
                    x: chartData.timestamps,
                    y: chartData.flow,
                    name: 'Flow (kg/h)',
                    type: 'scatter'
                }
            ];
            
            Plotly.redraw('chart', traces);
        }
        
        function updateLLMExplanation(data) {
            const explanation = document.getElementById('llmExplanation');
            explanation.innerHTML = `
                <strong>🤖 AI Analysis (${data.timestamp}):</strong><br>
                ${data.explanation.replace(/\n/g, '<br>')}
            `;
        }
        
        // Auto-refresh status
        setInterval(() => {
            fetch('/get_status')
                .then(response => response.json())
                .then(data => {
                    // Update any status indicators
                });
        }, 5000);
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    dashboard = MVPDashboard()
    dashboard.run()
