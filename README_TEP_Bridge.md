# 🎛️ TEP-FaultExplainer Bridge

## 🎯 What This Does

Connects your **live TEP simulator** to **FaultExplainer** for LLM-powered fault analysis:

1. **Runs your TEP simulator** with normal and fault conditions
2. **Automatically generates CSV data** in FaultExplainer format
3. **Sends data to FaultExplainer** for LLM analysis
4. **Shows explanations** in a simple web interface

## 🚀 Quick Start

### Step 1: Activate Your TEP Environment
```bash
# Use your existing tep_env virtual environment
source tep_env/bin/activate
```

### Step 2: Start FaultExplainer Backend
```bash
cd external_repos/FaultExplainer-MultiLLM/backend
python main.py
```
*Keep this terminal open*

### Step 3: Start TEP Bridge (New Terminal)
```bash
# In a new terminal, from project root
./start_tep_bridge.sh
```
*This will automatically use your tep_env*

### Step 4: Open Browser
Go to: **http://localhost:8083**

## 🎛️ How to Use

### 1. **Establish Normal Baseline**
- Click "📊 Run Normal Operation (5 min)"
- This creates baseline data for comparison

### 2. **Simulate Fault**
- Select fault type (1, 4, 6, 8, or 13)
- Set intensity (0.1 to 2.0)
- Click "🚨 Start Fault Simulation"

### 3. **View LLM Explanations**
- Explanations appear automatically
- Shows detailed fault analysis from AI

## 🔍 Finding LLM Explanations in FaultExplainer

You asked where the LLM explanations are in FaultExplainer. Here's how to find them:

### **In FaultExplainer UI:**
1. **Click "Assistant" tab** (left sidebar)
2. **Select your fault data** from dropdown
3. **Click "Explain" button**
4. **LLM explanation appears** in chat panel

### **Why You Didn't See It:**
- You were on "Monitoring" and "Fault History" tabs
- **LLM explanations are in "Assistant" tab**
- Need to manually trigger explanation

## 📊 Data Flow

```
Live TEP Simulator → CSV Generation → FaultExplainer → LLM Analysis → Explanation
```

### **Files Generated:**
- `normal_baseline.csv` - Normal operation data
- `live_fault_X_TIMESTAMP.csv` - Fault data files
- Saved to: `external_repos/FaultExplainer-MultiLLM/backend/data/`

## 🎯 Your Insight is Perfect!

You correctly identified that FaultExplainer:
- **Uses historical data** (pre-recorded fault scenarios)
- **Compares fault vs normal** operation
- **Sends differences to LLM** for explanation

### **Your Architecture Should Be:**
1. **Normal Operation Simulator** (baseline)
2. **Fault Injection System** (trigger faults)
3. **Real-time Difference Calculator** 
4. **LLM Explanation Engine**
5. **Live Dashboard** (real-time alerts)

## 🔄 Next Steps

### **Batch Analysis (Current):**
- Use this bridge for **offline analysis**
- Generate fault scenarios and analyze
- Perfect for **research and validation**

### **Real-time Analysis (Future):**
- Modify bridge for **live monitoring**
- Add **real-time fault detection**
- Integrate with **plant control systems**

## 🛠️ Technical Details

### **TEP Variables Mapped:**
- XMEAS(1-22) → FaultExplainer format
- Automatic time series generation
- Compatible with existing FaultExplainer data

### **LLM Integration:**
- Supports **Claude, LMStudio, Gemini**
- Streaming responses
- Detailed technical explanations

## 🎯 Example LLM Output

```
🔍 FAULT ANALYSIS: Live Fault 1

The data shows significant deviation in A/C feed ratio:
- Component A feed: +15.3% above baseline
- Component C feed: -8.7% below baseline
- Reactor temperature: +2.1°C increase

🎯 ROOT CAUSE:
Feed composition controller malfunction causing
improper A/C ratio regulation

⚡ IMPACT:
- Reduced Product G yield (-12%)
- Increased byproduct formation (+8%)
- Temperature instability detected

🔧 RECOMMENDED ACTIONS:
1. Check A/C feed ratio controller
2. Verify feed composition analyzers  
3. Adjust feed rates manually
4. Monitor reactor temperature closely
```

## 🎛️ Perfect for Industrial Use

This approach gives you:
- **Professional fault analysis**
- **AI-powered explanations**
- **Research-grade methodology**
- **Scalable to real-time**

**Ready to connect your live TEP simulator to professional LLM analysis!** 🚀🤖✨
