# 📚 TEP FaultExplainer System - Restart Documentation

## 🎯 **Documentation Overview**

This folder contains comprehensive documentation for the complete TEP FaultExplainer system, designed to help you understand, restart, and work with both integrated projects.

## 📁 **Documentation Structure**

### **📋 [01_PROJECT_OVERVIEW.md](01_PROJECT_OVERVIEW.md)**
- **Purpose**: High-level system architecture and goals
- **Content**: Two-project integration, data flow, key features
- **Audience**: Anyone wanting to understand the complete system

### **🔬 [02_TEP_SIMULATOR_PROJECT.md](02_TEP_SIMULATOR_PROJECT.md)**
- **Purpose**: Deep dive into the TEP dynamic simulator (Project 1)
- **Content**: Physics engine, GUI options, simulation flow, file structure
- **Audience**: Developers working on simulation components

### **🤖 [03_FAULTEXPLAINER_PROJECT.md](03_FAULTEXPLAINER_PROJECT.md)**
- **Purpose**: Complete analysis of the FaultExplainer AI system (Project 2)
- **Content**: React frontend, FastAPI backend, LLM integration, PCA analysis
- **Audience**: Developers working on AI analysis components

### **🌉 [04_SYSTEM_INTEGRATION.md](04_SYSTEM_INTEGRATION.md)**
- **Purpose**: How the two projects connect and communicate
- **Content**: Data bridge, variable mapping, timing, API integration
- **Audience**: System integrators and DevOps engineers

### **🚀 [05_QUICK_START_GUIDE.md](05_QUICK_START_GUIDE.md)**
- **Purpose**: Get the complete system running in 5 minutes
- **Content**: Step-by-step startup, troubleshooting, basic usage
- **Audience**: Anyone wanting to run the system immediately

### **🛠️ [06_TECH_STACK_SUMMARY.md](06_TECH_STACK_SUMMARY.md)**
- **Purpose**: Complete technology inventory and dependencies
- **Content**: All frameworks, libraries, tools, versions, configurations
- **Audience**: Technical architects and system administrators

## 🎯 **Quick Navigation**

### **🆕 New to the System?**
Start with: **[01_PROJECT_OVERVIEW.md](01_PROJECT_OVERVIEW.md)** → **[05_QUICK_START_GUIDE.md](05_QUICK_START_GUIDE.md)**

### **🔧 Want to Develop?**
Read: **[02_TEP_SIMULATOR_PROJECT.md](02_TEP_SIMULATOR_PROJECT.md)** + **[03_FAULTEXPLAINER_PROJECT.md](03_FAULTEXPLAINER_PROJECT.md)**

### **🌉 Need Integration Details?**
Focus on: **[04_SYSTEM_INTEGRATION.md](04_SYSTEM_INTEGRATION.md)**

### **📊 Planning Deployment?**
Review: **[06_TECH_STACK_SUMMARY.md](06_TECH_STACK_SUMMARY.md)**

## 🏗️ **System Architecture Summary**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TEP FaultExplainer System                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────┐ │
│  │   TEP Simulator     │    │   Data Bridge        │    │ FaultExplainer  │ │
│  │   (Project 1)       │◄──►│   Integration        │◄──►│ (Project 2)     │ │
│  │                     │    │                      │    │                 │ │
│  │ • Real tep2py       │    │ • Variable mapping   │    │ • React UI      │ │
│  │ • 52 variables      │    │ • Time windowing     │    │ • FastAPI       │ │
│  │ • Fault injection   │    │ • Format conversion  │    │ • Multi-LLM     │ │
│  │ • Multiple GUIs     │    │ • API communication  │    │ • PCA analysis  │ │
│  └─────────────────────┘    └──────────────────────┘    └─────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🚀 **Quick Start Summary**

### **5-Terminal Startup**
```bash
# Terminal 1: TEP Simulator
source tep_env/bin/activate && python real_tep_simulator.py

# Terminal 2: FaultExplainer Backend  
cd external_repos/FaultExplainer-main/backend
source ../../../tep_env/bin/activate && python app.py

# Terminal 3: FaultExplainer Frontend
cd external_repos/FaultExplainer-main/frontend && npm run dev

# Terminal 4: Data Bridge
source tep_env/bin/activate && python tep_faultexplainer_bridge.py

# Terminal 5: System Monitor (Optional)
source tep_env/bin/activate && python working_system_dashboard.py
```

### **Access Points**
- **Main Interface**: http://localhost:5173 (FaultExplainer Web UI)
- **Backend API**: http://localhost:8000 (FastAPI with docs)
- **System Data**: `data/live_tep_data.csv` (Live simulation data)

## 🎯 **Key Features**

### **Industrial Realism**
- ✅ **Authentic TEP Physics**: Compiled Fortran simulation from academic research
- ✅ **52 Process Variables**: Complete industrial process monitoring
- ✅ **20 Fault Types**: Real industrial disturbances (IDV 1-20)
- ✅ **Chemical Process**: Ethylene Oxide/Ethylene Glycol production

### **AI-Powered Analysis**
- ✅ **PCA Anomaly Detection**: T² statistics with configurable thresholds
- ✅ **Multi-LLM Diagnosis**: Claude 3.5 Sonnet + LMStudio local models
- ✅ **Feature Analysis**: Top contributing variables identification
- ✅ **Natural Language**: Industrial-grade fault diagnosis reports

### **Professional Interfaces**
- ✅ **React Frontend**: Modern web interface with real-time charts
- ✅ **Multiple TEP GUIs**: Tkinter, Flask, Qt5 options
- ✅ **Unified Control**: System management dashboard
- ✅ **Data Visualization**: Time series, anomaly detection, T² statistics

## 📊 **Technology Stack Overview**

### **Project 1: TEP Simulator**
- **Core**: Python + Fortran (tep2py)
- **GUI**: Tkinter, Flask, Qt5
- **Data**: NumPy, Pandas, Matplotlib
- **Real-time**: Threading, WebSocket

### **Project 2: FaultExplainer**
- **Frontend**: React + TypeScript + Vite
- **Backend**: FastAPI + Python
- **AI**: Anthropic Claude, LMStudio
- **Analysis**: Scikit-learn (PCA), NumPy
- **UI**: Mantine, D3.js, Recharts

### **Integration**
- **Bridge**: Python data processing
- **Communication**: HTTP REST APIs
- **Data Flow**: CSV → JSON → Analysis
- **Timing**: Industrial hierarchy (3min → 6min → 12min)

## 🔧 **Current Configuration**

### **LLM Models**
- ✅ **Claude 3.5 Sonnet**: Primary AI analysis (API: `your-anthropic-api-key-here`)
- ✅ **LMStudio**: Local backup model (URL: `http://localhost:1234/v1`)
- ❌ **Google Gemini**: Disabled (replaced with Claude)

### **System Status**
- ✅ **Virtual Environment**: `tep_env/` activated and configured
- ✅ **Dependencies**: All packages installed and tested
- ✅ **API Integration**: Claude API tested and working
- ✅ **Data Flow**: Complete pipeline tested
- ✅ **Documentation**: Comprehensive restart guides created

## 📚 **Additional Resources**

### **In Main Directory**
- `conversation_history.md` - Complete development history
- `API_UPDATE_SUMMARY.md` - Recent API configuration changes
- `COMPLETE_SYSTEM_GUIDE.md` - Detailed operational guide

### **Configuration Files**
- `external_repos/FaultExplainer-main/config.json` - LLM settings
- `requirements.txt` - Python dependencies
- `external_repos/FaultExplainer-main/frontend/package.json` - Node.js dependencies

## 🎉 **System Status: READY FOR PRODUCTION**

This system represents a **complete industrial AI solution** combining:
- ✅ Authentic process simulation
- ✅ Modern AI analysis
- ✅ Professional web interfaces  
- ✅ Industrial-grade reliability
- ✅ Comprehensive documentation

**Ready to detect and diagnose industrial faults with AI!** 🚀

---

*Documentation created by Augment Agent - Last updated: 2025-01-08*
