# TEP Simulator Parameter Guide

## 🎯 What Parameters Should You Change?

This guide helps you understand which parameters to modify for different research and learning objectives.

## 📊 Parameter Categories

### 1. **Simulation Duration** (`duration_hours`)

| Purpose | Recommended Duration | Why |
|---------|---------------------|-----|
| **Quick Test** | 1-2 hours | Fast feedback, parameter testing |
| **Fault Detection Study** | 6-8 hours | Standard industrial benchmark |
| **Control System Design** | 12-24 hours | Long-term stability analysis |
| **Statistical Analysis** | 48+ hours | Sufficient data for ML/statistics |

```python
# Examples
simulator.run_simulation(duration_hours=2)   # Quick test
simulator.run_simulation(duration_hours=8)   # Standard study
simulator.run_simulation(duration_hours=24)  # Comprehensive analysis
```

### 2. **Fault Types** (`fault_type`) - Most Important Parameter!

#### **Beginner-Friendly Faults (Clear, Visible Effects)**
| Fault ID | Name | Effect | Difficulty | Best For |
|----------|------|--------|------------|----------|
| **1** | A/C Feed Ratio | Composition changes | Easy | Learning basics |
| **4** | Reactor Cooling Water | Temperature spike | Easy | Safety studies |
| **6** | A Feed Loss | Flow reduction | Easy | Production impact |
| **8** | Feed Composition | Multiple variables | Medium | Complex analysis |

#### **Advanced Faults (Subtle, Challenging)**
| Fault ID | Name | Effect | Difficulty | Best For |
|----------|------|--------|------------|----------|
| **13** | Reaction Kinetics | Slow degradation | Hard | Advanced detection |
| **14** | Cooling Water Valve | Gradual changes | Hard | Control studies |
| **15** | Condenser Valve | Pressure effects | Hard | System dynamics |

#### **Research-Standard Faults**
```python
# Most cited in literature (use for comparisons)
standard_faults = [1, 2, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14]

# Run standard benchmark
for fault in standard_faults:
    simulator.run_simulation(duration_hours=8, fault_type=fault, fault_start_hour=1)
```

### 3. **Fault Timing** (`fault_start_hour`)

| Timing Strategy | Start Time | Purpose |
|----------------|------------|---------|
| **Immediate** | 0.1 hours | Study fault from beginning |
| **Early** | 1 hour | Quick fault detection |
| **Standard** | 2-3 hours | Industry benchmark |
| **Late** | 5+ hours | Long-term stability first |

```python
# Timing studies
for start_time in [0.5, 1, 2, 4]:
    simulator.run_simulation(duration_hours=8, fault_type=1, fault_start_hour=start_time)
```

## 🔬 Research-Based Parameter Recommendations

### **Fault Detection Research**
```python
# Standard benchmark used in 100+ papers
benchmark_config = {
    'duration_hours': 8,
    'fault_types': [1, 2, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14],
    'fault_start_hour': 1,
    'normal_operation_hours': 8  # for comparison
}
```

### **Control System Design**
```python
# Focus on controllable faults
control_faults = [4, 5, 11, 12, 14, 15]  # Temperature/valve faults
for fault in control_faults:
    simulator.run_simulation(duration_hours=12, fault_type=fault, fault_start_hour=2)
```

### **Machine Learning Training**
```python
# Generate diverse dataset
ml_config = {
    'normal_samples': 10,      # 10 normal operation runs
    'fault_samples_each': 5,   # 5 runs per fault type
    'duration_hours': 6,       # Manageable size
    'fault_types': range(1, 21)  # All fault types
}
```

### **Safety Analysis**
```python
# Focus on dangerous faults
safety_critical = [3, 4, 9, 11]  # Temperature-related faults
for fault in safety_critical:
    simulator.run_simulation(duration_hours=10, fault_type=fault, fault_start_hour=1)
```

## 📈 Variables to Monitor for Each Fault

### **Fault 1: A/C Feed Ratio**
- **Primary**: XMEAS(6) - Reactor feed rate
- **Secondary**: XMEAS(9) - Reactor temperature
- **Impact**: Composition changes, production rate

### **Fault 4: Reactor Cooling Water**
- **Primary**: XMEAS(9) - Reactor temperature ⚠️
- **Secondary**: XMEAS(7) - Reactor pressure
- **Impact**: Safety critical, temperature runaway

### **Fault 6: A Feed Loss**
- **Primary**: XMEAS(1) - A feed flow
- **Secondary**: XMEAS(11) - Product flow
- **Impact**: Production loss, economic impact

### **Fault 13: Reaction Kinetics**
- **Primary**: XMEAS(17) - Stripper steam flow
- **Secondary**: XMEAS(9) - Reactor temperature
- **Impact**: Subtle, long-term degradation

## 🎛️ Advanced Parameter Combinations

### **Comparative Studies**
```python
# Compare fault severity
mild_faults = [2, 5, 10]
severe_faults = [4, 6, 8]

for fault_list, name in [(mild_faults, "mild"), (severe_faults, "severe")]:
    for fault in fault_list:
        simulator.run_simulation(duration_hours=8, fault_type=fault, 
                               fault_start_hour=2, save_results=True)
```

### **Timing Sensitivity Analysis**
```python
# Study how fault timing affects detectability
fault_type = 4  # Cooling water fault
for start_hour in [0.5, 1, 2, 3, 4, 5]:
    results = simulator.run_simulation(duration_hours=8, fault_type=fault_type, 
                                     fault_start_hour=start_hour)
    # Analyze detection delay vs fault start time
```

### **Duration Impact Studies**
```python
# How does simulation length affect results?
fault_type = 13  # Slow-developing fault
for duration in [4, 8, 12, 24]:
    simulator.run_simulation(duration_hours=duration, fault_type=fault_type, 
                           fault_start_hour=2)
```

## 🏭 Industrial Relevance

### **Real-World Equivalent Scenarios**

| TEP Fault | Real Industrial Scenario | Why Important |
|-----------|-------------------------|---------------|
| Fault 1 | Feed composition drift | Quality control |
| Fault 4 | Cooling system failure | Safety shutdown |
| Fault 6 | Raw material shortage | Supply chain |
| Fault 8 | Multiple feed issues | Complex diagnosis |
| Fault 13 | Catalyst deactivation | Maintenance planning |

### **Parameter Selection by Industry**

#### **Chemical Manufacturing**
- Focus: Faults 1, 2, 8 (composition-related)
- Duration: 8-12 hours (shift length)
- Timing: 2-3 hours (after startup)

#### **Process Safety**
- Focus: Faults 3, 4, 9, 11 (temperature-related)
- Duration: 6-8 hours (emergency response time)
- Timing: 1 hour (early detection critical)

#### **Production Optimization**
- Focus: Faults 6, 7, 11 (flow-related)
- Duration: 24+ hours (production cycles)
- Timing: Various (study different scenarios)

## 🎯 Quick Start Recommendations

### **If You're New to TEP:**
```python
# Start with these 4 simulations
simulator.run_simulation(duration_hours=4, fault_type=0)   # Normal
simulator.run_simulation(duration_hours=6, fault_type=1, fault_start_hour=2)   # Easy fault
simulator.run_simulation(duration_hours=6, fault_type=4, fault_start_hour=2)   # Dramatic fault
simulator.run_simulation(duration_hours=8, fault_type=13, fault_start_hour=2)  # Subtle fault
```

### **If You're Doing Research:**
```python
# Standard academic benchmark
for fault in [1, 2, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14]:
    simulator.run_simulation(duration_hours=8, fault_type=fault, fault_start_hour=1)
    simulator.run_simulation(duration_hours=8, fault_type=0)  # Normal for comparison
```

### **If You're Learning Control Systems:**
```python
# Focus on controllable variables
control_study_faults = [4, 5, 11, 12, 14, 15]
for fault in control_study_faults:
    simulator.run_simulation(duration_hours=10, fault_type=fault, fault_start_hour=3)
```

## 💡 Pro Tips

1. **Always run normal operation first** to establish baseline
2. **Use consistent fault_start_hour=2** for comparisons
3. **Start with duration_hours=6-8** for most studies
4. **Enable plotting** to visualize what's happening
5. **Save all results** for later analysis

**Remember: The TEP simulator is deterministic - same parameters = same results!** 🎯
