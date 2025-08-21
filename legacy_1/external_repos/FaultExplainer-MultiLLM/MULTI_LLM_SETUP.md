# Multi-LLM FaultExplainer Setup Guide

🎯 **Enhanced FaultExplainer with support for multiple LLM providers**

## 🤖 **Supported LLM Providers**

### **1. LMStudio (Local) - RECOMMENDED for you** ⭐
- **Model**: Mistral Small (your current setup)
- **Cost**: FREE (runs locally)
- **Privacy**: Complete (no data sent to cloud)
- **Speed**: Fast (local inference)

### **2. Claude (Anthropic)**
- **Model**: Claude-3-Sonnet
- **Cost**: Pay-per-use (~$3/1M tokens)
- **Quality**: Excellent reasoning

### **3. Google Gemini**
- **Model**: Gemini Pro
- **Cost**: Nearly FREE (generous free tier)
- **Quality**: Good performance

### **4. OpenAI (Original)**
- **Model**: GPT-4o
- **Cost**: Pay-per-use (~$5/1M tokens)
- **Quality**: High performance

## 🚀 **Quick Setup**

### **Option A: LMStudio (Your Setup)** ⭐

1. **Start LMStudio Server**:
   ```bash
   # In LMStudio app:
   # 1. Load your Mistral Small model
   # 2. Go to "Local Server" tab
   # 3. Start server on port 1234
   ```

2. **Configure FaultExplainer**:
   ```json
   {
       "llm_provider": "lmstudio",
       "model": "mistral-small",
       ...
   }
   ```

3. **No API keys needed!** ✅

### **Option B: Google Gemini (Nearly Free)**

1. **Get API Key**:
   - Go to https://makersuite.google.com/app/apikey
   - Create free API key

2. **Set Environment Variable**:
   ```bash
   export GOOGLE_API_KEY="your-gemini-api-key"
   ```

3. **Configure**:
   ```json
   {
       "llm_provider": "gemini",
       "model": "gemini-pro",
       ...
   }
   ```

### **Option C: Claude (Anthropic)**

1. **Get API Key**:
   - Go to https://console.anthropic.com/
   - Create API key

2. **Set Environment Variable**:
   ```bash
   export ANTHROPIC_API_KEY="your-claude-api-key"
   ```

3. **Configure**:
   ```json
   {
       "llm_provider": "claude",
       "model": "claude-3-sonnet-20240229",
       ...
   }
   ```

## 🔧 **Installation**

### **1. Install Dependencies**
```bash
cd external_repos/FaultExplainer-MultiLLM/backend
pip install -r requirements.txt

# For Claude support:
pip install anthropic

# For Gemini support:
pip install google-generativeai
```

### **2. Configure Your Provider**
Edit `config.json`:
```json
{
    "llm_provider": "lmstudio",  // Change this
    "model": "mistral-small",
    "fault_trigger_consecutive_step": 6,
    "topkfeatures": 6,
    "prompt": "explain"
}
```

### **3. Start the Backend**
```bash
cd external_repos/FaultExplainer-MultiLLM/backend
fastapi dev app.py
```

### **4. Test the Connection**
```bash
curl http://localhost:8000/
```

## 🎯 **My Recommendation for You**

### **Start with LMStudio** (Your Current Setup)
```json
{
    "llm_provider": "lmstudio",
    "model": "mistral-small"
}
```

**Why LMStudio?**
- ✅ **FREE** - No API costs
- ✅ **Private** - Data stays local
- ✅ **Fast** - No network latency
- ✅ **You already have it** - Mistral Small loaded

**Mistral Small Quality:**
- 🎯 **Good for fault analysis** - Strong reasoning
- 🎯 **Industrial knowledge** - Understands process engineering
- 🎯 **Fast responses** - Local inference

### **Backup Option: Google Gemini**
If LMStudio has issues, Gemini is nearly free and works well.

## 🔄 **Switching Between Providers**

Just change the `config.json`:

```bash
# Use LMStudio
{"llm_provider": "lmstudio", "model": "mistral-small"}

# Use Gemini  
{"llm_provider": "gemini", "model": "gemini-pro"}

# Use Claude
{"llm_provider": "claude", "model": "claude-3-sonnet-20240229"}
```

Restart the backend after changes.

## 🧪 **Testing**

1. **Start LMStudio server** (port 1234)
2. **Start FaultExplainer backend**:
   ```bash
   cd external_repos/FaultExplainer-MultiLLM/backend
   fastapi dev app.py
   ```
3. **Run the AI-enhanced simulator**:
   ```bash
   python simulators/live/live_tep_with_llm.py
   ```

## 🎉 **You're Ready!**

Your TEP simulator can now use:
- 🏠 **Local Mistral Small** (via LMStudio)
- 🌐 **Cloud providers** (Claude, Gemini, OpenAI)
- 🔄 **Easy switching** between providers

**Perfect for industrial AI demonstrations!** 🚀
