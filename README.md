# Tennessee E# 🎛️ Tennessee Eastman Process (TEP) Simulator

A comprehensive industrial process simulator for academic research, education, and fault analysis.

## 🚀 Quick Start

### **Prerequisites**
- Python 3.8+
- macOS, Linux, or Windows

### **Installation**
```bash
# Clone repository
git clone https://github.com/your-username/TE.git
cd TE

# Create virtual environment
python -m venv tep_env
source tep_env/bin/activate  # macOS/Linux
# tep_env\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run simulator
python run_simulator.py
```

## 🎛️ Available Simulators

### **1. Qt Desktop Simulator**
- Native desktop application
- Professional interface with comprehensive plots
- No browser required

### **2. Enhanced Web Simulator**
- Browser-based interface (http://localhost:8082)
- Multiple product flows and compositions
- Real-time monitoring

### **3. Process Utilities**
- Background process checker and cleanup
- Training data generator for ML applications

## 📊 What the Simulator Shows

### **🏭 Multiple Product Flows**
- Product Separator Underflow (main liquid products)
- Stripper Underflow (purified final products)
- Purge Rate (waste gas stream)

### **💰 Product Quality (Economic Value)**
- Component G concentration (high-value primary product)
- Component H concentration (high-value co-product)
- Component F concentration (lower-value byproduct)

### **🚨 Safety Parameters**
- Reactor Temperature (safety critical)
- Reactor Pressure (safety critical)

### **⚙️ Process Health**
- Separator Level (inventory control)
- Reactor Level (process stability)

## 🎓 Educational Use

Perfect for:
- **Chemical Engineering Education** - Process control and fault analysis
- **Industrial Systems Research** - Anomaly detection and optimization
- **Machine Learning Projects** - Time series analysis and fault prediction
- **Control Systems Study** - MIMO system behavior and dynamics

## 📚 Documentation

- **TEP_VARIABLES.md** - Complete variable reference (52 variables)
- **SETUP_GUIDE.md** - Detailed installation and troubleshooting

## 🔬 Tennessee Eastman Process

The TEP is a realistic simulation of an industrial chemical plant featuring:
- **4 Feed Streams** (A, D, E, C components)
- **1 Main Reactor** (CSTR with chemical reactions)
- **1 Separator** (Gas/liquid separation)
- **1 Stripper** (Distillation for purification)
- **20 Fault Types** for analysis and training

### **Chemical Reactions:**
```
A + C + D → G (Primary high-value product)
A + C + E → H (Secondary high-value product)
A + E → F (Unwanted byproduct)
3D → 2F (Side reaction)
```

## 🤖 Machine Learning Integration

Generate training datasets:
```bash
python generate_training_data.py
```

Creates CSV files with:
- All 52 process variables
- 20 different fault scenarios
- Normal operation baselines
- Time series data for ML training

## 📄 License

This project is licensed under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License**.

**✅ Allowed:** Academic research, education, personal learning, open source projects
**❌ Not Allowed:** Commercial use, proprietary software, commercial consulting

For commercial licensing, please contact the author.

## 🙏 Attribution

When using this work, please include:
- Credit to the original author (Chennan Li)
- Link to this repository
- Note any changes made
- Include license notice

## 📧 Contact

For questions, commercial licensing, or collaboration opportunities, please open an issue or contact the repository owner.

---

**Built for academic excellence and industrial education** 🎛️✨stman Process (TEP) Simulator

🎯 **A comprehensive Python-based industrial process simulation platform with AI-powered fault detection and analysis.**

## 🚀 Quick Start

### 1. Activate Virtual Environment
```bash
source tep_env/bin/activate
```

### 2. Verify Installation
```bash
python scripts/setup/setup_tep.py
```

### 3. Run Live Simulator
```bash
python simulators/live/live_tep_with_llm.py
```

## 📁 Project Structure

```
TE/
├── 📚 docs/                          # All documentation
│   ├── README.md                     # Main technical documentation
│   ├── guides/                       # User guides and tutorials
│   ├── roadmaps/                     # Development roadmaps
│   ├── status/                       # Project status reports
│   ├── Academic_materials/           # Research papers and references
│   └── action_items/                 # Implementation tasks
│
├── 🎮 simulators/                    # All simulator applications
│   ├── core/                         # Basic TEP simulator
│   ├── live/                         # Interactive live simulators
│   └── demos/                        # Example and demo scripts
│
├── 📊 data/                          # Generated data and results
│   ├── simulation_results/           # CSV output files
│   └── plots/                        # Generated visualizations
│
├── 🔧 scripts/                       # Utility and setup scripts
│   ├── setup/                        # Installation and configuration
│   └── utilities/                    # Helper scripts
│
├── 🔗 external_repos/                # Third-party integrations
│   ├── tep2py-master/               # Core TEP Python wrapper
│   ├── FaultExplainer-main/         # LLM fault analysis
│   ├── sensorscan-main/             # AI anomaly detection
│   └── tennessee-eastman-profBraatz-master/  # Original Fortran code
│
└── 🐍 tep_env/                       # Python virtual environment
```

## 🎯 Main Applications

### Core Simulator
```bash
python simulators/core/tep_simulator_easy.py
```
- Basic TEP simulation with all 20 fault types
- CSV data export and visualization
- Simple command-line interface

### Live Interactive Simulator
```bash
python simulators/live/live_tep_simulator.py
```
- Real-time parameter control
- Live plotting and visualization
- Interactive fault triggering

### AI-Enhanced Simulator
```bash
python simulators/live/live_tep_with_llm.py
```
- LLM-powered root cause analysis
- Natural language fault explanations
- Operator recommendations
- Advanced anomaly detection

## 📖 Documentation

- **[Main Guide](docs/README.md)** - Complete technical documentation
- **[User Guides](docs/guides/)** - Step-by-step tutorials
- **[Project Status](docs/status/)** - Current development status
- **[Roadmaps](docs/roadmaps/)** - Future development plans

## 🔧 Setup & Configuration

All setup scripts are in `scripts/setup/`:
- `setup_tep.py` - Verify TEP simulator installation
- `setup_llm_integration.py` - Configure AI components

## 📊 Available Fault Types

| ID | Description |
|----|-------------|
| 0  | Normal operation |
| 1  | A/C feed ratio fault |
| 4  | Reactor cooling water temperature |
| 6  | A feed loss |
| 8  | A, B, C feed composition |
| 13 | Reaction kinetics |
| ... | (20 total fault scenarios) |

## 🤖 AI Features

- **FaultExplainer**: GPT-4 powered root cause analysis
- **SensorSCAN**: Deep learning anomaly detection
- **Real-time Analysis**: Live fault detection and explanation
- **Natural Language**: Human-readable fault descriptions

## 🎉 What's New

✅ **Clean Project Structure** - Organized into logical folders
✅ **Multiple Simulator Options** - From basic to AI-enhanced
✅ **Comprehensive Documentation** - Easy to navigate guides
✅ **AI Integration** - LLM-powered fault analysis
✅ **Live Interaction** - Real-time parameter control

---

**🚀 Ready to simulate!** Start with the Quick Start section above.
