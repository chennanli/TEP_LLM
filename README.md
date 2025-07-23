# Tennessee Eastman Process (TEP) Simulator

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
