# TEP Fortran Speed Acceleration - Expert Handoff

## 🎯 MISSION
Modify TEP (Tennessee Eastman Process) Fortran simulation to run 5-10x faster while maintaining correct physics values.

## 📊 CURRENT STATUS
- ❌ **FAILED**: Multiple attempts to speed up TEP simulation
- ✅ **WORKING**: Original TEP simulation produces correct values
- ✅ **BACKUP**: Original files safely backed up
- ❌ **ISSUE**: Speed modifications corrupt physics values

## 🔍 PROBLEM ANALYSIS

### What User Wants:
```
20-minute chemical reaction → 2-4 minute reaction (5-10x faster)
Like fast-forwarding a video of the chemical process
```

### What I Tried (FAILED):
1. **Scaling DELTAT**: `DELTAT = (1.0 / SPEED_FACTOR) / 3600.0`
2. **Scaling controller timing**: `MOD(I, INT(180/SPEED_FACTOR))`
3. **Scaling total steps**: `TOTAL_STEPS = NPTS * SPEED_FACTOR`

### Results:
- **Original TEP**: Pressure=2703.9 kPa, Temp=120.4°C ✅
- **Speed-modified**: Pressure=1512.4 kPa, Temp=177.0°C ❌

## 📁 CRITICAL FILES

### Location: `/Users/chennanli/Desktop/LLM_Project/TE/legacy/external_repos/tep2py-master/src/tep/`

1. **temain_mod_ORIGINAL_BACKUP.f** - SAFE ORIGINAL (DO NOT MODIFY)
2. **teprob_ORIGINAL_BACKUP.f** - SAFE ORIGINAL (DO NOT MODIFY)  
3. **temain_mod.f** - CURRENT (contains my failed attempts)
4. **teprob.f** - Physics equations (may need modification)

## 🎯 EXPERT TASK

### PRIMARY OBJECTIVE:
Create a new function `TEMAIN_ACCELERATED` that:
- Takes `SPEED_FACTOR` parameter (1.0 = normal, 5.0 = 5x faster)
- Produces IDENTICAL results to original when SPEED_FACTOR=1.0
- Runs 5x faster when SPEED_FACTOR=5.0 with same final values

### TECHNICAL REQUIREMENTS:

#### 1. Time Scale Synchronization:
```fortran
! All timing must scale together:
DELTAT = (1.0 / SPEED_FACTOR) / 3600.0
Controller_Interval = INT(ORIGINAL_INTERVAL / SPEED_FACTOR)
Sample_Interval = INT(180 / SPEED_FACTOR)
```

#### 2. Numerical Stability:
- Smaller DELTAT may cause integration instability
- May need adaptive timestep or different integration method
- Check `INTGTR` subroutine for stability issues

#### 3. Physics Preservation:
- Chemical time constants may need scaling
- Process dynamics must remain realistic
- Control loops must maintain stability

### SUCCESS CRITERIA:
```fortran
! Test 1: Baseline
SPEED_FACTOR = 1.0 → IDENTICAL to original TEMAIN

! Test 2: Acceleration  
SPEED_FACTOR = 5.0 → Same final values:
- Reactor Pressure: ~2700 kPa
- Reactor Temperature: ~120°C
- A Feed: ~0.25
- D Feed: ~3600
```

## 🚨 KNOWN ISSUES TO SOLVE

### 1. Controller Timing Conflicts:
```fortran
! Original timing intervals:
MOD(I,3)    - Every 3 seconds
MOD(I,360)  - Every 6 minutes  
MOD(I,900)  - Every 15 minutes
MOD(I,180)  - Every 3 minutes (sampling)

! These must scale proportionally with SPEED_FACTOR
```

### 2. Integration Stability:
- Smaller DELTAT may cause numerical oscillations
- Chemical equations may have stiff components
- May need implicit integration or smaller timesteps

### 3. Process Time Constants:
- TEP has time constants from seconds to hours
- All must scale consistently
- Control tuning may need adjustment

## 🛠️ IMPLEMENTATION APPROACH

### Step 1: Copy Original Function
```fortran
! Create TEMAIN_ACCELERATED based on original TEMAIN
! Start with SPEED_FACTOR=1.0 and verify identical results
```

### Step 2: Scale Time Components
```fortran
! Scale DELTAT, controller intervals, sampling intervals
! Test each component individually
```

### Step 3: Debug Physics Issues
```fortran
! If values diverge, check:
! - Integration stability in INTGTR
! - Time constants in physics equations
! - Controller stability
```

## 🧪 TESTING PROTOCOL

### Test Environment:
```python
# Location: /Users/chennanli/Desktop/LLM_Project/TE/legacy/external_repos/tep2py-master/
# Virtual env: tep_env
# Compile: python -m numpy.f2py -c temain_mod-smart.pyf src/tep/temain_mod.f src/tep/teprob.f
```

### Test Code:
```python
import numpy as np
import temain_mod

idata = np.zeros((3, 20))  # No faults

# Test original
result_orig = temain_mod.temain(540, 3, idata, 1)

# Test accelerated
result_accel = temain_mod.temain_accelerated(540, 3, idata, 1, 1.0)

# Compare values
print("Pressure diff:", abs(result_orig[-1,6] - result_accel[-1,6]))
print("Temp diff:", abs(result_orig[-1,8] - result_accel[-1,8]))
```

## 🎯 DELIVERABLE

Create working `TEMAIN_ACCELERATED` function that passes all tests and enables true time acceleration of TEP simulation.

## 📞 CONTACT INFO

User expects the next AI to:
1. Read this document
2. Understand the failed attempts  
3. Implement correct solution
4. Test thoroughly
5. Deliver working accelerated simulation

## 🔬 DETAILED TECHNICAL ANALYSIS

### Root Cause of Failures:
1. **Integration Method**: TEP uses explicit Euler integration which becomes unstable with smaller timesteps
2. **Time Constant Mismatch**: Chemical time constants not scaled with DELTAT
3. **Controller Tuning**: PID controllers tuned for specific timesteps
4. **Stiff Equations**: Chemical reactions have vastly different time scales

### Potential Solutions:
1. **Implicit Integration**: Replace explicit Euler with implicit method
2. **Adaptive Timestep**: Use variable DELTAT based on system dynamics
3. **Time Constant Scaling**: Scale all time constants in physics equations
4. **Controller Retuning**: Adjust PID gains for new timestep

### Critical Code Locations:
- `INTGTR` subroutine: Integration method
- `TEFUNC` subroutine: Physics equations
- `CONTRL*` subroutines: Controller logic
- `DELTAT` variable: Global timestep

### Previous Attempts Summary:
- **Attempt 1**: Scale DELTAT only → Values corrupted
- **Attempt 2**: Scale DELTAT + controller timing → Still wrong
- **Attempt 3**: Scale DELTAT + keep original timing → Still wrong
- **Attempt 4**: Keep DELTAT, scale sampling only → Not true acceleration

**File to give next AI**: `docs/TEP_SPEED_ACCELERATION_HANDOFF.md` (this file)
