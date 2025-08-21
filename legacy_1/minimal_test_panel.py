#!/usr/bin/env python3
"""
Minimal test version of the control panel to isolate JavaScript issues.
"""

from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

MINIMAL_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>🔧 Minimal Test Panel</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .btn { padding: 10px 20px; margin: 10px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        .btn:hover { background: #0056b3; }
        .btn-success { background: #28a745 !important; }
        .btn-danger { background: #dc3545 !important; }
        #status { display: none; margin: 20px 0; padding: 15px; border-radius: 8px; font-weight: bold; }
        .debug-section { background: #fff; padding: 20px; margin: 20px 0; border: 2px solid #007bff; border-radius: 8px; }
        .test-section { background: #f8f9fa; padding: 15px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>🔧 Minimal JavaScript Test Panel</h1>
    
    <div id="status"></div>
    
    <div class="debug-section">
        <h2>🚨 JavaScript Debug Tests</h2>
        
        <div class="test-section">
            <h3>Test 1: Basic Alert</h3>
            <button class="btn" onclick="alert('Basic alert works!')">Test Alert</button>
        </div>
        
        <div class="test-section">
            <h3>Test 2: Function Call</h3>
            <button class="btn" onclick="testFunction()">Test Function</button>
        </div>
        
        <div class="test-section">
            <h3>Test 3: API Call</h3>
            <button class="btn" onclick="testAPI()">Test API</button>
        </div>
        
        <div class="test-section">
            <h3>Test 4: Original Button</h3>
            <button class="btn" onclick="startBackend()">Start Backend (Original)</button>
        </div>
    </div>
    
    <div class="debug-section">
        <h2>📊 Console Output</h2>
        <div id="console-output" style="background: #000; color: #0f0; padding: 10px; font-family: monospace; height: 200px; overflow-y: auto;"></div>
    </div>

    <script>
        // Override console.log to show in page
        const originalLog = console.log;
        const originalError = console.error;
        const consoleDiv = document.getElementById('console-output');
        
        function addToConsole(message, type = 'log') {
            const timestamp = new Date().toLocaleTimeString();
            const color = type === 'error' ? '#f00' : type === 'warn' ? '#ff0' : '#0f0';
            consoleDiv.innerHTML += `<div style="color: ${color}">[${timestamp}] ${message}</div>`;
            consoleDiv.scrollTop = consoleDiv.scrollHeight;
        }
        
        console.log = function(...args) {
            originalLog.apply(console, args);
            addToConsole(args.join(' '), 'log');
        };
        
        console.error = function(...args) {
            originalError.apply(console, args);
            addToConsole(args.join(' '), 'error');
        };

        // Initial test
        console.log('🚀 Minimal Test Panel JavaScript Loading...');
        
        function testFunction() {
            console.log('✅ testFunction() called successfully');
            alert('Test function works!');
            showMessage('Test function executed successfully!', 'success');
        }
        
        function showMessage(message, type = 'info') {
            console.log('showMessage called:', message, type);
            const statusDiv = document.getElementById('status');
            if (!statusDiv) {
                console.error('❌ Status div not found!');
                alert(message);
                return;
            }
            statusDiv.textContent = message;
            statusDiv.className = type === 'success' ? 'btn-success' :
                                 type === 'error' ? 'btn-danger' : 'btn';
            statusDiv.style.display = 'block';
            
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 3000);
        }
        
        function testAPI() {
            console.log('🔍 Testing API call...');
            fetch('/api/test')
                .then(response => {
                    console.log('✅ API Response status:', response.status);
                    return response.json();
                })
                .then(data => {
                    console.log('✅ API Data received:', data);
                    showMessage(`API Test: ${data.message}`, 'success');
                })
                .catch(error => {
                    console.error('❌ API Error:', error);
                    showMessage(`API Error: ${error}`, 'error');
                });
        }
        
        function startBackend() {
            console.log('🔍 Testing startBackend() function...');
            showMessage('startBackend() function called!', 'success');
            
            fetch('/api/test-backend')
                .then(response => response.json())
                .then(data => {
                    console.log('✅ Backend test response:', data);
                    showMessage(`Backend Test: ${data.message}`, 'success');
                })
                .catch(error => {
                    console.error('❌ Backend test error:', error);
                    showMessage(`Backend Error: ${error}`, 'error');
                });
        }
        
        console.log('✅ All JavaScript functions defined');
        console.log('🎯 Ready for testing!');
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(MINIMAL_HTML)

@app.route('/api/test')
def test_api():
    return jsonify({'success': True, 'message': 'API is working!'})

@app.route('/api/test-backend')
def test_backend():
    return jsonify({'success': True, 'message': 'Backend test successful!'})

if __name__ == "__main__":
    print("🚀 Starting Minimal Test Panel on http://localhost:9002")
    app.run(host='0.0.0.0', port=9002, debug=False)
