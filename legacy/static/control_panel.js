// TEP Control Panel JavaScript - Safari Compatible
console.log('External JavaScript file loading...');

// Safari compatibility polyfills
if (!Array.prototype.forEach) {
    Array.prototype.forEach = function(callback, thisArg) {
        for (var i = 0; i < this.length; i++) {
            callback.call(thisArg, this[i], i, this);
        }
    };
}

// Global error handler
window.onerror = function(msg, url, lineNo, columnNo, error) {
    console.error('JavaScript Error:', msg, 'at line', lineNo);
    alert('JavaScript Error: ' + msg);
    return false;
};

// Test functions
function simpleTest() {
    alert('Simple test button clicked!');
    console.log('Simple test button clicked!');
    var statusEl = document.getElementById('status');
    if (statusEl) {
        statusEl.innerHTML = '<div style="background: blue; color: white; padding: 10px;">Button clicked at ' + new Date().toLocaleTimeString() + '</div>';
    }
}

function testFunction() {
    console.log('testFunction() executed');
    alert('Test function works!');
    showMessage('Test function works!', 'success');
}

// Anomaly Detection Stabilization Functions
function checkPCAStatus() {
    console.log('Checking Anomaly Detection status...');
    fetch('/api/pca/status')
        .then(function(response) { return response.json(); })
        .then(function(data) {
            console.log('Anomaly Detection Status:', data);
            var statusText = 'Anomaly Detection Status: ';
            if (data.training_mode) {
                statusText += 'Training (' + data.collected + '/' + data.target + ')';
            } else if (data.is_stable) {
                statusText += 'System Stable - Ready for Retraining';
            } else {
                statusText += 'System Stabilizing...';
            }
            showMessage(statusText, data.is_stable ? 'success' : 'info');
        })
        .catch(function(error) {
            console.error('Anomaly Detection status check failed:', error);
            showMessage('Anomaly Detection status check failed', 'error');
        });
}

function stabilizePCA() {
    console.log('Starting Anomaly Detection stabilization...');
    showMessage('Checking system stability...', 'info');

    fetch('/api/pca/stabilize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(function(response) { return response.json(); })
    .then(function(data) {
        console.log('Anomaly Detection Stabilization Response:', data);
        if (data.success) {
            showMessage(data.message, 'success');
            // Start monitoring progress
            setTimeout(monitorPCAProgress, 2000);
        } else {
            showMessage(data.message, 'error');
        }
    })
    .catch(function(error) {
        console.error('Anomaly Detection stabilization failed:', error);
        showMessage('Anomaly Detection stabilization failed', 'error');
    });
}

function monitorPCAProgress() {
    fetch('/api/pca/status')
        .then(function(response) { return response.json(); })
        .then(function(data) {
            if (data.training_mode) {
                var progress = Math.round(data.progress);
                showMessage('Anomaly Detection Training: ' + data.collected + '/' + data.target + ' (' + progress + '%)', 'info');
                // Continue monitoring
                setTimeout(monitorPCAProgress, 3000);
            } else {
                showMessage('Anomaly Detection Training Complete! System ready for testing.', 'success');
            }
        })
        .catch(function(error) {
            console.error('Anomaly Detection progress monitoring failed:', error);
        });
}

function showMessage(message, type) {
    console.log('showMessage:', message, type);
    var statusDiv = document.getElementById('status');
    if (!statusDiv) {
        console.error('Status div not found!');
        alert(message);
        return;
    }

    // Clear previous content and set new message
    statusDiv.textContent = message;
    statusDiv.className = type === 'success' ? 'btn-success' :
                         type === 'error' ? 'btn-danger' : 'btn-primary';
    statusDiv.style.display = 'block';
    statusDiv.style.padding = '15px';
    statusDiv.style.borderRadius = '8px';
    statusDiv.style.marginBottom = '20px';
    statusDiv.style.fontWeight = 'bold';
    statusDiv.style.fontSize = '16px';
    statusDiv.style.textAlign = 'center';
    statusDiv.style.border = '2px solid ' + (type === 'success' ? '#4CAF50' :
                                           type === 'error' ? '#f44336' : '#2196F3');

    // Auto-hide after 5 seconds
    setTimeout(function() {
        statusDiv.style.display = 'none';
    }, 5000);
}

// Enhanced button feedback function
function showButtonFeedback(buttons, success) {
    for (var i = 0; i < buttons.length; i++) {
        if (buttons[i]) {
            var btn = buttons[i];
            var originalClass = btn.className;

            if (success) {
                btn.classList.add('btn-success');
                btn.style.transform = 'scale(1.05)';
                btn.style.boxShadow = '0 4px 8px rgba(76, 175, 80, 0.3)';

                (function(button, origClass) {
                    setTimeout(function() {
                        button.classList.remove('btn-success');
                        button.style.transform = '';
                        button.style.boxShadow = '';
                    }, 1200);
                })(btn, originalClass);
            } else {
                btn.classList.add('btn-danger');
                btn.style.transform = 'scale(1.05)';
                btn.style.boxShadow = '0 4px 8px rgba(244, 67, 54, 0.3)';

                (function(button, origClass) {
                    setTimeout(function() {
                        button.classList.remove('btn-danger');
                        button.style.transform = '';
                        button.style.boxShadow = '';
                    }, 1200);
                })(btn, originalClass);
            }
        }
    }
}

function startBackend() {
    console.log('startBackend() called from external JS');
    var btns = document.querySelectorAll("button[onclick*='startBackend']");
    console.log('Found buttons:', btns.length);

    // Disable buttons and show loading state
    for (var i = 0; i < btns.length; i++) {
        if (btns[i]) {
            btns[i].disabled = true;
            btns[i].style.opacity = '0.7';
        }
    }

    fetch('/api/faultexplainer/backend/start', {method: 'POST'})
        .then(function(response) {
            console.log('Backend response:', response.status);
            return response.json();
        })
        .then(function(data) {
            console.log('Backend data:', data);
            showMessage(data.message, data.success ? 'success' : 'error');
            showButtonFeedback(btns, data.success);

            // Force status update after successful start
            if (data.success) {
                setTimeout(updateStatus, 1000);
            }
        })
        .catch(function(e) {
            console.error('Backend error:', e);
            showMessage('Backend start failed: ' + e, 'error');
            showButtonFeedback(btns, false);
        })
        .finally(function() {
            for (var i = 0; i < btns.length; i++) {
                if (btns[i]) {
                    btns[i].disabled = false;
                    btns[i].style.opacity = '1';
                }
            }
        });
}

function startTEP() {
    console.log('startTEP() called from external JS');
    var btns = document.querySelectorAll("button[onclick*='startTEP']");

    // Disable buttons and show loading state
    for (var i = 0; i < btns.length; i++) {
        if (btns[i]) {
            btns[i].disabled = true;
            btns[i].style.opacity = '0.7';
        }
    }

    fetch('/api/tep/start', {method: 'POST'})
        .then(function(response) { return response.json(); })
        .then(function(data) {
            showMessage(data.message, data.success ? 'success' : 'error');
            showButtonFeedback(btns, data.success);

            // Force status update after successful start
            if (data.success) {
                setTimeout(updateStatus, 1000);
            }
        })
        .catch(function(e) {
            showMessage('Start TEP failed: ' + e, 'error');
            showButtonFeedback(btns, false);
        })
        .finally(function() {
            for (var i = 0; i < btns.length; i++) {
                if (btns[i]) {
                    btns[i].disabled = false;
                    btns[i].style.opacity = '1';
                }
            }
        });
}

function startFrontend() {
    console.log('startFrontend() called from external JS');
    var btns = document.querySelectorAll("button[onclick*='startFrontend']");

    for (var i = 0; i < btns.length; i++) {
        if (btns[i]) btns[i].disabled = true;
    }

    fetch('/api/faultexplainer/frontend/start', {method: 'POST'})
        .then(function(response) { return response.json(); })
        .then(function(data) {
            showMessage(data.message, data.success ? 'success' : 'error');
            if (data.success) {
                for (var i = 0; i < btns.length; i++) {
                    btns[i].classList.add('btn-success');
                    (function(btn) {
                        setTimeout(function() { btn.classList.remove('btn-success'); }, 800);
                    })(btns[i]);
                }
            }
        })
        .catch(function(e) { showMessage('Frontend start failed: ' + e, 'error'); })
        .finally(function() {
            for (var i = 0; i < btns.length; i++) {
                if (btns[i]) btns[i].disabled = false;
            }
        });
}

function startBridge() {
    console.log('startBridge() called from external JS');
    fetch('/api/bridge/start', {method: 'POST'})
        .then(function(r) { return r.json(); })
        .then(function(d) { showMessage(d.message, d.success ? 'success' : 'error'); })
        .catch(function(e) { showMessage('Bridge start failed: ' + e, 'error'); });
}

function stopBridge() {
    console.log('stopBridge() called from external JS');
    fetch('/api/bridge/stop', {method: 'POST'})
        .then(function(r) { return r.json(); })
        .then(function(d) { showMessage(d.message, d.success ? 'success' : 'error'); })
        .catch(function(e) { showMessage('Bridge stop failed: ' + e, 'error'); });
}

function setSpeed(mode) {
    console.log('setSpeed() called with mode:', mode);

    // Find the clicked button for feedback
    var clickedBtn = mode === 'demo' ? document.getElementById('btn-speed-demo') :
                     mode === 'real' ? document.getElementById('btn-speed-real') : null;
    var btns = clickedBtn ? [clickedBtn] : [];

    // Show loading state
    if (clickedBtn) {
        clickedBtn.disabled = true;
        clickedBtn.style.opacity = '0.7';
    }

    fetch('/api/speed', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({mode: mode})
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        showMessage('Speed set to ' + data.mode + ' (' + data.step_interval_seconds + 's/step)', 'success');
        showButtonFeedback(btns, true);

        // Update UI elements
        var speedModeEl = document.getElementById('speed-mode');
        if (speedModeEl) {
            speedModeEl.textContent = data.mode === 'demo' ? 'Demo (' + data.step_interval_seconds + 's)' : 'Real (' + data.step_interval_seconds + 's)';
        }
        var di = document.getElementById('demo-interval');
        if (di) di.textContent = data.step_interval_seconds;
        var ds = document.getElementById('demo-interval-slider');
        if (ds && data.mode === 'demo') ds.value = data.step_interval_seconds;

        // Update button active states
        var demoBtn = document.getElementById('btn-speed-demo');
        var realBtn = document.getElementById('btn-speed-real');
        if (demoBtn) demoBtn.classList.toggle('btn-active', data.mode === 'demo');
        if (realBtn) realBtn.classList.toggle('btn-active', data.mode !== 'demo');
    })
    .catch(function(e) {
        showMessage('Speed update failed: ' + e, 'error');
        showButtonFeedback(btns, false);
    })
    .finally(function() {
        if (clickedBtn) {
            clickedBtn.disabled = false;
            clickedBtn.style.opacity = '1';
        }
    });
}

function updateStatus() {
    console.log('updateStatus() called from external JS');
    fetch('/api/status')
        .then(function(response) { return response.json(); })
        .then(function(data) {
            console.log('Status data received:', data);

            // Update TEP status with color change
            var tepStatus = document.getElementById('tep-status');
            var tepStep = document.getElementById('tep-step');
            var tepCard = tepStatus ? tepStatus.closest('.status-card') : null;

            if (tepStatus) tepStatus.textContent = data.tep_running ? 'Running' : 'Stopped';
            if (tepStep) tepStep.textContent = data.current_step;
            if (tepCard) {
                tepCard.className = 'status-card ' + (data.tep_running ? 'status-running' : 'status-stopped');
            }

            // Update backend status with color change
            var backendStatus = document.getElementById('backend-status');
            var backendCard = backendStatus ? backendStatus.closest('.status-card') : null;

            if (backendStatus) backendStatus.textContent = data.backend_running ? 'Running' : 'Stopped';
            if (backendCard) {
                backendCard.className = 'status-card ' + (data.backend_running ? 'status-running' : 'status-stopped');
            }

            // Update frontend status with color change
            var frontendStatus = document.getElementById('frontend-status');
            var frontendCard = frontendStatus ? frontendStatus.closest('.status-card') : null;

            if (frontendStatus) frontendStatus.textContent = data.frontend_running ? 'Running' : 'Stopped';
            if (frontendCard) {
                frontendCard.className = 'status-card ' + (data.frontend_running ? 'status-running' : 'status-stopped');
            }

            // Update data counts
            var rawCount = document.getElementById('raw-count');
            var pcaCount = document.getElementById('pca-count');
            var llmCount = document.getElementById('llm-count');

            if (rawCount) rawCount.textContent = data.raw_data_points || 0;
            if (pcaCount) pcaCount.textContent = data.pca_data_points || 0;
            if (llmCount) llmCount.textContent = data.llm_data_points || 0;

            // Update live connection status
            var liveConnection = document.getElementById('live-connection');
            var liveCount = document.getElementById('live-count');

            if (liveConnection) {
                var connected = data.backend_running && data.tep_running;
                liveConnection.textContent = connected ? 'Live: Connected' : 'Live: Disconnected';
                liveConnection.className = connected ? 'live-badge live-ok' : 'live-badge live-bad';
            }

            if (liveCount) {
                var totalReceived = (data.raw_data_points || 0);
                liveCount.textContent = 'Received: ' + totalReceived;
            }

            // Update speed display
            var speedModeEl = document.getElementById('speed-mode');
            var speedFactorEl = document.getElementById('speed-factor');
            var speedSlider = document.getElementById('speed-factor-slider');

            if (speedModeEl && data.speed_factor) {
                var speedText = data.speed_factor + 'x (' + data.step_interval_seconds + 's)';
                speedModeEl.textContent = speedText;
            }

            if (speedFactorEl && data.speed_factor) {
                speedFactorEl.textContent = data.speed_factor;
            }

            if (speedSlider && data.speed_factor) {
                speedSlider.value = data.speed_factor;
            }
        })
        .catch(function(error) { console.error('Status update failed:', error); });
}

// Initialize when DOM is ready
function initializeApp() {
    console.log('Initializing app from external JS...');
    try {
        // Update JavaScript status indicator
        var jsStatus = document.getElementById('js-status');
        if (jsStatus) {
            jsStatus.textContent = 'Working ✅';
            jsStatus.style.color = 'green';
        }

        // Test basic functionality
        var statusEl = document.getElementById('status');
        if (statusEl) {
            statusEl.innerHTML = '<div style="background: green; color: white; padding: 10px;">✅ External JavaScript is WORKING!</div>';
        }

        // Initialize dynamic updates
        initializeDynamicUpdates();

        // Test if functions are accessible
        console.log('Testing function availability:');
        console.log('- startTEP:', typeof startTEP);
        console.log('- startBackend:', typeof startBackend);
        console.log('- startFrontend:', typeof startFrontend);
        console.log('- setSpeed:', typeof setSpeed);
        console.log('- startDynamicStatusUpdates:', typeof startDynamicStatusUpdates);

        console.log('✅ External JavaScript initialized successfully');

        // Auto-test backend connection
        autoTestBackend();

    } catch(e) {
        console.error('❌ External JavaScript initialization failed:', e);
        var jsStatus = document.getElementById('js-status');
        if (jsStatus) {
            jsStatus.textContent = 'Error: ' + e.message;
            jsStatus.style.color = 'red';
        }
        alert('Initialization Error: ' + e.message);
    }
}

// GLOBAL SCOPE: Dynamic refresh rate based on simulation speed
var statusUpdateInterval = null;

function startDynamicStatusUpdates() {
    // Clear existing interval
    if (statusUpdateInterval) {
        clearInterval(statusUpdateInterval);
    }

    // Get current speed factor from backend
    fetch('/api/status')
        .then(function(response) { return response.json(); })
        .then(function(data) {
            var speedFactor = data.speed_factor || 1.0;
            var baseInterval = 5000; // 5 seconds default

            // Calculate dynamic update rate
            // For speed > 1x: update more frequently
            // For speed < 1x: update less frequently
            var updateRate = Math.max(1000, Math.min(10000, baseInterval / speedFactor));

            console.log('Setting dynamic update rate:', updateRate + 'ms (speed factor: ' + speedFactor + 'x)');

            // Start new interval with dynamic rate
            statusUpdateInterval = setInterval(updateStatus, updateRate);
        })
        .catch(function(e) {
            console.error('Failed to get speed factor, using default 5s updates:', e);
            statusUpdateInterval = setInterval(updateStatus, 5000);
        });
}

// Initialize dynamic updates when app starts
function initializeDynamicUpdates() {
    // Start dynamic updates
    startDynamicStatusUpdates();
    updateStatus();
}

// Multiple initialization methods for Safari compatibility
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

window.onload = function() {
    console.log('Window loaded - external JS final initialization');
    initializeApp();
};

// Additional missing functions
function stopTEP() {
    console.log('stopTEP() called from external JS');
    var btns = document.querySelectorAll("button[onclick*='stopTEP']");

    for (var i = 0; i < btns.length; i++) {
        if (btns[i]) btns[i].disabled = true;
    }

    fetch('/api/tep/stop', {method: 'POST'})
        .then(function(response) { return response.json(); })
        .then(function(data) {
            showMessage(data.message, data.success ? 'success' : 'error');
            if (data.success) {
                for (var i = 0; i < btns.length; i++) {
                    btns[i].classList.add('btn-success');
                    (function(btn) {
                        setTimeout(function() { btn.classList.remove('btn-success'); }, 800);
                    })(btns[i]);
                }
            }
        })
        .catch(function(e) { showMessage('Stop TEP failed: ' + e, 'error'); })
        .finally(function() {
            for (var i = 0; i < btns.length; i++) {
                if (btns[i]) btns[i].disabled = false;
            }
        });
}

function stopAll() {
    console.log('🛑 EMERGENCY STOP: stopAll() called from external JS');

    // Show immediate feedback
    showMessage('🛑 EMERGENCY STOP: Shutting down all services...', 'warning');

    // Disable the stop button to prevent multiple clicks
    var stopBtn = document.querySelector("button[onclick*='stopAll']");
    if (stopBtn) {
        stopBtn.disabled = true;
        stopBtn.textContent = '🛑 Stopping...';
    }

    // Call the comprehensive stop endpoint
    fetch('/api/stop/all', {method: 'POST'})
        .then(function(response) {
            if (!response.ok) {
                throw new Error('Stop request failed: ' + response.status);
            }
            return response.json();
        })
        .then(function(data) {
            showMessage('✅ ' + data.message, 'success');

            // Additional cleanup - call external stop script
            return fetch('/api/emergency/shutdown', {method: 'POST'});
        })
        .then(function(response) {
            if (response && response.ok) {
                return response.json();
            }
            return {message: 'External shutdown script not available'};
        })
        .then(function(data) {
            console.log('External shutdown result:', data);
            showMessage('🎉 Complete shutdown successful! All services stopped.', 'success');

            // Re-enable button after 5 seconds
            setTimeout(function() {
                if (stopBtn) {
                    stopBtn.disabled = false;
                    stopBtn.textContent = '🛑 Stop Everything';
                }
            }, 5000);
        })
        .catch(function(error) {
            console.error('Stop error:', error);
            showMessage('⚠️ Stop request completed with warnings: ' + error.message, 'warning');

            // Re-enable button
            if (stopBtn) {
                stopBtn.disabled = false;
                stopBtn.textContent = '🛑 Stop Everything';
            }
        });
}

function setLLMInterval(sec) {
    console.log('setLLMInterval() called with:', sec);
    var seconds = parseInt(sec);
    fetch('/api/backend/config/runtime', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ llm_min_interval_seconds: seconds })
    })
    .then(function(r) { return r.json(); })
    .then(function(_) {
        var lab = document.getElementById('llm-interval-label');
        if (lab) lab.textContent = seconds;
        showMessage('LLM refresh interval set to ' + seconds + 's', 'success');
    })
    .catch(function(e) { showMessage('Failed to set LLM interval: ' + e, 'error'); });
}

function checkBaselineStatus() {
    console.log('checkBaselineStatus() called from external JS');
    fetch('http://localhost:8000/metrics')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            showMessage('Backend ok. live_buffer=' + data.live_buffer + ', window=' + data.pca_window + ', baseline_features=' + data.baseline_features, 'success');
        })
        .catch(function(e) {
            showMessage('Metrics check failed: ' + e, 'error');
        });
}

function restartTEP() {
    console.log('restartTEP() called from external JS');
    fetch('/api/tep/restart', {method: 'POST'})
        .then(function(r) { return r.json(); })
        .then(function(d) { showMessage(d.message, d.success ? 'success' : 'error'); })
        .catch(function(e) { showMessage('Restart failed: ' + e, 'error'); });
}

function systemHealthCheck() {
    console.log('systemHealthCheck() called');
    showMessage('Checking system health...', 'info');

    fetch('/api/health')
        .then(function(r) { return r.json(); })
        .then(function(health) {
            var message = '🔍 System Health Check:\n\n';
            message += 'Overall Status: ' + health.overall_status + '\n\n';

            message += 'Components:\n';
            for (var component in health.components) {
                message += '• ' + component + ': ' + health.components[component] + '\n';
            }

            if (health.issues.length > 0) {
                message += '\nIssues Found:\n';
                for (var i = 0; i < health.issues.length; i++) {
                    message += '⚠️ ' + health.issues[i] + '\n';
                }
            }

            if (health.recommendations.length > 0) {
                message += '\nRecommendations:\n';
                for (var i = 0; i < health.recommendations.length; i++) {
                    message += '💡 ' + health.recommendations[i] + '\n';
                }
            }

            var isReady = health.overall_status.indexOf('✅') !== -1;
            showMessage(message, isReady ? 'success' : 'error');

            // Also show in alert for better visibility
            alert(message);
        })
        .catch(function(e) {
            showMessage('Health check failed: ' + e, 'error');
        });
}

function ultraStart() {
    console.log('ultraStart() called - One-click 50x speed startup');
    showMessage('🚀 Starting ultra-fast system (50x speed)...', 'info');

    fetch('/api/ultra_start', {method: 'POST'})
        .then(function(r) { return r.json(); })
        .then(function(data) {
            showMessage(data.message, data.success ? 'success' : 'error');

            if (data.success) {
                // 🔥 CRITICAL FIX: Restart dynamic updates for ultra speed
                console.log('🔄 Restarting dynamic status updates for ultra speed (50x)');
                startDynamicStatusUpdates();

                // Force status update to show new speed
                setTimeout(updateStatus, 1000);

                // Show success alert
                alert('🎉 ULTRA-FAST SYSTEM READY!\n\n' +
                      '⚡ Speed: 50x (data every ' + data.interval_seconds.toFixed(1) + 's)\n' +
                      '📊 Monitor: http://localhost:3000\n' +
                      '🔥 You should see VERY fast updates now!\n' +
                      '📱 Frontend will update every ' + Math.max(1, 5/50).toFixed(1) + 's');
            }
        })
        .catch(function(e) {
            showMessage('Ultra start failed: ' + e, 'error');
        });
}

function loadLog(name) {
    console.log('loadLog() called with:', name);
    fetch('/api/logs/' + name)
        .then(function(r) { return r.json(); })
        .then(function(d) {
            var el = document.getElementById('log-view');
            if (el) {
                el.textContent = (d.lines || []).join('');
                el.scrollTop = el.scrollHeight;
            }
        })
        .catch(function(e) {
            showMessage('Failed to load log: ' + e, 'error');
        });
}

function clearLog() {
    console.log('clearLog() called from external JS');
    var el = document.getElementById('log-view');
    if (el) el.textContent = '';
}

// More missing functions
function reloadBaseline() {
    console.log('reloadBaseline() called from external JS');
    var btn = document.getElementById('btn-reload-baseline');
    if (btn) {
        btn.disabled = true;
        btn.classList.add('btn-active');
    }
    fetch('/api/backend/config/baseline/reload', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({})
    })
    .then(function(r) {
        return r.text().then(function(t) {
            try {
                return JSON.parse(t);
            } catch(e) {
                return {status: 'error', error: 'Non-JSON (' + r.status + '): ' + t.slice(0, 160)};
            }
        });
    })
    .then(function(data) {
        if (data.status === 'ok') {
            showMessage('Baseline reloaded (' + data.features + ' features)', 'success');
            if (btn) {
                btn.classList.add('btn-success');
                setTimeout(function() { btn.classList.remove('btn-success'); }, 1200);
            }
        } else {
            showMessage('Baseline reload error: ' + data.error, 'error');
        }
    })
    .catch(function(e) { showMessage('Baseline reload failed: ' + e, 'error'); })
    .finally(function() {
        if (btn) {
            btn.disabled = false;
            btn.classList.remove('btn-active');
        }
    });
}

function applyStabilityDefaults() {
    console.log('applyStabilityDefaults() called from external JS');
    var payload = {
        llm_min_interval_seconds: 70,
        feature_shift_min_interval_seconds: 999,
        feature_shift_jaccard_threshold: 1.0
    };
    var btn = document.getElementById('btn-stability-defaults');
    if (btn) {
        btn.disabled = true;
        btn.classList.add('btn-active');
    }
    fetch('/api/backend/config/runtime', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    })
    .then(function(r) {
        return r.json().catch(function(e) {
            return r.text().then(function(t) {
                throw new Error('Non-JSON (' + r.status + '): ' + t.slice(0, 160));
            });
        });
    })
    .then(function(_) {
        showMessage('Stability defaults applied', 'success');
        if (btn) {
            btn.classList.add('btn-success');
            setTimeout(function() { btn.classList.remove('btn-success'); }, 1200);
        }
    })
    .catch(function(e) { showMessage('Failed to apply defaults: ' + e, 'error'); })
    .finally(function() {
        if (btn) {
            btn.disabled = false;
            btn.classList.remove('btn-active');
        }
    });
}

function showAnalysisHistory() {
    console.log('showAnalysisHistory() called from external JS');
    var limitSel = document.getElementById('history-limit');
    var limit = limitSel ? parseInt(limitSel.value) : 5;

    showMessage('Loading analysis history...', 'info');

    fetch('/api/backend/analysis/history?limit=' + limit)
        .then(function(r) {
            console.log('Analysis history response status:', r.status);
            return r.json();
        })
        .then(function(data) {
            console.log('Analysis history data:', data);
            var box = document.getElementById('analysis-history');
            if (!box) {
                console.error('analysis-history element not found!');
                return;
            }

            if (!data.items || !data.items.length) {
                box.textContent = '(no analysis history yet - try triggering some anomalies first)';
                showMessage('No analysis history found', 'info');
            } else {
                var lines = data.items.map(function(it, idx) {
                    var ts = it.timestamp || new Date((it.time || 0) * 1000).toLocaleTimeString();
                    var header = '#' + (idx + 1) + ' — ' + ts;
                    var featureAnalysis = it.feature_analysis || '';
                    var summary = it.performance_summary ? JSON.stringify(it.performance_summary) : '';

                    // Add LLM analysis content
                    var llmContent = '';
                    if (it.llm_analyses) {
                        for (var model in it.llm_analyses) {
                            var analysis = it.llm_analyses[model];
                            if (analysis && analysis.analysis) {
                                llmContent += '\n\n=== ' + model.toUpperCase() + ' ANALYSIS ===\n';
                                llmContent += analysis.analysis;
                                if (analysis.response_time) {
                                    llmContent += '\n(Response time: ' + analysis.response_time + 's)';
                                }
                            }
                        }
                    }

                    return header + '\n' + featureAnalysis + llmContent + '\n' + summary + '\n';
                });
                box.textContent = lines.join('\n-------------------------------------\n');
                showMessage('Loaded ' + data.items.length + ' analysis entries with LLM content', 'success');
            }
            box.style.display = 'block';
        })
        .catch(function(e) {
            console.error('Analysis history error:', e);
            showMessage('Failed to load analysis history: ' + e, 'error');
            var box = document.getElementById('analysis-history');
            if (box) {
                box.textContent = 'Error loading analysis history. Make sure backend is running on port 8000.';
                box.style.display = 'block';
            }
        });
}



function downloadAnalysis(fmt) {
    console.log('downloadAnalysis() called with format:', fmt);
    showMessage('Preparing download...', 'info');

    // Get analysis history and create download
    var limitSel = document.getElementById('history-limit');
    var limit = limitSel ? parseInt(limitSel.value) : 5;

    fetch('/api/backend/analysis/history?limit=' + limit)
        .then(function(r) {
            if (!r.ok) throw new Error('Backend not available (port 8000)');
            return r.json();
        })
        .then(function(data) {
            if (!data.items || !data.items.length) {
                showMessage('No analysis data to download', 'error');
                return;
            }

            var content = '';
            var filename = '';

            if (fmt === 'json') {
                // JSON format - single JSON array
                content = JSON.stringify(data.items, null, 2);
                filename = 'tep_analysis_history.json';
            } else if (fmt === 'md') {
                // Markdown format
                var lines = ['# TEP Analysis History\n'];
                data.items.forEach(function(item, i) {
                    var ts = item.timestamp || 'Unknown time';
                    lines.push('## Analysis #' + (i + 1) + ' - ' + ts + '\n');
                    lines.push('**Feature Analysis:**\n```\n' + (item.feature_analysis || 'N/A') + '\n```\n');

                    if (item.llm_analyses) {
                        lines.push('**LLM Analysis Results:**\n');
                        for (var model in item.llm_analyses) {
                            var analysis = item.llm_analyses[model];
                            if (analysis && analysis.analysis) {
                                lines.push('### ' + model.toUpperCase() + '\n');
                                lines.push(analysis.analysis + '\n');
                                if (analysis.response_time) {
                                    lines.push('*Response time: ' + analysis.response_time + 's*\n');
                                }
                            }
                        }
                    }

                    if (item.performance_summary) {
                        lines.push('**Performance Summary:**\n');
                        for (var model in item.performance_summary) {
                            var perf = item.performance_summary[model];
                            lines.push('- ' + model + ': ' + (perf.response_time || 0) + 's, ' + (perf.word_count || 0) + ' words\n');
                        }
                    }
                    lines.push('\n---\n');
                });
                content = lines.join('\n');
                filename = 'tep_analysis_history.md';
            } else {
                showMessage('Invalid format: ' + fmt, 'error');
                return;
            }

            // Create and trigger download
            var blob = new Blob([content], { type: 'text/plain' });
            var url = window.URL.createObjectURL(blob);
            var a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            showMessage('Downloaded ' + filename + ' with ' + data.items.length + ' analysis entries', 'success');
        })
        .catch(function(e) {
            showMessage('Download failed: ' + e + '. Make sure FaultExplainer backend is running on port 8000, or try copying the displayed analysis instead.', 'error');
        });
}

function downloadAnalysisByDate() {
    console.log('downloadAnalysisByDate() called from external JS');
    var inp = document.getElementById('history-date');
    if (!inp || !inp.value) {
        showMessage('Please select a date', 'error');
        return;
    }
    var ds = inp.value; // YYYY-MM-DD
    window.location = '/api/analysis/history/download/bydate/' + ds;
}

// Missing slider and preset functions
function setDemoInterval(sec) {
    console.log('setDemoInterval() called with:', sec);
    var seconds = parseInt(sec);
    fetch('/api/speed', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({mode: 'demo', seconds: seconds})
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        var intervalEl = document.getElementById('demo-interval');
        var speedModeEl = document.getElementById('speed-mode');
        if (intervalEl) intervalEl.textContent = d.step_interval_seconds;
        if (speedModeEl) speedModeEl.textContent = 'Demo (' + d.step_interval_seconds + 's)';
        showMessage('Demo interval set to ' + d.step_interval_seconds + 's', 'success');
    })
    .catch(function(e) { showMessage('Failed to set interval: ' + e, 'error'); });
}

// New speed factor control function
function setSpeedFactor(factor) {
    console.log('setSpeedFactor() called with:', factor);
    var speedFactor = parseFloat(factor);

    // Update display
    var label = document.getElementById('speed-factor');
    if (label) {
        var description = speedFactor < 1.0 ? (speedFactor + 'x (Slower)') :
                         speedFactor === 1.0 ? '1.0x (Normal)' :
                         speedFactor + 'x (Faster)';
        label.textContent = description;
    }

    // Send to backend (will need new API endpoint)
    fetch('/api/speed/factor', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({speed_factor: speedFactor})
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        console.log('setSpeedFactor response:', d);
        showMessage('Speed factor set to ' + speedFactor + 'x (interval: ' + d.step_interval_seconds + 's)', 'success');

        // 🔥 CRITICAL FIX: Restart dynamic updates with new speed
        console.log('🔄 Restarting dynamic status updates for new speed factor:', speedFactor);
        startDynamicStatusUpdates();

        // Force immediate status update
        setTimeout(updateStatus, 500);
    })
    .catch(function(e) {
        console.error('setSpeedFactor error:', e);
        showMessage('Failed to set speed factor: ' + e, 'error');
    });
}

function setPreset(mode) {
    console.log('setPreset() called with mode:', mode);
    var demo = {
        pca_window_size: 8,
        fault_trigger_consecutive_step: 3,
        decimation_N: 1,
        llm_min_interval_seconds: 0
    };
    var balanced = {
        decimation_N: 4,
        pca_window_size: 12,
        fault_trigger_consecutive_step: 2,
        llm_min_interval_seconds: 20,
        feature_shift_min_interval_seconds: 60,
        feature_shift_jaccard_threshold: 0.8
    };
    var real = {
        pca_window_size: 20,
        fault_trigger_consecutive_step: 6,
        decimation_N: 1,
        llm_min_interval_seconds: 300
    };
    var cfg = mode === 'demo' ? demo : (mode === 'balanced' ? balanced : real);
    cfg.preset = mode;

    fetch('/api/backend/config/runtime', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(cfg)
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        showMessage('Backend runtime config updated: ' + JSON.stringify(data.updated), 'success');
        var label = mode === 'demo' ? 'Demo' : (mode === 'balanced' ? 'Balanced' : 'Realistic');
        var presetModeEl = document.getElementById('preset-mode');
        if (presetModeEl) presetModeEl.textContent = label;

        var demoBtn = document.getElementById('btn-preset-demo');
        var balancedBtn = document.getElementById('btn-preset-balanced');
        var realBtn = document.getElementById('btn-preset-real');

        if (demoBtn) demoBtn.classList.toggle('btn-active', mode === 'demo');
        if (balancedBtn) balancedBtn.classList.toggle('btn-active', mode === 'balanced');
        if (realBtn) realBtn.classList.toggle('btn-active', mode === 'real');
    })
    .catch(function(e) { showMessage('Config update failed: ' + e, 'error'); });
}

function setIngestion(mode) {
    console.log('setIngestion() called with mode:', mode);
    var internal = mode === 'internal';
    var internalBtn = document.getElementById('btn-ingest-internal');
    var csvBtn = document.getElementById('btn-ingest-csv');

    if (internalBtn) internalBtn.classList.toggle('btn-active', internal);
    if (csvBtn) csvBtn.classList.toggle('btn-active', !internal);

    var hint = document.getElementById('ingest-hint');
    if (hint) {
        hint.textContent = internal ?
            'Using Internal Simulator. Bridge controls disabled.' :
            'Using CSV Bridge. Internal Simulator controls disabled.';
    }

    // Enable/disable relevant buttons
    var simButtons = document.querySelectorAll("button[onclick*='startTEP'], button[onclick*='stopTEP']");
    var bridgeButtons = [
        document.getElementById('btn-bridge-start'),
        document.querySelectorAll("button[onclick*='stopBridge']")
    ];

    for (var i = 0; i < simButtons.length; i++) {
        if (simButtons[i]) simButtons[i].disabled = !internal;
    }

    if (bridgeButtons[0]) bridgeButtons[0].disabled = internal;
    if (bridgeButtons[1]) {
        for (var j = 0; j < bridgeButtons[1].length; j++) {
            if (bridgeButtons[1][j]) bridgeButtons[1][j].disabled = internal;
        }
    }
}

function setXMV(xmvNum, value) {
    console.log('setXMV() called with:', xmvNum, value);
    var floatValue = parseFloat(value);  // Convert to float (0.0-100.0)
    var valueSpan = document.getElementById('xmv' + xmvNum + '-value');
    if (valueSpan) valueSpan.textContent = floatValue.toFixed(1);

    fetch('/api/xmv/set', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            xmv_num: xmvNum,
            value: floatValue
        })
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        console.log('XMV set response:', data);
        if (!data.success) {
            console.error('Failed to set XMV:', data.message);
            showMessage('Failed to set XMV_' + xmvNum + ': ' + data.message, 'error');
        } else {
            console.log('XMV_' + xmvNum + ' set to ' + floatValue + '%');
        }
    })
    .catch(function(error) {
        console.error('Error setting XMV:', error);
        showMessage('Error setting XMV_' + xmvNum + ': ' + error.message, 'error');
    });
}

function setIDV(idvNum, value) {
    console.log('setIDV() called with:', idvNum, value);
    var intValue = parseInt(value);  // Convert to integer (0 or 1)
    var valueSpan = document.getElementById('idv' + idvNum + '-value');
    if (valueSpan) valueSpan.textContent = intValue === 1 ? 'ON' : 'OFF';

    fetch('/api/idv/set', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({idv_num: idvNum, value: intValue})  // Send integer 0 or 1
    })
    .then(function(response) { return response.json(); })
    .then(function(data) {
        if (data.success) {
            showMessage('IDV_' + idvNum + ' set to ' + value, 'success');
        }
    })
    .catch(function(e) { showMessage('IDV update failed: ' + e, 'error'); });
}

// Test IDV impact function
function testIDVImpact() {
    console.log('testIDVImpact() called');
    showMessage('Testing IDV impact...', 'info');

    fetch('/api/idv/test', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({})
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        console.log('IDV test response:', d);
        if (d.test_successful) {
            var message = 'IDV Test Results:\n';
            message += 'Baseline Reactor Temp: ' + d.baseline_reactor_temp + '\n';
            message += 'Fault Reactor Temp: ' + d.fault_reactor_temp + '\n';
            message += 'Difference Detected: ' + d.difference_detected;
            alert(message);
            showMessage('IDV test completed - check console for details', 'success');
        } else {
            showMessage('IDV test failed: ' + (d.error || 'Unknown error'), 'error');
        }
    })
    .catch(function(e) {
        console.error('IDV test error:', e);
        showMessage('IDV test failed: ' + e, 'error');
    });
}

// Test functions for emergency fallback
function simpleTest() {
    console.log('simpleTest() called from external JS');
    alert('Simple test button clicked!');
    var statusEl = document.getElementById('status');
    if (statusEl) {
        statusEl.innerHTML = '<div style="background: blue; color: white; padding: 10px;">Button clicked at ' + new Date().toLocaleTimeString() + '</div>';
    }
}

function testFunction() {
    console.log('testFunction() called from external JS');
    alert('Test function executed!');
}

// Backend connectivity test
function testBackendConnection() {
    console.log('Testing backend connection...');
    showMessage('Testing backend connection...', 'info');

    // Test multiple endpoints
    var tests = [
        {name: 'Status', url: 'http://localhost:8000/status'},
        {name: 'Metrics', url: 'http://localhost:8000/metrics'},
        {name: 'Analysis History', url: '/api/backend/analysis/history?limit=1'}
    ];

    var results = [];
    var completed = 0;

    tests.forEach(function(test) {
        fetch(test.url)
            .then(function(r) {
                results.push(test.name + ': ✅ OK (' + r.status + ')');
                return r.json();
            })
            .then(function(data) {
                console.log(test.name + ' data:', data);
            })
            .catch(function(e) {
                results.push(test.name + ': ❌ FAILED (' + e + ')');
            })
            .finally(function() {
                completed++;
                if (completed === tests.length) {
                    var message = 'Backend Test Results:\n' + results.join('\n');
                    showMessage(message, results.some(function(r) { return r.includes('❌'); }) ? 'error' : 'success');
                }
            });
    });
}

// Auto-test backend connection on load
function autoTestBackend() {
    setTimeout(function() {
        console.log('Auto-testing backend connection...');
        fetch('http://localhost:8000/status')
            .then(function(r) {
                console.log('✅ Backend is reachable on port 8000');
                var liveConnection = document.getElementById('live-connection');
                if (liveConnection && liveConnection.textContent.includes('Disconnected')) {
                    // Update connection status if backend is reachable
                    liveConnection.textContent = 'Live: Backend OK';
                    liveConnection.className = 'live-badge live-ok';
                }
            })
            .catch(function(e) {
                console.log('❌ Backend not reachable on port 8000:', e);
                var liveConnection = document.getElementById('live-connection');
                if (liveConnection) {
                    liveConnection.textContent = 'Live: Backend Down';
                    liveConnection.className = 'live-badge live-bad';
                }
            });
    }, 2000);
}

console.log('✅ External JavaScript file loaded completely');
