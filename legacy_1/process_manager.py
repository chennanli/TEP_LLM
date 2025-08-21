#!/usr/bin/env python3
"""
Process Manager Module
- Manages FaultExplainer backend/frontend processes
- Handles process lifecycle and monitoring
- Cross-platform process management
"""

import os
import sys
import subprocess
import signal
import time
import psutil
from tep_bridge import resolve_venv_python, resolve_npm_cmd


class ProcessManager:
    """Manages external processes for FaultExplainer components."""
    
    def __init__(self):
        self.processes = {}
        self.python_path = resolve_venv_python()
        self.npm_cmd = resolve_npm_cmd()
        print("✅ Process Manager initialized")

    def start_faultexplainer_backend(self):
        """Start FaultExplainer backend."""
        if self.check_process_status('faultexplainer_backend'):
            return {'success': True, 'message': 'Backend already running'}
            
        try:
            backend_dir = 'external_repos/FaultExplainer-main/backend'
            if not os.path.exists(backend_dir):
                return {'success': False, 'message': f'Backend directory not found: {backend_dir}'}
            
            print(f"🚀 Starting backend: {self.python_path} app.py in {os.path.abspath(backend_dir)}")
            
            process = subprocess.Popen(
                [self.python_path, 'app.py'],
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            self.processes['faultexplainer_backend'] = process
            
            # Wait a moment to check if it started successfully
            time.sleep(2)
            if process.poll() is None:
                print("✅ Backend process started successfully")
                return {'success': True, 'message': 'Backend started successfully'}
            else:
                return {'success': False, 'message': 'Backend failed to start'}
                
        except Exception as e:
            return {'success': False, 'message': f'Failed to start backend: {e}'}

    def start_faultexplainer_frontend(self):
        """Start FaultExplainer frontend."""
        if self.check_process_status('faultexplainer_frontend'):
            return {'success': True, 'message': 'Frontend already running'}
            
        try:
            frontend_dir = 'external_repos/FaultExplainer-main/frontend'
            if not os.path.exists(frontend_dir):
                return {'success': False, 'message': f'Frontend directory not found: {frontend_dir}'}
            
            print(f"🚀 Starting frontend: npm start in {os.path.abspath(frontend_dir)}")
            
            process = subprocess.Popen(
                [self.npm_cmd, 'run', 'dev'],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            self.processes['faultexplainer_frontend'] = process
            
            # Wait a moment to check if it started successfully
            time.sleep(3)
            if process.poll() is None:
                print("✅ Frontend process started successfully")
                return {'success': True, 'message': 'Frontend started successfully'}
            else:
                return {'success': False, 'message': 'Frontend failed to start'}
                
        except Exception as e:
            return {'success': False, 'message': f'Failed to start frontend: {e}'}

    def stop_process(self, process_name):
        """Stop a specific process."""
        if process_name not in self.processes:
            return {'success': True, 'message': f'{process_name} not running'}
            
        try:
            process = self.processes[process_name]
            if process.poll() is None:  # Process is still running
                # Try graceful shutdown first
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    process.kill()
                    process.wait()
                    
            del self.processes[process_name]
            print(f"🛑 Stopped {process_name}")
            return {'success': True, 'message': f'{process_name} stopped'}
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to stop {process_name}: {e}'}

    def stop_all_processes(self):
        """Stop all managed processes."""
        results = []
        for process_name in list(self.processes.keys()):
            result = self.stop_process(process_name)
            results.append(f"{process_name}: {result['message']}")
        return {'success': True, 'message': '; '.join(results)}

    def check_process_status(self, process_name):
        """Check if a process is running."""
        if process_name not in self.processes:
            return False
            
        process = self.processes[process_name]
        return process.poll() is None

    def check_port_status(self, port):
        """Check if a port is in use."""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    for conn in proc.connections(kind='inet'):
                        if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except Exception:
            return False

    def get_all_status(self):
        """Get status of all components."""
        return {
            'backend_process': self.check_process_status('faultexplainer_backend'),
            'frontend_process': self.check_process_status('faultexplainer_frontend'),
            'backend_port': self.check_port_status(8000),
            'frontend_port': self.check_port_status(5173) or self.check_port_status(5174),
            'processes': {name: self.check_process_status(name) for name in self.processes.keys()}
        }
