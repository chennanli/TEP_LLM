# 🎛️ Unified TEP-FaultExplainer Solution

## ✅ **SOLUTION SUMMARY**

I've created a **unified control panel** that addresses all your requirements:

1. **✅ Keeps the good work**: Data queue from dynamic simulation
2. **✅ Fixes all mistakes**: Correct IDV ranges (0-1), threshold (0.01)
3. **✅ Proper timing**: 3min → 6min → 12min hierarchy
4. **✅ Single interface**: No more manual process management
5. **✅ Uses original FaultExplainer**: Backend + frontend integration
6. **✅ Accurate results**: No more random changes

## 🚀 **QUICK START**

```bash
# 1. Setup (one-time)
./setup_faultexplainer.sh

# 2. Start unified control panel
source tep_env/bin/activate
python unified_tep_control_panel.py

# 3. Open browser
# http://localhost:9001
```

## 📊 **DATA FLOW ARCHITECTURE**

```
TEP Dynamic Simulation (tep2py)
    ↓ Every 3 minutes
Raw Data Queue (1000 points)
    ↓ Every 6 minutes (half speed)
PCA Analysis Queue (500 points)
    ↓ Every 12 minutes (quarter speed)
LLM Diagnosis Queue (250 points)
    ↓ 
FaultExplainer Backend/Frontend
```

## 🎛️ **UNIFIED CONTROL PANEL FEATURES**

### **Single Interface Controls:**
- **🏭 TEP Simulation**: Start/stop dynamic simulation
- **🔍 Backend**: Start FaultExplainer analysis engine
- **🖥️ Frontend**: Start React visualization interface
- **🛑 Emergency Stop**: Kill all processes

### **Corrected IDV Controls:**
- **Range**: 0.0 to 1.0 (standard TEP, not 0-2)
- **Variables**: IDV_1, IDV_4, IDV_6, IDV_8, IDV_13
- **Real-time**: Changes affect running simulation

### **Status Monitoring:**
- **TEP Status**: Running/stopped, current step
- **Data Counts**: Raw/PCA/LLM queue sizes
- **Process Status**: Backend/frontend health
- **Auto-refresh**: Every 5 seconds

## 🔧 **TECHNICAL IMPLEMENTATION**

### **TEPDataBridge Class:**
```python
# Correct IDV range (0.0 to 1.0)
def set_idv(self, idv_num, value):
    if 1 <= idv_num <= 20 and 0.0 <= value <= 1.0:
        self.idv_values[idv_num - 1] = value

# Proper timing hierarchy
self.pca_interval = 6 * 60    # 6 minutes
self.llm_interval = 12 * 60   # 12 minutes
```

### **Data Export for FaultExplainer:**
```python
# Saves in FaultExplainer CSV format
def save_data_for_faultexplainer(self, data_point):
    # Header: timestamp, step, XMEAS_1...41, XMV_1...11, IDV_1...20
    # Uses original FaultExplainer data structure
```

### **Process Management:**
```python
# Starts original FaultExplainer components
def start_faultexplainer_backend(self):
    # Runs: python app.py in backend/
    
def start_faultexplainer_frontend(self):
    # Runs: npm start in frontend/
```

## 📈 **CORRECTED VALUES**

| Component | Previous (Wrong) | Current (Correct) | Source |
|-----------|------------------|-------------------|---------|
| IDV Range | 0.0 - 2.0 | **0.0 - 1.0** | TEP Standard |
| Anomaly Threshold | 30.0 | **0.01** | FaultExplainer config.json |
| Timing | 5s refresh | **3min → 6min → 12min** | Your specification |
| Interface | Flask refresh | **React + Flask API** | Original FaultExplainer |

## 🎯 **USAGE WORKFLOW**

### **Step 1: Start Control Panel**
```bash
python unified_tep_control_panel.py
# Opens: http://localhost:9001
```

### **Step 2: Start Components (in order)**
1. **Click "▶️ Start TEP Simulation"**
   - Begins real tep2py simulation
   - 3-minute intervals
   - Saves data to CSV

2. **Click "▶️ Start Backend"**
   - Starts FaultExplainer analysis engine
   - Port 5000
   - Uses correct threshold (0.01)

3. **Click "▶️ Start Frontend"**
   - Starts React interface
   - Port 3000
   - Original FaultExplainer UI

### **Step 3: Inject Faults**
- **Use IDV sliders**: 0.0 (normal) to 1.0 (full fault)
- **Real-time effect**: Changes immediately affect simulation
- **Proper timing**: PCA every 6min, LLM every 12min

### **Step 4: Monitor Results**
- **FaultExplainer UI**: http://localhost:3000
- **Control Panel**: Real-time status updates
- **Data Flow**: Watch queue sizes grow

## 🔍 **TROUBLESHOOTING**

### **If TEP Simulation Fails:**
```bash
# Check tep2py installation
cd external_repos/tep2py-master
python -c "import tep2py; print('OK')"
```

### **If Frontend Won't Start:**
```bash
# Install dependencies
cd external_repos/FaultExplainer-main/frontend
npm install
```

### **If Backend Fails:**
```bash
# Install Python dependencies
cd external_repos/FaultExplainer-main/backend
pip install -r requirements.txt
```

## 📊 **DATA VERIFICATION**

### **Check Live Data:**
```bash
# View generated CSV
head -5 data/live_tep_data.csv

# Should show: timestamp,step,XMEAS_1...41,XMV_1...11,IDV_1...20
```

### **Verify Timing:**
- **TEP logs**: "Simulation is done" every 3 minutes
- **PCA logs**: "PCA data point added" every 6 minutes  
- **LLM logs**: "LLM data point added" every 12 minutes

## 🎉 **BENEFITS OF THIS SOLUTION**

1. **✅ Single Interface**: No more manual process management
2. **✅ Correct Values**: IDV 0-1, threshold 0.01
3. **✅ Proper Timing**: Prevents LLM overload
4. **✅ Real Integration**: Uses original FaultExplainer
5. **✅ Live Data**: Dynamic simulation feeds FaultExplainer
6. **✅ Accurate Results**: No more random changes

## 🔗 **QUICK ACCESS LINKS**

- **Control Panel**: http://localhost:9001
- **FaultExplainer UI**: http://localhost:3000 (after starting)
- **Backend API**: http://localhost:5000 (after starting)

This solution maintains the **good work** (data queues) while **fixing all mistakes** (values, timing, integration) and providing a **single, easy-to-use interface**.
