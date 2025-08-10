# 🚀 TEP Dashboard - Pure Flask (No JavaScript Issues!)

## ✅ **What's Fixed:**
- **NO MORE JAVASCRIPT PROBLEMS** - Pure HTML forms, 100% reliable
- **Cross-platform** - Works on Windows, Mac, Linux
- **Auto-refresh** - Page updates every 5 seconds automatically
- **All FaultExplainer features** - 6 plots, T² statistics, LLM analysis, IDV controls

## 🎯 **How to Run (Simple!):**

### **Step 1: Activate Virtual Environment**
```bash
# On Mac/Linux:
source tep_env/bin/activate

# On Windows:
tep_env\Scripts\activate
```

### **Step 2: Start Dashboard**
```bash
python working_tep_dashboard.py
```

### **Step 3: Open Browser**
```
http://localhost:8080
```

## 🎛️ **How to Use:**

### **1. Start TEP Simulation**
- Click **"Start TEP"** button
- Page will refresh and show "✅ Running"
- 6 matplotlib plots will start showing real-time data

### **2. Start Backend (Optional)**
- Click **"Start Backend"** button  
- Enables advanced FaultExplainer features

### **3. Trigger Faults**
- Use IDV sliders to inject faults:
  - **IDV_1**: A/C Feed Ratio
  - **IDV_4**: Cooling Water Issues
  - **IDV_6**: Feed Loss
  - **IDV_8**: Feed Composition
  - **IDV_13**: Reaction Kinetics ⭐ (BEST DEMO)

### **4. LLM Analysis**
- Click **"🧠 Diagnose with LLM"** button
- Get comprehensive fault analysis

## 🔧 **Features:**

### **✅ 6 Professional Plots (FaultExplainer Style):**
1. 🌡️ **Reactor Temperature** (XMEAS_9)
2. 📊 **Reactor Pressure** (XMEAS_7)  
3. 📈 **Reactor Level** (XMEAS_8)
4. 🔄 **Feed Rate** (XMEAS_6)
5. ❄️ **Coolant Temperature** (XMEAS_21)
6. 🚨 **T² Statistic** (Anomaly Detection)

### **✅ Real-Time Monitoring:**
- **T² Score**: Current anomaly statistic
- **T² Threshold**: 11.345 (FaultExplainer standard)
- **Anomaly Status**: ✅ Normal / 🚨 ANOMALY
- **Data Points**: Live count
- **Simulation Step**: Current step

### **✅ Timing Hierarchy:**
- **TEP Simulation**: Every 3 minutes
- **PCA Analysis**: Every 6 minutes (half frequency)
- **LLM Analysis**: Every 12 minutes (quarter frequency)

## 🛠️ **Troubleshooting:**

### **Port Already in Use:**
```bash
# Kill any existing process on port 8080
lsof -ti:8080 | xargs kill -9
```

### **Virtual Environment Issues:**
```bash
# Recreate if needed
python -m venv tep_env
source tep_env/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

### **Missing Dependencies:**
```bash
pip install flask matplotlib numpy requests
```

## 🎯 **Best Demo Sequence:**

1. **Start TEP** → See baseline plots
2. **Set IDV_13 = 0.5** → Watch T² statistic rise
3. **Wait for anomaly** → See 🚨 ANOMALY indicator
4. **Click LLM Diagnosis** → Get detailed fault analysis
5. **Reset IDV_13 = 0** → Return to normal

## 📁 **Key Files:**
- `working_tep_dashboard.py` - Main dashboard (pure Flask)
- `simple_fault_backend.py` - FaultExplainer backend
- `requirements.txt` - Python dependencies
- `tep_env/` - Virtual environment

## 🚀 **Why This Version is Better:**
- ✅ **No JavaScript failures** - Pure HTML forms
- ✅ **100% reliable buttons** - Always work
- ✅ **Cross-platform** - Windows compatible
- ✅ **Auto-refresh** - No manual refresh needed
- ✅ **Professional plots** - Industrial-grade visualization
- ✅ **Easy debugging** - Simple HTTP requests
