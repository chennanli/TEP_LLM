# 🏭 Complete TEP-FaultExplainer System Guide

## 🎯 **What You Actually Have Now**

You have a **complete industrial fault detection system** with these components:

### **1. TEP Dynamic Simulator** 
- **Real physics-based simulation** of Tennessee Eastman Process
- **Generates live sensor data** (52 variables) every 3 minutes
- **Fault injection capability** via IDV controls (0.0 to 1.0)
- **Saves data to**: `data/live_tep_data.csv`

### **2. FaultExplainer Analysis Engine**
- **PCA-based anomaly detection** (T² statistics)
- **Multi-LLM fault diagnosis** (Gemini + LMStudio)
- **Web-based visualization** interface
- **Trained on TEP fault patterns**

### **3. Data Bridge** (NEW!)
- **Connects live TEP data to FaultExplainer**
- **Real-time data flow** monitoring
- **Variable name mapping** (XMEAS → FaultExplainer format)
- **Time window buffering** for analysis

### **4. Visual Dashboard** (NEW!)
- **Live system monitoring** 
- **Real-time data display**
- **System status checking**
- **Complete data flow visualization**

---

## 🚀 **How to Start the Complete System**

### **Terminal 1: TEP Simulation**
```bash
cd /Users/chennanli/Desktop/LLM_Project/TE
source tep_env/bin/activate
python real_tep_simulator.py
```
**What it does**: Generates live industrial process data every 3 minutes

### **Terminal 2: FaultExplainer Backend**
```bash
cd /Users/chennanli/Desktop/LLM_Project/TE
cd external_repos/FaultExplainer-main/backend
source ../../../tep_env/bin/activate
python app.py
```
**What it does**: Runs analysis engine on port 8000

### **Terminal 3: FaultExplainer Frontend**
```bash
cd /Users/chennanli/Desktop/LLM_Project/TE
cd external_repos/FaultExplainer-main/frontend
npm run dev
```
**What it does**: Runs web interface on port 5173

### **Terminal 4: Data Bridge**
```bash
cd /Users/chennanli/Desktop/LLM_Project/TE
source tep_env/bin/activate
python tep_faultexplainer_bridge.py
```
**What it does**: Connects TEP data to FaultExplainer analysis

### **Terminal 5: System Dashboard**
```bash
cd /Users/chennanli/Desktop/LLM_Project/TE
source tep_env/bin/activate
python working_system_dashboard.py
```
**What it does**: Shows live system status and data flow

---

## 🌐 **Access Points**

### **Main Interfaces:**
- **FaultExplainer UI**: http://localhost:5173 (fault analysis & visualization)
- **System Dashboard**: GUI window (live data monitoring)
- **Backend API**: http://localhost:8000 (raw analysis endpoints)

### **Data Files:**
- **Live TEP Data**: `data/live_tep_data.csv`
- **Analysis Results**: `data/pca_results.csv`, `data/llm_analyses.csv`

---

## 🔄 **Complete Data Flow**

```
TEP Simulation → CSV File → Data Bridge → FaultExplainer → Web UI
     ↓              ↓           ↓             ↓           ↓
  Physics        Live Data   Variable     PCA + LLM   Visualization
 Equations       Storage     Mapping      Analysis    & Diagnosis
```

### **Step-by-Step Process:**
1. **TEP Simulator** runs physics equations → generates sensor readings
2. **CSV Export** saves data with timestamp and step number
3. **Data Bridge** reads new data → maps variable names → buffers time windows
4. **FaultExplainer** receives time windows → runs PCA analysis → detects anomalies
5. **LLM Analysis** explains detected faults → provides diagnosis
6. **Web Interface** displays results → shows trends and explanations

---

## 🎛️ **How to Use the System**

### **Normal Operation:**
1. **Start all 5 terminals** as shown above
2. **Wait for data accumulation** (need ~20 data points for analysis)
3. **Monitor the dashboard** for system status
4. **View analysis in web UI** at http://localhost:5173

### **Fault Injection:**
1. **Modify TEP simulation** to inject faults (edit `real_tep_simulator.py`)
2. **Set IDV values** between 0.0 (no fault) and 1.0 (maximum fault)
3. **Watch anomaly detection** trigger in FaultExplainer
4. **Get LLM explanations** of the detected fault patterns

### **Data Analysis:**
- **Real-time monitoring**: System dashboard shows live variables
- **Fault detection**: PCA T² statistics detect anomalies  
- **Root cause analysis**: LLM explains what caused the fault
- **Historical trends**: Web UI shows data over time

---

## 🔧 **Key Features**

### **✅ Industrial Realism:**
- **Physics-based simulation** (not random data)
- **Authentic fault scenarios** (based on real chemical plant)
- **Realistic timing** (3-minute intervals like real plants)

### **✅ Advanced Analytics:**
- **PCA anomaly detection** (industry standard)
- **Multi-LLM analysis** (Gemini + local models)
- **Time series analysis** (sliding window approach)

### **✅ Complete Integration:**
- **Live data flow** (simulation → analysis → visualization)
- **Real-time processing** (automatic fault detection)
- **Web-based interface** (modern, interactive UI)

---

## 🎯 **What Makes This Special**

This is **NOT just two separate apps**. This is a **complete industrial fault detection system** where:

1. **TEP generates realistic industrial data** (like a real chemical plant)
2. **Data flows automatically** to the analysis engine
3. **AI detects and explains faults** in real-time
4. **Everything is connected** and works together

**You now have a professional-grade industrial AI system!** 🏭✨

---

## 💡 **Next Steps**

1. **Start all components** following the terminal instructions
2. **Let it run for 10-15 minutes** to accumulate data
3. **Inject a fault** by modifying IDV values
4. **Watch the AI detect and explain** the fault
5. **Explore the web interface** for detailed analysis

**This is exactly how real industrial AI systems work!** 🎉
