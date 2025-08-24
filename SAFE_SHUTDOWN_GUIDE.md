# 🛑 TEP Services Safe Shutdown Guide

## 🎯 **Problem Solved**

You were concerned about:
- ✅ **TEP processes running in background** consuming API credits
- ✅ **Ctrl+C not fully stopping** all services
- ✅ **Stop buttons not being comprehensive** enough
- ✅ **No clear way to verify** all processes are stopped

## 🛡️ **Complete Shutdown Solutions**

### **Method 1: Emergency Stop Button (Recommended)**

**In the Web Interface:**
1. Open http://localhost:9001 (Legacy) or http://localhost:9002 (Integration)
2. Click **🛑 Stop Everything** button
3. Wait for confirmation message: "🎉 Complete shutdown successful!"

**What it does:**
- ✅ Stops TEP simulation immediately
- ✅ Terminates all backend processes
- ✅ Kills processes on all ports (9001, 9002, 8001, 8000, 5173, 3000)
- ✅ Clears data files to prevent API consumption
- ✅ Runs comprehensive cleanup script
- ✅ Shows clear success/failure messages

### **Method 2: Command Line Script (Most Thorough)**

**Run the comprehensive shutdown script:**
```bash
cd /Users/chennanli/Desktop/LLM_Project/TE
./stop_all_tep_services.sh
```

**What it does:**
- 🔍 **Checks all TEP ports** and kills any processes using them
- 🔍 **Searches for TEP processes** by name pattern and terminates them
- 🧹 **Cleans up data files** that might trigger API calls
- 🧹 **Clears log files** to free disk space
- ✅ **Verifies complete shutdown** with final status check
- 📊 **Shows detailed report** of what was stopped

### **Method 3: Enhanced Ctrl+C (Terminal)**

**When running in terminal:**
1. Press **Ctrl+C** to interrupt the main process
2. The improved shutdown handler will:
   - Stop TEP simulation loop
   - Terminate all child processes
   - Clean up data files
   - Kill processes on all ports

## 🔍 **Verification Methods**

### **Check if Everything is Stopped:**

**Quick Check:**
```bash
lsof -i :9001 -i :9002 -i :8001 -i :8000
# Should return nothing if all stopped
```

**Detailed Check:**
```bash
ps aux | grep -E "(unified_tep|unified_control|tep.*python)" | grep -v grep
# Should return nothing if all stopped
```

**Port Status:**
```bash
netstat -an | grep -E "(9001|9002|8001|8000)"
# Should show no LISTEN status if all stopped
```

## 🚨 **Emergency Situations**

### **If Stop Button Doesn't Work:**

1. **Run the script directly:**
   ```bash
   ./stop_all_tep_services.sh
   ```

2. **Force kill by port:**
   ```bash
   sudo lsof -ti :9001 | xargs kill -9
   sudo lsof -ti :9002 | xargs kill -9
   sudo lsof -ti :8001 | xargs kill -9
   sudo lsof -ti :8000 | xargs kill -9
   ```

3. **Nuclear option (kills ALL Python):**
   ```bash
   pkill -f python
   # ⚠️ WARNING: This kills ALL Python processes on your system!
   ```

### **If API is Still Being Consumed:**

1. **Check data files:**
   ```bash
   ls -la legacy/data/live_tep_data.csv
   ls -la integration/data/live_tep_data.csv
   # Files should be empty (0 bytes) when stopped
   ```

2. **Clear data files manually:**
   ```bash
   > legacy/data/live_tep_data.csv
   > integration/data/live_tep_data.csv
   ```

3. **Check for hidden processes:**
   ```bash
   ps aux | grep -i llm
   ps aux | grep -i anthropic
   ps aux | grep -i openai
   ```

## 📊 **Status Indicators**

### **System is STOPPED when:**
- ✅ All ports (9001, 9002, 8001, 8000) are free
- ✅ No TEP-related Python processes running
- ✅ Data files are empty (0 bytes)
- ✅ No network connections to LLM APIs
- ✅ Web interfaces return "connection refused"

### **System is RUNNING when:**
- ⚠️ Ports show LISTEN status
- ⚠️ Python processes with "tep" in name exist
- ⚠️ Data files are growing in size
- ⚠️ Network activity to api.anthropic.com or api.openai.com
- ⚠️ Web interfaces are accessible

## 🎯 **Best Practices**

### **Before Leaving Computer:**
1. **Always run the shutdown script:**
   ```bash
   ./stop_all_tep_services.sh
   ```
2. **Verify all ports are free**
3. **Check data files are empty**

### **Before Starting New Session:**
1. **Run shutdown script first** (cleans any stale processes)
2. **Then start the system you want to use**

### **For Demonstrations:**
1. **Test the stop button** before the demo
2. **Have the shutdown script ready** as backup
3. **Show the verification commands** to prove system is stopped

## 🔧 **Troubleshooting**

### **"Port already in use" errors:**
```bash
./stop_all_tep_services.sh
# Wait 5 seconds, then restart
```

### **"Process not found" errors:**
- This is normal - means the process was already stopped
- The script handles this gracefully

### **API charges still appearing:**
1. Check for other Python projects using the same API keys
2. Verify API keys are not hardcoded in other scripts
3. Check browser tabs - close any FaultExplainer interfaces

## 🎉 **Success Confirmation**

**When you see this output, everything is safely stopped:**
```
🎉 TEP Services Shutdown Complete!
==================================
✅ All ports cleared
✅ All processes terminated  
✅ Temporary files cleaned
✅ Safe to restart services
```

**Your API credits are now safe!** 💰
