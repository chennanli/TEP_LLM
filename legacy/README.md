# TEP Legacy System

This folder contains the original working TEP system that was developed as a proof-of-concept.

## 🎯 **What's Here**
- **unified_tep_control_panel.py** - Main control panel with Flask web interface
- **tep_bridge.py** - Bridge between TEP simulator and other components
- **external_repos/** - External dependencies and repositories
- **data/** - Generated simulation data and results
- **logs/** - System logs and debugging information

## 🚀 **How to Run Legacy System**

### **Method 1: Quick Start (Recommended)**
```bash
# Navigate to legacy folder
cd legacy

# Run startup script
./start_legacy_system.sh

# Access at http://localhost:9001
```

### **Method 2: Manual Start**
```bash
# Activate virtual environment
source ../tep_env/bin/activate

# Run the unified control panel
python unified_tep_control_panel.py

# Access at http://localhost:9001
```

### **Optional: Enable RAG (Knowledge Base) Features**
```bash
# Install RAG dependencies (optional)
./install_rag_dependencies.sh

# Add PDF documents to:
# external_repos/FaultExplainer-main/log_materials/

# Then start system normally
./start_legacy_system.sh
```

## 📊 **System Components**
- **TEP Simulator** - Tennessee Eastman Process dynamic simulation
- **PCA Anomaly Detection** - Principal Component Analysis for fault detection
- **Multi-LLM Analysis** - Claude, Gemini, and local LLM integration
- **Web Interface** - Flask-based control panel

## 🔄 **Migration Status**
This system is being migrated to the production-ready architecture in `../integration/`.
The legacy system remains functional and can be used as a reference or backup.

## 📚 **Documentation**
See `../docs/` for comprehensive documentation and migration guides.
