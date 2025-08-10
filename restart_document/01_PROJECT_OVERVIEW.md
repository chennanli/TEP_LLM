# 🏭 TEP FaultExplainer System - Project Overview

## 🎯 **System Purpose**

This is a **complete industrial fault detection and diagnosis system** that combines:
- **Real-time Tennessee Eastman Process (TEP) simulation** with authentic chemical engineering physics
- **AI-powered fault analysis** using PCA anomaly detection + Multi-LLM diagnosis
- **Industrial-grade web interfaces** for monitoring and control

## 🏗️ **Two Main Projects Architecture**

### **Project 1: TEP Dynamic Simulator** 🔬
**Location**: Root directory + `simulators/` folder
**Purpose**: Physics-based chemical process simulation with GUI interfaces

### **Project 2: FaultExplainer** 🤖  
**Location**: `external_repos/FaultExplainer-main/`
**Purpose**: AI-powered fault analysis with React frontend + FastAPI backend

## 🔄 **System Integration**

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   TEP Simulator     │    │   Data Bridge        │    │  FaultExplainer     │
│   (Project 1)       │───▶│  tep_faultexplainer  │───▶│   (Project 2)       │
│                     │    │  _bridge.py          │    │                     │
│ • Real tep2py       │    │                      │    │ • PCA Analysis      │
│ • 52 variables      │    │ • Variable mapping   │    │ • Multi-LLM         │
│ • Fault injection   │    │ • Time windowing     │    │ • Web interface     │
│ • Multiple GUIs     │    │ • Format conversion  │    │ • Visualization     │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
```

## 🎛️ **Key Features**

### **Industrial Realism**
- **Authentic TEP Physics**: Uses compiled Fortran code (`tep2py`) from academic research
- **52 Process Variables**: 41 measurements (XMEAS) + 11 manipulated variables (XMV)
- **20 Fault Types**: IDV 1-20 representing real industrial disturbances
- **Chemical Process**: Ethylene Oxide/Ethylene Glycol production simulation

### **AI-Powered Analysis**
- **PCA Anomaly Detection**: T² statistics with configurable thresholds
- **Multi-LLM Diagnosis**: Claude 3.5 Sonnet + LMStudio local models
- **Feature Analysis**: Identifies top contributing variables to faults
- **Natural Language Explanations**: Industrial-grade fault diagnosis reports

### **Professional Interfaces**
- **React Frontend**: Modern web interface with real-time charts
- **Multiple TEP GUIs**: Tkinter, Flask, Qt5 options
- **Control Panels**: Unified system management
- **Data Visualization**: Time series plots, anomaly detection charts

## 📊 **Data Flow**

1. **TEP Simulation** generates authentic process data (every 3 minutes simulation time)
2. **Data Bridge** converts TEP format to FaultExplainer format
3. **PCA Model** detects anomalies using sliding window (20 data points)
4. **LLM Analysis** provides natural language fault diagnosis
5. **Web Interface** displays results with interactive charts

## 🔧 **Technology Stack Summary**

### **TEP Simulator (Project 1)**
- **Core**: Python + Fortran (tep2py)
- **GUI**: Tkinter, Flask, Qt5
- **Data**: NumPy, Pandas, Matplotlib
- **Real-time**: Threading, WebSocket

### **FaultExplainer (Project 2)**
- **Frontend**: React + TypeScript + Vite
- **Backend**: FastAPI + Python
- **AI**: Anthropic Claude, LMStudio
- **Analysis**: Scikit-learn (PCA), NumPy
- **UI**: Mantine, D3.js, Recharts

## 🚀 **Current Status**

✅ **Fully Functional System**
- TEP simulator with real physics
- Multi-LLM fault analysis (Claude + LMStudio)
- Complete web interface
- Data bridge connecting both projects
- Professional documentation

✅ **Ready for Production Use**
- Industrial-grade timing (3min → 6min → 12min)
- Robust error handling
- Multiple startup options
- Comprehensive logging

## 📁 **Project Structure**

```
TE/                                    # Root directory
├── simulators/                        # TEP Simulator (Project 1)
├── external_repos/FaultExplainer-main/  # FaultExplainer (Project 2)
├── tep_faultexplainer_bridge.py      # Integration bridge
├── data/                              # Shared data directory
├── tep_env/                           # Python virtual environment
└── restart_document/                  # This documentation
```

This system represents a **complete industrial AI solution** combining authentic process simulation with modern AI analysis capabilities.
