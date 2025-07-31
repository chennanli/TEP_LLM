# 🎛️ Unified TEP Simulator with LLM Fault Diagnosis

## 🎯 **What You Get - All in One Interface!**

✅ **Single Application** - No multiple terminals needed  
✅ **LLM Selection** - Choose 1, 2, 3, or any combination  
✅ **Live Simulation** - Real-time TEP process monitoring  
✅ **Training Data** - Generate ML datasets  
✅ **Fault Diagnosis** - Intelligent LLM analysis  
✅ **User-Friendly** - Simple click-and-go interface  

## 🚀 **One-Command Launch**

```bash
# Just run this one command:
cd /Users/chennanli/Desktop/LLM_Project/TE
source tep_env/bin/activate
python run_unified_tep.py
```

**That's it! Everything else is handled in the GUI.**

## 🎛️ **Interface Overview**

### **📋 Control Panel**
- **Simulation Mode:** Choose Live or Training Data generation
- **LLM Providers:** Select your preferred AI assistants
- **Action Buttons:** Start, Enable Diagnosis, Stop

### **🤖 LLM Provider Options**
- **1. LMStudio (Local)** ✅ Already configured with your Mistral model
- **2. Claude (Anthropic)** ✅ Your API key pre-configured  
- **3. Gemini (Google)** ✅ Your API key pre-configured

### **📊 Status & Analysis Area**
- Real-time logs and status updates
- LLM fault analysis results
- Comparison between different AI providers

## 🎯 **How to Use**

### **Step 1: Launch**
```bash
python run_unified_tep.py
```

### **Step 2: Configure**
- **Simulation Mode:** Select "Live Simulation" for real-time analysis
- **LLM Providers:** Check the boxes for providers you want:
  - ☑️ **1. LMStudio** (always recommended - local and fast)
  - ☑️ **2. Claude** (excellent analysis quality)
  - ☑️ **3. Gemini** (good alternative perspective)

### **Step 3: Start**
- Click **"🚀 Start TEP Simulator"**
- Wait for "✅ TEP Simulator initialized successfully"

### **Step 4: Enable Diagnosis**
- Click **"🔍 Enable Fault Diagnosis"**
- The system will monitor for faults automatically

### **Step 5: Watch the Magic!**
- Introduce faults in the TEP process
- Watch as multiple LLMs analyze the same fault
- Compare different AI perspectives on the same problem

## 🎛️ **Example LLM Comparison**

When a fault occurs, you'll see analysis from each selected provider:

```
🚨 FAULT DETECTED: Type 1

🤖 LMStudio (Local) Analysis [14:23:15]:
====================================
🔍 FAULT ANALYSIS: Feed ratio imbalance detected
🎯 ROOT CAUSE: A/C feed composition shifted
⚡ RECOMMENDED ACTIONS: Adjust valve XMV(3)
⏰ EXPECTED RECOVERY: 10-15 minutes
====================================

🤖 Claude (Anthropic) Analysis [14:23:18]:
==========================================
🔍 FAULT ANALYSIS: Reactor temperature rising due to 
reaction stoichiometry changes...
🎯 ROOT CAUSE: Feed stream A/C ratio deviation causing
excess heat generation...
⚡ RECOMMENDED ACTIONS: 1) Reduce feed rate 2) Increase
cooling 3) Monitor product quality...
⏰ EXPECTED RECOVERY: 12-18 minutes with proper action
==========================================

🤖 Google Gemini Analysis [14:23:21]:
=====================================
🔍 FAULT ANALYSIS: Process imbalance in reactor
🎯 ROOT CAUSE: Feed composition anomaly
⚡ RECOMMENDED ACTIONS: Immediate valve adjustment
⏰ EXPECTED RECOVERY: 15 minutes
=====================================
```

## 🎯 **Benefits of Multiple LLMs**

### **🔍 Different Perspectives**
- **LMStudio:** Fast, local analysis
- **Claude:** Detailed, technical explanations
- **Gemini:** Concise, practical advice

### **🎯 Validation**
- Compare analyses for consistency
- Get multiple expert opinions
- Identify the most reliable diagnosis

### **📊 Research Value**
- Study how different AI models interpret industrial data
- Compare reasoning approaches
- Validate fault diagnosis accuracy

## 🔧 **Advanced Features**

### **🎛️ Training Data Generation**
- Select "Generate Training Data" mode
- Creates CSV files for all 20 fault types
- Perfect for machine learning research

### **⚙️ Customization**
- Modify fault detection thresholds in the code
- Add new LLM providers
- Customize analysis prompts

### **📊 Data Export**
- All analyses are logged with timestamps
- Copy/paste results for reports
- Compare LLM performance over time

## 🎓 **Perfect for Research**

### **📚 Academic Use**
- Demonstrate AI in industrial applications
- Compare different LLM capabilities
- Generate datasets for student projects

### **🔬 Industrial Research**
- Validate AI-based fault diagnosis
- Study multi-model consensus
- Develop hybrid AI systems

## 🚀 **Next Steps**

1. **Start with LMStudio only** - Get familiar with the interface
2. **Add Claude** - Compare analysis quality
3. **Include Gemini** - See three-way comparison
4. **Experiment with faults** - Try different fault types
5. **Analyze results** - Study LLM consistency and accuracy

## 🎯 **Troubleshooting**

### **"LMStudio Error"**
- Make sure LMStudio is running on http://127.0.0.1:1234
- Check that your model is loaded

### **"Claude/Gemini Error"**
- API keys are pre-configured in the code
- Check internet connection for cloud APIs

### **"TEP Simulator Error"**
- Make sure you're in the tep_env virtual environment
- Check that external_repos/tep2py-master exists

**You now have a professional, unified interface that combines TEP simulation with multi-LLM fault diagnosis - all in one easy-to-use application!** 🎛️🤖✨
