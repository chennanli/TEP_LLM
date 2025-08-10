# 🛠️ TEP Simulator Setup Guide

## 🚀 Quick Installation

### **1. Prerequisites**
- Python 3.8 or higher
- Git (for cloning)
- 2GB free disk space

### **2. Installation Steps**
```bash
# Clone the repository
git clone https://github.com/your-username/TE.git
cd TE

# Create virtual environment
python -m venv tep_env

# Activate virtual environment
source tep_env/bin/activate  # macOS/Linux
# tep_env\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Test installation
python run_simulator.py
```

## 🎛️ Running the Simulators

### **Option 1: Qt Desktop Simulator**
```bash
python run_simulator.py
# Choose option 1
```
- Native desktop application
- No browser required
- Professional interface

### **Option 2: Enhanced Web Simulator**
```bash
python run_simulator.py
# Choose option 2
# Open browser to http://localhost:8082
```
- Modern web interface
- Multiple product monitoring
- Real-time updates

### **Option 3: Process Utilities**
```bash
python run_simulator.py
# Choose option 3
```
- Check running processes
- Clean up background simulators

## 📊 Generate Training Data

```bash
# Generate ML datasets
python generate_training_data.py

# Creates CSV files with:
# - All 52 process variables
# - 20 fault scenarios
# - Time series data
```

## 🔧 Troubleshooting

### **Common Issues:**

#### **"Module not found" errors**
```bash
# Make sure virtual environment is activated
source tep_env/bin/activate
pip install -r requirements.txt
```

#### **Qt simulator won't start**
```bash
# Install Qt dependencies
pip install PyQt5
```

#### **Web simulator timeout**
```bash
# Check if port 8082 is available
python run_simulator.py
# Choose option 3 to clean processes
```

#### **Large repository size**
```bash
# If git push fails due to size:
git gc --aggressive --prune=now
```

## 📋 Dependencies

### **Core Requirements:**
- `numpy` - Numerical computations
- `matplotlib` - Plotting and visualization
- `pandas` - Data handling
- `flask` - Web interface
- `PyQt5` - Desktop interface
- `psutil` - Process monitoring

### **Optional:**
- `pytest` - Testing framework
- `requests` - HTTP requests (for LLM integration)

## 🎯 Verification

### **Test All Components:**
```bash
# Run comprehensive test
python -c "
import numpy, matplotlib, pandas, flask, PyQt5, psutil
print('✅ All dependencies installed successfully!')
"

# Test TEP simulator core
python -c "
import sys
sys.path.append('external_repos/tep2py-master')
from tep2py import tep2py
print('✅ TEP simulator core working!')
"
```

## 📁 Project Structure

```
TE/
├── README.md                    # Main documentation
├── SETUP_GUIDE.md              # This file
├── TEP_VARIABLES.md             # Variable reference
├── LICENSE                      # CC BY-NC-SA 4.0
├── requirements.txt             # Dependencies
├── .gitignore                   # Git exclusions
│
├── run_simulator.py             # Main launcher
├── generate_training_data.py    # ML data generator
│
├── simulators/live/
│   ├── clean_qt_tep_simulator.py      # Qt desktop app
│   └── improved_tep_simulator.py      # Web interface
│
├── scripts/utilities/
│   └── check_simulators.py            # Process utilities
│
└── external_repos/
    └── tep2py-master/                  # Core TEP engine
```

## 🎓 Usage Tips

### **For Education:**
- Start with Qt simulator for demonstrations
- Use web simulator for detailed analysis
- Generate training data for student projects

### **For Research:**
- Modify fault scenarios in the code
- Export data for external analysis
- Integrate with your ML pipelines

### **For Development:**
- All simulators use the same TEP core
- Modify plots by editing the simulator files
- Add new variables by updating the plotting code

## 📧 Getting Help

1. **Check this guide** for common solutions
2. **Review error messages** carefully
3. **Verify virtual environment** is activated
4. **Check dependencies** are installed
5. **Open GitHub issue** if problems persist

## 🎯 Next Steps

After successful installation:
1. **Explore both simulators** to understand the interface
2. **Review TEP_VARIABLES.md** to understand the process
3. **Generate training data** for your projects
4. **Modify and experiment** with the code

**Happy simulating!** 🎛️✨
