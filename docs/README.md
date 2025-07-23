# Tennessee Eastman Process (TEP) Simulator

🎯 **A Python interface to the Tennessee Eastman Process dynamic simulator with easy-to-use tools for fault simulation and analysis.**

## 📋 Overview

This project provides a complete setup for running Tennessee Eastman Process simulations in Python. The TEP is a well-known benchmark process used for testing process control and fault detection methods. This implementation:

- ✅ Compiles original Fortran code to Python extensions
- ✅ Provides an easy-to-use Python interface
- ✅ Supports all 20 fault scenarios
- ✅ Generates CSV data and visualization plots
- ✅ Runs in a virtual environment for isolation

## 🚀 Quick Start

### 1. Activate Virtual Environment
```bash
source tep_env/bin/activate
```

### 2. Verify Installation
```bash
python setup_tep.py
```

### 3. Run Example Simulations
```bash
python tep_simulator_easy.py
```

## 📁 Project Structure

```
TE/
├── tep_env/                          # Virtual environment
├── Other_Repo/
│   ├── tep2py-master/               # Python wrapper for TEP
│   │   ├── temain_mod.cpython-39-darwin.so  # Compiled Fortran module
│   │   ├── tep2py.py               # Core TEP interface
│   │   └── src/tep/                # Fortran source files
│   └── tennessee-eastman-profBraatz-master/  # Original TEP code
├── tep_simulator_easy.py           # 🎯 Main user interface
├── setup_tep.py                    # Setup verification script
└── README_TEP_SIMULATOR.md         # This file
```

## 🔧 Available Fault Types

| Fault ID | Description |
|----------|-------------|
| 0 | Normal operation (no fault) |
| 1 | A/C feed ratio, B composition constant (Stream 4) |
| 2 | B composition, A/C ratio constant (Stream 4) |
| 3 | D feed temperature (Stream 2) |
| 4 | Reactor cooling water inlet temperature |
| 5 | Condenser cooling water inlet temperature |
| 6 | A feed loss (Stream 1) |
| 7 | C header pressure loss-reduced availability (Stream 4) |
| 8 | A, B, C feed composition (Stream 4) |
| 9 | D feed temperature (Stream 2) |
| 10 | C feed temperature (Stream 4) |
| 11 | Reactor cooling water inlet temperature |
| 12 | Condenser cooling water inlet temperature |
| 13 | Reaction kinetics |
| 14 | Reactor cooling water valve |
| 15 | Condenser cooling water valve |
| 16-20 | Unknown/Additional faults |

## 💻 Usage Examples

### Basic Usage
```python
from tep_simulator_easy import TEPSimulatorEasy

# Create simulator
simulator = TEPSimulatorEasy()

# Run normal operation
results = simulator.run_simulation(
    duration_hours=8,
    fault_type=0,
    save_results=True,
    plot_results=True
)
```

### Fault Simulation
```python
# Run simulation with fault
results = simulator.run_simulation(
    duration_hours=10,
    fault_type=1,           # A/C feed ratio fault
    fault_start_hour=3,     # Introduce fault at 3 hours
    save_results=True,
    plot_results=True
)
```

### Custom Analysis
```python
# Access raw data
print(f"Generated {len(results)} data points")
print(f"Variables: {list(results.columns)}")

# Analyze specific measurements
reactor_pressure = results['XMEAS(7)']
reactor_temp = results['XMEAS(9)']
```

## 📊 Output Data

### Process Measurements (XMEAS)
- 41 process measurements including:
  - Flow rates, pressures, temperatures
  - Compositions, levels
  - Product quality measurements

### Manipulated Variables (XMV)
- 11 manipulated variables:
  - Feed flow rates
  - Valve positions
  - Setpoints

### Generated Files
- `tep_simulation_fault_X_Yh.csv`: Raw simulation data
- `tep_simulation_fault_X_plot.png`: Visualization plots

## 🛠️ Advanced Usage

### Modify Simulation Parameters
Edit `tep_simulator_easy.py` to customize:
- Simulation duration
- Fault timing and types
- Plot configurations
- Data export formats

### Direct TEP2PY Usage
```python
import sys
sys.path.append('Other_Repo/tep2py-master')
from tep2py import tep2py
import numpy as np

# Create disturbance matrix
idata = np.zeros((100, 20))  # 100 samples, 20 disturbances
idata[50:, 0] = 1           # Activate fault 1 at sample 50

# Run simulation
tep = tep2py(idata)
tep.simulate()
data = tep.process_data
```

## 🔍 Troubleshooting

### Common Issues

1. **Import Error**: Make sure virtual environment is activated
   ```bash
   source tep_env/bin/activate
   ```

2. **Compilation Issues**: Recompile Fortran module
   ```bash
   cd Other_Repo/tep2py-master
   python -m numpy.f2py -c temain_mod-smart.pyf src/tep/temain_mod.f src/tep/teprob.f
   ```

3. **Missing Dependencies**: Install required packages
   ```bash
   pip install numpy pandas matplotlib
   ```

4. **gfortran Not Found**: Install Fortran compiler
   ```bash
   brew install gcc
   ```

### Verification
Run the setup verification script:
```bash
python setup_tep.py
```

## 📚 Technical Details

- **Simulation Frequency**: 1 sample every 3 minutes (180 seconds)
- **Data Points**: 20 samples per hour
- **Process Variables**: 41 measurements + 11 manipulated variables
- **Fault Types**: 20 different fault scenarios
- **Language**: Python 3.9+ with Fortran backend

## 🎯 Next Steps

1. **Explore Different Faults**: Try all 20 fault types
2. **Analyze Results**: Use pandas/matplotlib for custom analysis
3. **Develop Control Strategies**: Test different control approaches
4. **Fault Detection**: Implement fault detection algorithms
5. **Machine Learning**: Use data for ML model training

## 📖 References

- Original TEP Paper: Downs & Vogel (1993)
- Modified TEP: Russell, Chiang & Braatz (2000)
- Python Interface: tep2py project

---

**🎉 Happy Simulating!** 

For questions or issues, check the troubleshooting section or run `python setup_tep.py` for diagnostics.
