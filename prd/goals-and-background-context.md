# Goals and Background Context

## Goals

The primary goal is to create a **working MVP** that connects the existing TEP simulator with FaultExplainer to demonstrate real-time fault detection and LLM-powered root cause analysis.

### MVP Goals (Phase 1):
1. **Dynamic TEP Integration**: Connect live TEP simulator with parameter adjustment capability (A/C ratio, fault injection) to FaultExplainer's PCA anomaly detection.

2. **Real-Time Fault Detection**: Use existing PCA model (20-point window) to detect anomalies when users adjust parameters or inject faults via dashboard.

3. **LLM Root Cause Analysis**: Leverage existing Gemini/Claude API integration to provide natural language explanations of detected faults.

4. **Simple Dashboard MVP**: Create unified interface where users can adjust TEP parameters, see real-time data, trigger faults, and view LLM explanations.

### Future Goals (Phase 2+):
- Multi-LLM comparison interface
- Chemical engineering context enhancement
- Advanced safety prioritization
- Industrial deployment features

## Background Context

We have existing working components that need to be connected into a cohesive MVP system for real-time fault detection and analysis.

### Current System Status:
- **TEP Simulator**: Working Python wrapper (`tep2py`) with multiple UI options
- **FaultExplainer**: Functional backend with PCA anomaly detection and LLM integration
- **API Keys**: Gemini and Claude APIs already configured and working
- **Bridge System**: Partial connection between TEP and FaultExplainer exists
- **Data Flow**: TEP generates 52 variables → CSV export → FaultExplainer analysis

### Technical Gaps to Address:
- **Real-Time Connection**: Current system requires manual CSV file handling
- **Parameter Control**: Need unified interface for adjusting A/C ratio and fault injection
- **Window Sizing**: FaultExplainer uses 20-point PCA window, bridge collects 50 points
- **User Experience**: Multiple separate interfaces need consolidation

### MVP Opportunity:
- **Proven Components**: All core pieces (TEP, PCA, LLM) are working independently
- **Clear Data Path**: TEP (52 vars) → PCA (20 window) → LLM (explanation)
- **User Story**: "Adjust A/C ratio → See anomaly detected → Get LLM explanation"
- **Quick Win**: Connect existing pieces rather than build from scratch

### Success Criteria:
- User can adjust TEP parameters via web interface
- System detects anomalies in real-time using existing PCA model
- LLM provides explanations using existing Gemini/Claude integration
- Single dashboard shows: controls, live data, anomaly status, explanations

## Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-01-30 | Initial PRD creation with chemical foundation | Chemical Engineering Team |
| 1.1 | TBD | Multi-LLM integration specifications | AI/ML Team |
| 1.2 | TBD | Real-time integration requirements | Systems Integration Team |
