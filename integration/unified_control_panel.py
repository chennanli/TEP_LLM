#!/usr/bin/env python3
"""
TEP Integration - Unified Control Panel
=======================================
Flask-based unified control panel that connects to the integration backend
with REAL Fortran physics (no synthetic effects).

Features:
- XMV/IDV controls connected to real TEP simulation
- Real-time data display
- Anomaly detection integration
- LLM analysis integration
"""

import os
import sys
import time
import json
import requests
import threading
from flask import Flask, render_template_string, jsonify, request

# Configuration
BACKEND_URL = "http://localhost:8001"  # Different from legacy (8000)
FRONTEND_PORT = 9002  # Different from legacy (9001)

app = Flask(__name__)

# Simple CORS headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

# Global state
current_status = {
    "backend_connected": False,
    "xmv_values": [63.0, 53.0, 24.0, 61.0, 22.0, 40.0, 38.0, 46.0, 47.0, 41.0, 18.0],
    "idv_values": [0.0] * 20,
    "simulation_running": False,
    "last_update": time.time(),
    "process_measurements": [0.0] * 41,  # XMEAS_1 to XMEAS_41
    "anomaly_detected": False,
    "anomaly_score": 0.0,
    "llm_analysis": None,
    "simulation_data": []
}

def check_backend_connection():
    """Check if integration backend is running."""
    try:
        response = requests.get(f"{BACKEND_URL}/status", timeout=2)
        return response.status_code == 200
    except:
        return False

def get_controls_status():
    """Get current XMV/IDV values from backend."""
    try:
        response = requests.get(f"{BACKEND_URL}/api/controls/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            current_status["xmv_values"] = data["xmv_values"]
            current_status["idv_values"] = data["idv_values"]
            current_status["backend_connected"] = True
            return data
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        current_status["backend_connected"] = False
    return None

@app.route('/')
def index():
    """Main control panel interface."""
    return render_template_string(CONTROL_PANEL_HTML)

@app.route('/api/status')
def api_status():
    """Get current system status."""
    # Update backend connection status
    current_status["backend_connected"] = check_backend_connection()
    
    # Get latest control values
    controls = get_controls_status()
    
    return jsonify({
        "backend_connected": current_status["backend_connected"],
        "backend_url": BACKEND_URL,
        "xmv_values": current_status["xmv_values"],
        "idv_values": current_status["idv_values"],
        "simulation_running": current_status["simulation_running"],
        "last_update": current_status["last_update"],
        "controls_data": controls
    })

@app.route('/api/xmv/set', methods=['POST'])
def set_xmv():
    """Set XMV value via backend."""
    try:
        data = request.json
        response = requests.post(f"{BACKEND_URL}/api/xmv/set", json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            # Update local state
            if result.get("success"):
                xmv_num = result["xmv_num"]
                value = result["value"]
                current_status["xmv_values"][xmv_num - 1] = value
                current_status["last_update"] = time.time()
            return jsonify(result)
        else:
            return jsonify({"success": False, "error": "Backend request failed"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/idv/set', methods=['POST'])
def set_idv():
    """Set IDV value via backend."""
    try:
        data = request.json
        response = requests.post(f"{BACKEND_URL}/api/idv/set", json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            # Update local state
            if result.get("success"):
                idv_num = result["idv_num"]
                value = result["value"]
                current_status["idv_values"][idv_num - 1] = value
                current_status["last_update"] = time.time()
            return jsonify(result)
        else:
            return jsonify({"success": False, "error": "Backend request failed"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/simulation/start', methods=['POST'])
def start_simulation():
    """Start simulation via backend."""
    try:
        response = requests.post(f"{BACKEND_URL}/api/simulation/start", json={}, timeout=10)
        if response.status_code == 200:
            current_status["simulation_running"] = True
            return response.json()
        else:
            return jsonify({"success": False, "error": "Backend request failed"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/simulation/stop', methods=['POST'])
def stop_simulation():
    """Stop simulation via backend."""
    try:
        response = requests.post(f"{BACKEND_URL}/api/simulation/stop", json={}, timeout=10)
        if response.status_code == 200:
            current_status["simulation_running"] = False
            return response.json()
        else:
            return jsonify({"success": False, "error": "Backend request failed"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/simulation/data')
def get_simulation_data():
    """Get latest simulation data from backend."""
    try:
        response = requests.get(f"{BACKEND_URL}/api/simulation/data", timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Update local state with latest measurements
            if "measurements" in data:
                current_status["process_measurements"] = data["measurements"][:41]  # First 41 are XMEAS
            if "anomaly_detected" in data:
                current_status["anomaly_detected"] = data["anomaly_detected"]
                current_status["anomaly_score"] = data.get("anomaly_score", 0.0)
            return jsonify(data)
        else:
            return jsonify({"error": "No data available"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/measurements')
def get_measurements():
    """Get current process measurements (XMEAS)."""
    return jsonify({
        "xmeas_values": current_status["process_measurements"],
        "xmeas_labels": [
            "A Feed", "D Feed", "E Feed", "A+C Feed", "Recycle Flow",
            "Reactor Feed Rate", "Reactor Pressure", "Reactor Level", "Reactor Temperature",
            "Purge Rate", "Product Sep Temp", "Product Sep Level", "Product Sep Pressure",
            "Product Sep Underflow", "Stripper Level", "Stripper Pressure", "Stripper Underflow",
            "Stripper Temperature", "Stripper Steam Flow", "Compressor Work", "Reactor Coolant Temp",
            "Separator Coolant Temp", "Component A", "Component B", "Component C", "Component D",
            "Component E", "Component F", "Component G", "Component H", "Component A Purge",
            "Component B Purge", "Component C Purge", "Component D Purge", "Component E Purge",
            "Component F Purge", "Component G Purge", "Component H Purge", "Component D Feed",
            "Component E Feed", "Component A Feed", "Component A+C Feed"
        ],
        "anomaly_detected": current_status["anomaly_detected"],
        "anomaly_score": current_status["anomaly_score"]
    })

# Simple Working Dashboard HTML (Like Legacy System)
CONTROL_PANEL_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TEP Integration - Working Control Panel</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
        .status-panel { background: #ecf0f1; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .status-item { margin: 8px 0; font-size: 14px; }
        .status-indicator { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }
        .status-connected { background: #27ae60; }
        .status-disconnected { background: #e74c3c; }
        .status-running { background: #f39c12; }
        .physics-badge { background: #e67e22; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }

        .controls-section { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
        .control-panel { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .control-item { margin: 8px 0; display: flex; align-items: center; gap: 10px; }
        .control-item label { min-width: 140px; font-weight: bold; font-size: 12px; }
        .control-item input { width: 80px; padding: 4px; border: 1px solid #ddd; border-radius: 4px; }
        .control-item button { padding: 4px 12px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 11px; }
        .control-item button:hover { background: #2980b9; }

        .simulation-controls { text-align: center; margin: 20px 0; }
        .simulation-controls button { padding: 12px 25px; margin: 0 10px; font-size: 16px; font-weight: bold; border: none; border-radius: 4px; cursor: pointer; }
        .btn-start { background: #27ae60; color: white; }
        .btn-stop { background: #e74c3c; color: white; }
        .btn-start:hover { background: #229954; }
        .btn-stop:hover { background: #c0392b; }

        .data-section { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .measurements-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; max-height: 500px; overflow-y: auto; }
        .measurement-item { background: #f8f9fa; padding: 12px; border-radius: 6px; border-left: 4px solid #3498db; }
        .measurement-label { font-size: 11px; color: #666; margin-bottom: 4px; }
        .measurement-name { font-weight: bold; font-size: 12px; margin-bottom: 4px; }
        .measurement-value { font-size: 16px; font-weight: bold; color: #2c3e50; }

        .anomaly-section { margin: 20px 0; }
        .anomaly-normal { background: #27ae60; color: white; padding: 15px; border-radius: 8px; text-align: center; }
        .anomaly-alert { background: #e74c3c; color: white; padding: 15px; border-radius: 8px; text-align: center; animation: pulse 2s infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.7; } 100% { opacity: 1; } }

        .data-info { background: #d5dbdb; padding: 10px; border-radius: 4px; margin-bottom: 15px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏭 TEP Integration - Working Control Panel</h1>
        <p>Real Fortran Physics • Actual Data Display • Clear Status</p>
        <span class="physics-badge">REAL PHYSICS</span>
    </div>

    <!-- System Status -->
    <div class="status-panel">
        <h3>📊 System Status</h3>
        <div class="status-item">
            <span class="status-indicator status-disconnected" id="backend-indicator"></span>
            <strong>Backend:</strong> <span id="backend-status">Checking...</span>
        </div>
        <div class="status-item">
            <span class="status-indicator status-disconnected" id="simulation-indicator"></span>
            <strong>Simulation:</strong> <span id="simulation-status">Stopped</span>
        </div>
        <div class="status-item">
            <strong>Last Update:</strong> <span id="last-update">Never</span>
        </div>
        <div class="status-item">
            <strong>Data Points:</strong> <span id="data-points">0</span>
        </div>
    </div>

    <!-- Simulation Controls -->
    <div class="simulation-controls">
        <button class="btn-start" onclick="startSimulation()">🚀 Start Simulation</button>
        <button class="btn-stop" onclick="stopSimulation()">🛑 Stop Simulation</button>
    </div>

    <!-- Anomaly Detection -->
    <div class="anomaly-section">
        <div id="anomaly-status" class="anomaly-normal">
            <strong>🟢 System Normal</strong> - No anomalies detected
        </div>
    </div>

    <!-- Process Controls -->
    <div class="controls-section">
        <div class="control-panel">
            <h3>🎛️ XMV Controls (Manipulated Variables)</h3>
            <div id="xmv-controls">
                <!-- XMV controls will be populated by JavaScript -->
            </div>
        </div>
        <div class="control-panel">
            <h3>🔧 IDV Controls (Disturbance Variables)</h3>
            <div id="idv-controls">
                <!-- IDV controls will be populated by JavaScript -->
            </div>
        </div>
    </div>

    <!-- Live Process Data -->
    <div class="data-section">
        <h3>📊 Live Process Measurements (XMEAS)</h3>
        <div class="data-info">
            <strong>Status:</strong> <span id="measurements-status">Waiting for data...</span> |
            <strong>Updates:</strong> Every 3 seconds |
            <strong>Source:</strong> Real Fortran TEP Physics
        </div>
        <div class="measurements-grid" id="measurements-grid">
            <!-- Measurements will be populated by JavaScript -->
        </div>
    </div>

    <script>
        let currentStatus = {};
        let simulationRunning = false;

        const xmvLabels = [
            "D Feed Flow", "E Feed Flow", "A Feed Flow", "A+C Feed Flow",
            "Compressor Recycle", "Purge Valve", "Separator Liquid",
            "Stripper Liquid", "Stripper Steam", "Reactor Cooling", "Condenser Cooling"
        ];

        const idvLabels = [
            "A/C Feed Ratio", "B Composition", "D Feed Temp", "Reactor Cooling Inlet",
            "Condenser Cooling Inlet", "A Feed Loss", "C Header Pressure",
            "A,B,C Feed Composition", "D Feed Temp Random", "C Feed Temp Random"
        ];

        const xmeasLabels = [
            "A Feed (kscmh)", "D Feed (kg/h)", "E Feed (kg/h)", "A+C Feed (kscmh)", "Recycle Flow (kscmh)",
            "Reactor Feed Rate (kscmh)", "Reactor Pressure (kPa)", "Reactor Level (%)", "Reactor Temperature (°C)",
            "Purge Rate (kscmh)", "Product Sep Temp (°C)", "Product Sep Level (%)", "Product Sep Pressure (kPa)",
            "Product Sep Underflow (m³/h)", "Stripper Level (%)", "Stripper Pressure (kPa)", "Stripper Underflow (m³/h)",
            "Stripper Temperature (°C)", "Stripper Steam Flow (kg/h)", "Compressor Work (kW)", "Reactor Coolant Temp (°C)",
            "Separator Coolant Temp (°C)", "Component A (%)", "Component B (%)", "Component C (%)", "Component D (%)",
            "Component E (%)", "Component F (%)", "Component G (%)", "Component H (%)", "Component A Purge (%)",
            "Component B Purge (%)", "Component C Purge (%)", "Component D Purge (%)", "Component E Purge (%)",
            "Component F Purge (%)", "Component G Purge (%)", "Component H Purge (%)", "Component D Feed (%)",
            "Component E Feed (%)", "Component A Feed (%)", "Component A+C Feed (%)"
        ];

        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    currentStatus = data;

                    // Update backend status
                    const backendIndicator = document.getElementById('backend-indicator');
                    const backendStatus = document.getElementById('backend-status');
                    if (data.backend_connected) {
                        backendIndicator.className = 'status-indicator status-connected';
                        backendStatus.textContent = 'Connected ✅';
                    } else {
                        backendIndicator.className = 'status-indicator status-disconnected';
                        backendStatus.textContent = 'Disconnected ❌';
                    }

                    // Update simulation status
                    const simIndicator = document.getElementById('simulation-indicator');
                    const simStatus = document.getElementById('simulation-status');
                    if (data.simulation_running) {
                        simIndicator.className = 'status-indicator status-running';
                        simStatus.textContent = 'Running 🔄';
                        simulationRunning = true;
                    } else {
                        simIndicator.className = 'status-indicator status-disconnected';
                        simStatus.textContent = 'Stopped ⏹️';
                        simulationRunning = false;
                    }

                    // Update last update time
                    document.getElementById('last-update').textContent = new Date(data.last_update * 1000).toLocaleTimeString();

                    // Update control values
                    updateControlValues();

                    // Update measurements if backend is connected and simulation is running
                    if (data.backend_connected && data.simulation_running) {
                        updateMeasurements();
                    } else {
                        document.getElementById('measurements-status').textContent = 'Simulation not running - no data available';
                    }
                })
                .catch(error => {
                    console.error('Status update failed:', error);
                    document.getElementById('backend-status').textContent = 'Connection Error ❌';
                    document.getElementById('measurements-status').textContent = 'Connection error - no data available';
                });
        }

        function updateMeasurements() {
            fetch('/api/measurements')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('measurements-status').textContent = 'Receiving live data from Fortran TEP simulator';
                    document.getElementById('data-points').textContent = data.xmeas_values ? data.xmeas_values.length : 0;

                    // Update anomaly status
                    const anomalyStatus = document.getElementById('anomaly-status');
                    if (data.anomaly_detected) {
                        anomalyStatus.className = 'anomaly-alert';
                        anomalyStatus.innerHTML = `<strong>🔴 ANOMALY DETECTED</strong> - Score: ${data.anomaly_score.toFixed(3)}`;
                    } else {
                        anomalyStatus.className = 'anomaly-normal';
                        anomalyStatus.innerHTML = '<strong>🟢 System Normal</strong> - No anomalies detected';
                    }

                    // Update measurements grid
                    if (data.xmeas_values && data.xmeas_values.length > 0) {
                        updateMeasurementsGrid(data.xmeas_values);
                    }
                })
                .catch(error => {
                    console.error('Measurements update failed:', error);
                    document.getElementById('measurements-status').textContent = 'Error fetching measurement data';
                });
        }

        function updateMeasurementsGrid(values) {
            const grid = document.getElementById('measurements-grid');
            grid.innerHTML = '';

            // Show first 20 most important measurements
            for (let i = 0; i < Math.min(20, values.length); i++) {
                const div = document.createElement('div');
                div.className = 'measurement-item';
                div.innerHTML = `
                    <div class="measurement-label">XMEAS_${i+1}</div>
                    <div class="measurement-name">${xmeasLabels[i] || 'Unknown'}</div>
                    <div class="measurement-value">${values[i] ? values[i].toFixed(2) : '0.00'}</div>
                `;
                grid.appendChild(div);
            }
        }

        function startSimulation() {
            fetch('/api/simulation/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✅ Simulation started successfully!');
                    simulationRunning = true;
                } else {
                    alert('❌ Failed to start simulation: ' + data.error);
                }
            })
            .catch(error => {
                alert('❌ Error starting simulation: ' + error);
            });
        }

        function stopSimulation() {
            fetch('/api/simulation/stop', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✅ Simulation stopped successfully!');
                    simulationRunning = false;
                } else {
                    alert('❌ Failed to stop simulation: ' + data.error);
                }
            })
            .catch(error => {
                alert('❌ Error stopping simulation: ' + error);
            });
        }

        function updateControlValues() {
            // Update XMV displays
            for (let i = 0; i < 11; i++) {
                const input = document.getElementById(`xmv-${i+1}`);
                if (input && currentStatus.xmv_values) {
                    input.value = currentStatus.xmv_values[i].toFixed(1);
                }
            }

            // Update IDV displays
            for (let i = 0; i < 10; i++) {
                const input = document.getElementById(`idv-${i+1}`);
                if (input && currentStatus.idv_values) {
                    input.value = currentStatus.idv_values[i].toFixed(3);
                }
            }
        }

        function setXMV(index) {
            const input = document.getElementById(`xmv-${index}`);
            const value = parseFloat(input.value);

            fetch('/api/controls/xmv', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ index: index, value: value })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log(`XMV_${index} set to ${value}`);
                } else {
                    alert('❌ Failed to set XMV: ' + data.error);
                }
            })
            .catch(error => {
                alert('❌ Error setting XMV: ' + error);
            });
        }

        function setIDV(index) {
            const input = document.getElementById(`idv-${index}`);
            const value = parseFloat(input.value);

            fetch('/api/controls/idv', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ index: index, value: value })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log(`IDV_${index} set to ${value}`);
                } else {
                    alert('❌ Failed to set IDV: ' + data.error);
                }
            })
            .catch(error => {
                alert('❌ Error setting IDV: ' + error);
            });
        }

        function createControls() {
            // Create XMV controls
            const xmvContainer = document.getElementById('xmv-controls');
            for (let i = 1; i <= 11; i++) {
                const div = document.createElement('div');
                div.className = 'control-item';
                div.innerHTML = `
                    <label>XMV_${i} (${xmvLabels[i-1]}):</label>
                    <input type="number" id="xmv-${i}" step="0.1" min="0" max="100" value="63.0">
                    <button onclick="setXMV(${i})">Set</button>
                `;
                xmvContainer.appendChild(div);
            }
            
            // Create IDV controls (first 10 most common)
            const idvContainer = document.getElementById('idv-controls');
            for (let i = 1; i <= 10; i++) {
                const div = document.createElement('div');
                div.className = 'control-item';
                div.innerHTML = `
                    <label>IDV_${i} (${idvLabels[i-1]}):</label>
                    <input type="number" id="idv-${i}" step="0.001" min="0" max="1" value="0.000">
                    <button onclick="setIDV(${i})">Set</button>
                `;
                idvContainer.appendChild(div);
            }
        }

        // Initialize the dashboard
        document.addEventListener('DOMContentLoaded', function() {
            createControls();
            updateStatus();

            // Update status every 3 seconds
            setInterval(updateStatus, 3000);

            console.log('✅ TEP Integration Control Panel initialized');
            console.log('📊 Real Fortran Physics • Live Data Display • Clear Status');
        });
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("🏭 TEP Integration - Unified Control Panel")
    print("=" * 50)
    print("🔧 Connecting to integration backend...")
    print(f"📡 Backend URL: {BACKEND_URL}")
    print(f"🌐 Control Panel: http://localhost:{FRONTEND_PORT}")
    print("🎯 Features: Real Fortran Physics • XMV/IDV Control • No Synthetic Effects")
    print()
    
    # Check backend connection
    if check_backend_connection():
        print("✅ Backend connection successful")
    else:
        print("⚠️ Backend not responding - start integration backend first")
        print("   Run: cd integration && ./start-backend.sh")
    
    print()
    print("🚀 Starting unified control panel...")
    app.run(host='0.0.0.0', port=FRONTEND_PORT, debug=False)
