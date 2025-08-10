# 🏭 TEP Industrial Intelligence Platform

A comprehensive industrial intelligence platform for Tennessee Eastman Process monitoring, fault detection, and AI-powered diagnosis.

## 🎯 **Quick Start**

### **Production System (Recommended)**
```bash
cd integration
./quick-start.sh
# Access at http://localhost:3000
```

### **Legacy System (Backup)**
```bash
cd legacy
source ../tep_env/bin/activate
python unified_tep_control_panel.py
# Access at http://localhost:9001
```

## 📁 **Repository Structure**

- **`integration/`** - Production-ready microservices system
- **`legacy/`** - Original working POC system
- **`docs/`** - Comprehensive documentation
- **`scripts/`** - Utilities and tools

## 🚀 **Systems Overview**

### **Integration System (Production)**
- 🎛️ Unified React dashboard with 5 tabs
- 🏗️ Microservices architecture (Docker containers)
- 🔄 Real-time WebSocket data streaming
- 🤖 Multi-LLM fault analysis
- 📊 Professional UI with Mantine components

### **Legacy System (Backup)**
- 🎛️ Flask web interface
- 🔧 Direct Python integration
- 📊 Basic HTML/JavaScript UI
- 🤖 Multi-LLM support

## 📚 **Documentation**

- **[Migration Strategy](docs/migration/migration-strategy.md)** - Repository organization
- **[Integration System](integration/README.md)** - Production system docs
- **[Legacy System](legacy/README.md)** - Original system docs
- **[Architecture](docs/architecture/)** - System design documents

## 🎯 **Which System to Use?**

- **For Production**: Use `integration/` system
- **For Quick Testing**: Use `legacy/` system
- **For Development**: Both systems available

## 🤝 **Contributing**

See individual system README files for specific contribution guidelines.
