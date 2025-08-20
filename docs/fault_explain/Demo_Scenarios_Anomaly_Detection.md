# TEP Demo Scenarios for Anomaly Detection Presentation

**Purpose:** Designed demo scenarios to showcase early anomaly detection capabilities  
**Target Audience:** Management, stakeholders, technical demonstrations  
**Key Message:** Anomaly detection catches problems before traditional alarms

## 🎯 **Demo Strategy Overview**

### **Demonstration Goals:**
1. **Show control variable manipulation** → Process changes
2. **Measurements appear normal** → Within traditional alarm limits  
3. **Anomaly detection triggers early** → Before obvious problems
4. **LLM provides intelligent diagnosis** → Root cause analysis

### **Why This Works:**
- **Traditional monitoring**: Waits for measurements to exceed limits
- **Anomaly detection**: Detects **patterns** and **correlations** breaking down
- **Early warning**: 15-30 minutes before traditional alarms
- **Intelligent diagnosis**: LLM explains what's happening

## 🎛️ **Recommended Demo Scenarios**

### **Scenario 1: Feed Composition Drift (Subtle but Detectable)**

#### **Control Actions:**
```
1. Gradually increase XMV(4) from 61% to 75% over 15 minutes
   (A+C Feed Flow - increases A and C to reactor)

2. Slightly decrease XMV(1) from 63% to 58% over 10 minutes  
   (D Feed Flow - reduces D availability)

3. Keep all other controls unchanged
```

#### **What Happens:**
- **A/C to D ratio changes** → Affects reaction stoichiometry
- **Individual measurements stay in normal ranges**
- **Correlation patterns change** → Anomaly detection triggers
- **Product quality slowly shifts** → But still within specs initially

#### **Expected Timeline:**
```
t=0-15min:  Gradual XMV changes
t=10-20min: Composition ratios start shifting  
t=15-25min: Anomaly detection triggers (PCA SPE increases)
t=20-30min: Product composition measurably different
t=30-45min: Traditional alarms might trigger (if at all)
```

#### **Measurements to Watch:**
| **XMEAS** | **Variable** | **Expected** | **Status** |
|-----------|--------------|--------------|------------|
| **XMEAS(4)** | A+C Feed Flow | ↑ (75%) | Within limits |
| **XMEAS(2)** | D Feed Flow | ↓ (58%) | Within limits |
| **XMEAS(23)** | Reactor Feed A% | ↑ slowly | Within limits initially |
| **XMEAS(26)** | Reactor Feed D% | ↓ slowly | Within limits initially |
| **XMEAS(40)** | Product G% | Changes | Within specs initially |
| **XMEAS(41)** | Product H% | Changes | Within specs initially |

#### **LLM Diagnosis Expected:**
*"Feed composition imbalance detected. Increased A+C feed (XMV4: 61%→75%) combined with reduced D feed (XMV1: 63%→58%) is creating stoichiometric imbalance. This will affect G/H product ratio and may lead to reduced conversion efficiency. Recommend adjusting feed ratios to maintain optimal A:C:D stoichiometry."*

---

### **Scenario 2: Cooling System Degradation (Equipment Issue)**

#### **Control Actions:**
```
1. Gradually reduce XMV(10) from 41% to 35% over 20 minutes
   (Reactor Cooling Water Flow - simulates reduced cooling capacity)

2. Slightly increase XMV(4) from 61% to 65% over 15 minutes
   (A+C Feed Flow - increases heat generation)

3. Keep temperature setpoint unchanged
```

#### **What Happens:**
- **Reduced cooling + increased feed** → Higher heat generation
- **Temperature controller works harder** → More aggressive control
- **Temperature oscillations develop** → Control performance degrades
- **Anomaly detection sees control degradation** → Early warning

#### **Expected Timeline:**
```
t=0-20min:  Gradual cooling reduction + feed increase
t=10-25min: Temperature controller starts working harder
t=15-30min: Anomaly detection triggers (control performance metrics)
t=20-35min: Temperature oscillations become visible
t=30-45min: Traditional temperature alarms might trigger
```

#### **Measurements to Watch:**
| **XMEAS** | **Variable** | **Expected** | **Status** |
|-----------|--------------|--------------|------------|
| **XMEAS(9)** | Reactor Temperature | Oscillates | Within ±2°C initially |
| **XMEAS(21)** | Cooling Water Outlet | ↑ slowly | Within limits |
| **XMEAS(4)** | A+C Feed Flow | ↑ (65%) | Within limits |
| **XMV(10)** | Cooling Water Valve | 35% | Manually set |

#### **LLM Diagnosis Expected:**
*"Cooling system performance degradation detected. Reduced cooling water flow (XMV10: 41%→35%) combined with increased feed rate (XMV4: 61%→65%) is causing thermal imbalance. Temperature control is becoming more aggressive with developing oscillations. This suggests either cooling system fouling, valve problems, or insufficient cooling capacity. Recommend investigating cooling system and consider reducing feed rate."*

---

### **Scenario 3: Recycle System Imbalance (Process Optimization Gone Wrong)**

#### **Control Actions:**
```
1. Increase XMV(5) from 22% to 35% over 25 minutes
   (Compressor Recycle Valve - increases recycle ratio)

2. Decrease XMV(6) from 40% to 30% over 20 minutes  
   (Purge Valve - reduces purge rate)

3. Slightly increase XMV(1,2,3) by 2-3% each
   (Feed flows - compensate for recycle changes)
```

#### **What Happens:**
- **Higher recycle + lower purge** → Inerts accumulate
- **Feed increases** → More material in system
- **Pressure slowly builds** → System becomes less stable
- **Composition patterns change** → Anomaly detection triggers

#### **Expected Timeline:**
```
t=0-25min:  Gradual recycle/purge/feed changes
t=15-30min: Inert accumulation starts
t=20-35min: Anomaly detection triggers (composition correlations)
t=25-40min: Pressure trends upward (still within limits)
t=35-50min: Traditional pressure alarms might trigger
```

#### **Measurements to Watch:**
| **XMEAS** | **Variable** | **Expected** | **Status** |
|-----------|--------------|--------------|------------|
| **XMEAS(5)** | Recycle Flow | ↑ | Within limits |
| **XMEAS(10)** | Purge Rate | ↓ | Within limits |
| **XMEAS(7)** | Reactor Pressure | ↑ slowly | Within limits initially |
| **XMEAS(30)** | Purge B% | ↑ slowly | Inerts accumulating |
| **XMEAS(20)** | Compressor Work | ↑ | Higher load |

#### **LLM Diagnosis Expected:**
*"Recycle system imbalance detected. Increased recycle flow (XMV5: 22%→35%) with reduced purge rate (XMV6: 40%→30%) is causing inert accumulation. Component B concentration in purge is increasing, indicating buildup of non-reactive components. This will lead to pressure buildup and reduced process efficiency. Recommend increasing purge rate or reducing recycle ratio to maintain material balance."*

## 🎯 **Demo Execution Guide**

### **Pre-Demo Setup:**
1. **Start with normal operation** → All measurements stable
2. **Show baseline anomaly scores** → PCA SPE, T² normal
3. **Explain traditional alarm limits** → Show current margins
4. **Set expectations** → "Watch for early detection"

### **During Demo:**
1. **Make gradual changes** → Avoid sudden jumps
2. **Narrate actions** → "Increasing A+C feed to optimize production"
3. **Point out normal measurements** → "Everything looks fine so far"
4. **Highlight anomaly detection** → "But our AI sees a pattern"

### **Demo Script Example:**
```
"Let me show you how our advanced monitoring works. I'm going to make 
some process optimizations that look reasonable - increasing our A+C 
feed flow to boost production, and adjusting our D feed slightly.

[Make changes]

Notice that all our measurements are still within normal operating 
ranges - temperature is fine, pressure is stable, flows are reasonable. 
A traditional control system would see no problems.

[Wait 15-20 minutes]

But look here - our anomaly detection system is starting to flag 
something. The PCA score is rising, indicating that the correlations 
between variables are changing in an unexpected way.

[LLM analysis appears]

And now our AI diagnosis explains what's happening - we've created a 
stoichiometric imbalance that will affect product quality. We caught 
this 20-30 minutes before any traditional alarm would trigger, giving 
us time to correct the issue before it impacts production."
```

### **Key Demo Points:**
1. **Gradual changes** → Realistic operational scenarios
2. **Normal measurements** → Traditional monitoring misses it
3. **Early detection** → 15-30 minute advantage
4. **Intelligent diagnosis** → AI explains root cause
5. **Actionable insights** → Clear recommendations

## 📊 **Expected Results Summary**

### **Scenario Comparison:**
| **Scenario** | **Detection Time** | **Traditional Alarm** | **Advantage** |
|--------------|-------------------|---------------------|---------------|
| **Feed Composition** | 15-25 min | 30-45 min | 15-20 min earlier |
| **Cooling Degradation** | 15-30 min | 30-45 min | 15-20 min earlier |
| **Recycle Imbalance** | 20-35 min | 35-50 min | 15-20 min earlier |

### **Success Metrics:**
- **Anomaly detection triggers** before traditional alarms
- **Measurements remain** within normal ranges initially
- **LLM provides** accurate root cause analysis
- **Recommendations are** actionable and correct

## 🎯 **Backup Scenarios (If Primary Fails)**

### **Simple Valve Position Demo:**
```
1. Set XMV(10) to 50% (higher than normal 41%)
2. Watch temperature response and anomaly detection
3. Show how AI detects the manual override
```

### **Feed Flow Ratio Demo:**
```
1. Increase XMV(1) to 70% and decrease XMV(2) to 45%
2. Keep total feed roughly constant
3. Show composition ratio changes detected early
```

## 📋 **Demo Success Factors**

### **Technical Requirements:**
- **Stable baseline** → System in normal operation
- **Responsive anomaly detection** → PCA/monitoring working
- **LLM integration** → AI analysis available
- **Real-time updates** → Live data display

### **Presentation Tips:**
- **Start simple** → Explain what you're changing
- **Build suspense** → "Everything looks normal, but..."
- **Show the reveal** → Anomaly detection triggers
- **Explain the value** → Early warning prevents problems

**These scenarios are designed to showcase the power of advanced process monitoring - catching problems early when they can still be prevented, rather than reacting after damage is done.**
