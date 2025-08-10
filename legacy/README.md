# TEP Legacy System

This folder contains the original working TEP system that was developed as a proof-of-concept.

## 🎯 **What's Here**
- **unified_tep_control_panel.py** - Main control panel with Flask web interface
- **tep_bridge.py** - Bridge between TEP simulator and other components
- **external_repos/** - External dependencies and repositories
- **data/** - Generated simulation data and results
- **logs/** - System logs and debugging information

## 🚀 **How to Run Legacy System**
```bash
# Activate virtual environment
source ../tep_env/bin/activate

# Run the unified control panel
python unified_tep_control_panel.py

# Access at http://localhost:9001
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
