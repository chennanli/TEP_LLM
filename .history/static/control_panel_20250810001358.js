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

function showMessage(message, type) {
    console.log('showMessage:', message, type);
    var statusDiv = document.getElementById('status');
    if (!statusDiv) {
        console.error('Status div not found!');
        alert(message);
        return;
    }
    statusDiv.textContent = message;
    statusDiv.className = type === 'success' ? 'btn-success' :
                         type === 'error' ? 'btn-danger' : 'btn-primary';
    statusDiv.style.display = 'block';
    statusDiv.style.padding = '15px';
    statusDiv.style.borderRadius = '8px';
    statusDiv.style.marginBottom = '20px';
    statusDiv.style.fontWeight = 'bold';

    setTimeout(function() {
        statusDiv.style.display = 'none';
    }, 5000);
}

function startBackend() {
    console.log('startBackend() called from external JS');
    var btns = document.querySelectorAll("button[onclick*='startBackend']");
    console.log('Found buttons:', btns.length);
    
    for (var i = 0; i < btns.length; i++) {
        if (btns[i]) btns[i].disabled = true;
    }

    fetch('/api/faultexplainer/backend/start', {method: 'POST'})
        .then(function(response) {
            console.log('Backend response:', response.status);
            return response.json();
        })
        .then(function(data) {
            console.log('Backend data:', data);
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
        .catch(function(e) {
            console.error('Backend error:', e);
            showMessage('Backend start failed: ' + e, 'error');
        })
        .finally(function() {
            for (var i = 0; i < btns.length; i++) {
                if (btns[i]) btns[i].disabled = false;
            }
        });
}

function startTEP() {
    console.log('startTEP() called from external JS');
    var btns = document.querySelectorAll("button[onclick*='startTEP']");
    
    for (var i = 0; i < btns.length; i++) {
        if (btns[i]) btns[i].disabled = true;
    }
    
    fetch('/api/tep/start', {method: 'POST'})
        .then(function(response) { return response.json(); })
        .then(function(data) {
            showMessage(data.message, data.success ? 'success' : 'error');
            if (data.success) {
                for (var i = 0; i < btns.length; i++) {
                    btns[i].classList.add('btn-success');
                    setTimeout(function() { btns[i].classList.remove('btn-success'); }, 800);
                }
            }
        })
        .catch(function(e) { showMessage('Start TEP failed: ' + e, 'error'); })
        .finally(function() {
            for (var i = 0; i < btns.length; i++) {
                if (btns[i]) btns[i].disabled = false;
            }
        });
}

function updateStatus() {
    console.log('updateStatus() called from external JS');
    fetch('/api/status')
        .then(function(response) { return response.json(); })
        .then(function(data) {
            console.log('Status data received:', data);
            // Update TEP status
            var tepStatus = document.getElementById('tep-status');
            var tepStep = document.getElementById('tep-step');
            if (tepStatus) tepStatus.textContent = data.tep_running ? 'Running' : 'Stopped';
            if (tepStep) tepStep.textContent = data.current_step;

            // Update backend/frontend status
            var backendStatus = document.getElementById('backend-status');
            var frontendStatus = document.getElementById('frontend-status');
            if (backendStatus) backendStatus.textContent = data.backend_running ? 'Running' : 'Stopped';
            if (frontendStatus) frontendStatus.textContent = data.frontend_running ? 'Running' : 'Stopped';
        })
        .catch(function(error) { console.error('Status update failed:', error); });
}

// Initialize when DOM is ready
function initializeApp() {
    console.log('Initializing app from external JS...');
    try {
        // Test basic functionality
        var statusEl = document.getElementById('status');
        if (statusEl) {
            statusEl.innerHTML = '<div style="background: green; color: white; padding: 10px;">✅ External JavaScript is WORKING!</div>';
        }
        
        // Auto-refresh status every 5 seconds
        setInterval(updateStatus, 5000);
        updateStatus();
        
        console.log('✅ External JavaScript initialized successfully');
    } catch(e) {
        console.error('❌ External JavaScript initialization failed:', e);
        alert('Initialization Error: ' + e.message);
    }
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

console.log('✅ External JavaScript file loaded completely');
