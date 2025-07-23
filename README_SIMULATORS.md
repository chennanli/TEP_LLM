# 🎛️ TEP Process Simulators - Simple Guide

## 🎯 **Three Professional Simulators Ready for Demonstrations**

Clean, professional interfaces with enhanced fault effects for clear demonstrations.

---

## 🚀 **How to Run**

### **Step 1: Activate Virtual Environment**
```bash
cd /Users/chennanli/Desktop/LLM_Project/TE
source tep_env/bin/activate
```

### **Step 2: Choose Your Simulator**

#### **🌟 Simple Web Simulator (BEST for demos)**
```bash
python simple_web_tep_simulator.py
```
**Open:** http://localhost:8081
- Ultra-clean interface
- Easy to read
- Perfect for customer demos
- Built-in demo guide button

#### **🎛️ Clean Qt Simulator (Desktop app)**
```bash
python clean_qt_tep_simulator.py
```
- Professional desktop application
- Native macOS interface
- Clear labels and readable text

#### **🚀 All Three Simulators (Advanced)**
```bash
python smart_launcher.py
```
- Runs all simulators with proper cleanup
- Auto-opens browsers
- No orphaned background processes

---

## 🎯 **Demo Guide**

### **🌟 BEST FAULT FOR DEMOS: Fault 13 - Reaction Kinetics**
- **Why:** Most dramatic changes across multiple parameters
- **Expected Changes:** ↑ Temperature (+3-4°C), ↑ Pressure (+20-30 kPa), ↓ Flow (-1-2 m³/h)
- **Demo Intensity:** 1.6-2.0
- **Visibility:** Changes visible within 30 seconds

### **⭐ OTHER GOOD DEMO FAULTS:**
- **Fault 1 - A/C Feed Ratio:** Temperature/pressure coupling
- **Fault 4 - Cooling Water:** Immediate temperature response

### **📋 Complete Demo Guide:**
- **In Simple Web Simulator:** Click "📋 Demo Guide" button
- **Standalone file:** Open `DEMO_GUIDE.md`

---

## 🎯 **Quick Demo Steps**

1. **Start with Normal Operation** (baseline)
2. **Select Fault 13, intensity 1.8** (dramatic changes)
3. **Watch real-time changes** (temperature +3°C, pressure +30 kPa)
4. **Reset and try other faults** for comparison

---

## 🛠️ **Utilities**

### **Check for Background Processes:**
```bash
python check_simulators.py
```
- Find running simulators
- Clean up orphaned processes
- Check port usage

---

## 📁 **File Structure**

### **Main Simulators:**
- `simple_web_tep_simulator.py` - Clean web interface (RECOMMENDED)
- `clean_qt_tep_simulator.py` - Professional desktop app
- `smart_launcher.py` - Run all three with auto-cleanup

### **Utilities:**
- `check_simulators.py` - Process checker and cleanup
- `DEMO_GUIDE.md` - Complete demonstration guide

### **Documentation:**
- `README_SIMULATORS.md` - This guide

---

## 🎉 **Ready for Demonstrations!**

**Three professional simulators with:**
- ✅ Clean, readable interfaces
- ✅ Enhanced fault effects
- ✅ Perfect demo capabilities
- ✅ Proper process management
- ✅ Built-in demo guidance

**Perfect for customer demonstrations and professional presentations!** 🎛️✨
