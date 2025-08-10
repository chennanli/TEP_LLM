# 🎛️ TEP Enhanced Dashboard - User Guide

## 🚀 How to Run the Dashboard

### **Quick Start:**
```bash
# Navigate to project directory
cd /Users/chennanli/Desktop/LLM_Project/TE

# Activate virtual environment
source tep_env/bin/activate

# Run the enhanced dashboard
python tep_enhanced_dashboard.py
```

**Then open:** http://localhost:8085

---

## 📊 Understanding the Interface

### **Main Dashboard Layout:**

#### **Left Panel - Process Controls:**
- **Simulation Controls:** Start/Stop/Reset buttons
- **A/C Feed Ratio:** Slider with guidance ranges
- **Fault Injection:** Dropdown with fault descriptions
- **System Status:** Real-time metrics and values

#### **Right Panel - 6-Plot Visualization:**
1. **Temperature (°C)** - Shows reactor temperature with normal range (118-122°C)
2. **Pressure (bar)** - Shows reactor pressure with normal range (2.7-2.9 bar)
3. **🚨 Anomaly Score** - **NEW!** Shows anomaly detection score with threshold line
4. **Flow Rate (kg/h)** - Shows product flow with normal range (43-47 kg/h)
5. **Level (%)** - Shows reactor level with normal range (64-70%)
6. **📊 Stability Score (%)** - **NEW!** Shows system stability percentage

#### **Bottom Panel - AI Analysis:**
- **🤖 AI Fault Analysis** - Gemini-powered explanations when anomalies detected

---

## 🎯 How to Use the Dashboard

### **Step 1: Start with Stable Conditions**
1. **Click "▶️ Start Simulation"**
2. **Observe:** System begins in stable operating conditions
   - Temperature: ~120°C (green zone)
   - Pressure: ~2.8 bar (green zone)
   - Anomaly Score: ~0-1 (green zone)
   - Stability: 100% (all variables in normal range)

### **Step 2: Understand Normal Operation**
- **Green zones** in plots = Normal operating ranges
- **Status shows:** "✅ STABLE: Normal Operation"
- **All metrics** should be green in the status panel
- **Stability duration** counter shows how long system has been stable

### **Step 3: Experiment with Controls**

#### **A/C Feed Ratio Control:**
- **Normal (0.9-1.1):** ✅ Stable operation, minimal effects
- **Caution (0.8-0.9, 1.1-1.3):** ⚠️ May cause temperature/pressure changes
- **Danger (<0.8, >1.3):** 🚨 Will trigger anomaly detection

**Try this:** Move slider to 1.3 and watch:
- Temperature rises by ~15-20°C
- Pressure increases by ~0.3-0.5 bar
- Anomaly score starts climbing
- Status changes to "⚠️ UNSTABLE"

#### **Fault Injection:**
Each fault type has specific effects:

1. **🌡️ A/C Feed Ratio Fault:**
   - **Effect:** Temperature spikes, pressure increases
   - **Symptoms:** Reactor overheating, product quality issues
   - **Anomaly Trigger:** Usually within 10-20 seconds

2. **❄️ Cooling Water Fault:**
   - **Effect:** Reduced cooling, temperature rise
   - **Symptoms:** High temperatures, thermal runaway risk
   - **Anomaly Trigger:** Gradual temperature increase

3. **📉 Feed Loss Fault:**
   - **Effect:** Reduced flow, level drops
   - **Symptoms:** Low production rates, inventory issues
   - **Anomaly Trigger:** Flow and level deviations

4. **⚗️ Feed Composition Fault:**
   - **Effect:** Process instability, variable responses
   - **Symptoms:** Fluctuating temperatures and pressures
   - **Anomaly Trigger:** High variability detection

5. **⚡ Reaction Kinetics Fault:**
   - **Effect:** Altered reaction rates, pressure variations
   - **Symptoms:** Pressure instability, temperature changes
   - **Anomaly Trigger:** Pressure and temperature deviations

### **Step 4: Watch Anomaly Detection**

#### **Anomaly Score Interpretation:**
- **0-1.5 (Green Zone):** Normal operation, no concerns
- **1.5-3.0 (Yellow Zone):** Elevated, system monitoring
- **>3.0 (Red Zone):** 🚨 ANOMALY DETECTED! AI analysis triggered

#### **What Triggers Anomalies:**
- Temperature outside 118-122°C range
- Pressure outside 2.7-2.9 bar range
- High process variability (instability)
- Multiple variables deviating simultaneously

### **Step 5: AI Fault Analysis**

When anomaly score > 3.0:
1. **Status changes** to "🚨 ANOMALY DETECTED!"
2. **AI analysis panel** shows "🤖 Analyzing..."
3. **Gemini AI provides:**
   - Root cause analysis
   - Safety implications
   - Recommended actions

**Example AI Response:**
```
The anomaly is caused by an A/C feed ratio imbalance (1.4) combined 
with active fault injection. This has led to reactor overheating 
(135°C vs normal 120°C) and elevated pressure (3.2 bar vs normal 2.8 bar).

Safety implications: Risk of thermal runaway and pressure vessel stress.

Immediate actions:
1. Reduce A/C ratio to 1.0-1.1 range
2. Increase cooling water flow
3. Monitor pressure closely for further increases
4. Consider emergency shutdown if temperature exceeds 140°C
```

---

## 🎯 Recommended Testing Scenarios

### **Scenario 1: Gradual Fault Development**
1. Start simulation (stable conditions)
2. Slowly increase A/C ratio: 1.0 → 1.1 → 1.2 → 1.3
3. Watch anomaly score gradually increase
4. Observe when AI analysis triggers (score > 3.0)

### **Scenario 2: Sudden Fault Injection**
1. Start simulation (stable conditions)
2. Inject "Cooling Water Fault" at intensity 1.5
3. Watch rapid temperature rise
4. Observe anomaly detection and AI response

### **Scenario 3: Multiple Fault Conditions**
1. Start simulation
2. Set A/C ratio to 1.4 (unstable)
3. Inject "A/C Feed Ratio Fault" at intensity 1.2
4. Watch compound effects and high anomaly scores

### **Scenario 4: Recovery Testing**
1. Create anomaly condition (any method above)
2. Wait for AI analysis
3. Follow AI recommendations to restore stability
4. Watch anomaly score decrease and stability return

---

## 📊 Understanding the Plots

### **Plot 1: Temperature**
- **Red line:** Current temperature
- **Green band:** Normal range (118-122°C)
- **Watch for:** Spikes above 125°C or below 115°C

### **Plot 2: Pressure**
- **Blue line:** Current pressure
- **Green band:** Normal range (2.7-2.9 bar)
- **Watch for:** Pressure above 3.0 bar (safety concern)

### **Plot 3: 🚨 Anomaly Score (KEY PLOT!)**
- **Orange line:** Anomaly detection score
- **Red dashed line:** Threshold (3.0)
- **Color zones:** Green (normal), Yellow (elevated), Red (anomaly)
- **This is where you see when AI analysis will trigger!**

### **Plot 4: Flow Rate**
- **Green line:** Product flow rate
- **Green band:** Normal range (43-47 kg/h)
- **Watch for:** Drops below 40 kg/h (production issues)

### **Plot 5: Level**
- **Purple line:** Reactor level
- **Green band:** Normal range (64-70%)
- **Watch for:** Levels below 60% or above 75%

### **Plot 6: 📊 Stability Score (KEY PLOT!)**
- **Navy line:** Percentage of variables in normal range
- **Green dashed line:** Stable threshold (75%)
- **Color zones:** Green (stable), Red (unstable)
- **This shows overall system health!**

---

## 🔧 Troubleshooting

### **Dashboard Won't Load:**
- Check if port 8085 is available
- Ensure virtual environment is activated
- Verify all dependencies installed

### **Plots Not Updating:**
- Check browser console for JavaScript errors
- Refresh the page
- Restart the dashboard

### **AI Analysis Not Working:**
- Verify GOOGLE_API_KEY in .env file
- Check internet connection
- Ensure anomaly score > 3.0 to trigger analysis

### **Status Panel Shows Errors:**
- This version has fixed JSON serialization issues
- If errors persist, restart the dashboard

---

## ✅ Success Indicators

### **You're Using It Correctly When:**
- You can start simulation and see stable conditions immediately
- You understand what each control does before using it
- You can predict when anomaly score will increase
- You can interpret AI analysis and take corrective actions
- You can restore stability after creating faults

### **Key Learning Objectives:**
1. **Recognize normal vs abnormal conditions**
2. **Understand cause-and-effect relationships**
3. **Use anomaly score to predict problems**
4. **Apply AI recommendations effectively**
5. **Maintain process stability**

---

## 🎯 Next Steps

After mastering the enhanced dashboard:
1. **Explore all fault types** and their unique signatures
2. **Practice fault diagnosis** using AI analysis
3. **Learn process optimization** by maintaining stability
4. **Understand industrial safety** through fault scenarios
5. **Prepare for real TEP integration** with actual plant data
