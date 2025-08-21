# Technical Handoff: TEP Fortran-Python Integration

## 🎯 **Mission for Next AI**
Fix the fundamental disconnect between TEP control interface and Fortran simulation to enable real physics-based process control.

## 🔍 **Critical Technical Analysis**

### **The Core Problem**
```python
# Current broken flow:
User moves XMV slider → Python synthetic effects → Fake "responsive" data
# Should be:
User moves XMV slider → Fortran TEMAIN function → Real process physics
```

### **Evidence of the Problem**
1. **TEMAIN Error**: `temain_mod.temain() takes at most 5 arguments (6 given)`
2. **Synthetic Effects**: Python overlays fake changes instead of real physics
3. **No Real Control**: XMV values never reach actual Fortran simulation

## 🔧 **Technical Deep Dive**

### **File: `legacy/external_repos/tep2py-master/tep2py.py`**
**Problem Lines 83-93:**
```python
# This is WRONG - passes 6 args to function expecting 5
result = temain_mod.temain(npts, nx, idv_matrix, 0, self.speed_factor, self.user_xmv)
```

**Should be:**
```python
# Fix the Fortran function signature first, then:
result = temain_mod.temain(npts, nx, idv_matrix, self.user_xmv, self.speed_factor)
```

### **File: `legacy/external_repos/tep2py-master/teprob.f`**
**Current Signature (WRONG):**
```fortran
SUBROUTINE TEMAIN(NN, TIME, YY, YP, SPEED_FACTOR)
```

**Should be:**
```fortran
SUBROUTINE TEMAIN(NN, TIME, YY, YP, USER_XMV, SPEED_FACTOR)
    INTEGER NN
    REAL*8 TIME, YY(*), YP(*)
    REAL*8 USER_XMV(11)  ! XMV(1) to XMV(11) user controls
    REAL*8 SPEED_FACTOR
    
    ! Apply USER_XMV to actual process equations
    ! Modify feed flows, valve positions, etc. in the physics
```

### **File: `legacy/external_repos/tep2py-master/tep2py.py` Lines 154-192**
**Current Approach (WRONG):**
```python
# Synthetic Python overlays - NOT real physics
xmv_effects = {
    0: {1: 200.0, 5: 1.2, 6: 2.0},  # Fake effects
    # ... more fake effects
}
```

**Should be:**
```python
# Remove all synthetic effects - let Fortran handle real physics
# Just pass user_xmv to TEMAIN and trust the process model
```

## 🎯 **Step-by-Step Fix Plan**

### **Step 1: Analyze Current Fortran Code**
```bash
cd legacy/external_repos/tep2py-master
grep -n "SUBROUTINE TEMAIN" teprob.f
grep -A 20 "SUBROUTINE TEMAIN" teprob.f
```

### **Step 2: Fix Fortran Function Signature**
- Modify `TEMAIN` to accept `USER_XMV(11)` parameter
- Update all calls to `TEMAIN` in Fortran code
- Recompile the Fortran module

### **Step 3: Fix Python Wrapper**
- Update `tep2py.py` line ~93 to pass correct parameters
- Remove synthetic effect overlays (lines 154-192)
- Test with simple XMV changes

### **Step 4: Add Integration Support**
- Add XMV endpoints to `integration/src/backend/services/llm-analysis/app.py`
- Update `tep_bridge.py` to support XMV controls
- Connect frontend sliders to backend

### **Step 5: Calibrate Anomaly Detection**
- Test with real physics-based changes
- Adjust threshold if needed (currently 0.001)
- Validate with multiple XMV/IDV combinations

## 🔍 **Key Files to Examine**

### **Fortran Source**
- `legacy/external_repos/tep2py-master/teprob.f` - Main process model
- `legacy/external_repos/tep2py-master/temain_mod.f90` - Module wrapper

### **Python Integration**
- `legacy/external_repos/tep2py-master/tep2py.py` - Python wrapper
- `legacy/external_repos/tep2py-master/setup.py` - Build configuration

### **Control Interface**
- `legacy/unified_tep_control_panel.py` - Working XMV controls
- `integration/src/backend/services/simulation/tep_bridge.py` - Needs XMV support

## 🧪 **Testing Strategy**

### **Phase 1: Basic Fortran Integration**
```python
# Test simple XMV change
user_xmv = [63.0, 53.0, 24.0, 61.0, 100.0, 40.0, 38.0, 46.0, 47.0, 41.0, 18.0]
# Change XMV_5 from 22% to 100%
# Should see real pressure change, not synthetic overlay
```

### **Phase 2: Anomaly Detection**
```python
# Verify real changes trigger anomalies
# Without synthetic amplification
# Based on actual process physics
```

## 🚨 **Critical Success Indicators**
1. **No TEMAIN parameter errors** in logs
2. **Real process response** to XMV changes (not synthetic)
3. **Anomaly detection** triggered by authentic physics
4. **Consistent behavior** across multiple control changes

## 📊 **Current System Status**
- **Legacy System**: Functional but uses synthetic effects
- **Integration System**: Missing XMV support entirely
- **Fortran Code**: Parameter mismatch prevents real control
- **Anomaly Detection**: Tuned for synthetic effects (may need recalibration)

## 🎯 **Expected Outcome**
After fixes, XMV slider movements should cause **real Fortran-calculated process changes** that naturally trigger anomaly detection without artificial amplification.

---
**Next AI: Start with Step 1 - analyze the current Fortran TEMAIN function signature and understand the parameter mismatch.**
