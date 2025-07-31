#!/usr/bin/env python3
"""
TEP-FaultExplainer Bridge
========================

Connects your live TEP simulator to FaultExplainer:
1. Monitors your live TEP simulator for fault data
2. Automatically generates CSV files when faults occur
3. Sends data to FaultExplainer for LLM analysis
4. Shows explanations in a simple interface

Author: Augment Agent
Date: 2025-07-23
"""

import sys
import os
import pandas as pd
import numpy as np
import time
import threading
import requests
import json
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request

# Add TEP simulator to path
sys.path.append('external_repos/tep2py-master')

try:
    from tep2py import tep2py
    print("✅ TEP simulator loaded successfully!")
except ImportError as e:
    print(f"❌ Error loading TEP simulator: {e}")
    sys.exit(1)

class TEPFaultExplainerBridge:
    """Bridge between live TEP simulator and FaultExplainer."""
    
    def __init__(self):
        self.tep_simulator = None
        self.monitoring = False
        self.fault_data_buffer = []
        self.normal_data_baseline = None
        self.current_fault = None
        self.llm_explanations = []
        
        # TEP variable mapping (simplified for key variables)
        self.variable_mapping = {
            'XMEAS(1)': 'A Feed',
            'XMEAS(2)': 'D Feed', 
            'XMEAS(3)': 'E Feed',
            'XMEAS(4)': 'A and C Feed',
            'XMEAS(5)': 'Recycle Flow',
            'XMEAS(6)': 'Reactor Feed Rate',
            'XMEAS(7)': 'Reactor Pressure',
            'XMEAS(8)': 'Reactor Level',
            'XMEAS(9)': 'Reactor Temperature',
            'XMEAS(10)': 'Purge Rate',
            'XMEAS(11)': 'Product Sep Temp',
            'XMEAS(12)': 'Product Sep Level',
            'XMEAS(13)': 'Product Sep Pressure',
            'XMEAS(14)': 'Product Sep Underflow',
            'XMEAS(15)': 'Stripper Level',
            'XMEAS(16)': 'Stripper Pressure',
            'XMEAS(17)': 'Stripper Underflow',
            'XMEAS(18)': 'Stripper Temp',
            'XMEAS(19)': 'Stripper Steam Flow',
            'XMEAS(20)': 'Compressor Work',
            'XMEAS(21)': 'Reactor Coolant Temp',
            'XMEAS(22)': 'Separator Coolant Temp'
        }
    
    def start_normal_operation(self, duration_minutes=5):
        """Start normal operation to establish baseline."""
        print("📊 Establishing normal operation baseline...")
        
        # Initialize TEP with no faults
        idata = np.zeros((2, 20))
        self.tep_simulator = tep2py(idata)
        
        normal_data = []
        steps = int(duration_minutes * 60 / 3)  # 3-second intervals
        
        for i in range(steps):
            self.tep_simulator.simulate()
            data = self.tep_simulator.process_data
            
            if len(data) > 0:
                latest = data.iloc[-1].to_dict()
                normal_data.append(latest)
            
            time.sleep(0.1)  # Fast simulation for baseline
        
        # Calculate baseline statistics
        if normal_data:
            self.normal_data_baseline = pd.DataFrame(normal_data)
            print(f"✅ Normal baseline established with {len(normal_data)} data points")
            
            # Save baseline for FaultExplainer
            baseline_file = 'normal_baseline.csv'
            self.save_data_for_faultexplainer(self.normal_data_baseline, baseline_file)
            return True
        
        return False
    
    def start_fault_simulation(self, fault_type, intensity=1.0):
        """Start simulation with specified fault."""
        print(f"🚨 Starting fault simulation: Type {fault_type}, Intensity {intensity}")
        
        # Initialize TEP with fault
        idata = np.zeros((2, 20))
        if fault_type > 0:
            idata[1, fault_type-1] = intensity
        
        self.tep_simulator = tep2py(idata)
        self.current_fault = {'type': fault_type, 'intensity': intensity}
        self.fault_data_buffer = []
        
        return True
    
    def monitor_for_faults(self, duration_minutes=10):
        """Monitor simulation and collect fault data."""
        print(f"👁️ Monitoring for {duration_minutes} minutes...")
        
        steps = int(duration_minutes * 60 / 3)  # 3-second intervals
        
        for i in range(steps):
            if not self.monitoring:
                break
                
            self.tep_simulator.simulate()
            data = self.tep_simulator.process_data
            
            if len(data) > 0:
                latest = data.iloc[-1].to_dict()
                self.fault_data_buffer.append(latest)
                
                # Check if we have enough data for analysis
                if len(self.fault_data_buffer) >= 50:  # Analyze every 50 points
                    self.analyze_fault_data()
                    self.fault_data_buffer = self.fault_data_buffer[-20:]  # Keep last 20 points
            
            time.sleep(0.1)  # Fast simulation
    
    def analyze_fault_data(self):
        """Analyze current fault data and send to FaultExplainer."""
        if not self.fault_data_buffer or self.normal_data_baseline is None:
            return
        
        print("🔍 Analyzing fault data...")
        
        # Convert to DataFrame
        fault_df = pd.DataFrame(self.fault_data_buffer)
        
        # Save fault data for FaultExplainer
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        fault_file = f'live_fault_{self.current_fault["type"]}_{timestamp}.csv'
        
        self.save_data_for_faultexplainer(fault_df, fault_file)
        
        # Send to FaultExplainer for LLM analysis
        self.request_llm_analysis(fault_df, fault_file)
    
    def save_data_for_faultexplainer(self, data_df, filename):
        """Save data in FaultExplainer format."""
        # Map TEP variables to FaultExplainer format
        mapped_data = {}
        
        for tep_var, fe_name in self.variable_mapping.items():
            if tep_var in data_df.columns:
                mapped_data[fe_name] = data_df[tep_var].tolist()
        
        # Add time column
        mapped_data['time'] = [i * 0.05 for i in range(len(data_df))]
        
        # Convert to DataFrame and save
        fe_df = pd.DataFrame(mapped_data)
        
        # Save to FaultExplainer data directory
        fe_data_dir = 'external_repos/FaultExplainer-MultiLLM/backend/data'
        if not os.path.exists(fe_data_dir):
            os.makedirs(fe_data_dir)
        
        filepath = os.path.join(fe_data_dir, filename)
        fe_df.to_csv(filepath, index=False)
        
        print(f"💾 Saved data to {filepath}")
        return filepath
    
    def request_llm_analysis(self, fault_df, fault_file):
        """Request LLM analysis from FaultExplainer."""
        try:
            # Prepare data for FaultExplainer API
            latest_data = fault_df.iloc[-1]
            
            # Map to FaultExplainer variable names
            fe_data = {}
            for tep_var, fe_name in self.variable_mapping.items():
                if tep_var in latest_data:
                    fe_data[fe_name] = [float(latest_data[tep_var])]
            
            # Prepare request
            request_data = {
                "data": fe_data,
                "id": f"live_analysis_{datetime.now().strftime('%H%M%S')}",
                "file": fault_file
            }
            
            print("🤖 Requesting LLM analysis...")
            
            # Send to FaultExplainer
            response = requests.post(
                'http://localhost:8000/explain',
                json=request_data,
                timeout=60
            )
            
            if response.status_code == 200:
                # Handle streaming response
                explanation = ""
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            explanation += line_str[6:] + "\n"
                
                if explanation.strip():
                    self.llm_explanations.append({
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'fault_type': self.current_fault['type'],
                        'explanation': explanation.strip(),
                        'file': fault_file
                    })
                    
                    print("✅ LLM analysis received!")
                    print(f"📝 Explanation: {explanation[:100]}...")
                else:
                    print("⚠️ Empty explanation received")
            else:
                print(f"❌ FaultExplainer returned status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error requesting LLM analysis: {e}")

# Flask web interface
app = Flask(__name__)
bridge = TEPFaultExplainerBridge()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🎛️ TEP-FaultExplainer Bridge</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        .section { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .btn { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; background: #007bff; color: white; margin: 5px; }
        .btn:hover { opacity: 0.8; }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .status { padding: 15px; background: #e9ecef; border-radius: 5px; margin: 10px 0; }
        .explanation { background: white; margin: 10px 0; padding: 15px; border-radius: 5px; border-left: 4px solid #007bff; }
        .timestamp { font-weight: bold; color: #007bff; }
        .content { white-space: pre-wrap; font-family: monospace; font-size: 12px; }
        select, input { padding: 8px; margin: 5px; border-radius: 3px; border: 1px solid #ccc; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎛️ TEP-FaultExplainer Bridge</h1>
        <p>Connect your live TEP simulator to FaultExplainer for LLM analysis</p>
        
        <div class="section">
            <h3>🎯 Step 1: Establish Normal Baseline</h3>
            <button class="btn" onclick="establishBaseline()">📊 Run Normal Operation (5 min)</button>
            <div id="baselineStatus" class="status">Ready to establish baseline</div>
        </div>
        
        <div class="section">
            <h3>🚨 Step 2: Simulate Fault</h3>
            <label>Fault Type:</label>
            <select id="faultType">
                <option value="1">Fault 1 - A/C Feed Ratio</option>
                <option value="4">Fault 4 - Cooling Water</option>
                <option value="6">Fault 6 - Feed Loss</option>
                <option value="8">Fault 8 - Feed Composition</option>
                <option value="13">Fault 13 - Reaction Kinetics</option>
            </select>
            
            <label>Intensity:</label>
            <input type="number" id="intensity" value="1.0" min="0.1" max="2.0" step="0.1">
            
            <button class="btn" onclick="startFaultSim()">🚨 Start Fault Simulation</button>
            <button class="btn" onclick="stopMonitoring()">⏹️ Stop</button>
            <div id="faultStatus" class="status">Ready to simulate fault</div>
        </div>
        
        <div class="section">
            <h3>🤖 LLM Explanations</h3>
            <div id="explanations">No explanations yet. Run fault simulation first.</div>
        </div>
    </div>
    
    <script>
        function establishBaseline() {
            document.getElementById('baselineStatus').textContent = '⏳ Establishing normal baseline...';
            
            fetch('/establish_baseline', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                document.getElementById('baselineStatus').textContent = data.message;
            });
        }
        
        function startFaultSim() {
            const faultType = document.getElementById('faultType').value;
            const intensity = document.getElementById('intensity').value;
            
            document.getElementById('faultStatus').textContent = `⏳ Starting fault ${faultType} simulation...`;
            
            fetch('/start_fault', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({fault_type: parseInt(faultType), intensity: parseFloat(intensity)})
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('faultStatus').textContent = data.message;
                if (data.success) {
                    startPolling();
                }
            });
        }
        
        function stopMonitoring() {
            fetch('/stop', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                document.getElementById('faultStatus').textContent = data.message;
                stopPolling();
            });
        }
        
        let pollingInterval;
        
        function startPolling() {
            pollingInterval = setInterval(updateExplanations, 5000);
        }
        
        function stopPolling() {
            if (pollingInterval) {
                clearInterval(pollingInterval);
            }
        }
        
        function updateExplanations() {
            fetch('/get_explanations')
            .then(response => response.json())
            .then(data => {
                if (data.explanations && data.explanations.length > 0) {
                    let html = '';
                    data.explanations.forEach(exp => {
                        html += `
                            <div class="explanation">
                                <div class="timestamp">🤖 Fault ${exp.fault_type} Analysis [${exp.timestamp}]</div>
                                <div class="content">${exp.explanation}</div>
                                <small>Data file: ${exp.file}</small>
                            </div>
                        `;
                    });
                    document.getElementById('explanations').innerHTML = html;
                }
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/establish_baseline', methods=['POST'])
def establish_baseline():
    try:
        success = bridge.start_normal_operation()
        if success:
            return jsonify({'success': True, 'message': '✅ Normal baseline established'})
        else:
            return jsonify({'success': False, 'message': '❌ Failed to establish baseline'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'❌ Error: {e}'})

@app.route('/start_fault', methods=['POST'])
def start_fault():
    try:
        data = request.get_json()
        fault_type = data.get('fault_type', 1)
        intensity = data.get('intensity', 1.0)
        
        bridge.start_fault_simulation(fault_type, intensity)
        bridge.monitoring = True
        
        # Start monitoring in background
        threading.Thread(target=bridge.monitor_for_faults, args=(10,), daemon=True).start()
        
        return jsonify({'success': True, 'message': f'✅ Fault {fault_type} simulation started'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'❌ Error: {e}'})

@app.route('/stop', methods=['POST'])
def stop():
    bridge.monitoring = False
    return jsonify({'success': True, 'message': '⏹️ Monitoring stopped'})

@app.route('/get_explanations')
def get_explanations():
    return jsonify({'explanations': bridge.llm_explanations})

if __name__ == '__main__':
    print("🎛️ Starting TEP-FaultExplainer Bridge")
    print("🌐 Open your browser to: http://localhost:8083")
    print("📋 Make sure FaultExplainer backend is running on port 8000")
    
    app.run(host='0.0.0.0', port=8083, debug=False)
