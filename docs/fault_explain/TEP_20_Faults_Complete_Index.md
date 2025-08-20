# TEP 20 Faults - Complete Index and Overview

**Purpose:** Comprehensive reference for all 20 Tennessee Eastman Process faults  
**Source:** Original Downs & Vogel (1993) paper + Research literature  
**Last Updated:** August 19, 2025

## 🎯 **Fault Classification Overview**

### **By Fault Type:**
- **Step Disturbances (IDV 1-7)**: Immediate permanent changes
- **Random Variations (IDV 8-12)**: Continuous random walk disturbances  
- **Slow Drift (IDV 13)**: Gradual parameter changes
- **Valve Sticking (IDV 14-15, 19)**: Equipment mechanical problems
- **Unknown/Reserved (IDV 16-18, 20)**: Not implemented in original

### **By Detection Difficulty:**
- **Easy (IDV 1, 2, 6, 7)**: Clear signatures, >95% detection rate
- **Medium (IDV 3, 4, 5, 9, 10, 11, 12)**: Moderate signatures, 80-95% detection
- **Hard (IDV 13, 14, 15, 19)**: Subtle effects, 60-85% detection

## 📋 **Complete Fault Descriptions**

### **Step Disturbances (IDV 1-7)**

#### **IDV(1): A/C Feed Ratio, B Composition Constant (Stream 4)**
- **File:** `IDV_01_AC_Feed_Ratio_Fault.md`
- **Type:** Step change in feed composition
- **Impact:** Changes A/C ratio while keeping B constant
- **Detection:** Easy (95-99% rate)
- **Code:** `XST(1,4)` and `XST(3,4)` modified via TESUB8

#### **IDV(2): B Composition, A/C Ratio Constant (Stream 4)**  
- **Type:** Step change in B composition
- **Impact:** Increases B content while maintaining A/C ratio
- **Detection:** Easy (95-99% rate)
- **Code:** `XST(2,4) += IDV(2)*0.005` (Line in teprob.f)

#### **IDV(3): D Feed Temperature (Stream 2)**
- **Type:** Step increase in D feed temperature
- **Impact:** Higher inlet temperature affects reactor thermal balance
- **Detection:** Medium (85-95% rate)
- **Code:** `TST(1) += IDV(3)*5.0°C`

#### **IDV(4): Reactor Cooling Water Inlet Temperature**
- **Type:** Step increase in cooling water temperature  
- **Impact:** Reduced cooling capacity, higher reactor temperature
- **Detection:** Medium (80-90% rate)
- **Code:** `TCWR += IDV(4)*5.0°C`

#### **IDV(5): Condenser Cooling Water Inlet Temperature**
- **Type:** Step increase in condenser cooling water temperature
- **Impact:** Reduced condensation, affects separation efficiency
- **Detection:** Medium (75-85% rate)  
- **Code:** `TCWS += IDV(5)*5.0°C`

#### **IDV(6): A Feed Loss (Stream 1)**
- **File:** `IDV_06_A_Feed_Loss.md`
- **Type:** Complete loss of A feed
- **Impact:** Catastrophic - eliminates primary reactant
- **Detection:** Very Easy (99-100% rate)
- **Code:** `FTM(3) *= (1.0-IDV(6))` → Complete loss when IDV(6)=1

#### **IDV(7): C Header Pressure Loss (Stream 4)**
- **Type:** Reduced availability of A+C feed
- **Impact:** 20% reduction in Stream 4 flow capacity
- **Detection:** Easy (90-95% rate)
- **Code:** `FTM(4) *= (1.0-IDV(7)*0.2)`

### **Random Variations (IDV 8-12)**

#### **IDV(8): A, B, C Feed Composition Random Variation (Stream 4)**
- **Type:** Random walk in feed composition
- **Impact:** Continuous composition fluctuations
- **Detection:** Medium (70-85% rate)
- **Code:** Random walk process in TESUB8

#### **IDV(9): D Feed Temperature Random Variation (Stream 2)**
- **Type:** Random walk in D feed temperature
- **Impact:** Thermal disturbances to reactor
- **Detection:** Medium (65-80% rate)
- **Code:** Random walk in TST(1)

#### **IDV(10): C Feed Temperature Random Variation (Stream 4)**
- **Type:** Random walk in A+C feed temperature
- **Impact:** Thermal disturbances, affects reaction rates
- **Detection:** Medium (60-75% rate)
- **Code:** Random walk in TST(4)

#### **IDV(11): Reactor Cooling Water Inlet Temperature Random Variation**
- **Type:** Random walk in cooling water temperature
- **Impact:** Continuous cooling capacity variations
- **Detection:** Hard (50-70% rate)
- **Code:** Random walk in TCWR

#### **IDV(12): Condenser Cooling Water Inlet Temperature Random Variation**
- **Type:** Random walk in condenser cooling temperature
- **Impact:** Separation efficiency variations
- **Detection:** Hard (45-65% rate)
- **Code:** Random walk in TCWS

### **Slow Drift (IDV 13)**

#### **IDV(13): Reaction Kinetics Slow Drift**
- **Type:** Gradual catalyst deactivation
- **Impact:** Slowly decreasing reaction rates over time
- **Detection:** Very Hard (40-60% rate)
- **Code:** Slow drift in reaction rate constants

### **Valve Sticking (IDV 14-15, 19)**

#### **IDV(14): Reactor Cooling Water Valve Sticking**
- **File:** `IDV_14_Reactor_Cooling_Valve_Sticking.md`
- **Type:** XMV(10) becomes sticky (2% threshold)
- **Impact:** Poor temperature control, oscillations
- **Detection:** Medium (85-90% rate)
- **Code:** `IVST(10) = IDV(14)`, VST(10) = 2.0%

#### **IDV(15): Condenser Cooling Water Valve Sticking**
- **Type:** XMV(11) becomes sticky (2% threshold)
- **Impact:** Poor condenser control, affects separation
- **Detection:** Medium (80-85% rate)
- **Code:** `IVST(11) = IDV(15)`, VST(11) = 2.0%

#### **IDV(19): Multiple Valve Sticking**
- **Type:** Four valves stick simultaneously
- **Impact:** Multiple control loops affected
- **Detection:** Medium (75-85% rate)
- **Code:** `IVST(5,7,8,9) = IDV(19)` - Recycle, separator, stripper valves

### **Unknown/Reserved (IDV 16-18, 20)**

#### **IDV(16-18, 20): Unknown Disturbances**
- **Status:** Not implemented in original TEP
- **Purpose:** Reserved for future fault types
- **Research:** Some papers define custom faults for these
- **Code:** No implementation in original teprob.f

## 🔍 **Research Summary by Fault**

### **Detection Performance Ranking:**
| **Rank** | **IDV** | **Fault** | **Detection Rate** | **Difficulty** |
|----------|---------|-----------|-------------------|----------------|
| 1 | IDV(6) | A Feed Loss | 99-100% | Very Easy |
| 2 | IDV(1) | A/C Feed Ratio | 95-99% | Easy |
| 3 | IDV(2) | B Composition | 95-99% | Easy |
| 4 | IDV(7) | C Header Pressure | 90-95% | Easy |
| 5 | IDV(4) | Reactor Cooling Temp | 80-90% | Medium |
| 6 | IDV(14) | Cooling Valve Sticking | 85-90% | Medium |
| 7 | IDV(3) | D Feed Temperature | 85-95% | Medium |
| 8 | IDV(15) | Condenser Valve Sticking | 80-85% | Medium |
| 9 | IDV(5) | Condenser Cooling Temp | 75-85% | Medium |
| 10 | IDV(19) | Multiple Valve Sticking | 75-85% | Medium |
| 11 | IDV(8) | Feed Composition Random | 70-85% | Medium |
| 12 | IDV(9) | D Feed Temp Random | 65-80% | Medium |
| 13 | IDV(10) | C Feed Temp Random | 60-75% | Medium |
| 14 | IDV(11) | Cooling Water Random | 50-70% | Hard |
| 15 | IDV(13) | Kinetics Drift | 40-60% | Very Hard |
| 16 | IDV(12) | Condenser Random | 45-65% | Hard |

### **Key Research Papers:**
1. **Downs & Vogel (1993)**: Original TEP paper with fault definitions
2. **Chiang et al. (2000)**: Comprehensive PCA-based detection study
3. **Russell et al. (2000)**: Multivariate statistical process monitoring
4. **Kano et al. (2002)**: Valve sticking detection methods
5. **Yin et al. (2012)**: Comprehensive review of TEP fault detection

## 🎛️ **Control System Impact**

### **Most Disruptive Faults:**
1. **IDV(6)**: Complete feed loss - catastrophic
2. **IDV(1,2)**: Feed composition - affects product quality
3. **IDV(14,15,19)**: Valve sticking - control system degradation

### **Hardest to Detect:**
1. **IDV(13)**: Slow drift - gradual changes
2. **IDV(11,12)**: Random cooling variations - masked by noise
3. **IDV(10)**: Random feed temperature - small effects

### **Best for Benchmarking:**
1. **IDV(1)**: Clear signature, well-studied
2. **IDV(6)**: Obvious fault, tests basic detection
3. **IDV(14)**: Realistic industrial problem

## 🎯 **Demo Scenarios for Anomaly Detection**

### **Recommended Demo Sequence:**

#### **Scenario 1: Subtle but Detectable (IDV 1)**
- **Change:** A/C feed ratio shift
- **Measurements:** Still within normal ranges initially
- **Anomaly Detection:** Triggers within 15-30 minutes
- **LLM Diagnosis:** "Feed composition imbalance detected"

#### **Scenario 2: Equipment Degradation (IDV 14)**
- **Change:** Cooling valve becomes sticky
- **Measurements:** Temperature oscillations develop
- **Anomaly Detection:** Detects control performance degradation
- **LLM Diagnosis:** "Valve sticking suspected - temperature control issues"

#### **Scenario 3: Feed Supply Issue (IDV 6)**
- **Change:** A feed loss
- **Measurements:** Immediate flow drop
- **Anomaly Detection:** Immediate alarm
- **LLM Diagnosis:** "Critical feed supply failure - immediate action required"

## 📁 **File Organization**

### **Detailed Fault Files:**
- `IDV_01_AC_Feed_Ratio_Fault.md` ✅ Created
- `IDV_06_A_Feed_Loss.md` ✅ Created  
- `IDV_14_Reactor_Cooling_Valve_Sticking.md` ✅ Created
- `IDV_02_B_Composition_Fault.md` (To be created)
- `IDV_03_D_Feed_Temperature.md` (To be created)
- ... (Additional files as needed)

### **Reference Files:**
- `TEP_Parameter_Master_Reference.md` ✅ Created
- `TEP_20_Faults_Complete_Index.md` ✅ This file

## 📋 **Usage Notes**

### **For Researchers:**
- Use this index to select appropriate faults for studies
- Consider detection difficulty when designing experiments
- Reference original papers for detailed fault characteristics

### **For Operators:**
- Focus on high-impact faults (IDV 1,2,6,14) for training
- Understand fault signatures for faster diagnosis
- Practice with realistic scenarios (valve sticking, feed issues)

### **For System Developers:**
- Test detection algorithms across difficulty spectrum
- Use easy faults (IDV 1,6) for algorithm validation
- Challenge systems with hard faults (IDV 11,13) for robustness

**This index provides comprehensive coverage of all TEP faults with practical guidance for research, operations, and system development applications.**
