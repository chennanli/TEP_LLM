#!/usr/bin/env python3
"""
Ultra-simple button test to isolate JavaScript issues.
"""

from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

SIMPLE_HTML = '''<!DOCTYPE html>
<html>
<head>
    <title>Simple Button Test</title>
</head>
<body>
    <h1>Simple Button Test</h1>
    
    <div id="status" style="display:none; padding:10px; margin:10px; background:#ddd;"></div>
    
    <button onclick="testAlert()">Test Alert</button>
    <button onclick="testAPI()">Test API</button>
    <button onclick="startBackend()">Start Backend</button>
    
    <script>
        console.log('Simple test script loading...');
        
        function testAlert() {
            console.log('testAlert called');
            alert('Alert works!');
        }
        
        function showMessage(msg) {
            console.log('showMessage:', msg);
            const div = document.getElementById('status');
            div.textContent = msg;
            div.style.display = 'block';
            setTimeout(() => div.style.display = 'none', 3000);
        }
        
        function testAPI() {
            console.log('testAPI called');
            fetch('/api/test')
                .then(r => r.json())
                .then(data => {
                    console.log('API response:', data);
                    showMessage('API: ' + data.message);
                })
                .catch(e => {
                    console.error('API error:', e);
                    showMessage('API Error: ' + e);
                });
        }
        
        function startBackend() {
            console.log('startBackend called');
            fetch('/api/faultexplainer/backend/start', {method: 'POST'})
                .then(r => r.json())
                .then(data => {
                    console.log('Backend response:', data);
                    showMessage('Backend: ' + data.message);
                })
                .catch(e => {
                    console.error('Backend error:', e);
                    showMessage('Backend Error: ' + e);
                });
        }
        
        console.log('Simple test script loaded');
    </script>
</body>
</html>'''

@app.route('/')
def index():
    return render_template_string(SIMPLE_HTML)

@app.route('/api/test')
def test():
    return jsonify({'success': True, 'message': 'Test API works!'})

@app.route('/api/faultexplainer/backend/start', methods=['POST'])
def start_backend():
    return jsonify({'success': True, 'message': 'Backend test successful!'})

if __name__ == "__main__":
    print("🚀 Starting Simple Button Test on http://localhost:9004")
    app.run(host='0.0.0.0', port=9004, debug=False)
