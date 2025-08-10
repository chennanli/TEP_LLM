# LLM Timing and Queue Management for Real-Time Systems

## ⚡ **The Timing Challenge**

### **Problem Scenario:**
```
Time 0:  PCA detects anomaly → Send to LLM (Request #1)
Time 3:  PCA detects anomaly → Send to LLM (Request #2)  
Time 6:  PCA detects anomaly → Send to LLM (Request #3)
Time 5:  LLM Response #1 arrives (late!)
Time 8:  LLM Response #2 arrives
Time 12: LLM Response #3 arrives
```

**Issues:**
- **Fast PCA detection** (every 3 minutes)
- **Slow LLM analysis** (5-10 seconds per request)
- **Out-of-order responses** (Response #1 arrives after Request #2 sent)
- **Queue overflow** (too many pending requests)

## 🔄 **Solution: Timestamped Queue System**

### **Architecture:**
```
PCA Detection → Request Queue → LLM Worker → Response Queue → Dashboard
    (fast)         (buffer)      (slow)        (ordered)      (display)
```

### **Key Components:**

#### **1. Request Tracking:**
```python
pending_requests = {
    'req_001': {
        'request_id': 'req_001',
        'timestamp': '2025-01-07 14:30:15',
        'anomaly_data': {...},
        'status': 'pending',
        'submitted_at': 1704636615.0
    }
}
```

#### **2. Response Management:**
```python
completed_analyses = deque([
    {
        'request_id': 'req_001',
        'timestamp': '2025-01-07 14:30:15',
        'completed_at': 1704636625.0,
        'processing_time': 10.0,
        'analysis_result': {...}
    }
], maxlen=50)  # Keep last 50 analyses
```

#### **3. Queue Overflow Protection:**
```python
if len(pending_requests) >= max_concurrent:
    # Drop oldest pending request
    oldest_id = min(pending_requests.keys(), 
                   key=lambda x: pending_requests[x]['submitted_at'])
    dropped_request = pending_requests.pop(oldest_id)
    print(f"⚠️ Dropped request {oldest_id} (too many pending)")
```

## 📊 **Timeline Management**

### **Analysis Timeline Structure:**
```python
timeline = [
    {
        'timestamp': datetime(2025, 1, 7, 14, 30, 15),
        'type': 'completed',
        'request_id': 'req_001',
        'processing_time': 8.5,
        'explanation': 'Temperature spike detected. Likely A/C feed ratio fault...'
    },
    {
        'timestamp': datetime(2025, 1, 7, 14, 33, 18),
        'type': 'pending',
        'request_id': 'req_002',
        'processing_time': 12.3,  # Still processing
        'explanation': 'Analysis in progress...'
    }
]
```

### **Dashboard Display:**
```
📋 Analysis Timeline:
14:30:15 - COMPLETED - req_001 - Temperature spike detected (8.5s)
14:33:18 - PENDING   - req_002 - Analysis in progress... (12.3s)
14:36:22 - COMPLETED - req_003 - Pressure deviation identified (6.2s)
```

## ⏰ **Recommended Timing Strategy**

### **Current Problem:**
- **TEP simulation:** Every 3 minutes
- **PCA analysis:** Every 3 minutes (after buffer full)
- **LLM analysis:** Every anomaly detection (too frequent!)

### **Improved Timing:**
```
TEP Simulation:    Every 3 minutes  ←─ Keep this (process dynamics)
PCA Analysis:      Every 6 minutes  ←─ Reduce frequency
LLM Analysis:      Every 12 minutes ←─ Even less frequent
```

### **Implementation:**
```python
class TimingManager:
    def __init__(self):
        self.last_pca_time = 0
        self.last_llm_time = 0
        self.pca_interval = 6 * 60    # 6 minutes in seconds
        self.llm_interval = 12 * 60   # 12 minutes in seconds
    
    def should_run_pca(self, current_time):
        return (current_time - self.last_pca_time) >= self.pca_interval
    
    def should_run_llm(self, current_time):
        return (current_time - self.last_llm_time) >= self.llm_interval
```

## 📝 **Logging and Persistence**

### **Log File Structure:**
```
logs/
├── tep_simulation.log      # TEP simulation data
├── pca_analysis.log        # PCA results and T² scores
├── llm_diagnoses.log       # LLM analysis results
└── system_events.log       # System status and errors
```

### **LLM Diagnosis Log Format:**
```
2025-01-07 14:30:15 | ANOMALY_DETECTED | T²=15.234 | req_001
2025-01-07 14:30:23 | LLM_ANALYSIS     | req_001 | Temperature spike detected. A/C feed ratio imbalance likely cause. Recommend: (1) Check feed ratio setpoint (2) Verify cooling water temperature (3) Monitor reactor temperature trend
2025-01-07 14:33:18 | ANOMALY_DETECTED | T²=18.567 | req_002
2025-01-07 14:33:31 | LLM_ANALYSIS     | req_002 | Pressure deviation with temperature rise. Pattern suggests cooling water fault. Recommend: (1) Check cooling water flow (2) Verify cooling water temperature (3) Consider backup cooling
```

### **Data Persistence:**
```python
# Save analysis results to CSV for future reference
analysis_df = pd.DataFrame([
    {
        'timestamp': '2025-01-07 14:30:15',
        'request_id': 'req_001',
        't2_statistic': 15.234,
        'fault_type': 'A/C Feed Ratio',
        'confidence': 0.87,
        'processing_time': 8.5,
        'explanation': 'Temperature spike detected...',
        'recommendations': 'Check feed ratio setpoint; Verify cooling water'
    }
])
analysis_df.to_csv('logs/llm_analyses.csv', mode='a', header=False)
```

## 🎯 **Benefits of This Approach**

### **1. Reduced LLM Load:**
- **Before:** LLM call every 3 minutes (20 calls/hour)
- **After:** LLM call every 12 minutes (5 calls/hour)
- **75% reduction** in LLM requests

### **2. Better User Experience:**
- **Fewer notifications:** Not overwhelmed with constant alerts
- **More meaningful analyses:** Each LLM call has more context
- **Clear timeline:** Easy to see when each analysis occurred

### **3. System Reliability:**
- **Queue management:** Prevents system overload
- **Graceful degradation:** Drops oldest requests when overloaded
- **Persistent logging:** All analyses saved for future reference

### **4. Cost Efficiency:**
- **Reduced API calls:** Lower LLM usage costs
- **Better resource utilization:** System not constantly processing
- **Focused attention:** Operators see important alerts, not noise

## 📋 **Implementation Timeline**

### **Phase 1: Basic Timing (Immediate)**
```python
# Simple interval-based approach
if (current_time - last_llm_time) >= 12 * 60:  # 12 minutes
    if anomaly_detected:
        submit_to_llm()
        last_llm_time = current_time
```

### **Phase 2: Smart Queuing (Next)**
```python
# Queue-based approach with overflow protection
if anomaly_detected:
    if len(pending_requests) < max_concurrent:
        submit_to_llm()
    else:
        log_dropped_request()
```

### **Phase 3: Adaptive Timing (Future)**
```python
# Adjust timing based on system load and anomaly severity
if high_severity_anomaly:
    llm_interval = 6 * 60   # More frequent for critical issues
else:
    llm_interval = 12 * 60  # Standard interval
```

## 🔧 **Configuration Options**

### **Timing Parameters:**
```python
TIMING_CONFIG = {
    'tep_simulation_interval': 3 * 60,      # 3 minutes
    'pca_analysis_interval': 6 * 60,        # 6 minutes  
    'llm_analysis_interval': 12 * 60,       # 12 minutes
    'max_concurrent_llm': 3,                # Max parallel LLM requests
    'analysis_retention_days': 30,          # Keep analyses for 30 days
    'log_rotation_size': '100MB'            # Rotate logs at 100MB
}
```

This approach provides a balanced system that maintains real-time monitoring while preventing information overload and system resource exhaustion!
