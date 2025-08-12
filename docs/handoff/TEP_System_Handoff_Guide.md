# TEP System Handoff Guide for Developers & AI Assistants

## 🎯 **Quick Start Context**

This document provides essential context for anyone (human developer or AI assistant) taking over the TEP (Tennessee Eastman Process) monitoring and fault analysis system.

### **Current System State** (as of August 12, 2025)
- ✅ **Fully functional** TEP monitoring with enhanced operational ranges
- ✅ **Dual architecture**: Integration folder (production) + Legacy folders (reference)
- ✅ **Multi-LLM support**: Claude, Gemini, LM Studio integration
- ✅ **Real-time monitoring**: Dynamic simulation with PCA anomaly detection
- ✅ **Industrial-grade UI**: Professional process monitoring interface

## 📁 **Project Structure Overview**

```
TE/
├── integration/                    # 🎯 MAIN PRODUCTION SYSTEM
│   ├── src/frontend/              # React frontend (Mantine UI)
│   ├── src/backend/               # FastAPI backend
│   └── src/simulator/             # TEP Fortran simulator
├── legacy/external_repos/         # 📚 REFERENCE SYSTEMS
│   ├── FaultExplainer-main/       # Original implementation
│   └── FaultExplainer-MultiLLM/   # Multi-LLM variant
├── docs/                          # 📖 DOCUMENTATION
│   ├── conversation-summaries/    # Session summaries
│   └── handoff/                   # This file
└── data/                          # 📊 TEP simulation data
```

### **🚨 IMPORTANT**: Always work in `integration/` folder for production changes!

## 🔧 **Recent Major Enhancements** (August 12, 2025)

### **1. Enhanced TEP Monitoring System**
**What was done**: Added comprehensive operational ranges for 33 TEP variables
**Files modified**:
- `integration/src/frontend/src/pages/PlotPage.tsx`
- `legacy/external_repos/FaultExplainer-main/frontend/src/pages/PlotPage.tsx`
- `legacy/external_repos/FaultExplainer-MultiLLM/frontend/src/pages/PlotPage.tsx`

**Key improvements**:
- ✅ Realistic operational ranges based on actual simulation data
- ✅ Smart Y-axis scaling (50% padding around ranges)
- ✅ Intelligent plot ordering (largest ranges first)
- ✅ Safety-critical variable identification (🚨 indicators)

### **2. Fixed LLM Attribution**
**What was done**: Corrected display name mapping in LLM analysis results
**Files modified**:
- `integration/src/frontend/src/pages/ComparativeLLMResults.tsx`
- `legacy/external_repos/FaultExplainer-main/frontend/src/pages/ComparativeLLMResults.tsx`

**Fix applied**:
```typescript
// Corrected mapping
const nameMap = {
  'anthropic': 'Claude',    // Was showing 'LM Studio'
  'gemini': 'Gemini',       // Was showing 'Claude'
  'lmstudio': 'LM Studio'   // Added support
};
```

## 🚀 **How to Run the System**

### **Prerequisites**:
1. **Virtual Environment**: Always use `tep_env` virtual environment
2. **API Keys**: Anthropic (Claude) and Google (Gemini) keys configured
3. **Browser**: Safari-compatible JavaScript (user preference)

### **Startup Sequence**:
```bash
# 1. Activate virtual environment
source tep_env/bin/activate

# 2. Start backend (from integration folder)
cd integration/src/backend
python main.py

# 3. Start frontend (new terminal)
cd integration/src/frontend
npm start

# 4. Access system
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

## 🎛️ **Key System Components**

### **1. TEP Simulator**
- **Location**: `integration/src/simulator/`
- **Type**: Fortran-based Tennessee Eastman Process simulation
- **Function**: Generates real-time process data every 3 minutes
- **Data**: 52 variables (22 XMEAS measurements + 11 XMV inputs + compositions)

### **2. Frontend Monitoring**
- **Framework**: React + Mantine UI
- **Key Pages**:
  - `PlotPage.tsx`: Real-time process monitoring with operational ranges
  - `ComparativeLLMResults.tsx`: Multi-LLM fault analysis results
- **Features**: 
  - Dynamic Y-axis scaling
  - Operational range indicators
  - Safety-critical variable highlighting

### **3. Backend API**
- **Framework**: FastAPI
- **Functions**:
  - TEP data collection and storage
  - PCA anomaly detection
  - Multi-LLM integration (Claude, Gemini, LM Studio)
  - Real-time data streaming

### **4. LLM Integration**
- **Primary**: Claude (Anthropic API)
- **Secondary**: Gemini (Google API)
- **Backup**: LM Studio (local Mistral Small)
- **Function**: Root cause analysis of process anomalies

## 📊 **TEP Variable Ranges** (Current Configuration)

### **Critical Variables** (🚨 Safety-Critical):
- **Reactor Pressure**: 2650-2750 kPa
- **Reactor Temperature**: 120.2-120.6°C
- **Reactor Level**: 70-80%
- **Product Sep Level**: 45-55%
- **Compressor recycle valve**: 15-35%
- **Separator liquid load**: 30-50%
- **Stripper liquid load**: 35-55%
- **Reactor coolant load**: 35-55%

### **Process Variables** (Wide Ranges):
- **D Feed**: 3500-3800 kg/h
- **E Feed**: 4300-4700 kg/h
- **A and C Feed**: 8.5-10.0 kscmh
- **Stripper Steam Flow**: 220-250 kg/h

## 🔍 **Common Troubleshooting**

### **Frontend Issues**:
1. **Charts not loading**: Check backend API connection
2. **Range lines not visible**: Verify TEP_RANGES object in PlotPage.tsx
3. **Wrong LLM attribution**: Check nameMap in ComparativeLLMResults.tsx
4. **Safari compatibility**: Ensure ES5/ASCII JavaScript, avoid modern syntax

### **Backend Issues**:
1. **TEP simulator not running**: Check Fortran compilation and execution
2. **LLM API failures**: Verify API keys in environment variables
3. **Data not updating**: Check 3-minute simulation cycle timing

### **Integration vs Legacy**:
- **Always modify integration folder first**
- **Legacy folders are for reference only**
- **Keep both systems synchronized for consistency**

## 📋 **Development Guidelines**

### **For Human Developers**:
1. **Use virtual environment**: Always activate `tep_env`
2. **Test in Safari**: User's primary browser
3. **Industrial UX**: Focus on process monitoring usability
4. **Safety first**: Prioritize safety-critical variables

### **For AI Assistants**:
1. **Read this file first**: Understand current system state
2. **Check conversation summaries**: Review recent changes
3. **Use codebase-retrieval**: Get detailed code context before changes
4. **Maintain consistency**: Apply changes to both integration and legacy
5. **Document changes**: Update conversation summaries

## 🎯 **Current Priorities & Next Steps**

### **Immediate Tasks**:
- ✅ Enhanced monitoring system (COMPLETED)
- ✅ LLM attribution fixes (COMPLETED)
- ✅ Intelligent plot ordering (COMPLETED)

### **Future Enhancements**:
- [ ] Real-time range violation alerts
- [ ] Historical performance analytics
- [ ] User-customizable plot ordering
- [ ] Advanced anomaly detection models
- [ ] RAG system with chemical engineering knowledge base

### **Long-term Vision**:
- Industrial-grade process control system
- Multi-database integration (TDengine, MySQL, Snowflake)
- Advanced process control optimization
- Containerized deployment ready

## 📞 **User Preferences & Context**

### **Technical Preferences**:
- **OS**: Mac with Safari browser
- **Python**: Virtual environment required
- **UI**: Visual interfaces over terminal-based
- **Architecture**: Modular, replaceable components
- **Documentation**: SDD (Specs Driven Development) approach

### **Project Context**:
- **Goal**: Industrial process monitoring and fault analysis
- **Approach**: TEP simulator → PCA anomaly detection → LLM analysis
- **Timeline**: Batch analysis first, real-time implementation later
- **License**: Non-commercial (CC BY-NC, AGPL, GPL preferred)

## 📖 **Additional Resources**

### **Documentation Files**:
- `docs/conversation-summaries/`: Detailed session logs
- `docs/TEP_VARIABLES.md`: Complete variable documentation
- `docs/TEP_Input_Output_Documentation.md`: I/O specifications

### **Data Sources**:
- `data/live_tep_data.csv`: Real simulation data for range calibration
- TEP Fortran simulator: Original process equations

### **External References**:
- FaultExplainer paper: arxiv.org/pdf/2412.14492
- Tennessee Eastman Process: Industrial benchmark simulation

---

**🎯 SUCCESS INDICATOR**: If you can start the system, see operational ranges on charts, and get correct LLM attribution, the handoff is successful!

**📧 HANDOFF COMPLETE**: System ready for continued development with enhanced monitoring capabilities.**
