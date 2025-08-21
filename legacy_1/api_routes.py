#!/usr/bin/env python3
"""
API Routes Module
- Flask API endpoints
- Backend proxy functions
- Request handling logic
"""

from flask import jsonify, request, Response, send_from_directory
import requests
import json
import os
import time


class APIRoutes:
    """Handles all API routes for the unified control panel."""
    
    def __init__(self, app, bridge, process_manager):
        self.app = app
        self.bridge = bridge
        self.process_manager = process_manager
        self.setup_routes()

    def setup_routes(self):
        """Setup all API routes."""
        
        # Status endpoints
        @self.app.route('/api/status')
        def get_status():
            bridge_status = self.bridge.get_status()
            process_status = self.process_manager.get_all_status()
            
            return jsonify({
                'tep_running': bridge_status['running'],
                'backend_running': process_status['backend_port'],
                'frontend_running': process_status['frontend_port'],
                'bridge_running': bridge_status['running'],
                'idv_values': bridge_status['idv_values'],
                'current_step': bridge_status['current_step'],
                'simulation_mode': bridge_status['mode'],
                'simulation_interval': bridge_status['interval']
            })

        # TEP Control endpoints
        @self.app.route('/api/tep/start', methods=['POST'])
        def start_tep():
            success = self.bridge.start_simulation()
            return jsonify({'success': success})

        @self.app.route('/api/tep/stop', methods=['POST'])
        def stop_tep():
            success = self.bridge.stop_simulation()
            return jsonify({'success': success})

        @self.app.route('/api/tep/restart', methods=['POST'])
        def restart_tep():
            self.bridge.stop_simulation()
            time.sleep(1)
            success = self.bridge.start_simulation()
            return jsonify({'success': success})

        # IDV Control endpoints
        @self.app.route('/api/idv/set', methods=['POST'])
        def set_idv():
            data = request.get_json() or {}
            idv_number = data.get('idv_number')
            value = data.get('value')
            
            if idv_number is None or value is None:
                return jsonify({'success': False, 'message': 'Missing idv_number or value'}), 400
                
            success = self.bridge.set_idv(idv_number, value)
            return jsonify({'success': success})

        @self.app.route('/api/idv/reset', methods=['POST'])
        def reset_idv():
            for i in range(1, 21):
                self.bridge.set_idv(i, 0.0)
            return jsonify({'success': True, 'message': 'All IDV values reset to 0'})

        # Process Control endpoints
        @self.app.route('/api/faultexplainer/backend/start', methods=['POST'])
        def start_backend():
            result = self.process_manager.start_faultexplainer_backend()
            return jsonify(result)

        @self.app.route('/api/faultexplainer/frontend/start', methods=['POST'])
        def start_frontend():
            result = self.process_manager.start_faultexplainer_frontend()
            return jsonify(result)

        @self.app.route('/api/faultexplainer/backend/stop', methods=['POST'])
        def stop_backend():
            result = self.process_manager.stop_process('faultexplainer_backend')
            return jsonify(result)

        @self.app.route('/api/faultexplainer/frontend/stop', methods=['POST'])
        def stop_frontend():
            result = self.process_manager.stop_process('faultexplainer_frontend')
            return jsonify(result)

        @self.app.route('/api/stop/all', methods=['POST'])
        def stop_all():
            # Stop TEP simulation
            self.bridge.stop_simulation()
            
            # Stop all processes
            result = self.process_manager.stop_all_processes()
            return jsonify(result)

        # Configuration endpoints
        @self.app.route('/api/speed', methods=['POST'])
        def set_speed():
            data = request.get_json() or {}
            interval = data.get('interval', 4)
            self.bridge.simulation_interval = int(interval)
            return jsonify({'success': True, 'interval': interval})

        # Backend proxy endpoints
        @self.app.route('/api/backend/config/runtime', methods=['POST'])
        def proxy_backend_runtime_config():
            try:
                payload = request.get_json() or {}
                if 'preset' in payload:
                    self.bridge.current_preset = payload['preset']
                
                r = requests.post('http://localhost:8000/config/runtime', json=payload, timeout=5)
                return jsonify(r.json()), r.status_code
            except Exception as e:
                return jsonify({'status':'error','error':str(e)}), 500

        @self.app.route('/api/backend/config/baseline/reload', methods=['POST'])
        def proxy_backend_baseline_reload():
            try:
                payload = request.get_json(silent=True) or {}
                r = requests.post('http://localhost:8000/config/baseline/reload', json=payload, timeout=5)
                return jsonify(r.json()), r.status_code
            except Exception as e:
                return jsonify({'status':'error','error':str(e)}), 500

        @self.app.route('/api/backend/config/alpha', methods=['POST'])
        def proxy_backend_alpha():
            try:
                payload = request.get_json() or {}
                r = requests.post('http://localhost:8000/config/alpha', json=payload, timeout=5)
                return jsonify(r.json()), r.status_code
            except Exception as e:
                return jsonify({'status':'error','error':str(e)}), 500

        # Backend analysis history proxy
        @self.app.route('/api/backend/analysis/history', methods=['GET'])
        def proxy_backend_analysis_history():
            try:
                limit = request.args.get('limit', '5')
                r = requests.get(f'http://localhost:8000/analysis/history?limit={limit}', timeout=10)
                return jsonify(r.json()), r.status_code
            except Exception as e:
                return jsonify({'status':'error','error':str(e), 'message': 'Backend not reachable on port 8000. Make sure FaultExplainer backend is running.'}), 500

        # Download analysis history
        @self.app.route('/api/analysis/history/download/<format>')
        def download_analysis_history(format):
            try:
                limit = request.args.get('limit', '20')
                r = requests.get(f'http://localhost:8000/analysis/history?limit={limit}', timeout=10)
                data = r.json()
                
                if format == 'json':
                    # Standard JSON format
                    content = json.dumps(data.get('items', []), indent=2)
                    return Response(
                        content,
                        mimetype='application/json',
                        headers={'Content-Disposition': f'attachment; filename=tep_analysis_history.json'}
                    )
                    
                elif format == 'md':
                    # Markdown format
                    lines = ['# TEP Analysis History\n']
                    for i, item in enumerate(data.get('items', []), 1):
                        ts = item.get('timestamp', 'Unknown time')
                        lines.append(f'## Analysis #{i} - {ts}\n')
                        lines.append(f'**Feature Analysis:**\n```\n{item.get("feature_analysis", "N/A")}\n```\n')
                        
                        if 'llm_analyses' in item:
                            lines.append('**LLM Analysis Results:**\n')
                            for model, analysis in item['llm_analyses'].items():
                                if analysis and analysis.get('analysis'):
                                    lines.append(f'### {model.upper()}\n')
                                    lines.append(f'{analysis["analysis"]}\n')
                                    if analysis.get('response_time'):
                                        lines.append(f'*Response time: {analysis["response_time"]}s*\n')
                        
                        if 'performance_summary' in item:
                            lines.append('**Performance Summary:**\n')
                            for model, perf in item['performance_summary'].items():
                                lines.append(f'- {model}: {perf.get("response_time", 0):.2f}s, {perf.get("word_count", 0)} words\n')
                        lines.append('\n---\n')
                    
                    content = '\n'.join(lines)
                    return Response(
                        content,
                        mimetype='text/markdown',
                        headers={'Content-Disposition': f'attachment; filename=tep_analysis_history.md'}
                    )
                else:
                    return jsonify({'error': 'Invalid format. Use json or md'}), 400
                    
            except Exception as e:
                return jsonify({'error': str(e), 'message': 'Failed to download analysis history. Make sure backend is running.'}), 500

        # Download by date
        @self.app.route('/api/analysis/history/download/bydate/<date>')
        def download_history_by_date(date):
            try:
                backend_dir = 'external_repos/FaultExplainer-main/backend'
                path = os.path.join(backend_dir, 'diagnostics', 'analysis_history', f'{date}.md')
                
                if not os.path.exists(path):
                    return jsonify({'error': f'No analysis found for date {date}'}), 404
                
                return send_from_directory(
                    os.path.dirname(path),
                    os.path.basename(path),
                    as_attachment=True,
                    download_name=f'tep_analysis_{date}.md'
                )
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        # Static files
        @self.app.route('/static/<path:filename>')
        def serve_static(filename):
            return send_from_directory('static', filename)
