#!/usr/bin/env python3
"""
Test version using external JavaScript file to isolate the issue.
"""

from flask import Flask, render_template_string, jsonify, send_from_directory
import os

app = Flask(__name__)

EXTERNAL_JS_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>🔧 External JS Test Panel</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .btn { padding: 10px 20px; margin: 10px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        .btn:hover { background: #0056b3; }
        .btn-success { background: #28a745 !important; }
        .btn-danger { background: #dc3545 !important; }
        .btn-primary { background: #007bff !important; }
        #status { display: none; margin: 20px 0; padding: 15px; border-radius: 8px; font-weight: bold; }
        .debug-section { background: #fff; padding: 20px; margin: 20px 0; border: 2px solid #007bff; border-radius: 8px; }
        .test-section { background: #f8f9fa; padding: 15px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
        .status-card { background: #fff; padding: 15px; margin: 10px; border-radius: 8px; border: 1px solid #ddd; }
    </style>
</head>
<body>
    <h1>🔧 External JavaScript Test Panel</h1>
    
    <div id="status"></div>
    
    <div class="debug-section">
        <h2>🚨 JavaScript Tests (External File)</h2>
        
        <div class="test-section">
            <h3>Test 1: External JS Function</h3>
            <button class="btn" onclick="testFunction()">Test External Function</button>
        </div>
        
        <div class="test-section">
            <h3>Test 2: Backend Start (External)</h3>
            <button class="btn" onclick="startBackend()">Start Backend (External JS)</button>
        </div>
        
        <div class="test-section">
            <h3>Test 3: TEP Start (External)</h3>
            <button class="btn" onclick="startTEP()">Start TEP (External JS)</button>
        </div>
        
        <div class="test-section">
            <h3>Test 4: Status Update</h3>
            <button class="btn" onclick="updateStatus()">Update Status</button>
        </div>
    </div>
    
    <div class="debug-section">
        <h2>📊 System Status</h2>
        <div class="status-card">
            <h4>🏭 TEP Simulation</h4>
            <p id="tep-status">Stopped</p>
            <p>Step: <span id="tep-step">0</span></p>
        </div>
        <div class="status-card">
            <h4>🔍 Backend</h4>
            <p id="backend-status">Stopped</p>
        </div>
        <div class="status-card">
            <h4>🖥️ Frontend</h4>
            <p id="frontend-status">Stopped</p>
        </div>
    </div>

    <!-- Load external JavaScript -->
    <script src="/static/control_panel_js.js"></script>
    
    <script>
        // Additional inline test
        console.log('📝 Inline script after external JS loaded');
        
        // Test if external functions are available
        setTimeout(() => {
            if (typeof testFunction === 'function') {
                console.log('✅ External testFunction is available');
            } else {
                console.error('❌ External testFunction NOT available');
            }
            
            if (typeof startBackend === 'function') {
                console.log('✅ External startBackend is available');
            } else {
                console.error('❌ External startBackend NOT available');
            }
        }, 100);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(EXTERNAL_JS_HTML)

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

@app.route('/api/status')
def get_status():
    return jsonify({
        'tep_running': False,
        'backend_running': False,
        'frontend_running': False,
        'current_step': 0
    })

@app.route('/api/faultexplainer/backend/start', methods=['POST'])
def start_backend():
    return jsonify({'success': True, 'message': 'Backend start test successful!'})

@app.route('/api/tep/start', methods=['POST'])
def start_tep():
    return jsonify({'success': True, 'message': 'TEP start test successful!'})

if __name__ == "__main__":
    print("🚀 Starting External JS Test Panel on http://localhost:9003")
    app.run(host='0.0.0.0', port=9003, debug=False)
