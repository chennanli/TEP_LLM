# 🎯 TEP Simulator Demo Guide

## 🌟 BEST FAULTS FOR DEMONSTRATIONS

### 1. Fault 13 - Reaction Kinetics 🏆
**Why:** Most dramatic changes across multiple parameters
**Expected Changes:**
- ↑ Temperature (+3-4°C)
- ↑ Pressure (+20-30 kPa) 
- ↓ Flow (-1-2 m³/h)
**Demo Intensity:** 1.6-2.0
**Visibility:** VERY HIGH - Changes visible within 30 seconds

### 2. Fault 1 - A/C Feed Ratio ⭐
**Why:** Great for showing temperature/pressure coupling
**Expected Changes:**
- ↑ Temperature (+1-2°C)
- ↑ Pressure (+40-60 kPa)
**Demo Intensity:** 1.5
**Visibility:** HIGH - Clear coupling demonstration

### 3. Fault 4 - Cooling Water Temperature ⭐
**Why:** Immediate temperature response
**Expected Changes:**
- ↑ Temperature (+2-3°C)
- ↓ Pressure (-15-25 kPa)
**Demo Intensity:** 1.8
**Visibility:** HIGH - Immediate response

---

## 🎯 DEMO STEPS

### Step 1: Establish Baseline
- Start with **Normal Operation** (Fault 0)
- Click **Start** simulation
- Let it run for 30-60 seconds to show stable values
- Point out the steady temperature, pressure, flow, and level

### Step 2: Introduce Fault
- Select **Fault 13 - Reaction Kinetics** (best for demos)
- Set intensity to **1.8** for dramatic visibility
- Explain what this fault represents in real industrial processes

### Step 3: Observe Changes
- Watch temperature rise (+3-4°C)
- Watch pressure increase (+20-30 kPa)
- Watch flow decrease (-1-2 m³/h)
- Point out how quickly changes propagate through the system

### Step 4: Reset and Compare
- Click **Reset** to clear data
- Try different faults to show variety
- Compare different fault effects

---

## 🎛️ SIMULATOR SELECTION GUIDE

### For Customer Demos → **Simple Web Simulator**
- **URL:** http://localhost:8081
- **Why:** Ultra-clean, easy to read, no distractions
- **Best for:** Professional presentations, customer meetings

### For Training → **Enhanced Web Simulator** 
- **URL:** http://localhost:8080
- **Why:** Detailed fault information, educational content
- **Best for:** Training sessions, educational demos

### For Formal Presentations → **Qt Simulator**
- **Why:** Native desktop app, professional appearance
- **Best for:** Board meetings, formal presentations

---

## 🚀 QUICK START COMMANDS

```bash
# Activate environment
cd /Users/chennanli/Desktop/LLM_Project/TE
source tep_env/bin/activate

# Option 1: Interactive launcher (recommended)
python run_simulators.py

# Option 2: Direct launch - Simple Web (best for demos)
python simple_web_tep_simulator.py
# Then open: http://localhost:8081

# Option 3: Direct launch - Enhanced Web
python enhanced_web_tep_simulator.py  
# Then open: http://localhost:8080

# Option 4: Direct launch - Qt Desktop
python enhanced_qt_tep_simulator.py
```

---

## 💡 DEMO TIPS

### Before the Demo:
- ✅ Test the simulator beforehand
- ✅ Have this guide open for reference
- ✅ Prepare your talking points
- ✅ Check internet connection (for web versions)

### During the Demo:
- 🎯 Start with Normal Operation to establish baseline
- 🎯 Use Fault 13 for most dramatic effect
- 🎯 Explain what each parameter represents
- 🎯 Point out real-time changes as they happen
- 🎯 Reset between different fault demonstrations

### Talking Points:
- "This simulates a real industrial chemical process"
- "These faults represent actual problems that occur in plants"
- "Notice how quickly the fault propagates through the system"
- "In real plants, early detection prevents costly shutdowns"
- "The coupling between temperature and pressure is typical"

---

## 📊 PARAMETER EXPLANATIONS

### Temperature (°C)
- **Normal Range:** ~120-125°C
- **What it shows:** Reactor thermal conditions
- **Why it matters:** Critical for product quality and safety

### Pressure (kPa)
- **Normal Range:** ~2700-2800 kPa
- **What it shows:** System pressure conditions
- **Why it matters:** Safety and process efficiency

### Flow (m³/h)
- **Normal Range:** ~22-25 m³/h
- **What it shows:** Product flow rate
- **Why it matters:** Production throughput

### Level (%)
- **Normal Range:** ~50-65%
- **What it shows:** Reactor fill level
- **Why it matters:** Process stability and safety

---

## 🎯 CUSTOMER DEMO SCRIPT

### Opening (30 seconds)
*"Today I'll show you our industrial process simulation system. This represents a real chemical plant with multiple process variables that we monitor in real-time."*

### Baseline (1 minute)
*"Let's start with normal operation. You can see stable temperature around 120°C, pressure around 2700 kPa, steady flow, and consistent level. This is what we want to see in a healthy process."*

### Fault Introduction (30 seconds)
*"Now I'll introduce a fault - specifically a reaction kinetics problem. This represents a change in the chemical reaction rate, which is common in industrial processes."*

### Observation (2 minutes)
*"Watch what happens - temperature immediately starts rising, pressure increases due to thermal expansion, and flow decreases as the reaction becomes less efficient. This demonstrates how faults propagate through interconnected systems."*

### Conclusion (30 seconds)
*"This real-time monitoring and fault detection capability helps plant operators identify problems early, preventing costly shutdowns and ensuring safe operation."*

---

## 🔧 TROUBLESHOOTING

### If simulator won't start:
1. Check virtual environment is activated
2. Verify you're in the correct directory
3. Check if port is already in use

### If changes aren't visible:
1. Try Fault 13 with intensity 1.8
2. Wait 30-60 seconds for propagation
3. Reset and try again

### If interface is unclear:
1. Use Simple Web Simulator for cleanest view
2. Zoom browser to 110-125% if needed
3. Use full-screen mode for presentations

---

**Keep this guide handy during demonstrations for quick reference!** 🎯
