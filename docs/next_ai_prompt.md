# Expert Handoff Prompt for Next AI

## 🎯 MISSION CRITICAL TASK

You are taking over a **FAILED** TEP (Tennessee Eastman Process) live streaming integration. The previous AI could not solve the core Fortran simulation issue. The user needs **real-time TEP process data** flowing to a FaultExplainer frontend.

---

## 🚨 IMMEDIATE PROBLEM

**Status**: FaultExplainer frontend shows "Live: disconnected" (red)
**Root Cause**: TEP Fortran simulation fails every step with:
```
❌ TEP simulation step failed: 1-th dimension must be 20 but got 0 (not defined)
```

**User Goal**: Get moving charts with real TEP data at 50x speed (3.6 second intervals)

---

## 🔧 SYSTEM ARCHITECTURE

### Current State:
```
TEP Fortran (temain_mod.temain) ❌ BROKEN
    ↓
Unified Control Panel (port 9001) ✅ WORKING  
    ↓
FaultExplainer Backend (port 8000) ✅ WORKING
    ↓ (/stream endpoint)
FaultExplainer Frontend (port 5173) ✅ WORKING
```

### What's Running:
- ✅ **Frontend**: http://localhost:5173 (legacy/external_repos/FaultExplainer-main/frontend)
- ✅ **Backend**: http://localhost:8000 (legacy/external_repos/FaultExplainer-main/backend) 
- ✅ **Control Panel**: http://localhost:9001 (legacy/unified_tep_control_panel.py)

### What's Broken:
- ❌ **TEP Simulation**: Fortran binary failing dimension checks
- ❌ **Data Flow**: No data reaching `/stream` endpoint
- ❌ **Live Connection**: Frontend can't connect to stream

---

## 🔍 TECHNICAL DETAILS

### Key Files:
1. **Fortran Binary**: `legacy/external_repos/tep2py-master/temain_mod.cpython-39-darwin.so`
2. **Python Wrapper**: `legacy/external_repos/tep2py-master/tep2py.py`
3. **Control System**: `legacy/unified_tep_control_panel.py`
4. **Backend Stream**: `legacy/external_repos/FaultExplainer-main/backend/app.py`

### Error Details:
- **Function**: `temain_mod.temain()` in Fortran binary
- **Expected Input**: IDV matrix (N×20) 
- **Expected Output**: XDATA matrix (N×52)
- **Actual Error**: "1-th dimension must be 20 but got 0"

### Previous Fixes (FAILED):
1. Modified IDV history handling in control panel
2. Pre-allocated Fortran output arrays with proper ordering
3. Removed fake simulation workaround (user correctly rejected)

---

## 🎯 YOUR MISSION

### Priority 1: DEBUG FORTRAN INTEGRATION
**Start here** - This is the core blocker:

```python
# Test minimal TEMAIN call
import numpy as np
import sys
sys.path.append('legacy/external_repos/tep2py-master')
import temain_mod

# Try simplest possible call
idata = np.ones((1, 20), dtype=float)  # Single timestep, 20 IDV inputs
xdata = np.zeros((1, 52), dtype=float, order='F')  # Pre-allocated output
result = temain_mod.temain(180, 1, idata, xdata, 1)
```

### Priority 2: VERIFY DATA PIPELINE
Once Fortran works:
1. Confirm data reaches backend `/ingest`
2. Test `/stream` endpoint: `curl -N http://localhost:8000/stream`
3. Check frontend EventSource connection

### Priority 3: END-TO-END TESTING
1. Start unified control panel: `cd legacy && python unified_tep_control_panel.py`
2. Click "▶️ Start TEP" button
3. Verify frontend shows "Live: connected"
4. Confirm moving charts with real data

---

## 🛠️ DEBUGGING APPROACH

### Step 1: Fortran Binary Health Check
```bash
cd legacy/external_repos/tep2py-master
python -c "import temain_mod; print('Fortran binary loaded:', dir(temain_mod))"
```

### Step 2: Matrix Dimension Analysis
```python
# Check what TEMAIN expects vs what we're sending
import numpy as np
idata = np.zeros((5, 20), dtype=float)  # 5 timesteps, 20 IDV
print(f"IDV shape: {idata.shape}")
print(f"IDV dtype: {idata.dtype}")
print(f"IDV order: {'F' if idata.flags.f_contiguous else 'C'}")
```

### Step 3: Alternative TEP Sources
If Fortran binary is corrupted, consider:
- Recompiling from source in `legacy/external_repos/tep2py-master/src/`
- Using different TEP implementation
- Checking Fortran runtime dependencies

---

## 🎛️ USER REQUIREMENTS

### Must Have:
- ✅ **Real TEP Physics**: No fake/synthetic data
- ✅ **50x Speed**: 3.6 second update intervals  
- ✅ **Valve Control**: XMV/IDV manipulation capability
- ✅ **Moving Charts**: Live data visualization
- ✅ **Safari Compatible**: User's primary browser

### System Constraints:
- 🔒 **Legacy Folder Only**: Don't touch integration folder
- 🔒 **Mac Environment**: Darwin system, virtual env `tep_env`
- 🔒 **Industrial UX**: Professional interface expected

---

## 🚀 SUCCESS CRITERIA

### You'll know you've succeeded when:
1. ✅ TEP Fortran simulation runs without errors
2. ✅ Backend receives data via `/ingest` endpoint
3. ✅ Frontend shows "Live: connected" (green status)
4. ✅ Charts display moving TEP process measurements
5. ✅ User can control valves and trigger anomalies

### Expected Data Flow:
```
TEP Fortran → Control Panel → Backend /ingest → Backend /stream → Frontend Charts
```

---

## 📞 CONTEXT

**User Profile**: Industrial process engineer, expects reliability
**Browser**: Safari on Mac
**Workspace**: `/Users/chennanli/Desktop/LLM_Project/TE`
**Environment**: Python virtual env `tep_env`

---

## ⚠️ CRITICAL WARNINGS

1. **Don't Create Fake Data**: User specifically rejected synthetic simulation
2. **Focus on Fortran First**: Backend/frontend are working - fix the source
3. **Test Incrementally**: Start with minimal TEMAIN call, build up
4. **Safari Compatibility**: Ensure JavaScript works in Safari

---

**Your Goal**: Fix the TEP Fortran simulation so real process data flows to the frontend.
**Start With**: Debug `temain_mod.temain()` function call in `tep2py.py`
**Success Metric**: Frontend shows "Live: connected" with moving charts

Good luck! The user is counting on you to solve what the previous AI couldn't.
