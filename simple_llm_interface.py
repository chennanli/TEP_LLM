#!/usr/bin/env python3
"""
Simple LLM Interface for TEP Fault Analysis
===========================================

Simple Flask web interface to test LLM analysis without Node.js requirements.
"""

import sys
import os
import requests
import json
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

# Simple HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🤖 TEP LLM Fault Analysis</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; margin-bottom: 30px; }
        .section { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .btn { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; background: #007bff; color: white; }
        .btn:hover { opacity: 0.8; }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .result { background: white; margin: 10px 0; padding: 15px; border-radius: 5px; border-left: 4px solid #007bff; }
        .provider { font-weight: bold; color: #007bff; margin-bottom: 5px; }
        .analysis { white-space: pre-wrap; font-family: monospace; font-size: 12px; line-height: 1.4; }
        .status { padding: 15px; background: #e9ecef; border-radius: 5px; margin-bottom: 20px; font-weight: bold; }
        .status.success { background: #d4edda; color: #155724; }
        .status.error { background: #f8d7da; color: #721c24; }
        select, input { padding: 8px; border-radius: 3px; border: 1px solid #ccc; margin: 5px; }
        textarea { width: 100%; height: 100px; padding: 10px; border-radius: 5px; border: 1px solid #ccc; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 TEP LLM Fault Analysis</h1>
            <p>Simple interface to test LLM analysis of TEP fault data</p>
        </div>
        
        <div class="section">
            <h3>🎛️ Test LLM Analysis</h3>
            <div style="margin-bottom: 15px;">
                <label><strong>LLM Provider:</strong></label>
                <select id="providerSelect">
                    <option value="lmstudio">LMStudio (Local)</option>
                    <option value="claude">Claude (Anthropic)</option>
                    <option value="gemini">Gemini (Google)</option>
                </select>
                
                <label><strong>Fault Type:</strong></label>
                <select id="faultSelect">
                    <option value="1">Fault 1 - A/C Feed Ratio</option>
                    <option value="4">Fault 4 - Cooling Water</option>
                    <option value="6">Fault 6 - Feed Loss</option>
                    <option value="8">Fault 8 - Feed Composition</option>
                    <option value="13">Fault 13 - Reaction Kinetics</option>
                </select>
                
                <button class="btn" onclick="testAnalysis()">🧪 Test Analysis</button>
                <button class="btn" onclick="loadSampleData()">📊 Load Sample Data</button>
            </div>
            
            <div style="margin-bottom: 15px;">
                <label><strong>Sample TEP Data (JSON format):</strong></label>
                <textarea id="dataInput" placeholder='{"XMEAS(1)": 0.25, "XMEAS(2)": 3664, "XMEAS(3)": 4509, "XMEAS(4)": 9.35, "XMEAS(5)": 26.9}'></textarea>
            </div>
        </div>
        
        <div class="status" id="status">
            📋 Ready to test LLM analysis. Select provider and fault type, then click "Test Analysis".
        </div>
        
        <div id="results" style="display: none;">
            <h3>🤖 LLM Analysis Results</h3>
            <div id="resultContent"></div>
        </div>
    </div>
    
    <script>
        function loadSampleData() {
            const sampleData = {
                "XMEAS(1)": 0.25,
                "XMEAS(2)": 3664,
                "XMEAS(3)": 4509,
                "XMEAS(4)": 9.35,
                "XMEAS(5)": 26.9,
                "XMEAS(6)": 8.5,
                "XMEAS(7)": 2633,
                "XMEAS(8)": 75.0,
                "XMEAS(9)": 120.4,
                "XMEAS(10)": 0.337,
                "XMEAS(11)": 22.95
            };
            
            document.getElementById('dataInput').value = JSON.stringify(sampleData, null, 2);
        }
        
        function testAnalysis() {
            const provider = document.getElementById('providerSelect').value;
            const faultType = document.getElementById('faultSelect').value;
            const dataText = document.getElementById('dataInput').value;
            
            if (!dataText.trim()) {
                alert('Please enter some TEP data or click "Load Sample Data"');
                return;
            }
            
            let data;
            try {
                data = JSON.parse(dataText);
            } catch (e) {
                alert('Invalid JSON format. Please check your data.');
                return;
            }
            
            document.getElementById('status').textContent = '⏳ Analyzing with ' + provider + '...';
            document.getElementById('status').className = 'status';
            
            fetch('/analyze', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    provider: provider,
                    fault_type: parseInt(faultType),
                    data: data
                })
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    document.getElementById('status').textContent = '✅ Analysis complete!';
                    document.getElementById('status').className = 'status success';
                    
                    const resultHtml = `
                        <div class="result">
                            <div class="provider">🤖 ${result.provider} [${result.timestamp}]</div>
                            <div class="analysis">${result.analysis}</div>
                        </div>
                    `;
                    
                    document.getElementById('resultContent').innerHTML = resultHtml;
                    document.getElementById('results').style.display = 'block';
                } else {
                    document.getElementById('status').textContent = '❌ Error: ' + result.error;
                    document.getElementById('status').className = 'status error';
                }
            })
            .catch(error => {
                document.getElementById('status').textContent = '❌ Network error: ' + error;
                document.getElementById('status').className = 'status error';
            });
        }
        
        // Load sample data on page load
        window.onload = function() {
            loadSampleData();
        };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main page."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze fault data using FaultExplainer backend."""
    try:
        request_data = request.get_json()
        provider = request_data.get('provider', 'lmstudio')
        fault_type = request_data.get('fault_type', 1)
        data = request_data.get('data', {})
        
        # Update FaultExplainer config to use selected provider
        config_path = 'external_repos/FaultExplainer-MultiLLM/config.json'
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        config['llm_provider'] = provider
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Prepare data for FaultExplainer
        fault_data = {
            "fault_type": fault_type,
            "data": [data]  # FaultExplainer expects a list
        }
        
        # Call FaultExplainer backend
        response = requests.post(
            'http://localhost:8000/explain',
            json=fault_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            provider_names = {
                'lmstudio': 'LMStudio (Local)',
                'claude': 'Claude (Anthropic)', 
                'gemini': 'Google Gemini'
            }
            
            return jsonify({
                'success': True,
                'provider': provider_names.get(provider, provider),
                'analysis': result.get('explanation', 'No explanation returned'),
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
        else:
            return jsonify({
                'success': False,
                'error': f'FaultExplainer returned status {response.status_code}'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    print("🤖 Starting Simple LLM Interface")
    print("🌐 Open your browser to: http://localhost:8081")
    print("📋 This interface connects to FaultExplainer backend")
    print("   Make sure FaultExplainer backend is running on port 8000")
    
    app.run(host='0.0.0.0', port=8081, debug=False)
