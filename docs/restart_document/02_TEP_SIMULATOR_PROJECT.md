# 🔬 Project 1: TEP Dynamic Simulator

## 📍 **Project Location**
- **Root Directory**: `/Users/chennanli/Desktop/LLM_Project/TE/`
- **Simulators**: `simulators/` folder
- **Core Engine**: `external_repos/tep2py-master/`

## 🎯 **Project Purpose**
Real-time Tennessee Eastman Process simulation with multiple GUI interfaces for industrial process monitoring and fault injection.

## 🏗️ **Architecture**

### **Core Components**

#### **1. TEP Physics Engine**
- **Location**: `external_repos/tep2py-master/`
- **Technology**: Python wrapper around compiled Fortran code
- **Key File**: `tep2py.py` - Main simulation interface
- **Fortran Module**: `temain_mod.cpython-39-darwin.so` (compiled binary)

#### **2. Simulator Interfaces**
Multiple GUI options for different use cases:

**A. Live Interactive Simulators**
- `simulators/live/live_tep_simulator.py` - Tkinter GUI with real-time plots
- `simulators/live/tep_dashboard.py` - Advanced dashboard with animations
- `simulators/live/improved_tep_simulator.py` - Flask web interface

**B. Demo Simulators**
- `simulators/demos/step1_simple_visualization.py` - Static plot generation
- `simulators/demos/step3_compare_faults.py` - Fault comparison analysis

**C. Production Simulators**
- `real_tep_simulator.py` - Main production simulator
- `fast_tep_dashboard.py` - High-performance web dashboard
- `corrected_tep_dashboard.py` - Improved physics integration

## 🛠️ **Technology Stack**

### **Core Technologies**
```python
# Physics Engine
- Fortran (compiled to .so module)
- Python 3.9+ (tep2py wrapper)
- NumPy (numerical computations)
- Pandas (data handling)

# GUI Frameworks
- Tkinter (desktop GUI)
- Flask + SocketIO (web interface)
- Qt5 (advanced desktop GUI)
- Matplotlib (plotting)

# Real-time Processing
- Threading (concurrent simulation)
- WebSocket (real-time updates)
- Collections.deque (data buffering)
```

### **Key Dependencies**
```bash
# Core simulation
numpy>=1.20.0
pandas>=1.3.0
matplotlib>=3.4.0

# Web interfaces
flask>=2.0.0
flask-socketio

# Desktop GUIs
PyQt5>=5.15.0
tkinter (built-in)

# Process monitoring
psutil>=5.8.0
```

## 📊 **Data Model**

### **TEP Variables (52 total)**
```python
# Process Measurements (XMEAS 1-41)
XMEAS_1   # A Feed (Stream 1)
XMEAS_2   # D Feed (Stream 2)  
XMEAS_7   # Reactor Pressure
XMEAS_8   # Reactor Level
XMEAS_9   # Reactor Temperature
# ... (36 more measurements)

# Manipulated Variables (XMV 1-11)
XMV_1     # D Feed Flow
XMV_2     # E Feed Flow
XMV_3     # A Feed Flow
# ... (8 more control variables)
```

### **Fault Types (IDV 1-20)**
```python
IDV_1   # A/C Feed Ratio, B Composition Constant
IDV_4   # Reactor Cooling Water Inlet Temperature  
IDV_6   # A Feed Loss
IDV_8   # A, B, C Feed Composition
IDV_13  # Reaction Kinetics (slow drift)
# ... (15 more fault types)
```

## 🎮 **User Interfaces**

### **1. Tkinter Desktop GUI**
**File**: `simulators/live/live_tep_simulator.py`
```python
Features:
- Real-time variable plots
- Fault injection sliders
- Process control buttons
- Data export functionality
```

### **2. Flask Web Dashboard**
**File**: `fast_tep_dashboard.py`
```python
Features:
- Web-based interface (localhost:5000)
- Real-time WebSocket updates
- Interactive fault controls
- JSON API endpoints
```

### **3. Advanced Dashboard**
**File**: `working_tep_dashboard.py`
```python
Features:
- Unified control panel
- FaultExplainer integration
- System status monitoring
- Multi-terminal management
```

## 🔄 **Simulation Flow**

### **1. Initialization**
```python
# Load tep2py module
sys.path.append('external_repos/tep2py-master')
from tep2py import tep2py

# Create disturbance matrix
idata = np.zeros((samples, 20))  # 20 fault types

# Initialize simulator
tep = tep2py(idata)
```

### **2. Real-time Execution**
```python
# Simulation loop
while running:
    # Update fault conditions
    if fault_active:
        idata[current_step, fault_type-1] = fault_intensity
    
    # Run simulation step
    tep.simulate()
    
    # Extract results
    data = tep.process_data
    current_xmeas = data[XMEAS_columns].iloc[-1]
    current_xmv = data[XMV_columns].iloc[-1]
    
    # Update GUI/save data
    update_displays(current_xmeas, current_xmv)
```

### **3. Data Output**
```python
# CSV export format
columns = ['timestamp', 'step', 'fault_type', 'fault_intensity'] + \
          [f'XMEAS_{i}' for i in range(1,42)] + \
          [f'XMV_{i}' for i in range(1,12)]

# Save to data/live_tep_data.csv
df.to_csv('data/live_tep_data.csv', index=False)
```

## 🎛️ **Configuration Options**

### **Simulation Parameters**
```python
# Timing
SIMULATION_STEP = 3  # minutes (TEP standard)
UPDATE_FREQUENCY = 1  # seconds (GUI refresh)

# Data collection
BUFFER_SIZE = 100  # data points to keep
EXPORT_INTERVAL = 10  # steps between CSV saves

# Fault injection
FAULT_INTENSITY_RANGE = (0.0, 2.0)  # multiplier
FAULT_DURATION = 'continuous'  # or time-limited
```

### **GUI Customization**
```python
# Plot settings
PLOT_VARIABLES = ['XMEAS_9', 'XMEAS_7', 'XMEAS_8']  # Key variables
PLOT_HISTORY = 50  # data points to display
REFRESH_RATE = 1000  # milliseconds

# Interface options
SHOW_ALL_VARIABLES = False  # or True for full display
ENABLE_FAULT_CONTROLS = True
AUTO_SAVE = True
```

## 🚀 **Startup Options**

### **Quick Start (Recommended)**
```bash
source tep_env/bin/activate
python real_tep_simulator.py
```

### **Web Interface**
```bash
source tep_env/bin/activate
python fast_tep_dashboard.py
# Open: http://localhost:5000
```

### **Advanced Dashboard**
```bash
source tep_env/bin/activate
python working_tep_dashboard.py
# Includes FaultExplainer integration
```

## 📁 **File Structure**
```
TEP Simulator Project/
├── real_tep_simulator.py          # Main production simulator
├── fast_tep_dashboard.py          # Web dashboard
├── corrected_tep_dashboard.py     # Improved version
├── working_tep_dashboard.py       # Advanced control panel
├── simulators/
│   ├── core/
│   │   └── tep_simulator_easy.py  # Simplified interface
│   ├── demos/
│   │   ├── step1_simple_visualization.py
│   │   └── step3_compare_faults.py
│   └── live/
│       ├── live_tep_simulator.py  # Tkinter GUI
│       ├── tep_dashboard.py       # Advanced dashboard
│       └── improved_tep_simulator.py
├── external_repos/tep2py-master/  # Core physics engine
│   ├── tep2py.py                  # Python interface
│   └── temain_mod.cpython-39-darwin.so  # Compiled Fortran
└── data/                          # Output directory
    └── live_tep_data.csv          # Real-time data export
```

This project provides **authentic industrial process simulation** with multiple interface options for different use cases.
