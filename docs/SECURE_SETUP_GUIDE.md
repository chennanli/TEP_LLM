# 🔐 Secure TEP System Setup Guide

## 🚨 IMPORTANT: API Key Security

Your API keys are now stored securely in a `.env` file instead of being hardcoded in the Python scripts. This file is:
- ✅ Ignored by Git (won't be uploaded to GitHub)
- ✅ Loaded automatically when you run the scripts
- ✅ Easy to update without changing code

## 📋 Initial Setup (One Time Only)

### 1. **Activate Virtual Environment**
```bash
cd /Users/chennanli/Desktop/LLM_Project/TE
source tep_env/bin/activate
```

### 2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 3. **Configure API Keys**
The `.env` file has been created with your current keys. 

⚠️ **SECURITY WARNING**: Your current API keys have been exposed in the code. You should:
1. Go to [Anthropic Console](https://console.anthropic.com/account/keys) and revoke the old Claude key
2. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials) and revoke the old Gemini key
3. Generate new keys and update the `.env` file

To edit your API keys:
```bash
# Open the .env file in your editor
nano .env
# or
vim .env
# or use any text editor
```

## 🚀 How to Run the System

### **Option 1: Complete System with Frontend**
```bash
# Make sure you're in the TE directory with virtual env activated
python run_complete_system.py
```

This launches:
- TEP Simulator (Qt5 or Web)
- FaultExplainer Backend (API server)
- FaultExplainer Frontend (React UI)

### **Option 2: Simple System (No Node.js Required)**
```bash
python run_simple_system.py
```

This launches:
- TEP Simulator
- FaultExplainer Backend
- Simple Flask Web Interface

### **Option 3: Just the Simulator**
```bash
python run_simulator.py
```

## 📝 Managing API Keys

### **To Update API Keys:**
1. Edit the `.env` file:
   ```bash
   nano .env
   ```

2. Replace the keys with your new ones:
   ```
   ANTHROPIC_API_KEY=your-new-anthropic-key
   GOOGLE_API_KEY=your-new-google-key
   OPENAI_API_KEY=your-new-openai-key
   ```

3. Save and close the file

### **To Add New API Keys:**
Just add them to the `.env` file:
```
NEW_SERVICE_API_KEY=your-key-here
```

Then access in Python:
```python
import os
new_key = os.getenv('NEW_SERVICE_API_KEY')
```

## 🎯 Quick Daily Usage

Every time you want to use the system:

```bash
# 1. Navigate to project
cd /Users/chennanli/Desktop/LLM_Project/TE

# 2. Activate virtual environment
source tep_env/bin/activate

# 3. Run the system
python run_complete_system.py
# or
python run_simple_system.py
```

## 🔍 Troubleshooting

### **"No API keys found" Warning**
- Check that `.env` file exists in the main TE directory
- Make sure the keys are properly formatted (no quotes needed)

### **"Module 'dotenv' not found"**
```bash
pip install python-dotenv
```

### **API Key Not Working**
- Check for extra spaces or characters in the `.env` file
- Make sure you've saved the `.env` file after editing
- Verify the key is valid in your provider's console

## 🛡️ Security Best Practices

1. **Never commit `.env` to Git** - It's already in .gitignore
2. **Don't share your `.env` file** with others
3. **Revoke keys immediately** if exposed
4. **Use different keys** for development vs production
5. **Rotate keys regularly** (every 3-6 months)

## 📄 Files Changed

1. **`.env`** - Your API keys (git-ignored)
2. **`.env.template`** - Template for others to use
3. **`run_complete_system.py`** - Now uses environment variables
4. **`run_simple_system.py`** - Now uses environment variables
5. **`requirements.txt`** - Added python-dotenv

## ✅ Summary

Your API keys are now secure! The system will:
- Load keys from `.env` automatically
- Warn if no keys are found
- Still work with LMStudio even without API keys
- Never expose keys in the code or Git

Remember to revoke and replace your exposed keys as soon as possible!