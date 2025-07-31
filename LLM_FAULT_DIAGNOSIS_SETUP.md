# 🤖 LLM Fault Diagnosis Setup Guide

## 🎯 **Goal: Connect TEP Simulator with LLM for Real-time Fault Diagnosis**

Your TEP simulator will analyze sensor data and provide natural language explanations like:
- **"Temperature spike detected in reactor - likely cooling system malfunction"**
- **"Product composition deviation suggests feed ratio imbalance"**
- **"Pressure buildup indicates potential blockage in separator"**

## 🚀 **Quick Setup (3 Options)**

### **🌟 Option 1: Local LMStudio (Recommended - No API Keys)**

#### **Step 1: Install LMStudio**
```bash
# Download from https://lmstudio.ai/
# Install and run LMStudio
# Download a model (recommended: "mistral-small" or "llama-3.1-8b")
# Start local server (runs on localhost:1234)
```

#### **Step 2: Install FaultExplainer Dependencies**
```bash
cd external_repos/FaultExplainer-MultiLLM/backend
pip install -r requirements.txt
```

#### **Step 3: Start FaultExplainer Backend**
```bash
# In terminal 1: Start FaultExplainer
cd external_repos/FaultExplainer-MultiLLM/backend
python app.py

# Should show: "Server running on http://localhost:8000"
```

#### **Step 4: Run LLM-Integrated Simulator**
```bash
# In terminal 2: Start TEP with LLM
cd ../../..  # Back to main TE directory
python simulators/live/live_tep_with_llm.py
```

### **🔑 Option 2: OpenAI GPT-4 (Best Quality)**

#### **Setup:**
```bash
# Set API key
export OPENAI_API_KEY="your-api-key-here"

# Update config
cd external_repos/FaultExplainer-MultiLLM
# Edit config.json: change "llm_provider" to "openai"
```

### **🧠 Option 3: Claude (Anthropic)**

#### **Setup:**
```bash
# Set API key
export ANTHROPIC_API_KEY="your-api-key-here"

# Update config
# Edit config.json: change "llm_provider" to "claude"
```

## 🎛️ **How It Works**

### **🔄 Real-time Analysis Flow:**
```
TEP Simulator → Sensor Data → Anomaly Detection → LLM Analysis → Natural Language Explanation
```

### **📊 What the LLM Analyzes:**
1. **Sensor Patterns:** Temperature, pressure, flow deviations
2. **Process Context:** Understanding of TEP equipment and reactions
3. **Fault Signatures:** Recognizing known fault patterns
4. **Root Causes:** Identifying underlying problems
5. **Operator Guidance:** Suggesting corrective actions

### **🎯 Example LLM Responses:**

#### **Fault 1 (A/C Feed Ratio):**
```
🔍 FAULT DETECTED: Feed Composition Imbalance

📊 Analysis:
- Reactor temperature rising (+3.2°C above normal)
- Product G concentration increasing (+2.1 mole%)
- Feed A/C ratio deviation detected

🎯 Root Cause:
The A/C feed ratio has shifted, causing reaction imbalance. 
This leads to excess heat generation and altered product distribution.

⚡ Recommended Actions:
1. Adjust feed valve XMV(3) to restore A/C ratio
2. Increase cooling water flow to manage temperature
3. Monitor product quality for 15 minutes

⏰ Expected Recovery: 10-15 minutes
```

#### **Fault 4 (Cooling Water):**
```
🔍 FAULT DETECTED: Cooling System Malfunction

📊 Analysis:
- Reactor temperature climbing rapidly (+4.1°C)
- Cooling water outlet temperature elevated
- Heat removal capacity reduced

🎯 Root Cause:
Cooling water system performance degraded - possible pump 
malfunction or heat exchanger fouling reducing heat transfer.

⚡ Recommended Actions:
1. IMMEDIATE: Reduce reactor feed rates (XMV 1,2,4)
2. Check cooling water pump status
3. Verify heat exchanger performance
4. Consider emergency cooling if temperature continues rising

🚨 Priority: HIGH - Temperature approaching safety limits
```

## 🔧 **Configuration Options**

### **📝 Edit Config File:**
```json
{
    "llm_provider": "lmstudio",  // or "openai", "claude", "gemini"
    "model": "mistral-small",
    "fault_trigger_consecutive_step": 6,  // Sensitivity
    "topkfeatures": 6,  // Number of variables to analyze
    "prompt": "explain"  // Analysis depth
}
```

### **🎯 Tuning Parameters:**
- **fault_trigger_consecutive_step:** Lower = more sensitive detection
- **topkfeatures:** More features = more detailed analysis
- **prompt:** "explain" (detailed) vs "brief" (concise)

## 🧪 **Testing the Setup**

### **Step 1: Verify Components**
```bash
# Test TEP simulator
python -c "
import sys; sys.path.append('external_repos/tep2py-master')
from tep2py import tep2py
print('✅ TEP simulator working')
"

# Test FaultExplainer backend
curl http://localhost:8000/health
# Should return: {"status": "healthy"}

# Test LLM connection
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"test": "connection"}'
```

### **Step 2: Run Full System**
```bash
# Terminal 1: FaultExplainer backend
cd external_repos/FaultExplainer-MultiLLM/backend
python app.py

# Terminal 2: TEP with LLM
python simulators/live/live_tep_with_llm.py

# Terminal 3: Test fault injection
# In the GUI, select a fault and watch LLM analysis appear
```

## 🎓 **Usage Tips**

### **🎯 For Best Results:**
1. **Start with normal operation** - let LLM learn baseline
2. **Introduce faults gradually** - single fault at a time
3. **Read LLM explanations** - understand the reasoning
4. **Experiment with different faults** - see various patterns

### **🔍 Troubleshooting:**
- **"Connection refused":** Check if FaultExplainer backend is running
- **"LLM timeout":** Reduce analysis complexity or check API keys
- **"No fault detected":** Lower sensitivity in config.json
- **"Poor explanations":** Try different LLM provider or model

## 🎯 **Next Steps**

1. **Start with LMStudio** (easiest setup)
2. **Test basic fault detection** (Fault 1, 4, 6)
3. **Experiment with different LLMs** (compare quality)
4. **Customize prompts** for your specific needs
5. **Integrate with your research** workflow

**You'll have an intelligent TEP simulator that explains faults in natural language!** 🎛️🤖✨
