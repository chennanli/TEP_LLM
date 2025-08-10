# TEP2PY Input/Output Documentation

## 🎯 **Real TEP Input Structure**

### **TEP2PY Function Call:**
```python
from tep2py import tep2py
import numpy as np

# Create disturbance matrix
idata = np.zeros((time_steps, 20))  # 20 disturbance variables (IDV)

# Run simulation
tep = tep2py(idata)
tep.simulate()
data = tep.process_data  # 52 output variables
```

## 📊 **20 Real TEP Inputs (IDV - Independent Disturbance Variables)**

| IDV | Input Name | Description | Normal Value | Units | Effect When Changed |
|-----|------------|-------------|--------------|-------|-------------------|
| **IDV(1)** | A/C Feed Ratio | Feed composition ratio | 0.0 | - | Changes reactor temperature/pressure |
| **IDV(2)** | B Composition | B component in feed | 0.0 | - | Affects reaction rates |
| **IDV(3)** | D Feed Temperature | Feed stream temperature | 0.0 | °C | Changes reactor energy balance |
| **IDV(4)** | Reactor Cooling Water Inlet Temp | Cooling water temperature | 0.0 | °C | Affects reactor temperature control |
| **IDV(5)** | Condenser Cooling Water Inlet Temp | Condenser cooling | 0.0 | °C | Affects separation efficiency |
| **IDV(6)** | A Feed Loss | Feed flow reduction | 0.0 | - | Reduces production rate |
| **IDV(7)** | C Header Pressure Loss | Pressure drop | 0.0 | kPa | Affects flow rates |
| **IDV(8)** | A, B, C Feed Composition | Multi-component change | 0.0 | - | Complex reaction effects |
| **IDV(9)** | D Feed Temperature | Alternative D temp change | 0.0 | °C | Energy balance disturbance |
| **IDV(10)** | C Feed Temperature | C stream temperature | 0.0 | °C | Feed preheating effect |
| **IDV(11)** | Reactor Cooling Water Inlet Temp | Alternative cooling fault | 0.0 | °C | Temperature control issue |
| **IDV(12)** | Condenser Cooling Water Inlet Temp | Alternative condenser fault | 0.0 | °C | Separation problem |
| **IDV(13)** | Reaction Kinetics | Catalyst deactivation | 0.0 | - | Changes reaction rates |
| **IDV(14)** | Reactor Cooling Water Valve | Valve sticking | 0.0 | - | Cooling control failure |
| **IDV(15)** | Condenser Cooling Water Valve | Valve sticking | 0.0 | - | Condenser control failure |
| **IDV(16)** | Unknown | Reserved/unused | 0.0 | - | - |
| **IDV(17)** | Unknown | Reserved/unused | 0.0 | - | - |
| **IDV(18)** | Unknown | Reserved/unused | 0.0 | - | - |
| **IDV(19)** | Unknown | Reserved/unused | 0.0 | - | - |
| **IDV(20)** | Unknown | Reserved/unused | 0.0 | - | - |

## 🔧 **How TEP2PY Works:**

### **1. Input Matrix Structure:**
```python
# idata shape: (time_steps, 20)
# Each row = one time step (3 minutes in TEP time)
# Each column = one IDV disturbance variable

# Example: A/C Feed Ratio fault starting at step 10
idata = np.zeros((50, 20))  # 50 time steps
idata[10:, 0] = 1.5         # IDV(1) = 1.5 starting at step 10
```

### **2. Fortran Simulation Call:**
```python
tep = tep2py(idata)  # Initialize with disturbance matrix
tep.simulate()       # Run Fortran TEPROB.F simulation
data = tep.process_data  # Extract results DataFrame
```

### **3. Internal Fortran Process:**
```fortran
! In TEPROB.F:
! 1. Read IDV disturbances from idata matrix
! 2. Apply disturbances to process equations
! 3. Solve 50 differential equations (mass/energy balances)
! 4. Calculate 52 output variables (XMEAS + XMV)
! 5. Return time series data
```

## 📊 **52 TEP Outputs (What You Monitor)**

### **41 Measured Variables (XMEAS):**
| Variable | Description | Units | Normal Range | Fault Indicators |
|----------|-------------|-------|--------------|------------------|
| **XMEAS(1)** | A Feed Flow | kg/h | 0.5-1.0 | Feed system issues |
| **XMEAS(2)** | D Feed Flow | kg/h | 3.0-4.0 | Feed system issues |
| **XMEAS(3)** | E Feed Flow | kg/h | 4.0-5.0 | Feed system issues |
| **XMEAS(4)** | A+C Feed Flow | kg/h | 7.0-9.0 | Combined feed issues |
| **XMEAS(5)** | Recycle Flow | kg/h | 25-35 | Recycle system |
| **XMEAS(6)** | Reactor Feed Rate | kg/h | 40-50 | Overall feed rate |
| **XMEAS(7)** | Reactor Pressure | kPa | 2700-2800 | **KEY: Pressure control** |
| **XMEAS(8)** | Reactor Level | % | 65-75 | **KEY: Inventory control** |
| **XMEAS(9)** | Reactor Temperature | °C | 120-125 | **KEY: Temperature control** |
| **XMEAS(10)** | Purge Rate | kg/h | 0.1-0.3 | Purge system |
| **XMEAS(11)** | Product Sep Temp | °C | 80-90 | **KEY: Separation** |
| **XMEAS(12)** | Product Sep Level | % | 40-60 | **KEY: Product inventory** |
| **XMEAS(13)** | Product Sep Pressure | kPa | 2600-2700 | Separation pressure |
| **XMEAS(14)** | Product Sep Underflow | kg/h | 25-35 | Product flow |
| **XMEAS(15)** | Stripper Level | % | 45-55 | Stripper inventory |
| **XMEAS(16)** | Stripper Pressure | kPa | 3100-3200 | Stripper operation |
| **XMEAS(17)** | Stripper Underflow | kg/h | 22-28 | Stripper product |
| **XMEAS(18)** | Stripper Temperature | °C | 65-75 | Stripper thermal |
| **XMEAS(19)** | Stripper Steam Flow | kg/h | 230-250 | Steam system |
| **XMEAS(20)** | Compressor Work | kW | 340-360 | Compressor load |
| **XMEAS(21)** | Reactor Cooling Water Outlet Temp | °C | 35-45 | Cooling system |
| **XMEAS(22)** | Separator Cooling Water Outlet Temp | °C | 40-50 | Cooling system |
| **XMEAS(23-41)** | Component Compositions | mol% | Varies | Composition analysis |

### **11 Manipulated Variables (XMV):**
| Variable | Description | Units | Normal Range | Control Purpose |
|----------|-------------|-------|--------------|-----------------|
| **XMV(1)** | D Feed Flow Valve | % | 60-70 | Feed rate control |
| **XMV(2)** | E Feed Flow Valve | % | 50-60 | Feed rate control |
| **XMV(3)** | A Feed Flow Valve | % | 20-30 | Feed composition |
| **XMV(4)** | A+C Feed Flow Valve | % | 60-70 | Total feed control |
| **XMV(5)** | Compressor Recycle Valve | % | 20-30 | Pressure control |
| **XMV(6)** | Purge Valve | % | 40-50 | Composition control |
| **XMV(7)** | Separator Pot Liquid Flow Valve | % | 35-45 | Level control |
| **XMV(8)** | Stripper Liquid Product Flow Valve | % | 45-55 | Level control |
| **XMV(9)** | Stripper Steam Valve | % | 45-55 | Temperature control |
| **XMV(10)** | Reactor Cooling Water Flow Valve | % | 40-50 | Temperature control |
| **XMV(11)** | Condenser Cooling Water Flow Valve | % | 35-45 | Temperature control |

## 🎯 **Correct Fault Detection Approach:**

### **❌ WRONG (Current Approach):**
```python
# Direct fault injection
fault_type = 5  # "I'm telling you it's fault type 5"
intensity = 1.5  # "Make it severe"
```

### **✅ CORRECT (Physics-Based Approach):**
```python
# 1. Change process inputs (IDV)
idata = np.zeros((100, 20))
idata[50:, 0] = 1.2    # Change A/C feed ratio at step 50
idata[50:, 3] = 5.0    # Change reactor cooling water temp

# 2. Run real physics simulation
tep = tep2py(idata)
tep.simulate()
data = tep.process_data

# 3. Monitor sensor readings
temperature = data['XMEAS(9)']  # Reactor temperature
pressure = data['XMEAS(7)']     # Reactor pressure
level = data['XMEAS(8)']        # Reactor level

# 4. PCA detects anomaly from sensor patterns
anomaly_score = pca_model.detect_anomaly(sensor_data)

# 5. LLM diagnoses: "Based on temperature spike + pressure rise + 
#    timing, this appears to be an A/C feed ratio disturbance"
```

## 🔍 **Intensity Meaning:**

### **IDV Intensity Values:**
- **0.0:** No disturbance (normal operation) ✅
- **0.5:** Small disturbance (5% change from normal)
- **1.0:** Standard disturbance (10% change from normal)
- **1.5:** Large disturbance (15% change from normal)
- **2.0:** Severe disturbance (20% change from normal)

### **Example - A/C Feed Ratio (IDV(1)):**
```python
idata[10:, 0] = 0.0   # Normal A/C ratio
idata[10:, 0] = 0.5   # Slight imbalance → small temp rise
idata[10:, 0] = 1.0   # Moderate imbalance → noticeable effects
idata[10:, 0] = 1.5   # Large imbalance → significant temp/pressure changes
idata[10:, 0] = 2.0   # Severe imbalance → major process upset
```

## 🎛️ **Real Dashboard Should Work Like This:**

### **User Interface:**
```
Process Inputs (IDV Controls):
┌─────────────────────────────────────┐
│ A/C Feed Ratio: [====|====] 1.2     │  ← User adjusts this
│ Cooling Water Temp: [===|=====] 5°C │  ← User adjusts this
│ Feed Temperature: [====|====] 0°C   │  ← User adjusts this
└─────────────────────────────────────┘

Sensor Readings (XMEAS Outputs):
┌─────────────────────────────────────┐
│ 🌡️ Reactor Temp: 125.3°C (HIGH!)   │  ← Physics calculates this
│ 📊 Reactor Pressure: 2850 kPa       │  ← Physics calculates this
│ 📈 Anomaly Score: 4.2 (ALERT!)      │  ← PCA detects this
└─────────────────────────────────────┘

AI Analysis:
┌─────────────────────────────────────┐
│ 🤖 "Temperature spike detected.      │  ← LLM diagnoses this
│     Pattern suggests A/C feed ratio  │
│     imbalance. Recommend reducing    │
│     feed ratio to 1.0-1.1 range."   │
└─────────────────────────────────────┘
```

## 📋 **Summary:**

### **Real TEP Flow:**
1. **User changes IDV inputs** (process parameters)
2. **Fortran calculates physics** (mass/energy balances)
3. **XMEAS sensors respond** (temperature, pressure, flow, level)
4. **PCA detects anomalies** (from sensor patterns)
5. **LLM diagnoses fault type** (from process knowledge)

### **Key Points:**
- ✅ **IDV intensity 0.0 = normal operation**
- ✅ **Higher intensity = larger process disturbance**
- ✅ **No direct "fault type" injection**
- ✅ **Fault type diagnosed from sensor patterns**
- ✅ **Physics-based cause-and-effect relationships**

**This is the correct approach you described!** 🎯✨
