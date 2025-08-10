# Step-by-Step Usage Guide - TEP FaultExplainer System

## 🚀 **Complete System Setup and Usage**

### **📁 System Overview:**
You now have a complete TEP FaultExplainer system with:
- **Real TEP2PY integration** (Fortran physics simulation)
- **PCA anomaly detection** (statistical fault detection)
- **LLM fault diagnosis** (AI-powered explanations)
- **Optimized timing** (reduced notification frequency)
- **Comprehensive logging** (persistent analysis records)

## 🔧 **Step 1: Environment Setup**

### **Navigate to Project Directory:**
```bash
cd /Users/chennanli/Desktop/LLM_Project/TE
```

### **Activate Virtual Environment:**
```bash
source tep_env/bin/activate
```

### **Verify Environment:**
```bash
# Check Python version
python --version  # Should be 3.9+

# Check key packages
pip list | grep -E "(numpy|pandas|scikit-learn|flask)"
```

## 🚀 **Step 2: Start Unified System (ONE COMMAND!)**

### **Single Command Startup:**
```bash
python unified_tep_system.py
```

**Expected Output:**
```
✅ TEP simulator loaded successfully!
🚀 Starting Unified TEP FaultExplainer System...
📋 Automatic startup: FaultExplainer + TEP + Dashboard
🔧 Starting FaultExplainer backend...
✅ FaultExplainer backend started successfully!
✅ All components initialized successfully!
🌐 Open: http://localhost:8084
📝 Logs: logs/ directory
💾 Data: data/ directory
🎯 Just click 'Start Unified System' to begin!
 * Running on http://127.0.0.1:8084
```

### **What Happens Automatically:**
1. ✅ **FaultExplainer Backend** starts automatically (PCA + LLM)
2. ✅ **TEP Simulation Engine** initializes with physics model
3. ✅ **Web Dashboard** launches with unified interface
4. ✅ **Logging System** creates logs/ and data/ directories
5. ✅ **Optimized Timing** configured (3min → 6min → 12min)

## 🌐 **Step 3: Access Dashboard**

### **Open Web Browser:**
Navigate to: **http://localhost:8084**

### **No Multiple Terminals Needed!**
- ✅ **Everything runs from one command**
- ✅ **Automatic component startup**
- ✅ **Unified interface**
- ✅ **Single process management**

### **Dashboard Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│                TEP FaultExplainer Dashboard                 │
├─────────────────────────────────────────────────────────────┤
│ 🎛️ Process Inputs (IDV Variables)                          │
│ ├── A/C Feed Ratio (IDV1): [====|====] 0.0                │
│ ├── Cooling Water Temp (IDV4): [====|====] 0.0°C          │
│ ├── Feed Temperature (IDV3): [====|====] 0.0°C            │
│ └── Reaction Kinetics (IDV13): [====|====] 0.0            │
│                                                             │
│ [▶️ Start System] [⏹️ Stop] [🔄 Reset]                     │
├─────────────────────────────────────────────────────────────┤
│ 📊 Real-Time Monitoring (4 plots)                          │
│ ├── Reactor Temperature vs Time                            │
│ ├── Reactor Pressure vs Time                               │
│ ├── PCA T² Statistic vs Time                               │
│ └── Current Process Inputs                                  │
├─────────────────────────────────────────────────────────────┤
│ 📋 System Status                                            │
│ ├── 🔬 PCA Analysis: T² = 2.34 (Normal)                   │
│ ├── 🤖 LLM Status: 1 pending, 3 completed                 │
│ └── 📝 Latest Analysis: "Normal operation detected..."     │
└─────────────────────────────────────────────────────────────┘
```

## 🎮 **Step 4: System Operation**

### **4.1 Start Normal Operation:**
1. **Click "▶️ Start System"**
2. **Observe:** System begins collecting baseline data
3. **Wait:** 20 samples (60 minutes) for initial PCA buffer fill
4. **Status:** "🟢 Collecting baseline data... (Sample 5/20)"

### **4.2 Monitor Normal Operation:**
```
Expected Readings (Normal):
├── Reactor Temperature: 120-125°C
├── Reactor Pressure: 2700-2800 kPa  
├── PCA T² Statistic: 0-11 (below threshold)
└── Status: "✅ Normal operation - monitoring continues"
```

### **4.3 Create Process Disturbance:**
1. **Adjust A/C Feed Ratio:** Move slider to 1.5
2. **Observe:** Temperature begins to rise
3. **Wait:** 6 minutes for PCA analysis
4. **Result:** T² statistic increases

### **4.4 Watch Anomaly Detection:**
```
Anomaly Sequence:
Time 0:   A/C ratio changed to 1.5
Time 3:   Temperature rises to 128°C
Time 6:   PCA analysis: T² = 15.2 (> threshold 11.345)
Time 6:   Status: "🚨 ANOMALY DETECTED!"
Time 12:  LLM analysis triggered
Time 12:  Result: "Temperature spike detected. A/C feed ratio fault likely..."
```

## 📊 **Step 5: Understanding Results**

### **5.1 PCA Analysis Results:**
```
🔬 PCA Status:
├── T² Statistic: 15.234
├── Threshold: 11.345
├── Status: ANOMALY DETECTED
├── Confidence: High (T² > 1.3 × threshold)
└── Variables Contributing: Temperature (+3.2σ), Pressure (+1.8σ)
```

### **5.2 LLM Diagnosis Results:**
```
🤖 AI Analysis:
├── Fault Type: A/C Feed Ratio Imbalance
├── Confidence: 87%
├── Root Cause: Feed composition deviation affecting reaction kinetics
├── Safety Impact: Moderate - temperature approaching upper limit
└── Recommendations:
    ├── 1. Reduce A/C ratio to 1.0-1.1 range
    ├── 2. Increase cooling water flow if available
    └── 3. Monitor temperature trend for further increases
```

## 📝 **Step 6: Accessing Logs and Results**

### **6.1 Log File Locations:**
```bash
# View system logs
ls -la logs/
├── tep_simulation.log      # TEP data and process states
├── pca_analysis.log        # PCA results and T² scores  
├── llm_diagnoses.log       # LLM analysis results
└── system_events.log       # System status and errors
```

### **6.2 View Recent LLM Analyses:**
```bash
# Last 10 LLM diagnoses
tail -n 10 logs/llm_diagnoses.log

# Search for specific fault types
grep "A/C Feed Ratio" logs/llm_diagnoses.log

# View analyses from specific time period
grep "2025-01-07 14:" logs/llm_diagnoses.log
```

### **6.3 Saved Analysis Data:**
```bash
# CSV files with structured data
ls -la data/
├── llm_analyses.csv        # All LLM results with timestamps
├── pca_results.csv         # PCA T² scores and thresholds
└── tep_sensor_data.csv     # Raw TEP simulation data
```

## 🔄 **Step 7: Testing Different Scenarios**

### **Scenario 1: Gradual Fault Development**
```
1. Start with all IDV = 0.0 (normal)
2. Slowly increase A/C ratio: 0.0 → 0.5 → 1.0 → 1.5
3. Observe gradual T² increase
4. Watch LLM analysis when threshold exceeded
```

### **Scenario 2: Multiple Fault Conditions**
```
1. Set A/C ratio to 1.2
2. Set cooling water temp to 5°C
3. Observe compound effects
4. See how LLM identifies multiple contributing factors
```

### **Scenario 3: Recovery Testing**
```
1. Create anomaly condition
2. Wait for LLM analysis
3. Follow LLM recommendations
4. Return controls to normal
5. Watch T² score decrease
```

## 🛑 **Step 8: System Shutdown**

### **Simple Shutdown:**
1. **Dashboard:** Click "⏹️ Stop" button (stops simulation)
2. **Terminal:** Press Ctrl+C (stops entire unified system)
3. **Automatic cleanup:** All components shut down automatically
4. **Deactivate:** `deactivate` to exit virtual environment

### **Automatic Cleanup:**
- ✅ **FaultExplainer backend** terminated automatically
- ✅ **TEP simulation** stopped gracefully
- ✅ **Log files** saved and closed properly
- ✅ **Data files** finalized

## 📊 **Step 9: Results Analysis**

### **9.1 Performance Metrics:**
```bash
# Check system performance
grep "processing_time" logs/llm_diagnoses.log | tail -10

# Average LLM response time
grep "LLM_ANALYSIS" logs/llm_diagnoses.log | awk '{print $8}' | tail -20
```

### **9.2 Fault Detection Accuracy:**
```bash
# Count anomalies detected
grep "ANOMALY_DETECTED" logs/pca_analysis.log | wc -l

# Count LLM analyses completed  
grep "LLM_ANALYSIS" logs/llm_diagnoses.log | wc -l
```

## 🎯 **Expected Timeline for First Use**

### **Initial Setup (5 minutes):**
- Environment activation: 1 minute
- System startup: 2 minutes
- Dashboard access: 1 minute
- Normal operation start: 1 minute

### **Baseline Collection (60 minutes):**
- PCA buffer filling: 60 minutes
- First PCA analysis available: After 60 minutes

### **Anomaly Testing (15 minutes):**
- Create disturbance: 1 minute
- Wait for PCA detection: 6 minutes
- Wait for LLM analysis: 12 minutes total
- Review results: 3 minutes

### **Total First Session: ~80 minutes**

## ✅ **Success Indicators**

### **System Working Correctly When:**
- ✅ Both terminals show no errors
- ✅ Dashboard loads at http://localhost:8084
- ✅ PCA T² scores update every 6 minutes
- ✅ LLM analyses appear every 12 minutes (when anomalies detected)
- ✅ Log files are being written
- ✅ CSV data files are being updated

### **Troubleshooting:**
- **Port conflicts:** Change ports in configuration files
- **Missing dependencies:** Reinstall with `pip install -r requirements.txt`
- **TEP2PY errors:** Check Fortran compilation in external_repos/tep2py-master
- **LLM timeouts:** Verify API keys in .env file

This system provides a complete industrial fault detection and diagnosis platform with real physics simulation, statistical anomaly detection, and AI-powered explanations!
