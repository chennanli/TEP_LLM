# TEP Live Streaming Issue - Handoff Documentation

## 🚨 CRITICAL ISSUE SUMMARY

**Problem**: FaultExplainer frontend shows "Live: disconnected" despite multiple attempts to fix the TEP simulation → Backend → Frontend data flow.

**User Goal**: Get live TEP process data streaming to FaultExplainer frontend with:
- 50x speed (3.6 second intervals)
- Real valve/button control capability
- Moving charts showing process measurements
- Anomaly detection working

**Current Status**: ❌ FAILED - No data flowing to frontend

---

## 🔍 CURRENT SYSTEM STATE

### What's Running:
1. **FaultExplainer Frontend**: http://localhost:5173 (legacy/external_repos/FaultExplainer-main/frontend)
2. **FaultExplainer Backend**: http://localhost:8000 (legacy/external_repos/FaultExplainer-main/backend)
3. **Unified Control Panel**: http://localhost:9001 (legacy/unified_tep_control_panel.py)

### What's NOT Working:
- TEP simulation fails with Fortran errors
- No data reaching `/stream` endpoint
- Frontend shows "Live: disconnected"
- No moving charts or real-time data

---

## 🔧 ATTEMPTED FIXES (ALL FAILED)

### Fix #1: IDV History Matrix Issue
**Problem**: `❌ TEP simulation step failed: 1-th dimension must be 20 but got 0`
**Attempted Fix**: Modified `unified_tep_control_panel.py` lines 385-391 to handle empty IDV history
**Result**: ❌ Still failing

### Fix #2: Fortran TEMAIN Output Array
**Problem**: Fortran function rejecting zero-initialized output arrays
**Attempted Fix**: Modified `legacy/external_repos/tep2py-master/tep2py.py` lines 96-120 to pre-allocate output arrays with Fortran ordering
**Result**: ❌ Still failing

### Fix #3: Fake Simulation Workaround (REMOVED)
**Problem**: Created `simulate_live_data.py` as workaround
**User Feedback**: Correctly rejected - wants real TEP data, not fake simulation
**Action**: Removed fake simulation file

---

## 🎯 ROOT CAUSE ANALYSIS

### The Core Issue:
The **TEP Fortran simulation** (`temain_mod.temain()`) is fundamentally broken. Every simulation step fails with:
```
❌ TEP simulation step failed: 1-th dimension must be 20 but got 0 (not defined)
```

### Data Flow Breakdown:
```
TEP Fortran ❌ → FaultExplainer Backend ✅ → FaultExplainer Frontend ❌
```

- **TEP Fortran**: Failing every step
- **Backend**: Running correctly, has `/ingest` and `/stream` endpoints
- **Frontend**: Working but no data to display

### Technical Details:
1. **Fortran Integration**: `legacy/external_repos/tep2py-master/tep2py.py`
2. **Error Location**: `temain_mod.temain()` function calls
3. **Matrix Dimensions**: Expects IDV (N×20) → XDATA (N×52)
4. **Speed Factor**: 50x (3.6 second intervals)

---

## 📁 KEY FILES TO INVESTIGATE

### Primary Files:
1. `legacy/unified_tep_control_panel.py` - Main control system
2. `legacy/external_repos/tep2py-master/tep2py.py` - TEP Python wrapper
3. `legacy/external_repos/tep2py-master/temain_mod.cpython-39-darwin.so` - Fortran binary
4. `legacy/external_repos/FaultExplainer-main/backend/app.py` - Backend with `/stream` endpoint

### Configuration Files:
1. `legacy/external_repos/FaultExplainer-main/backend/config.json` - Backend config
2. `legacy/external_repos/FaultExplainer-main/frontend/src/config.js` - Frontend config

---

## 🔬 DEBUGGING STEPS FOR NEXT AI

### Step 1: Verify Fortran Binary
```bash
cd legacy/external_repos/tep2py-master
python -c "import temain_mod; print(dir(temain_mod))"
```

### Step 2: Test Minimal TEP Call
```python
import numpy as np
import temain_mod

# Test minimal TEMAIN call
idata = np.zeros((1, 20), dtype=float)
xdata = np.zeros((1, 52), dtype=float, order='F')
result = temain_mod.temain(180, 1, idata, xdata, 1)
```

### Step 3: Check Backend Stream
```bash
curl -N http://localhost:8000/stream --max-time 10
```

### Step 4: Verify Frontend Connection
Check browser console for WebSocket/EventSource errors

---

## 🎛️ USER REQUIREMENTS

### Must Have:
- ✅ Real TEP physics (not fake simulation)
- ✅ 50x speed (3.6 second updates)
- ✅ Valve/button control (XMV/IDV)
- ✅ Moving charts in frontend
- ✅ Anomaly detection working
- ✅ Safari compatibility (user's browser)

### System Architecture:
```
TEP Fortran Simulation (50x speed)
    ↓ (every 3.6 seconds)
FaultExplainer Backend (/ingest → /stream)
    ↓ (Server-Sent Events)
FaultExplainer Frontend (Live charts)
```

---

## 🚀 NEXT STEPS RECOMMENDATION

### Priority 1: Fix Fortran Integration
The core issue is the TEP Fortran binary. Consider:
1. **Recompile Fortran**: The binary might be corrupted
2. **Check Dependencies**: Fortran runtime libraries
3. **Alternative TEP**: Use different TEP implementation
4. **Debug Fortran**: Add verbose logging to TEMAIN calls

### Priority 2: Verify Data Pipeline
Once Fortran works:
1. Confirm data reaches `/ingest`
2. Verify `/stream` endpoint streams data
3. Check frontend EventSource connection

### Priority 3: Test End-to-End
1. Start all components
2. Click "Start TEP" in control panel
3. Verify "Live: connected" in frontend
4. Confirm moving charts

---

## 📞 USER CONTEXT

- **Browser**: Safari on Mac
- **Environment**: Virtual environment `tep_env`
- **Workspace**: `/Users/chennanli/Desktop/LLM_Project/TE`
- **Focus**: Legacy folder only (not integration folder)
- **Experience**: Expects industrial-grade reliability

---

## ⚠️ CRITICAL NOTES

1. **No Integration Folder**: User specifically wants legacy folder only
2. **No Fake Data**: Must use real TEP Fortran simulation
3. **Safari Compatibility**: Ensure JavaScript works in Safari
4. **50x Speed**: User specifically requested this timing
5. **Industrial UX**: User expects professional industrial interface

---

**Status**: UNRESOLVED - Requires Fortran debugging expertise
**Next AI**: Focus on TEP Fortran integration first, then data pipeline
