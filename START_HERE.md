# 🎛️ TEP Simulators - START HERE

## 📁 **Organized File Structure:**

### **🚀 Quick Start:**
- **`run_simulator.py`** 🎯 **MAIN LAUNCHER** - Start here!

### **📂 Folders Explained:**

#### **`simulators/live/`** - Ready-to-use simulators
- `simple_web_tep_simulator.py` 🌟 **BEST FOR DEMOS**
- `clean_qt_tep_simulator.py` 🎛️ **DESKTOP APP**
- `smart_launcher.py` 🚀 **ALL THREE TOGETHER**

#### **`scripts/utilities/`** - Helper tools
- `check_simulators.py` - Clean up background processes

#### **`docs/`** - Documentation
- Various project documentation and guides

#### **`external_repos/`** - Third-party code
- `tep2py-master/` - Core TEP simulation engine
- Other research repositories

#### **`data/`** - Simulation data and results
- `plots/` - Generated plots
- `simulation_results/` - Saved simulation data

#### **Root Documentation:**
- `START_HERE.md` 📋 **THIS FILE**
- `DEMO_GUIDE.md` - Complete demo instructions
- `README_SIMULATORS.md` - Detailed documentation

---

## 🚀 **Quick Start:**

### **🎯 Super Simple (RECOMMENDED):**
```bash
cd /Users/chennanli/Desktop/LLM_Project/TE
source tep_env/bin/activate
python run_simulator.py
```
**Then select option 1 for best demo experience!**

### **🔧 Direct Access (Advanced):**
```bash
# Web simulator (best for demos)
python simulators/live/simple_web_tep_simulator.py

# Desktop app
python simulators/live/clean_qt_tep_simulator.py

# All three simulators
python simulators/live/smart_launcher.py

# Check background processes
python scripts/utilities/check_simulators.py
```

---

## 🎯 **For Demonstrations:**

### **Best Demo Settings:**
- **Fault:** 13 - Reaction Kinetics
- **Intensity:** 1.8
- **Expected:** Temperature +3°C, Pressure +30 kPa

### **Demo Steps:**
1. Start with Normal Operation
2. Select Fault 13, intensity 1.8
3. Watch dramatic real-time changes
4. Reset and try other faults

### **Get Demo Guide:**
- **In web simulator:** Click "📋 Demo Guide" button
- **Standalone:** Open `DEMO_GUIDE.md` file

---

## 🧹 **If Things Go Wrong:**

### **Background processes running?**
```bash
python scripts/utilities/check_simulators.py
```

### **Ports occupied?**
```bash
lsof -ti:8080 | xargs kill -9
lsof -ti:8081 | xargs kill -9
```

### **Start fresh:**
```bash
python scripts/utilities/check_simulators.py  # Clean up first
python run_simulator.py  # Then start
```

---

## 📋 **Complete File Structure:**

```
TEP/
├── run_simulator.py                    🎯 MAIN LAUNCHER
├── START_HERE.md                       📋 QUICK GUIDE
├── DEMO_GUIDE.md                       📖 DEMO INSTRUCTIONS
├── README_SIMULATORS.md                📚 FULL DOCS
│
├── simulators/
│   ├── live/                          🚀 READY-TO-USE SIMULATORS
│   │   ├── simple_web_tep_simulator.py    🌟 BEST FOR DEMOS
│   │   ├── clean_qt_tep_simulator.py      🎛️ DESKTOP APP
│   │   ├── smart_launcher.py              🚀 ALL THREE
│   │   └── [other live simulators]
│   ├── core/                          🔧 BASIC SIMULATORS
│   └── demos/                         📊 DEMO SCRIPTS
│
├── scripts/
│   ├── setup/                         ⚙️ SETUP SCRIPTS
│   └── utilities/                     🛠️ HELPER TOOLS
│       └── check_simulators.py            🔍 PROCESS CHECKER
│
├── docs/                              📚 DOCUMENTATION
├── data/                              💾 SIMULATION DATA
├── external_repos/                    📦 THIRD-PARTY CODE
│   └── tep2py-master/                     🎛️ CORE TEP ENGINE
└── tep_env/                           🐍 VIRTUAL ENVIRONMENT
```

### **🎯 Why This Organization:**
- **Root level:** Main launcher and key docs
- **`simulators/live/`:** Production-ready simulators
- **`scripts/utilities/`:** Helper tools and utilities
- **Clear separation:** Each folder has a specific purpose

---

## 🎯 **Bottom Line:**

**For customer demos:** Run `python run_simulator.py` → Select option 1 → http://localhost:8081

**That's it! Clean, organized, and professional.** 🎛️✨
