# IDV(6): A Feed Loss (Stream 1) - Step Fault

**Fault Type:** Step Disturbance  
**Fault Category:** Feed Loss/Equipment Failure  
**Severity:** High  
**Detection Difficulty:** Easy

## 🎯 **Fault Description**

### **What Happens:**
- **Complete or partial loss of A Feed** (Stream 1)
- **Immediate step reduction** in feed flow
- **Permanent feed supply disruption**

### **Physical Meaning:**
This fault simulates a **critical feed supply failure**:
- Feed pump failure or shutdown
- Pipeline blockage or rupture  
- Upstream supply interruption
- Feed tank empty condition
- Valve closure or mechanical failure

## 🔧 **Implementation in TEP Code**

### **Location in `teprob.f`:**
```fortran
! Line 567: A Feed flow calculation with fault effect
FTM(3) = VPOS(3) * (1.0 - IDV(6)) * VRNG(3) / 100.0
```

### **Detailed Implementation:**
```fortran
! Normal Operation (IDV(6) = 0):
FTM(3) = VPOS(3) * (1.0 - 0) * VRNG(3) / 100.0
       = Valve_Position% * 1.0 * 100.0 kscmh / 100
       = 25% * 100 kscmh / 100 = 25 kscmh

! Fault Condition (IDV(6) = 1):  
FTM(3) = VPOS(3) * (1.0 - 1) * VRNG(3) / 100.0
       = Valve_Position% * 0.0 * 100.0 kscmh / 100
       = 25% * 0 kscmh / 100 = 0 kscmh  ← COMPLETE LOSS!
```

### **Variable Definitions:**
- **FTM(3)**: Actual A Feed flow rate (kscmh)
- **VPOS(3)**: A Feed valve position (%) - XMV(3) command
- **IDV(6)**: A Feed loss fault flag (0=normal, 1=fault)
- **VRNG(3)**: A Feed maximum flow = 100.0 kscmh

## 📊 **Process Impact Analysis**

### **Direct Effects:**
1. **Feed Flow Loss:**
   ```fortran
   ! Component A flow to reactor:
   FCM(1,3) = XST(1,3) * FTM(3)
            = 0.9999 * 0.0 = 0.0 mol/s  ← No A from Stream 1
   ```

2. **Total A Feed Reduction:**
   ```fortran
   ! Total A to reactor from all sources:
   Total_A = FCM(1,1) + FCM(1,2) + FCM(1,3) + FCM(1,4) + FCM(1,5)
   !         D Feed    E Feed    A Feed    A+C Feed   Recycle
   !         0.0       0.0       0.0       A+C_A      Recycle_A
   ! Stream 1 contribution = 0 (lost!)
   ```

### **Secondary Effects:**
1. **Reaction Rate Impact:**
   ```fortran
   ! Both main reactions need Component A:
   RR(1) = k₁ × P_A^1.1544 × P_C^0.3735 × P_D  ! A+C+D→G
   RR(2) = k₂ × P_A^1.1544 × P_C^0.3735 × P_E  ! A+C+E→H
   ! Reduced P_A → Reduced reaction rates → Lower production
   ```

2. **Mass Balance Disruption:**
   ```fortran
   ! Reactor mass balance affected:
   d(UCVR(1))/dt = FCM(1,7) - FCM(1,8) + CRXR(1)
   !               Feed_In   Vapor_Out   Reaction
   ! Reduced Feed_In → Accumulation decreases
   ```

3. **Control System Response:**
   - Controllers detect low reactor feed
   - Attempt to increase other feeds (XMV 1,2,4)
   - Recycle valve (XMV 5) may open more
   - Production rate controllers activate

## 🎛️ **Affected Measurements**

### **Primary Measurements:**
| **XMEAS** | **Variable** | **Expected Change** | **Magnitude** |
|-----------|--------------|-------------------|---------------|
| **XMEAS(1)** | A Feed Flow | ↓↓↓ | Drops to ~0 |
| **XMEAS(6)** | Reactor Feed Rate | ↓↓ | Significant drop |
| **XMEAS(23)** | Reactor Feed A% | ↓↓ | Major reduction |
| **XMEAS(29)** | Purge A% | ↓↓ | Reduced over time |

### **Secondary Measurements:**
| **XMEAS** | **Variable** | **Expected Change** | **Reason** |
|-----------|--------------|-------------------|------------|
| **XMEAS(9)** | Reactor Temperature | ↓ | Lower reaction rates |
| **XMEAS(7)** | Reactor Pressure | ↓ | Reduced feed, lower generation |
| **XMEAS(8)** | Reactor Level | ↓ | Less liquid accumulation |
| **XMEAS(40)** | Product G% | ↓ | A-limited reactions |
| **XMEAS(41)** | Product H% | ↓ | A-limited reactions |
| **XMEAS(20)** | Compressor Work | ↑ | Higher recycle ratio |

### **Control Response:**
| **XMV** | **Variable** | **Expected Change** | **Controller Action** |
|---------|--------------|-------------------|---------------------|
| **XMV(3)** | A Feed Valve | ↑ | Tries to increase (futile) |
| **XMV(4)** | A+C Feed Valve | ↑ | Compensate with A+C feed |
| **XMV(5)** | Recycle Valve | ↑ | Increase A recycle |
| **XMV(1,2)** | D,E Feed Valves | ↓ | Reduce to maintain ratios |

## 🔍 **Research Findings**

### **Detection Characteristics:**
- **Detection Rate**: 99-100% (Excellent)
- **Detection Time**: 3-10 minutes (Very fast)
- **False Alarm Rate**: Near 0% (Very reliable)

### **Key Research Papers:**
1. **Downs & Vogel (1993)**: Classified as "easy to detect" - obvious signature
2. **Chiang et al. (2000)**: PCA detects within 1-2 samples
3. **Lyman & Georgakis (1995)**: Used as benchmark for detection methods

### **Detection Methods Performance:**
| **Method** | **Detection Rate** | **Detection Time** | **Notes** |
|------------|-------------------|-------------------|-----------|
| **PCA** | 99-100% | 3-6 min | Immediate detection |
| **Univariate** | 100% | 1-3 min | XMEAS(1) drops to zero |
| **Neural Networks** | 95-100% | 5-10 min | Excellent performance |
| **Process Knowledge** | 100% | Immediate | Obvious from flow measurement |

## 🎯 **Diagnostic Strategy**

### **Root Cause Analysis:**
1. **Check A Feed flow** (XMEAS 1) - Should be near zero
2. **Verify valve position** (XMV 3) - May be high but no flow
3. **Monitor reactor composition** (XMEAS 23) - A% decreasing
4. **Check upstream A supply system**

### **Corrective Actions:**
1. **Emergency**: Switch to backup A feed supply
2. **Immediate**: Increase A+C feed (XMV 4) to compensate
3. **Short-term**: Repair A feed system (pump, pipeline)
4. **Long-term**: Install redundant A feed systems

## 🧪 **Simulation Notes**

### **Fault Characteristics:**
- **Fault magnitude**: Complete loss (100% reduction)
- **Fault timing**: Immediate step change
- **Recovery**: Not modeled (permanent fault)

### **Process Response Timeline:**
```
t=0:     IDV(6) activated → FTM(3) = 0
t=3min:  XMEAS(1) drops to zero
t=5min:  Reactor A composition starts declining  
t=10min: Controllers start compensating
t=30min: New steady state (if possible)
```

### **Interaction with Other Faults:**
- **Synergistic**: With IDV(7) - C header pressure loss
- **Compensated by**: Higher XMV(4) - A+C feed increase
- **Masked by**: None - too obvious to mask

## 🚨 **Safety and Operational Implications**

### **Process Safety:**
- **Production loss**: Significant reduction in G,H products
- **Quality impact**: Product composition changes
- **Economic impact**: High - lost production + repair costs

### **Operational Response:**
1. **Immediate shutdown** of affected section
2. **Switch to manual control** for critical loops
3. **Activate emergency procedures**
4. **Notify maintenance team**

## 📋 **Summary**

**IDV(6) represents a catastrophic feed supply failure** that is **extremely easy to detect** but **difficult to compensate**. It demonstrates the **vulnerability of chemical processes** to single-point failures and the **importance of redundant feed systems**. 

**Key Insights:**
- **Detection is trivial** - flow measurement goes to zero
- **Impact is severe** - affects entire process operation  
- **Recovery requires** physical repair or backup systems
- **Prevention is critical** - redundancy and maintenance

**This fault is often used as a benchmark** for testing detection algorithms because of its clear signature and immediate impact. It represents **real industrial scenarios** where equipment failures can cause complete process disruptions.
