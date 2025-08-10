#!/bin/bash

# TEP Repository Organization Script
# Organizes current repository structure for better management

set -e

echo "🏗️ TEP Repository Organization"
echo "=============================="

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p legacy
mkdir -p docs/migration
mkdir -p docs/architecture
mkdir -p docs/user-guides
mkdir -p scripts

# Move legacy files to legacy folder
echo "📦 Moving legacy files..."

# Core legacy files
legacy_files=(
    "unified_tep_control_panel.py"
    "tep_bridge.py"
    "tep_faultexplainer_bridge.py"
    "working_system_dashboard.py"
    "corrected_tep_dashboard.py"
    "fast_tep_dashboard.py"
    "minimal_test_panel.py"
    "simple_fault_backend.py"
    "real_tep_simulator.py"
    "run_simulator.py"
    "web_interface.py"
    "process_manager.py"
    "api_routes.py"
)

for file in "${legacy_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  Moving $file to legacy/"
        mv "$file" legacy/
    fi
done

# Move legacy directories
legacy_dirs=(
    "external_repos"
    "simulators"
    "backend"
    "static"
    "web-bundles"
    "logs"
    "data"
)

for dir in "${legacy_dirs[@]}"; do
    if [ -d "$dir" ] && [ "$dir" != "integration" ]; then
        echo "  Moving $dir to legacy/"
        mv "$dir" legacy/
    fi
done

# Move documentation files to docs
echo "📚 Organizing documentation..."

doc_files=(
    "*.md"
    "architecture"
    "prd"
    "restart_document"
    "Explanation_and_Questions"
    "NextSteps"
)

for pattern in "${doc_files[@]}"; do
    if ls $pattern 1> /dev/null 2>&1; then
        echo "  Moving $pattern to docs/"
        mv $pattern docs/ 2>/dev/null || true
    fi
done

# Create legacy README
echo "📝 Creating legacy README..."
cat > legacy/README.md << 'EOF'
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
EOF

# Create integration README update
echo "📝 Updating integration README..."
if [ -f "integration/README.md" ]; then
    # Add note about repository structure
    cat >> integration/README.md << 'EOF'

## 📁 **Repository Structure**

This integration system is part of a larger repository:
- `../legacy/` - Original working POC system
- `../docs/` - Shared documentation and migration guides
- `../scripts/` - Shared utilities and tools

See `../docs/migration/migration-strategy.md` for the complete migration plan.
EOF
fi

# Update root README
echo "📝 Creating root README..."
cat > README.md << 'EOF'
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
EOF

echo "✅ Repository organization complete!"
echo ""
echo "📁 New structure:"
echo "  • legacy/ - Your working POC system"
echo "  • integration/ - Production-ready system"
echo "  • docs/ - All documentation"
echo "  • scripts/ - Utilities and tools"
echo ""
echo "🚀 Next steps:"
echo "  1. Review the new structure"
echo "  2. Test both systems still work"
echo "  3. Commit the organized repository"
echo "  4. Continue development in integration/"
