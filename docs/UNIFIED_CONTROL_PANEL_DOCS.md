# 🎛️ Unified TEP Control Panel Documentation

## 📋 **Overview**

The Unified TEP Control Panel provides a single interface for controlling:
- **TEP Chemical Plant Simulation** (dynamic process simulation)
- **FaultExplainer Integration** (anomaly detection + LLM analysis)
- **Live Data Bridge** (automatic data flow)
- **IDV Fault Injection** (disturbance simulation)

## 🌉 **Bridge Functionality - FAQ**

### **Q: Why is "Start Bridge" optional?**

**A:** The TEP simulation has a **built-in bridge** that automatically posts data to FaultExplainer!

```
TEP Simulation → Automatic Data Flow → FaultExplainer
(No separate bridge needed!)
```

### **Two Bridge Options:**
1. **Built-in Bridge** (automatic) - TEP simulation directly posts to FaultExplainer
2. **External Bridge** (optional) - Separate `tep_faultexplainer_bridge.py` script

### **🎯 Recommendation:** 
Just use "Start TEP" + "Start Backend" - the bridge is automatic!

---

## 🎛️ **Preset Modes Comparison**

| Setting | 🚀 **Demo** | ⚖️ **Balanced** | 🏭 **Realistic** |
|---------|-------------|-----------------|------------------|
| **TEP Simulation Speed** | 4 seconds | 60 seconds (1 min) | 180 seconds (3 min) |
| **PCA Window Size** | 8 samples | 12 samples | 20 samples |
| **Anomaly Trigger** | 3 consecutive | 2 consecutive | 6 consecutive |
| **LLM Min Interval** | 0 seconds (instant) | 20 seconds | 300 seconds (5 min) |
| **Data Decimation** | 1 (all data) | 4 (every 4th) | 1 (all data) |
| **Use Case** | Testing & Demo | Development | Industrial Deployment |

---

## 📊 **Data Flow Ratios**

### **🚀 Demo Mode:**
- **TEP:** Every 4 seconds
- **Anomaly Detection:** Every 4 seconds (immediate)
- **LLM:** Instant when anomaly detected
- **Ratio:** 1:1:immediate (very fast, lots of analysis)

### **⚖️ Balanced Mode:**
- **TEP:** Every 60 seconds (1 min)
- **Anomaly Detection:** Every 60 seconds
- **LLM:** Minimum 20 seconds between calls
- **Ratio:** 1:1:controlled (moderate speed, controlled analysis)

### **🏭 Realistic Mode:**
- **TEP:** Every 180 seconds (3 min)
- **Anomaly Detection:** Every 180 seconds
- **LLM:** Minimum 300 seconds (5 min) between calls
- **Ratio:** 1:1:5min-minimum (real industrial timing)

---

## 🚀 **Quick Start Guide**

1. **Start TEP** (orange button) - Starts chemical plant simulation
2. **Start Backend** (blue button) - Starts FaultExplainer analysis engine
3. **Start Frontend** (purple button) - Starts FaultExplainer web interface (optional)
4. **Choose Preset:** Demo (fast testing) | Balanced (development) | Realistic (industrial)
5. **Inject Faults:** Use IDV sliders to simulate plant disturbances
6. **Monitor Results:** Click "Show Last 5 Analyses" to see LLM diagnosis

### **🎯 Note:** "Start Bridge" is optional - the bridge is built-in!

---

## 🔧 **IDV Fault Types**

- **IDV_1:** A/C Feed Ratio - Feed composition disturbance
- **IDV_2:** B Composition - Feed quality variation
- **IDV_3:** D Feed Temperature - Thermal disturbance
- **IDV_4:** Reactor Cooling - Heat removal issues
- **IDV_5:** Condenser Cooling - Cooling system problems
- **IDV_6:** A Feed Loss - Feed supply interruption

**Range:** 0.0 (no fault) to 1.0 (maximum fault intensity)

---

## 🏗️ **Architecture**

### **Modular Structure:**
- `unified_tep_control_panel.py` - Main orchestrator (1400+ lines)
- `tep_bridge.py` - TEP simulation and data bridge logic
- `process_manager.py` - Process lifecycle management
- `api_routes.py` - Flask API endpoints
- `web_interface.py` - HTML templates and UI components

### **Data Flow:**
```
TEP Simulation (tep2py) 
    ↓ (built-in bridge)
FaultExplainer Backend (PCA + LLM)
    ↓
Analysis Results
    ↓
Unified Control Panel UI
```

---

## 🔧 **Technical Details**

### **Ports Used:**
- **9001** - Unified Control Panel
- **8000** - FaultExplainer Backend
- **5173/5174** - FaultExplainer Frontend

### **File Outputs:**
- `data/live_tep_data.csv` - Live simulation data
- `backend/diagnostics/analysis_history/` - LLM analysis logs

### **API Endpoints:**
- `/api/status` - System status
- `/api/tep/start` - Start TEP simulation
- `/api/backend/analysis/history` - Get analysis history
- `/api/idv/set` - Set fault injection values

---

## 🎯 **Best Practices**

1. **Always start in order:** TEP → Backend → Frontend
2. **Use Demo mode** for testing and demonstrations
3. **Use Balanced mode** for development work
4. **Use Realistic mode** for actual industrial simulation
5. **Monitor the logs** for debugging information
6. **Use IDV sliders gradually** - start with small values (0.1-0.3)

---

## 🐛 **Troubleshooting**

### **Common Issues:**
- **Port conflicts:** Use "Stop All" button to clean up
- **Backend not responding:** Check if port 8000 is free
- **No analysis results:** Ensure anomalies are detected (try higher IDV values)
- **JavaScript errors:** Check browser console, use Safari-compatible code

### **Reset Procedure:**
1. Click "Stop All"
2. Wait 5 seconds
3. Restart in order: TEP → Backend → Frontend
4. Set desired preset mode
5. Inject faults using IDV sliders
