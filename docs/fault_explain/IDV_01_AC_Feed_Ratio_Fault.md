# IDV(1): A/C Feed Ratio, B Composition Constant (Stream 4) - Step Fault

**Fault Type:** Step Disturbance  
**Fault Category:** Feed Composition Change  
**Severity:** Medium  
**Detection Difficulty:** Easy to Medium

## 🎯 **Fault Description**

### **What Happens:**
- **A/C ratio in Stream 4 changes** while B composition remains constant
- **Step change** occurs at fault introduction time
- **Permanent shift** in feed composition ratios

### **Physical Meaning:**
This fault simulates a **feed preparation system malfunction** where:
- Feed mixing ratios change unexpectedly
- Could be caused by flow meter calibration drift
- Upstream process changes affecting feed composition
- Feed tank contamination or mixing issues

## 🔧 **Implementation in TEP Code**

### **Location in `teprob.f`:**
```fortran
! Lines 1161-1169: Stream 4 composition definition
XST(1,4) = 0.4850 + TESUB8(1,TIME)  ! Component A
XST(2,4) = 0.0050 + TESUB8(2,TIME)  ! Component B  
XST(3,4) = 0.5100 + TESUB8(3,TIME)  ! Component C
```

### **Fault Implementation:**
```fortran
! TESUB8 subroutine handles IDV(1) effect
! When IDV(1) = 1:
XST(1,4) = 0.4850 + step_change_A    ! A composition changes
XST(2,4) = 0.0050 + 0.0              ! B composition constant  
XST(3,4) = 0.5100 + step_change_C    ! C composition changes
! Where: step_change_A + step_change_C = 0 (mass balance)
```

### **Variable Definitions:**
- **XST(i,j)**: Mole fraction of component i in stream j
- **TESUB8(i,TIME)**: Disturbance interpolation function
- **Stream 4**: A+C Feed stream (controlled by XMV(4))

## 📊 **Process Impact Analysis**

### **Direct Effects:**
1. **Feed Composition Change:**
   ```
   Normal: A=48.5%, B=0.5%, C=51.0% in Stream 4
   Fault:  A=X%,    B=0.5%, C=Y%    (X+Y+0.5=100%)
   ```

2. **Reactor Feed Composition:**
   ```fortran
   ! Total reactor feed composition changes due to:
   FCM(1,6) = FCM(1,1) + FCM(1,2) + FCM(1,3) + FCM(1,4) + FCM(1,5)
   !          D Feed    E Feed    A Feed    A+C Feed   Recycle
   ! FCM(1,4) = XST(1,4) * FTM(4) ← Changes due to fault
   ```

### **Secondary Effects:**
1. **Reaction Rate Changes:**
   ```fortran
   ! Reaction rates depend on component concentrations:
   RR(1) = k₁ × P_A^1.1544 × P_C^0.3735 × P_D  ! A+C+D→G
   RR(2) = k₂ × P_A^1.1544 × P_C^0.3735 × P_E  ! A+C+E→H
   ! Changed A/C ratio affects both main reactions
   ```

2. **Product Quality Impact:**
   - G/H product ratio changes
   - Overall conversion efficiency affected
   - Byproduct F formation may change

3. **Control System Response:**
   - PID controllers try to compensate
   - Valve positions adjust automatically
   - Process oscillations during transition

## 🎛️ **Affected Measurements**

### **Primary Measurements:**
| **XMEAS** | **Variable** | **Expected Change** | **Reason** |
|-----------|--------------|-------------------|------------|
| **XMEAS(23)** | Reactor Feed A% | ↑/↓ | Direct feed composition change |
| **XMEAS(25)** | Reactor Feed C% | ↓/↑ | Complementary to A change |
| **XMEAS(40)** | Product G% | Changes | Reaction stoichiometry affected |
| **XMEAS(41)** | Product H% | Changes | Reaction stoichiometry affected |

### **Secondary Measurements:**
| **XMEAS** | **Variable** | **Expected Change** | **Reason** |
|-----------|--------------|-------------------|------------|
| **XMEAS(9)** | Reactor Temperature | ↑/↓ | Heat generation changes |
| **XMEAS(7)** | Reactor Pressure | ↑/↓ | Reaction rate changes |
| **XMEAS(4)** | A+C Feed Flow | Oscillates | Controller compensation |
| **XMEAS(6)** | Reactor Feed Rate | Oscillates | Flow control response |

## 🔍 **Research Findings**

### **Detection Characteristics:**
- **Detection Rate**: 95-99% with PCA methods
- **Detection Time**: 15-30 minutes after fault introduction
- **False Alarm Rate**: Low (< 1%)

### **Key Research Papers:**
1. **Downs & Vogel (1993)**: Original TEP paper - classified as "easy to detect"
2. **Chiang et al. (2000)**: PCA-based detection shows excellent performance
3. **Russell et al. (2000)**: Multivariate statistical methods effective

### **Detection Methods Performance:**
| **Method** | **Detection Rate** | **Detection Time** | **Notes** |
|------------|-------------------|-------------------|-----------|
| **PCA** | 95-99% | 15-30 min | Excellent performance |
| **ICA** | 90-95% | 20-35 min | Good performance |
| **Neural Networks** | 85-95% | 10-25 min | Variable performance |
| **SVM** | 90-98% | 15-30 min | Robust detection |

## 🎯 **Diagnostic Strategy**

### **Root Cause Analysis:**
1. **Check Stream 4 composition** (XMEAS 23, 25)
2. **Monitor A+C feed flow** (XMEAS 4, XMV 4)
3. **Analyze product composition** (XMEAS 40, 41)
4. **Review feed preparation system**

### **Corrective Actions:**
1. **Immediate**: Adjust XMV(4) to compensate
2. **Short-term**: Recalibrate feed composition analyzers
3. **Long-term**: Investigate upstream feed preparation

## 🧪 **Simulation Notes**

### **Fault Magnitude:**
- Typical step change: ±5-10% in A/C ratio
- B composition remains at 0.5% (constant)
- Mass balance maintained: ΣXᵢ = 1.0

### **Time Characteristics:**
- **Fault introduction**: Immediate step change
- **Process response**: 15-60 minutes to new steady state
- **Control system**: Attempts compensation within 5-15 minutes

### **Interaction with Other Faults:**
- **Compatible with**: Most other IDV faults
- **Synergistic effects**: With IDV(2), IDV(8)
- **Masking potential**: Low - distinctive signature

## 📋 **Summary**

**IDV(1) represents a realistic industrial fault** where feed composition ratios change due to upstream process issues. It's **relatively easy to detect** using multivariate statistical methods and has **clear diagnostic signatures** in composition measurements. The fault demonstrates the **importance of feed quality control** in chemical processes and the **effectiveness of modern process monitoring techniques**.

**Key Takeaway**: This fault shows how small changes in feed composition can propagate through the entire process, affecting product quality and requiring sophisticated monitoring systems for early detection.
