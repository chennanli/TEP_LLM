# 🚨 Immediate Fixes Required

## 📋 Current Issues Identified

### 1. **Missing Anomaly Score Visualization**
**Problem:** User cannot see anomaly score values or trends
**Impact:** Cannot understand when AI analysis should trigger
**Priority:** HIGH

**Solution:**
- Add dedicated anomaly score plot (time series)
- Show current anomaly score value prominently
- Add visual threshold line at 3.0
- Color-code: Green (normal), Yellow (elevated), Red (anomaly)

### 2. **Unclear Default/Stable Conditions**
**Problem:** Dashboard starts with random values, not stable baseline
**Impact:** User doesn't understand normal operating conditions
**Priority:** HIGH

**Solution:**
- Set default stable operating conditions:
  - Temperature: 120°C ± 2°C
  - Pressure: 2.8 bar ± 0.1 bar
  - A/C Ratio: 1.0 (balanced)
  - No faults active initially
- Show "STABLE" status indicator when in normal range

### 3. **Missing Control Explanations**
**Problem:** No guidance on what controls do or when they trigger anomalies
**Impact:** User doesn't know how to use the system effectively
**Priority:** MEDIUM

**Solution:**
- Add tooltips/help text for each control
- Show expected effects of parameter changes
- Add "What happens if..." guidance

### 4. **JSON Serialization Bug**
**Problem:** Status API returns 500 errors
**Impact:** Status panel doesn't update properly
**Priority:** HIGH

**Solution:**
- Fix boolean serialization in status endpoint
- Add proper error handling
- Test all API endpoints

## 🎯 Implementation Plan

### **Step 1: Fix Anomaly Score Visualization**
```python
# Add to create_plots() function:
# - 5th subplot for anomaly score
# - Time series line chart
# - Threshold line at 3.0
# - Color zones (green/yellow/red)
```

### **Step 2: Set Stable Defaults**
```python
# In __init__():
self.stable_temp_range = (118, 122)  # °C
self.stable_pressure_range = (2.7, 2.9)  # bar
self.stable_flow_range = (43, 47)  # kg/h
self.stable_level_range = (64, 70)  # %

# Add stability indicator
def check_stability(self):
    return all([
        self.stable_temp_range[0] <= current_temp <= self.stable_temp_range[1],
        self.stable_pressure_range[0] <= current_pressure <= self.stable_pressure_range[1],
        # ... other checks
    ])
```

### **Step 3: Add Control Explanations**
```html
<!-- Add to HTML template -->
<div class="control-help">
    <h4>🎛️ Control Guide</h4>
    <div class="help-item">
        <strong>A/C Feed Ratio:</strong>
        <p>Normal: 1.0 | Anomaly triggers: <0.8 or >1.3</p>
        <p>Effect: Changes reactor temperature and pressure</p>
    </div>
    <div class="help-item">
        <strong>Fault Types:</strong>
        <ul>
            <li><strong>A/C Feed Ratio:</strong> Causes temperature spikes</li>
            <li><strong>Cooling Water:</strong> Overheating risk</li>
            <li><strong>Feed Loss:</strong> Flow and level drops</li>
        </ul>
    </div>
</div>
```

## ⏰ Timeline

### **Today (2 hours):**
- [ ] Fix JSON serialization bug
- [ ] Add anomaly score plot
- [ ] Set stable default conditions

### **Tomorrow (3 hours):**
- [ ] Add control explanations and tooltips
- [ ] Improve UI layout for 5 plots
- [ ] Test all functionality

### **This Week:**
- [ ] Add stability indicator
- [ ] Enhance anomaly detection algorithm
- [ ] Create user guide documentation

## 🧪 Testing Checklist

### **Before Release:**
- [ ] Dashboard loads without errors
- [ ] All 5 plots display correctly
- [ ] Anomaly score visible and updating
- [ ] Controls have clear explanations
- [ ] Stable conditions clearly indicated
- [ ] AI analysis triggers at score > 3.0
- [ ] All API endpoints return 200 status

### **User Experience Test:**
- [ ] New user can understand normal conditions
- [ ] User can trigger anomaly intentionally
- [ ] User knows when to expect AI analysis
- [ ] Controls are self-explanatory
- [ ] Visual feedback is clear and immediate

## 📝 Success Criteria

### **User Should Be Able To:**
1. **Understand Normal State:** See stable baseline conditions clearly
2. **Trigger Anomalies:** Know which controls cause which effects
3. **Monitor Detection:** Watch anomaly score rise and fall
4. **Get AI Analysis:** See explanations when score > 3.0
5. **Learn System:** Use without external documentation

### **Technical Requirements:**
1. **Performance:** All plots update smoothly every 2 seconds
2. **Reliability:** No API errors or crashes
3. **Usability:** Intuitive interface requiring no training
4. **Accuracy:** Anomaly detection correlates with actual faults
5. **Responsiveness:** Controls provide immediate visual feedback
