# How to Use the TEP Simulator - Complete Guide

## 🎯 Quick Start (5 Minutes)

### Step 1: Activate Virtual Environment
```bash
cd /Users/chennanli/Desktop/LLM_Project/TE
source tep_env/bin/activate
```
**You should see `(tep_env)` in your terminal prompt**

### Step 2: Verify Everything Works
```bash
python setup_tep.py
```
**Expected output:** All checks should show ✅ green checkmarks

### Step 3: Run Your First Simulation
```bash
python tep_simulator_easy.py
```
**This will run 2 example simulations and create CSV files**

## 📋 Understanding What You're Running

### Program Verification - Is This the Real TEP?

**YES! This is the authentic Tennessee Eastman Process simulator.** Here's how to verify:

1. **Original Source Code Location:**
   ```bash
   ls Other_Repo/tennessee-eastman-profBraatz-master/
   # You'll see: temain_mod.f, teprob.f (original Fortran files)
   ```

2. **Check File Headers:**
   ```bash
   head -20 Other_Repo/tennessee-eastman-profBraatz-master/teprob.f
   ```
   **You'll see:**
   ```fortran
   C               Tennessee Eastman Process Control Test Problem
   C                    James J. Downs and Ernest F. Vogel
   C                  Process and Control Systems Engineering
   C                        Tennessee Eastman Company
   ```

3. **Academic References:**
   - Original Paper: Downs & Vogel (1993) - "A Plant-Wide Industrial Process Control Problem"
   - Modified Version: Russell, Chiang & Braatz (2000)
   - This is the **exact same code** used in hundreds of research papers

4. **Verification Commands:**
   ```bash
   # Check the compiled module exists
   ls Other_Repo/tep2py-master/*.so
   
   # Verify it's working with original parameters
   cd Other_Repo/tep2py-master && python tep2py.py
   ```

## 🎛️ Parameter Guide - What Should You Change?

### Essential Parameters for Beginners

#### 1. **Simulation Duration** (`duration_hours`)
```python
# Short test (recommended for learning)
results = simulator.run_simulation(duration_hours=2)

# Standard industrial test
results = simulator.run_simulation(duration_hours=8)

# Long-term study
results = simulator.run_simulation(duration_hours=24)
```

#### 2. **Fault Type** (`fault_type`) - Most Important!
```python
# Start with these common faults:
fault_type=0   # Normal operation (baseline)
fault_type=1   # Feed composition fault (easy to see)
fault_type=4   # Cooling water temperature (dramatic effect)
fault_type=6   # Feed loss (obvious impact)
fault_type=13  # Reaction kinetics (subtle but important)
```

#### 3. **Fault Timing** (`fault_start_hour`)
```python
# Early fault (see immediate impact)
fault_start_hour=0.5

# Standard timing (let system stabilize first)
fault_start_hour=2

# Late fault (compare before/after)
fault_start_hour=4
```

### Recommended Parameter Combinations for Learning

#### **Beginner Experiments:**
```python
# Experiment 1: See normal operation
simulator.run_simulation(duration_hours=4, fault_type=0)

# Experiment 2: Simple fault
simulator.run_simulation(duration_hours=6, fault_type=1, fault_start_hour=2)

# Experiment 3: Dramatic fault
simulator.run_simulation(duration_hours=8, fault_type=6, fault_start_hour=3)
```

#### **Advanced Studies:**
```python
# Compare multiple faults
for fault in [1, 4, 6, 13]:
    simulator.run_simulation(duration_hours=10, fault_type=fault, fault_start_hour=2)

# Study fault timing effects
for start_time in [1, 3, 5]:
    simulator.run_simulation(duration_hours=8, fault_type=4, fault_start_hour=start_time)
```

## 📊 Understanding the Output Data

### Process Measurements (XMEAS) - What to Watch
| Variable | Description | Normal Range | Why Important |
|----------|-------------|--------------|---------------|
| XMEAS(7) | Reactor Pressure | 2700-2800 kPa | Core process indicator |
| XMEAS(9) | Reactor Temperature | 120-125°C | Safety critical |
| XMEAS(11) | Product Flow | 22-26 m³/h | Production rate |
| XMEAS(12) | Reactor Level | 50-80% | Process stability |
| XMEAS(13) | Separator Level | 30-70% | Product quality |

### Key Variables to Monitor for Each Fault Type
```python
# Fault 1 (Feed composition): Watch XMEAS(6), XMEAS(9)
# Fault 4 (Cooling water): Watch XMEAS(9), XMEAS(7) 
# Fault 6 (Feed loss): Watch XMEAS(1), XMEAS(11)
# Fault 13 (Reaction): Watch XMEAS(9), XMEAS(17)
```

## 🎨 Visualization Options

### Option 1: Built-in Plots (Easiest)
```python
# Enable automatic plotting
simulator.run_simulation(duration_hours=6, fault_type=1, plot_results=True)
```
**Creates:** PNG files with 4-panel plots

### Option 2: Interactive Dashboard (Recommended!)
```python
# Run the visual dashboard
python tep_dashboard.py
```
**Features:**
- Real-time process monitoring
- Interactive parameter input
- Live trend plots
- Process flow diagram
- Status indicators

### Option 3: Custom Analysis
```python
import pandas as pd
import matplotlib.pyplot as plt

# Load your data
data = pd.read_csv('tep_simulation_fault_1_6h.csv')

# Create custom plots
plt.figure(figsize=(12, 8))
plt.subplot(2,1,1)
plt.plot(data['Time_Hours'], data['XMEAS(9)'], label='Reactor Temperature')
plt.ylabel('Temperature (°C)')
plt.legend()

plt.subplot(2,1,2)
plt.plot(data['Time_Hours'], data['XMEAS(7)'], label='Reactor Pressure', color='red')
plt.xlabel('Time (hours)')
plt.ylabel('Pressure (kPa)')
plt.legend()
plt.show()
```

### Option 4: Demo with Comparisons
```python
# Run comprehensive demo
python demo_with_plots.py
```

## 🖥️ Better User Experience Ideas

### Current Limitations You Identified:
- ❌ Hard to understand from terminal output
- ❌ No real-time visualization
- ❌ Difficult to see what's happening in the process

### Recommended Solutions:

#### **Immediate (Use Now):**
1. **Enable Plots:**
   ```python
   # Always use plot_results=True
   simulator.run_simulation(duration_hours=6, fault_type=1, plot_results=True)
   ```

2. **Run Demo with Visualization:**
   ```bash
   python demo_with_plots.py
   ```

3. **Use Jupyter Notebook:**
   ```bash
   pip install jupyter
   jupyter notebook
   # Create interactive analysis
   ```

#### **Future Enhancements (I can help build):**

1. **Web Dashboard:**
   - Real-time process display
   - Interactive parameter controls
   - Live plotting

2. **Process Flow Diagram:**
   - Visual representation of the plant
   - Color-coded status indicators
   - Click-to-zoom details

3. **Control Panel Interface:**
   - Slider controls for parameters
   - Start/stop buttons
   - Alarm indicators

## 🔧 Troubleshooting Common Issues

### "Import Error" or "Module Not Found"
```bash
# Make sure you're in the right directory
cd /Users/chennanli/Desktop/LLM_Project/TE

# Activate virtual environment
source tep_env/bin/activate

# Verify setup
python setup_tep.py
```

### "No Plots Showing"
```bash
# Install display backend
pip install matplotlib
# On macOS, you might need:
pip install PyQt5
```

### "Simulation Runs Too Slow"
```python
# Use shorter durations for testing
simulator.run_simulation(duration_hours=2, fault_type=1)
```

## 📈 Available Visualization Tools

I've created several visualization tools for you:

1. **🎛️ Interactive Dashboard** (`tep_dashboard.py`)
   - Real-time process monitoring
   - Visual process flow diagram
   - Live trend plots with status indicators
   - Interactive parameter input

2. **📊 Demo with Plots** (`demo_with_plots.py`)
   - Comparison analysis between normal and fault conditions
   - Multiple visualization examples
   - Statistical summaries

3. **📋 Built-in Plotting** (in `tep_simulator_easy.py`)
   - Automatic 4-panel process plots
   - Saved PNG files for each simulation

4. **🔍 Verification Tools** (`verify_authentic_tep.py`)
   - Proves this is the authentic TEP simulator
   - Benchmark validation against literature

## 🚀 Quick Visualization Demo

Try this for immediate visual feedback:
```bash
# Interactive dashboard with real-time monitoring
python tep_dashboard.py

# Or comprehensive demo with comparisons
python demo_with_plots.py
```

## 🎯 Summary

- ✅ **Verified Authentic**: This is the real TEP simulator used in research
- ✅ **Parameter Guidance**: Start with faults 1, 4, 6 for clear effects
- ✅ **Visualization Ready**: Use `plot_results=True` for immediate graphs
- ✅ **Easy to Extend**: Ready for custom dashboards and interfaces

**You're running the industry-standard TEP simulator - the same one used in hundreds of research papers worldwide!** 🎉
