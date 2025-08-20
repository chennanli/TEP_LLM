# IDV(14): Reactor Cooling Water Valve Sticking

**Fault Type:** Valve Sticking  
**Fault Category:** Equipment Malfunction  
**Severity:** Medium to High  
**Detection Difficulty:** Medium

## 🎯 **Fault Description**

### **What Happens:**
- **Reactor cooling water valve becomes sticky/sluggish**
- **Valve doesn't respond to small control commands**
- **Only moves when command change exceeds threshold**

### **Physical Meaning:**
This fault simulates **mechanical valve problems**:
- Valve stem corrosion or fouling
- Actuator mechanical wear
- Packing gland friction increase
- Positioner calibration drift
- Pneumatic actuator problems

## 🔧 **Implementation in TEP Code**

### **Location in `teprob.f`:**
```fortran
! Line 1107: Valve sticking flag initialization
IVST(I) = 0        ! Normal operation

! IDV(14) activation:
IVST(10) = IDV(14)  ! Reactor cooling valve sticking flag

! Line 1106: Sticking threshold
VST(I) = 2.0D0     ! 2% threshold for all valves
```

### **Valve Sticking Logic:**
```fortran
! Valve position update logic (conceptual):
IF (ABS(VCV(10) - XMV(10)) > VST(10) * IVST(10)) THEN
    VCV(10) = XMV(10)    ! Valve moves to new position
ELSE
    VCV(10) = VCV(10)    ! Valve stays at current position
END IF

! Where:
! VCV(10) = Current valve position (actual)
! XMV(10) = Controller command (desired)  
! VST(10) = Sticking threshold = 2.0%
! IVST(10) = Sticking flag (0=normal, 1=sticking)
```

### **Detailed Implementation:**
```fortran
! Normal Operation (IDV(14) = 0):
IVST(10) = 0
! Valve responds to any command change:
IF (ABS(VCV(10) - XMV(10)) > 2.0 * 0) THEN  ! Always true
    VCV(10) = XMV(10)  ! Immediate response

! Fault Condition (IDV(14) = 1):
IVST(10) = 1  
! Valve only responds to changes > 2%:
IF (ABS(VCV(10) - XMV(10)) > 2.0 * 1) THEN  ! Only if change > 2%
    VCV(10) = XMV(10)  ! Valve finally moves
ELSE
    VCV(10) = VCV(10)  ! Valve stuck at current position
```

### **Variable Definitions:**
- **VCV(10)**: Actual reactor cooling valve position (%)
- **XMV(10)**: Controller command to cooling valve (%)
- **IVST(10)**: Valve sticking flag (0=normal, 1=sticking)
- **VST(10)**: Sticking threshold = 2.0% (fixed)

## 📊 **Process Impact Analysis**

### **Direct Effects:**
1. **Cooling Water Flow Control:**
   ```fortran
   ! Cooling water flow calculation:
   FWR = VPOS(10) * VRNG(10) / 100.0
       = VCV(10) * 1000.0 / 100.0  kscmh
   ! If valve sticks, FWR doesn't respond to XMV(10) commands
   ```

2. **Heat Removal Impact:**
   ```fortran
   ! Reactor heat removal:
   QUR = UAR * (TCR - TCWR) * FWR_factor
   ! If FWR is wrong due to sticking → QUR is wrong → TCR affected
   ```

### **Secondary Effects:**
1. **Temperature Control Problems:**
   ```fortran
   ! Reactor energy balance:
   d(ETR)/dt = Energy_In - Energy_Out + RH + QUR
   ! If QUR doesn't respond properly → Temperature oscillations
   ```

2. **Control Loop Instability:**
   - Temperature controller increases XMV(10)
   - Valve doesn't respond (change < 2%)
   - Temperature continues rising
   - Controller increases XMV(10) more
   - Eventually valve jumps (change > 2%)
   - Overcooling occurs → Temperature drops
   - **Result: Oscillatory behavior**

3. **Cascade Effects:**
   - Temperature affects reaction rates
   - Reaction rates affect pressure
   - Pressure affects other control loops

## 🎛️ **Affected Measurements**

### **Primary Measurements:**
| **XMEAS** | **Variable** | **Expected Change** | **Pattern** |
|-----------|--------------|-------------------|-------------|
| **XMEAS(9)** | Reactor Temperature | Oscillates | Poor control |
| **XMEAS(21)** | Cooling Water Outlet Temp | Oscillates | Follows reactor temp |
| **XMEAS(7)** | Reactor Pressure | Oscillates | Temperature-dependent |

### **Control Variables:**
| **XMV** | **Variable** | **Expected Pattern** | **Behavior** |
|---------|--------------|---------------------|--------------|
| **XMV(10)** | Cooling Water Valve | Oscillates | Controller hunting |

### **Diagnostic Signatures:**
1. **XMV(10) vs Actual Cooling**: Mismatch during small changes
2. **Temperature Response**: Delayed and oscillatory
3. **Control Performance**: Degraded temperature control

## 🔍 **Research Findings**

### **Detection Characteristics:**
- **Detection Rate**: 85-95% (Good but not excellent)
- **Detection Time**: 30-60 minutes (Slower than step faults)
- **False Alarm Rate**: 5-15% (Higher than step faults)

### **Key Research Papers:**
1. **Downs & Vogel (1993)**: Classified as "moderate difficulty"
2. **Chiang et al. (2000)**: PCA shows good but not perfect detection
3. **Kano et al. (2002)**: Valve sticking detection using MPC residuals

### **Detection Methods Performance:**
| **Method** | **Detection Rate** | **Detection Time** | **Notes** |
|------------|-------------------|-------------------|-----------|
| **PCA** | 85-90% | 45-60 min | Moderate performance |
| **Control Performance** | 90-95% | 30-45 min | Better for valve faults |
| **Valve Signature Analysis** | 95-98% | 15-30 min | Specialized method |
| **Neural Networks** | 80-90% | 30-60 min | Variable performance |

## 🎯 **Diagnostic Strategy**

### **Root Cause Analysis:**
1. **Monitor XMV(10) vs temperature response**
2. **Check for oscillatory patterns** in XMEAS(9)
3. **Analyze control performance metrics**
4. **Compare commanded vs actual valve position**

### **Advanced Diagnostics:**
```
Valve Sticking Indicators:
1. Control effort increases (XMV variance)
2. Process variable oscillations (XMEAS variance)  
3. Delayed response to setpoint changes
4. Step-like valve movements instead of smooth
```

### **Corrective Actions:**
1. **Immediate**: Switch to manual control if severe
2. **Short-term**: Increase controller deadband
3. **Maintenance**: Service valve actuator/positioner
4. **Long-term**: Replace valve if severely degraded

## 🧪 **Simulation Notes**

### **Fault Characteristics:**
- **Sticking threshold**: 2.0% (fixed in code)
- **Affects**: Only XMV(10) - Reactor cooling valve
- **Behavior**: Valve "jumps" when threshold exceeded

### **Typical Scenario:**
```
Normal: XMV(10) = 41% → VCV(10) = 41% (immediate)
Fault:  XMV(10) = 42% → VCV(10) = 41% (no change, <2%)
        XMV(10) = 43% → VCV(10) = 43% (jumps, >2% total)
```

### **Control System Response:**
1. **Temperature rises** → Controller increases XMV(10)
2. **Small increases ignored** → Temperature keeps rising
3. **Large increase triggers valve** → Overcooling
4. **Temperature drops** → Controller decreases XMV(10)
5. **Cycle repeats** → Oscillatory behavior

## 🔧 **Engineering Insights**

### **Real-World Relevance:**
- **Very common industrial problem** - valve sticking affects 15-20% of control valves
- **Maintenance indicator** - early sign of valve degradation
- **Economic impact** - poor control reduces efficiency

### **Prevention Strategies:**
1. **Regular valve maintenance** and calibration
2. **Valve signature testing** during shutdowns
3. **Control performance monitoring** systems
4. **Predictive maintenance** programs

### **Detection Improvements:**
1. **Valve travel monitoring** - compare command vs position
2. **Control performance indices** - track loop performance
3. **Spectral analysis** - detect oscillatory patterns
4. **Model-based methods** - expected vs actual response

## 📋 **Summary**

**IDV(14) represents a realistic and common industrial problem** where mechanical valve degradation affects process control. It's **moderately difficult to detect** because the symptoms develop gradually and can be confused with other control issues.

**Key Characteristics:**
- **Gradual degradation** rather than sudden failure
- **Oscillatory symptoms** in temperature control
- **Requires specialized detection methods** beyond simple statistical approaches
- **High industrial relevance** - very common maintenance issue

**This fault demonstrates the importance of:**
- **Control performance monitoring** in addition to process monitoring
- **Valve maintenance programs** for reliable operation
- **Advanced diagnostic techniques** for equipment health assessment

**Detection Challenge**: Unlike step faults with obvious signatures, valve sticking requires **pattern recognition** and **control system analysis** for reliable detection.
