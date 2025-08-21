#!/usr/bin/env python3
"""
Web Interface Module
- HTML templates and UI components
- CSS styling and JavaScript integration
- User interface layout
"""

def get_main_html_template():
    """Return the main HTML template with documentation tab."""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎛️ Unified TEP Control Panel</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px;
            background: rgba(255,255,255,0.95);
            min-height: 100vh;
            box-shadow: 0 0 50px rgba(0,0,0,0.1);
        }
        .header { 
            text-align: center; 
            margin-bottom: 30px; 
            padding: 20px;
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            border-radius: 15px;
            color: white;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        .header h1 { 
            font-size: 2.5em; 
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        .timing-info {
            background: rgba(255,255,255,0.2);
            padding: 10px;
            border-radius: 8px;
            margin-top: 15px;
            font-size: 1.1em;
        }
        .live-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            margin: 0 5px;
        }
        .live-good { background: #4CAF50; color: white; }
        .live-bad { background: #f44336; color: white; }
        .section { 
            background: white;
            margin: 20px 0; 
            padding: 25px; 
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            border-left: 5px solid #4facfe;
        }
        .section h3 { 
            color: #2c3e50; 
            margin-bottom: 15px;
            font-size: 1.4em;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .btn { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            border: none; 
            padding: 12px 24px; 
            margin: 8px; 
            border-radius: 8px; 
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .btn:hover { 
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }
        .btn:active { transform: translateY(0); }
        .btn-primary { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
        .btn-success { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
        .btn-warning { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
        .btn-danger { background: linear-gradient(135deg, #ff6b6b 0%, #ffa500 100%); }
        .status-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 15px; 
            margin: 20px 0;
        }
        .status-card { 
            padding: 20px; 
            border-radius: 12px; 
            text-align: center;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .status-card:hover { transform: translateY(-3px); }
        .status-running { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white; }
        .status-stopped { background: linear-gradient(135deg, #ff6b6b 0%, #ffa500 100%); color: white; }
        .status-unknown { background: linear-gradient(135deg, #a8a8a8 0%, #d3d3d3 100%); color: white; }
        .control-card { 
            background: #f8f9fa; 
            padding: 20px; 
            margin: 15px 0; 
            border-radius: 12px;
            border: 2px solid #e9ecef;
        }
        .control-card h4 { 
            color: #495057; 
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        .slider { 
            width: 100%; 
            margin: 10px 0;
            -webkit-appearance: none;
            height: 8px;
            border-radius: 5px;
            background: #ddd;
            outline: none;
        }
        .slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #4facfe;
            cursor: pointer;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        }

        /* Tab Styles */
        .tab-btn {
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 0 5px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .tab-btn:hover { background: rgba(255,255,255,0.3); }
        .tab-btn.active { background: rgba(255,255,255,0.4); box-shadow: 0 2px 8px rgba(0,0,0,0.3); }
        .tab-content { display: none; }
        .tab-content.active { display: block; }

        /* Documentation Styles */
        .docs-section {
            background: #f8f9fa;
            padding: 25px;
            margin: 20px 0;
            border-radius: 15px;
            border-left: 5px solid #17a2b8;
        }
        .docs-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .docs-table th, .docs-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }
        .docs-table th {
            background: #4facfe;
            color: white;
            font-weight: 600;
        }
        .docs-table tr:hover { background: #f8f9fa; }
        .code-block {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            margin: 10px 0;
            overflow-x: auto;
        }
        .idv-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 15px; 
            margin: 20px 0;
        }
        .idv-control { 
            background: white; 
            padding: 15px; 
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .idv-control label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: 600;
            color: #2c3e50;
        }
        .correct-badge { 
            background: #28a745; 
            color: white; 
            padding: 2px 8px; 
            border-radius: 4px; 
            font-size: 11px;
            font-weight: bold;
        }
        .message { 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 8px; 
            font-weight: 500;
        }
        .message.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .message.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .message.info { background: #cce7ff; color: #004085; border: 1px solid #b3d7ff; }
        .data-flow { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            padding: 25px; 
            border-radius: 15px;
            margin: 20px 0;
        }
        .data-flow h3 { color: white; }
        .analysis-box { 
            background: #2c3e50; 
            color: #ecf0f1; 
            padding: 20px; 
            border-radius: 10px; 
            font-family: 'Courier New', monospace; 
            font-size: 13px; 
            max-height: 400px; 
            overflow-y: auto;
            white-space: pre-wrap;
            margin: 15px 0;
            border: 2px solid #34495e;
        }
        .flex-controls { 
            display: flex; 
            gap: 10px; 
            align-items: center; 
            flex-wrap: wrap;
            margin: 15px 0;
        }
        @media (max-width: 768px) {
            .container { padding: 10px; }
            .header h1 { font-size: 2em; }
            .status-grid { grid-template-columns: 1fr; }
            .idv-grid { grid-template-columns: 1fr; }
            .flex-controls { flex-direction: column; align-items: stretch; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎛️ Unified TEP Control Panel</h1>
            <p>Single interface for Dynamic TEP Simulation + FaultExplainer Integration
               <span id="live-connection" class="live-badge live-bad">Live: Disconnected</span>
               <span id="live-count" class="live-badge">Received: 0</span>
            </p>
            <div class="timing-info">
                ⏱️ <strong>Timing:</strong> TEP Simulation (3min) → Anomaly Detection (6min) → LLM Diagnosis (12min)
            </div>

            <!-- Navigation Tabs -->
            <div style="margin-top: 20px;">
                <button class="tab-btn active" onclick="showTab('control')">🎛️ Control Panel</button>
                <button class="tab-btn" onclick="showTab('docs')">📚 Documentation</button>
            </div>
        </div>

        <!-- Tab Content: Control Panel -->
        <div id="control-tab" class="tab-content active">

        <!-- JavaScript Status -->
        <div id="js-status-indicator" style="background: #e3f2fd; padding: 8px; margin: 10px; border-radius: 5px; font-size: 12px; text-align: center;">
            🔧 JavaScript Status: <span id="js-status" style="color: orange;">Loading...</span>
        </div>

        <!-- System Status -->
        <div class="section">
            <h3>📊 System Status</h3>
            <div class="status-grid" id="status-grid">
                <div class="status-card status-stopped">
                    <h4>🏭 TEP Simulation</h4>
                    <p id="tep-status">Stopped</p>
                </div>
                <div class="status-card status-stopped">
                    <h4>🔍 FaultExplainer Backend</h4>
                    <p id="backend-status">Stopped</p>
                </div>
                <div class="status-card status-stopped">
                    <h4>🖥️ FaultExplainer Frontend</h4>
                    <p id="frontend-status">Stopped</p>
                </div>
                <div class="status-card status-stopped">
                    <h4>🌉 Data Bridge</h4>
                    <p id="bridge-status">Stopped</p>
                </div>
            </div>
        </div>

        <!-- Control Buttons -->
        <div class="section">
            <h3>🎮 System Controls</h3>
            <div class="flex-controls">
                <button class="btn btn-success" onclick="startTEP()">▶️ Start TEP</button>
                <button class="btn btn-primary" onclick="startBackend()">▶️ Start Backend</button>
                <button class="btn btn-primary" onclick="startFrontend()">▶️ Start Frontend</button>
                <button class="btn btn-warning" onclick="startBridge()">▶️ Start Bridge</button>
                <button class="btn btn-danger" onclick="stopAll()">⏹️ Stop All</button>
            </div>
        </div>

        <!-- Configuration -->
        <div class="section">
            <h3>⚙️ Configuration</h3>
            <div class="control-card">
                <h4>🎛️ Simulation Speed</h4>
                <label>Demo interval: <span id="demo-interval">1</span>s</label>
                <input type="range" min="1" max="10" step="1" value="1" class="slider" id="demo-interval-slider" onchange="setDemoInterval(this.value)">
            </div>
            <div style="margin-top:10px;">
                <button id="btn-preset-demo" class="btn" onclick="setPreset('demo')">Set Backend Preset: Demo</button>
                <button id="btn-preset-balanced" class="btn" onclick="setPreset('balanced')">Set Backend Preset: Balanced</button>
                <button id="btn-preset-real" class="btn" onclick="setPreset('real')">Set Backend Preset: Realistic</button>
            </div>
        </div>

        <!-- Data Flow -->
        <div class="data-flow">
            <h3>📊 Data Flow</h3>
            <p>Live analysis results and system monitoring</p>
            
            <div class="control-card">
                <h4>🤖 LLM Analysis Control</h4>
                <label>LLM min interval: <span id="llm-interval">25</span>s</label>
                <input type="range" min="10" max="120" step="5" value="20" class="slider" id="llm-interval-slider" onchange="setLLMInterval(this.value)">

                <div style="display:flex; gap:8px; align-items:center; margin-top:6px">
                    <label style="font-size:12px; color:#666">Select date</label>
                    <input type="date" id="history-date" class="btn" style="padding:6px;">
                    <button class="btn" onclick="downloadAnalysisByDate()">⬇ Download MD by date</button>
                </div>
                <p style="margin-top:6px; font-size:12px; color:#666">Logs auto-saved at backend/diagnostics/analysis_history/YYYY-MM-DD.md</p>

                <div style="margin-top:6px">
                    <label>Show last</label>
                    <select id="history-limit" style="margin:0 8px; padding:4px;">
                        <option>5</option>
                        <option>10</option>
                        <option>20</option>
                    </select>
                    <button class="btn" onclick="showAnalysisHistory()">🔄 Refresh</button>
                    <button class="btn" onclick="downloadAnalysis('json')">⬇ Download JSON</button>
                    <button class="btn" onclick="downloadAnalysis('md')">⬇ Download MD</button>
                </div>

                <div style="margin-top:6px">
                    <button class="btn" onclick="showAnalysisHistory()">📊 Show Last 5 Analyses</button>
                </div>

                <div id="analysis-history-box" class="analysis-box">
                    (no analysis history yet - try triggering some anomalies first)
                </div>
            </div>
        </div>

        <!-- IDV Fault Controls -->
        <div class="section">
            <h3>🔧 Fault Injection (IDV Controls)</h3>
            <p><span class="correct-badge">CORRECTED</span> Range: 0.0 to 1.0 (standard TEP values)</p>
            <div class="idv-grid">
                <div class="idv-control">
                    <label><strong>IDV_1:</strong> A/C Feed Ratio</label>
                    <input type="range" class="slider" min="0" max="1" step="0.1" value="0"
                           onchange="setIDV(1, this.value)" id="idv1">
                    <span id="idv1-value">0.0</span>
                </div>
                <div class="idv-control">
                    <label><strong>IDV_2:</strong> B Composition</label>
                    <input type="range" class="slider" min="0" max="1" step="0.1" value="0"
                           onchange="setIDV(2, this.value)" id="idv2">
                    <span id="idv2-value">0.0</span>
                </div>
                <div class="idv-control">
                    <label><strong>IDV_3:</strong> D Feed Temperature</label>
                    <input type="range" class="slider" min="0" max="1" step="0.1" value="0"
                           onchange="setIDV(3, this.value)" id="idv3">
                    <span id="idv3-value">0.0</span>
                </div>
                <div class="idv-control">
                    <label><strong>IDV_4:</strong> Reactor Cooling</label>
                    <input type="range" class="slider" min="0" max="1" step="0.1" value="0"
                           onchange="setIDV(4, this.value)" id="idv4">
                    <span id="idv4-value">0.0</span>
                </div>
                <div class="idv-control">
                    <label><strong>IDV_5:</strong> Condenser Cooling</label>
                    <input type="range" class="slider" min="0" max="1" step="0.1" value="0"
                           onchange="setIDV(5, this.value)" id="idv5">
                    <span id="idv5-value">0.0</span>
                </div>
                <div class="idv-control">
                    <label><strong>IDV_6:</strong> A Feed Loss</label>
                    <input type="range" class="slider" min="0" max="1" step="0.1" value="0"
                           onchange="setIDV(6, this.value)" id="idv6">
                    <span id="idv6-value">0.0</span>
                </div>
            </div>
            
            <div style="margin-top: 20px;">
                <button class="btn btn-warning" onclick="resetAllIDV()">🔄 Reset All IDV to 0</button>
                <button class="btn" onclick="applyStabilityDefaults()">✓ Apply Stability Defaults</button>
                <button class="btn" onclick="reloadBaseline()">🔄 Reload Baseline</button>
            </div>
        </div>

        <!-- Messages -->
        <div id="messages"></div>
        </div> <!-- End Control Tab -->

        <!-- Tab Content: Documentation -->
        <div id="docs-tab" class="tab-content">
            <div class="docs-section">
                <h3>📚 System Documentation</h3>

                <div class="docs-section">
                    <h4>🌉 Bridge Functionality</h4>
                    <p><strong>Q: Why is "Start Bridge" optional?</strong></p>
                    <p><strong>A:</strong> The TEP simulation has a <strong>built-in bridge</strong> that automatically posts data to FaultExplainer!</p>

                    <div class="code-block">
TEP Simulation → Automatic Data Flow → FaultExplainer
(No separate bridge needed!)
                    </div>

                    <p><strong>Two Bridge Options:</strong></p>
                    <ul>
                        <li><strong>Built-in Bridge</strong> (automatic) - TEP simulation directly posts to FaultExplainer</li>
                        <li><strong>External Bridge</strong> (optional) - Separate bridge script for advanced scenarios</li>
                    </ul>

                    <p><strong>🎯 Recommendation:</strong> Just use "Start TEP" + "Start Backend" - the bridge is automatic!</p>
                </div>

                <div class="docs-section">
                    <h4>🎛️ Preset Modes Comparison</h4>
                    <table class="docs-table">
                        <thead>
                            <tr>
                                <th>Setting</th>
                                <th>🚀 Demo</th>
                                <th>⚖️ Balanced</th>
                                <th>🏭 Realistic</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>TEP Simulation Speed</strong></td>
                                <td>4 seconds</td>
                                <td>60 seconds (1 min)</td>
                                <td>180 seconds (3 min)</td>
                            </tr>
                            <tr>
                                <td><strong>PCA Window Size</strong></td>
                                <td>8 samples</td>
                                <td>12 samples</td>
                                <td>20 samples</td>
                            </tr>
                            <tr>
                                <td><strong>Anomaly Trigger</strong></td>
                                <td>3 consecutive</td>
                                <td>2 consecutive</td>
                                <td>6 consecutive</td>
                            </tr>
                            <tr>
                                <td><strong>LLM Min Interval</strong></td>
                                <td>0 seconds (instant)</td>
                                <td>20 seconds</td>
                                <td>300 seconds (5 min)</td>
                            </tr>
                            <tr>
                                <td><strong>Use Case</strong></td>
                                <td>Testing & Demo</td>
                                <td>Development</td>
                                <td>Industrial Deployment</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="docs-section">
                    <h4>🚀 Quick Start Guide</h4>
                    <ol>
                        <li><strong>Start TEP</strong> (orange button) - Starts chemical plant simulation</li>
                        <li><strong>Start Backend</strong> (blue button) - Starts FaultExplainer analysis engine</li>
                        <li><strong>Start Frontend</strong> (purple button) - Starts FaultExplainer web interface (optional)</li>
                        <li><strong>Choose Preset:</strong> Demo (fast testing) | Balanced (development) | Realistic (industrial)</li>
                        <li><strong>Inject Faults:</strong> Use IDV sliders to simulate plant disturbances</li>
                        <li><strong>Monitor Results:</strong> Click "Show Last 5 Analyses" to see LLM diagnosis</li>
                    </ol>

                    <p><strong>🎯 Note:</strong> "Start Bridge" is optional - the bridge is built-in!</p>
                </div>

                <div class="docs-section">
                    <h4>🔧 IDV Fault Types</h4>
                    <ul>
                        <li><strong>IDV_1:</strong> A/C Feed Ratio - Feed composition disturbance</li>
                        <li><strong>IDV_2:</strong> B Composition - Feed quality variation</li>
                        <li><strong>IDV_3:</strong> D Feed Temperature - Thermal disturbance</li>
                        <li><strong>IDV_4:</strong> Reactor Cooling - Heat removal issues</li>
                        <li><strong>IDV_5:</strong> Condenser Cooling - Cooling system problems</li>
                        <li><strong>IDV_6:</strong> A Feed Loss - Feed supply interruption</li>
                    </ul>
                    <p><strong>Range:</strong> 0.0 (no fault) to 1.0 (maximum fault intensity)</p>
                </div>
            </div>
        </div> <!-- End Documentation Tab -->
    </div>

    <!-- Load external JavaScript file for Safari compatibility -->
    <script src="/static/control_panel.js"></script>

    <script>
        // Initialize page
        document.addEventListener('DOMContentLoaded', function() {
            console.log('🚀 Unified TEP Control Panel loaded');
            updateStatus();
            setInterval(updateStatus, 5000); // Update every 5 seconds
        });

        // Tab switching function
        function showTab(tabName) {
            // Hide all tab contents
            var contents = document.querySelectorAll('.tab-content');
            contents.forEach(function(content) {
                content.classList.remove('active');
            });

            // Remove active class from all tab buttons
            var buttons = document.querySelectorAll('.tab-btn');
            buttons.forEach(function(btn) {
                btn.classList.remove('active');
            });

            // Show selected tab content
            document.getElementById(tabName + '-tab').classList.add('active');

            // Add active class to clicked button
            event.target.classList.add('active');
        }
    </script>
</body>
</html>
'''


def get_css_styles():
    """Return CSS styles as a separate string for easier maintenance."""
    return '''
        /* Additional styles can be added here */
        .fade-in { animation: fadeIn 0.5s ease-in; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        
        .pulse { animation: pulse 2s infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
    '''
