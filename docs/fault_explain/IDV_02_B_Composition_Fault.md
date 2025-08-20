# IDV(2): B Composition, A/C Ratio Constant (Stream 4) - Step Fault

**Fault Type:** Step Disturbance  
**Fault Category:** Feed Composition Change  
**Severity:** Medium  
**Detection Difficulty:** Easy

## 🎯 **Fault Description**

### **What Happens:**
- **B composition in Stream 4 increases** while A/C ratio remains constant
- **Step change** occurs at fault introduction time
- **Permanent increase** in inert component B

### **Physical Meaning:**
This fault simulates **inert contamination** in the feed system:
- Upstream process introduces more inert B
- Feed purification system degradation
- Cross-contamination from other process streams
- Feed tank contamination with inert material

## 🔧 **Implementation in TEP Code**

### **Location in `teprob.f`:**
```fortran
! Line in TESUB8 subroutine (exact line varies):
XST(2,4) = TESUB8(2,TIME) + IDV(2)*0.005D0
```

### **Detailed Implementation:**
```fortran
! Normal Operation (IDV(2) = 0):
XST(1,4) = 0.4850 + TESUB8(1,TIME)  ! A composition (48.5%)
XST(2,4) = 0.0050 + 0.0              ! B composition (0.5%)  
XST(3,4) = 0.5100 + TESUB8(3,TIME)  ! C composition (51.0%)

! Fault Condition (IDV(2) = 1):
XST(1,4) = 0.4850 + TESUB8(1,TIME)  ! A composition (unchanged)
XST(2,4) = 0.0050 + 1*0.005 = 0.010 ! B composition (1.0% - doubled!)
XST(3,4) = 0.5100 + TESUB8(3,TIME)  ! C composition (unchanged)
! Note: A/C ratio = 0.485/0.510 = 0.951 (constant)
```

### **Variable Definitions:**
- **XST(2,4)**: Mole fraction of Component B in Stream 4 (A+C Feed)
- **IDV(2)**: B composition fault flag (0=normal, 1=fault)
- **0.005**: Step increase magnitude (0.5% absolute increase)
- **TESUB8(2,TIME)**: Baseline disturbance interpolation

## 📊 **Process Impact Analysis**

### **Direct Effects:**
1. **Inert Accumulation:**
   ```fortran
   ! Component B flow to reactor increases:
   FCM(2,4) = XST(2,4) * FTM(4)
            = 0.010 * FTM(4)  (doubled from 0.005)
   ! More inert B enters the system
   ```

2. **Reactor Composition Change:**
   ```fortran
   ! Total B in reactor feed:
   Total_B = FCM(2,1) + FCM(2,2) + FCM(2,3) + FCM(2,4) + FCM(2,5)
   !         D Feed    E Feed    A Feed    A+C Feed   Recycle
   !         0.0001    0.0       0.0001    DOUBLED    Accumulates
   ```

### **Secondary Effects:**
1. **Reaction Dilution:**
   ```fortran
   ! B is inert - doesn't participate in reactions:
   ! Reaction 1: A + C + D → G  (B dilutes reactants)
   ! Reaction 2: A + C + E → H  (B dilutes reactants)
   ! Higher B → Lower effective concentrations → Slower reactions
   ```

2. **Pressure Buildup:**
   ```fortran
   ! More inert material in system:
   ! B accumulates in recycle loop
   ! Higher total molar holdup → Higher pressure
   ! Purge system must work harder
   ```

3. **Separation Effects:**
   - B concentrates in vapor phase (light component)
   - Affects vapor-liquid equilibrium
   - Changes separation efficiency

## 🎛️ **Affected Measurements**

### **Primary Measurements:**
| **XMEAS** | **Variable** | **Expected Change** | **Timeline** |
|-----------|--------------|-------------------|--------------|
| **XMEAS(24)** | Reactor Feed B% | ↑↑ | Immediate (doubles) |
| **XMEAS(30)** | Purge B% | ↑ | 30-60 min (accumulation) |
| **XMEAS(4)** | A+C Feed Flow | May ↓ | Controller response |

### **Secondary Measurements:**
| **XMEAS** | **Variable** | **Expected Change** | **Reason** |
|-----------|--------------|-------------------|------------|
| **XMEAS(7)** | Reactor Pressure | ↑ | More material in system |
| **XMEAS(10)** | Purge Rate | ↑ | Controller increases purge |
| **XMEAS(20)** | Compressor Work | ↑ | Higher system pressure |
| **XMEAS(40)** | Product G% | ↓ | Dilution effect |
| **XMEAS(41)** | Product H% | ↓ | Dilution effect |

### **Control System Response:**
| **XMV** | **Variable** | **Expected Response** | **Controller Logic** |
|---------|--------------|---------------------|---------------------|
| **XMV(6)** | Purge Valve | ↑ | Increase purge to remove inerts |
| **XMV(4)** | A+C Feed Valve | ↓ | Reduce feed to control pressure |
| **XMV(5)** | Recycle Valve | ↓ | Reduce recycle to limit buildup |

## 🔍 **Research Findings**

### **Detection Characteristics:**
- **Detection Rate**: 95-99% (Excellent)
- **Detection Time**: 10-20 minutes
- **False Alarm Rate**: <2% (Very reliable)

### **Key Research Papers:**
1. **Downs & Vogel (1993)**: Classified as "easy to detect"
2. **Chiang et al. (2000)**: PCA shows excellent detection performance
3. **Kano et al. (2001)**: Used as benchmark for composition monitoring

### **Detection Methods Performance:**
| **Method** | **Detection Rate** | **Detection Time** | **Notes** |
|------------|-------------------|-------------------|-----------|
| **PCA** | 95-99% | 10-20 min | Excellent performance |
| **Composition Monitoring** | 99% | 5-10 min | Direct measurement |
| **Mass Balance** | 90-95% | 15-25 min | Indirect detection |
| **Neural Networks** | 85-95% | 15-30 min | Good performance |

## 🎯 **Diagnostic Strategy**

### **Root Cause Analysis:**
1. **Check Stream 4 B composition** (XMEAS 24) - Should double
2. **Monitor purge B content** (XMEAS 30) - Increases over time
3. **Analyze pressure trends** (XMEAS 7) - Gradual increase
4. **Review upstream feed preparation**

### **Corrective Actions:**
1. **Immediate**: Increase purge rate (XMV 6) to remove excess B
2. **Short-term**: Reduce A+C feed rate (XMV 4) to limit B input
3. **Medium-term**: Investigate feed purification system
4. **Long-term**: Install B removal/purification equipment

## 🧪 **Simulation Notes**

### **Fault Characteristics:**
- **Magnitude**: 0.5% absolute increase (100% relative increase)
- **Timing**: Immediate step change
- **Persistence**: Permanent until corrected

### **Process Response Timeline:**
```
t=0:     IDV(2) activated → XST(2,4) doubles
t=5min:  XMEAS(24) shows doubled B composition
t=15min: Reactor B content starts increasing
t=30min: Purge B content (XMEAS 30) increases
t=45min: Pressure effects become noticeable
t=60min: New steady state (if controllers compensate)
```

### **Mass Balance Impact:**
```
Normal B Input:  0.005 * FTM(4) = 0.005 * 915 = 4.6 mol/s
Fault B Input:   0.010 * FTM(4) = 0.010 * 915 = 9.2 mol/s
Additional B:    4.6 mol/s extra inert material!
```

## 🔧 **Engineering Insights**

### **Industrial Relevance:**
- **Very common problem**: Feed contamination with inerts
- **Economic impact**: Reduced production efficiency
- **Safety concern**: Pressure buildup from inert accumulation

### **Process Design Implications:**
1. **Purge system sizing** must handle inert variations
2. **Feed purification** systems need monitoring
3. **Pressure relief** systems must account for inert buildup

### **Detection Advantages:**
- **Clear signature**: B composition directly measurable
- **Fast detection**: Immediate change in feed analysis
- **Unambiguous**: B is inert, so increase is always abnormal

## 📋 **Summary**

**IDV(2) represents a realistic feed contamination scenario** where inert material (Component B) increases in the feed stream. It's **easy to detect** because:

1. **Direct measurement**: B composition is directly monitored
2. **Clear signature**: Inerts don't belong in the process
3. **Immediate effect**: Step change is obvious
4. **Cascading effects**: Affects multiple measurements consistently

**Key Insights:**
- **Inert accumulation** is a common industrial problem
- **Early detection** prevents pressure buildup and efficiency loss
- **Root cause** is usually upstream feed preparation issues
- **Correction requires** both immediate control actions and long-term fixes

**This fault demonstrates the importance of:**
- **Feed quality monitoring** in chemical processes
- **Inert management** in recycle systems  
- **Integrated control strategies** for composition disturbances

**IDV(2) is often used as a benchmark** for testing composition monitoring systems because of its clear signature and realistic industrial relevance.
