# 🤖 Where to Find LLM Explanations in FaultExplainer

## 🎯 **Step-by-Step Guide**

### **Step 1: Start FaultExplainer**
```bash
source tep_env/bin/activate
cd external_repos/FaultExplainer-MultiLLM/frontend
npm start
```

### **Step 2: Open Browser**
Go to: **http://localhost:3000**

### **Step 3: Look for the Navigation Tabs**
You'll see **3 tabs** on the left sidebar:

1. **📊 "Monitoring"** - Real-time charts and data
2. **📈 "Fault History"** - T² statistics and fault detection  
3. **🤖 "Assistant"** - **THIS IS WHERE LLM EXPLANATIONS ARE!**

### **Step 4: Click "Assistant" Tab**
- Look for the **robot icon** 🤖
- The tab is labeled **"Assistant"**
- This opens the **ChatPage.tsx** component

### **Step 5: Upload Fault Data**
1. **Select a fault file** from the dropdown
2. **Available files:**
   - `fault1.csv`, `fault2.csv`, etc. (pre-loaded examples)
   - Your live data files (if uploaded)

### **Step 6: Get LLM Explanation**
1. **Type a question** like: "Explain this fault"
2. **Click Send** button
3. **LLM explanation streams in real-time**

## 🔍 **What You Should See**

### **In the Assistant Tab:**
```
🤖 Assistant

[Chat interface with:]
- Message input box at bottom
- Send button (paper plane icon)
- Conversation history above
- Real-time streaming responses
```

### **Example LLM Response:**
```
Based on the fault data analysis, I can identify several key issues:

📊 Process Deviations:
- Reactor temperature: +15.3°C above normal
- Feed composition: A/C ratio disrupted
- Product quality: 12% reduction in purity

🎯 Root Cause:
The fault appears to be related to feed composition 
controller malfunction affecting the A/C feed ratio...

🔧 Recommendations:
1. Check feed composition analyzers
2. Verify controller tuning
3. Monitor reactor temperature
```

## ❌ **Why You Might Not See It**

### **Common Issues:**
1. **Wrong tab** - You were on "Monitoring" or "Fault History"
2. **Backend not running** - LLM explanations need the backend
3. **No data selected** - Must select a fault file first
4. **API key issues** - LLM provider not configured

### **Backend Check:**
```bash
# Check if backend is running
curl http://localhost:8000/health
```

## 🚀 **Quick Test**

### **Use Pre-loaded Data:**
1. Open **http://localhost:3000**
2. Click **🤖 "Assistant"** tab
3. Select **"fault1.csv"** from dropdown
4. Type: **"What caused this fault?"**
5. Click **Send**
6. **Watch LLM explanation appear!**

## 🎯 **The Key Files**

### **Frontend Navigation:**
- `src/App.tsx` - Main navigation with 3 tabs
- `src/pages/ChatPage.tsx` - LLM chat interface
- `src/pages/PlotPage.tsx` - Monitoring charts
- `src/pages/FaultReports.tsx` - Fault history

### **Backend LLM:**
- `backend/app.py` - LLM API endpoints
- `backend/prompts.py` - LLM prompts for fault analysis
- `config.json` - LLM provider settings (Claude, Gemini, LMStudio)

## 🎛️ **Navigation Structure**

```
FaultExplainer Interface:
├── 📊 Monitoring (PlotPage.tsx)
├── 📈 Fault History (FaultReports.tsx)  
└── 🤖 Assistant (ChatPage.tsx) ← LLM EXPLANATIONS HERE!
```

**The LLM explanations are in the "Assistant" tab with the robot icon!** 🤖✅

**Ready to find your LLM explanations?**
