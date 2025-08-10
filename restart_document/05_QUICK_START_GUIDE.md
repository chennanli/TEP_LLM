# 🚀 Quick Start Guide

## 🎯 **Get Running in 5 Minutes**

This guide gets both projects running together for immediate fault analysis.

## ✅ **Prerequisites Check**

### **1. Virtual Environment**
```bash
cd /Users/chennanli/Desktop/LLM_Project/TE
source tep_env/bin/activate
python --version  # Should show Python 3.9+
```

### **2. Dependencies**
```bash
# Check key packages
python -c "import tep2py; print('✅ TEP simulator ready')"
python -c "import anthropic; print('✅ Claude API ready')"
python -c "import fastapi; print('✅ FastAPI ready')"
```

### **3. Node.js (for frontend)**
```bash
cd external_repos/FaultExplainer-main/frontend
npm --version  # Should show npm 6.0+
```

## 🚀 **5-Terminal Startup (Recommended)**

### **Terminal 1: TEP Simulator**
```bash
cd /Users/chennanli/Desktop/LLM_Project/TE
source tep_env/bin/activate
python real_tep_simulator.py
```
**Status**: ✅ Generating live process data
**Output**: `data/live_tep_data.csv`

### **Terminal 2: FaultExplainer Backend**
```bash
cd /Users/chennanli/Desktop/LLM_Project/TE
cd external_repos/FaultExplainer-main/backend
source ../../../tep_env/bin/activate
python app.py
```
**Status**: ✅ AI analysis server running
**URL**: http://localhost:8000

### **Terminal 3: FaultExplainer Frontend**
```bash
cd /Users/chennanli/Desktop/LLM_Project/TE
cd external_repos/FaultExplainer-main/frontend
npm run dev
```
**Status**: ✅ Web interface running
**URL**: http://localhost:5173

### **Terminal 4: Data Bridge**
```bash
cd /Users/chennanli/Desktop/LLM_Project/TE
source tep_env/bin/activate
python tep_faultexplainer_bridge.py
```
**Status**: ✅ Connecting TEP to FaultExplainer
**Function**: Real-time data processing

### **Terminal 5: System Dashboard (Optional)**
```bash
cd /Users/chennanli/Desktop/LLM_Project/TE
source tep_env/bin/activate
python working_system_dashboard.py
```
**Status**: ✅ System monitoring GUI
**Function**: Unified control panel

## 🌐 **Access Points**

Once all terminals are running:

### **Main Interface**
- **FaultExplainer Web UI**: http://localhost:5173
  - 📊 **Monitoring Tab**: Real-time charts
  - 📈 **Fault History Tab**: T² statistics  
  - 🤖 **Assistant Tab**: LLM fault analysis

### **API Endpoints**
- **Backend API**: http://localhost:8000
  - `/docs` - API documentation
  - `/health` - System status
  - `/config` - Configuration

### **Data Files**
- **Live Data**: `data/live_tep_data.csv`
- **Analysis Results**: `data/llm_analyses.csv`
- **System Events**: `data/system_events.csv`

## 🎮 **Basic Usage**

### **Step 1: Start Normal Operation**
1. All terminals running ✅
2. TEP simulator shows "Normal Operation" 
3. FaultExplainer shows steady data flow
4. No anomalies detected

### **Step 2: Inject a Fault**
```bash
# In TEP simulator terminal, you'll see fault controls
# Or use the web interface to set:
Fault Type: 4 (Cooling Water)
Fault Intensity: 1.0
```

### **Step 3: Watch Analysis**
1. **TEP Simulator**: Variables start changing
2. **Data Bridge**: Buffer fills up (20 data points)
3. **FaultExplainer**: PCA detects anomaly
4. **LLM Analysis**: Claude provides diagnosis

### **Step 4: View Results**
1. Open http://localhost:5173
2. Click **"Assistant"** tab 🤖
3. Select fault data file
4. Click **"Explain"** button
5. Read AI fault diagnosis

## ⚡ **Quick Test Sequence**

### **Test 1: System Health**
```bash
# Check all services
curl http://localhost:8000/health
curl http://localhost:5173  # Should load webpage
ls data/live_tep_data.csv   # Should exist and grow
```

### **Test 2: Fault Injection**
```bash
# Inject Fault 4 (Cooling Water) for 10 minutes
# Watch for:
# - Temperature increase in TEP
# - Anomaly detection in bridge logs  
# - LLM analysis in web interface
```

### **Test 3: LLM Analysis**
```bash
# In web interface:
# 1. Go to Assistant tab
# 2. Select "fault4.csv" 
# 3. Click "Explain"
# 4. Should see Claude analysis within 30 seconds
```

## 🔧 **Alternative Startup Options**

### **Option 1: Web-Only TEP**
```bash
source tep_env/bin/activate
python fast_tep_dashboard.py
# TEP web interface: http://localhost:5000
```

### **Option 2: Simple Backend**
```bash
source tep_env/bin/activate  
python simple_fault_backend.py
# Simplified API: http://localhost:8000
```

### **Option 3: Desktop GUI**
```bash
source tep_env/bin/activate
python simulators/live/live_tep_simulator.py
# Tkinter desktop interface
```

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **"tep2py not found"**
```bash
cd external_repos/tep2py-master
ls temain_mod.cpython-39-darwin.so  # Should exist
python -c "import tep2py"  # Should work
```

#### **"Port already in use"**
```bash
# Kill existing processes
lsof -ti:8000 | xargs kill  # Backend
lsof -ti:5173 | xargs kill  # Frontend
```

#### **"npm command not found"**
```bash
# Install Node.js
brew install node  # macOS
# or download from nodejs.org
```

#### **"Claude API error"**
```bash
# Check API key in config
cat external_repos/FaultExplainer-main/config.json
# Should show your Claude API key
```

### **System Status Check**
```bash
# Quick health check script
source tep_env/bin/activate
python -c "
import requests
import os

# Check TEP data
if os.path.exists('data/live_tep_data.csv'):
    print('✅ TEP data file exists')
else:
    print('❌ TEP data file missing')

# Check backend
try:
    r = requests.get('http://localhost:8000/health')
    print('✅ Backend responding')
except:
    print('❌ Backend not responding')

# Check frontend  
try:
    r = requests.get('http://localhost:5173')
    print('✅ Frontend responding')
except:
    print('❌ Frontend not responding')
"
```

## 📊 **Expected Behavior**

### **Normal Operation (First 5 minutes)**
- TEP variables stable around baseline values
- No anomalies detected
- Bridge processes data every 20 points
- No LLM analysis triggered

### **Fault Injection (After fault activated)**
- TEP variables start deviating
- PCA detects anomalies within 6 minutes
- LLM analysis triggered within 12 minutes
- Web interface shows fault explanation

### **Performance Expectations**
- **TEP Simulation**: 1 data point per 3 minutes
- **PCA Analysis**: <1 second per window
- **Claude Analysis**: 5-15 seconds
- **Web Interface**: Real-time updates

## 🎯 **Success Indicators**

✅ **All terminals show activity**
✅ **Web interface loads at localhost:5173**
✅ **TEP data file grows over time**
✅ **Bridge shows "Buffer size: X/20" messages**
✅ **LLM analysis appears in Assistant tab**

**You now have a complete industrial AI fault detection system running!** 🎉

## 📚 **Next Steps**

1. **Experiment with different fault types** (IDV 1, 4, 6, 8, 13)
2. **Compare Claude vs LMStudio responses**
3. **Analyze the T² statistics in Fault History tab**
4. **Export data for further analysis**
5. **Customize the system configuration**

The system is designed for **industrial-grade reliability** and **professional fault analysis**.
