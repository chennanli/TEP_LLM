// TEP Control Panel JavaScript
console.log('🚀 External JavaScript file loading...');

function testFunction() {
    alert('External JavaScript works!');
    console.log('testFunction() from external JS executed');
}

function showMessage(message, type = 'info') {
    console.log('showMessage:', message, type);
    const statusDiv = document.getElementById('status');
    if (!statusDiv) {
        console.error('Status div not found!');
        alert(message); // Fallback
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

    // Auto-hide after 5 seconds
    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 5000);
}

function startBackend() {
    console.log('startBackend() called from external JS');
    const btns = document.querySelectorAll("button[onclick*='startBackend']");
    console.log('Found buttons:', btns.length);
    btns.forEach(b=>b && (b.disabled=true));

    fetch('/api/faultexplainer/backend/start', {method: 'POST'})
        .then(response => {
            console.log('Backend response:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Backend data:', data);
            showMessage(data.message, data.success ? 'success' : 'error');
            if (data.success) {
                btns.forEach(b=>{
                    b.classList.add('btn-success');
                    setTimeout(()=>b.classList.remove('btn-success'), 800);
                });
            }
        })
        .catch(e => {
            console.error('Backend error:', e);
            showMessage(`Backend start failed: ${e}`, 'error');
        })
        .finally(()=>btns.forEach(b=>b && (b.disabled=false)));
}

function startTEP() {
    console.log('startTEP() called from external JS');
    const btns = document.querySelectorAll("button[onclick*='startTEP']");
    btns.forEach(b=>b && (b.disabled=true));
    fetch('/api/tep/start', {method: 'POST'})
        .then(response => response.json())
        .then(data => {
            showMessage(data.message, data.success ? 'success' : 'error');
            if (data.success) { btns.forEach(b=>{ b.classList.add('btn-success'); setTimeout(()=>b.classList.remove('btn-success'), 800); }); }
        })
        .catch(e=>showMessage(`Start TEP failed: ${e}`,'error'))
        .finally(()=>btns.forEach(b=>b && (b.disabled=false)));
}

function updateStatus() {
    console.log('updateStatus() called from external JS');
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            console.log('Status data received:', data);
            // Update TEP status
            const tepStatus = document.getElementById('tep-status');
            const tepStep = document.getElementById('tep-step');
            if (tepStatus) tepStatus.textContent = data.tep_running ? 'Running' : 'Stopped';
            if (tepStep) tepStep.textContent = data.current_step;

            // Update backend/frontend status
            const backendStatus = document.getElementById('backend-status');
            const frontendStatus = document.getElementById('frontend-status');
            if (backendStatus) backendStatus.textContent = data.backend_running ? 'Running' : 'Stopped';
            if (frontendStatus) frontendStatus.textContent = data.frontend_running ? 'Running' : 'Stopped';
        })
        .catch(error => console.error('Status update failed:', error));
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ DOM loaded, initializing external JavaScript...');
    
    // Auto-refresh status every 5 seconds
    setInterval(updateStatus, 5000);
    updateStatus(); // Initial load
    
    console.log('✅ Status updates started from external JS');
});

console.log('✅ External JavaScript file loaded completely');
