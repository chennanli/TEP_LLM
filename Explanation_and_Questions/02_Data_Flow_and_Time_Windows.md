# Data Flow: TEP → PCA → LLM with Time Windows

## 🔄 **Complete Data Flow Architecture**

### **Overview:**
```
TEP2PY → Time Window Buffer → PCA Analysis → LLM Diagnosis
(3 min)     (20 samples)        (T² score)    (explanation)
```

## ⏰ **Time Window Calculations**

### **TEP Simulation Timing:**
- **1 TEP sample = 3 minutes** (0.05 hours in TEP time)
- **Window size = 20 samples**
- **Total window = 20 × 3 minutes = 60 minutes = 1 hour**

### **Sliding Window Behavior:**
```
Time 0:    [A₀] → Buffer size 1 → No PCA (not full)
Time 3min: [A₀, A₁] → Buffer size 2 → No PCA (not full)
Time 6min: [A₀, A₁, A₂] → Buffer size 3 → No PCA (not full)
...
Time 57min: [A₀, A₁, ..., A₁₉] → Buffer size 20 → PCA Analysis! ✅
Time 60min: [A₁, A₂, ..., A₂₀] → Buffer size 20 → PCA Analysis! ✅
Time 63min: [A₂, A₃, ..., A₂₁] → Buffer size 20 → PCA Analysis! ✅
```

**Key Point:** After initial 1-hour fill, PCA runs every 3 minutes with sliding window!

## 📚 **Deque (Double-Ended Queue) Explained**

### **What is Deque:**
```python
from collections import deque

# Create deque with maximum size
buffer = deque(maxlen=20)

# How it works:
buffer.append(1)    # [1]
buffer.append(2)    # [1, 2]
buffer.append(3)    # [1, 2, 3]
# ... continue adding until...
# [1, 2, 3, ..., 20]  (size = 20)

buffer.append(21)   # [2, 3, 4, ..., 21]  ← Oldest (1) removed automatically!
```

### **Deque Properties:**
- **FIFO (First In, First Out)** with size limit
- **O(1) complexity** for append/pop operations (very fast!)
- **Automatic overflow handling** - oldest data removed when full
- **Memory efficient** - no manual size management needed
- **Thread-safe** for single-producer, single-consumer scenarios

### **Why Deque is Perfect for Time Windows:**
```python
# Traditional approach (inefficient):
if len(buffer) >= 20:
    buffer.pop(0)      # O(n) operation - slow!
    buffer.append(new_data)

# Deque approach (efficient):
buffer.append(new_data)  # O(1) operation - fast!
# Automatic size management, no manual removal needed
```

## 📊 **Data Structure Flow**

### **Step 1: TEP2PY Single Point Output**
```python
# TEP2PY generates one data point per simulation step
tep = tep2py(idata)  # Input: IDV disturbances
tep.simulate()       # Run Fortran physics
data = tep.process_data  # Output: 52 variables (XMEAS + XMV)

# Single data point structure:
data_point = {
    'time': 0.05,           # Time in hours
    'XMEAS(1)': 0.25038,    # A Feed Flow
    'XMEAS(2)': 3674.0,     # D Feed Flow
    'XMEAS(7)': 2704.3,     # Reactor Pressure
    'XMEAS(8)': 74.863,     # Reactor Level
    'XMEAS(9)': 120.41,     # Reactor Temperature
    # ... 47 more variables
}
```

### **Step 2: Buffer Management**
```python
class DataBuffer:
    def __init__(self, window_size=20):
        self.window_size = window_size
        self.buffer = deque(maxlen=window_size)  # Automatic size management
        
    def add_point(self, tep_data_point):
        # Convert TEP variable names to FaultExplainer names
        mapped_point = self.map_tep_to_faultexplainer(tep_data_point)
        self.buffer.append(mapped_point)  # O(1) operation
        
        # When buffer is full, we have a time window matrix
        if len(self.buffer) == self.window_size:
            return self.create_matrix()
        return None
```

### **Step 3: Time Window Matrix Creation**
```python
# Time window matrix (20×52):
window_matrix = pd.DataFrame([
    # Time    A Feed   D Feed   Reactor Temp   Reactor Pressure   ...
    [0.05,   0.250,   3674.0,     120.41,        2704.3,         ...],
    [0.10,   0.251,   3659.4,     120.41,        2705.0,         ...],
    [0.15,   0.250,   3660.3,     120.42,        2706.2,         ...],
    # ...
    [1.00,   0.294,   3654.3,     120.37,        2703.2,         ...]
])

# For PCA analysis, remove time column:
feature_matrix = window_matrix.drop('time', axis=1)  # (20×52) features only
```

## 🔬 **PCA Analysis Process**

### **Data Preprocessing:**
```python
# 1. Standardization (Z-score normalization)
scaler = StandardScaler()
z = scaler.fit_transform(feature_matrix)  # Mean=0, Std=1 for each variable

# 2. PCA Transformation
pca = PCA(n_components=0.9)  # Keep 90% of variance
pca.fit(z)

# 3. T² Statistic Calculation
t2_stat = z @ P @ diag(λ⁻¹) @ P.T @ z.T
```

### **Time Handling in PCA:**
**Important:** PCA treats the 20 rows as **independent observations**, not time series!

```python
# PCA sees this (no time information):
feature_matrix = [
    [0.250, 3674.0, 120.41, 2704.3, ...],  # Sample 1
    [0.251, 3659.4, 120.41, 2705.0, ...],  # Sample 2
    [0.250, 3660.3, 120.42, 2706.2, ...],  # Sample 3
    # ...
]

# Time information preserved separately for:
# 1. LLM context (time series patterns)
# 2. Result timestamps
# 3. Trend analysis
```

### **Data Cleaning for Industrial Applications:**
For TEP and similar industrial processes:
- **Missing values:** Rare (sensors always report something)
- **Outliers:** Handled by T² threshold detection
- **Noise:** Included (represents real sensor noise)
- **No extensive cleaning needed** - PCA is robust to industrial noise

## 🤖 **LLM Integration**

### **When Anomaly Detected (T² > threshold):**
```python
def trigger_llm_analysis(self, pca_result):
    if pca_result['is_anomaly']:
        # Prepare context: recent time window + current state
        payload = {
            "time_series_data": pca_result['data_window'].to_dict('records'),
            "t2_statistic": pca_result['t2_statistic'],
            "threshold": pca_result['threshold'],
            "process_inputs": self.current_idv_inputs,
            "timestamp": datetime.now().isoformat()
        }
        
        # Send to FaultExplainer LLM endpoint
        response = requests.post(
            "http://localhost:8000/analyze_fault",
            json=payload
        )
```

### **LLM Context Includes:**
1. **Time series data:** Full 20-sample window with timestamps
2. **Process state:** Current IDV input values
3. **Anomaly metrics:** T² statistic and threshold
4. **Trend information:** How variables changed over time

## 📈 **Variable Mapping**

### **TEP2PY → FaultExplainer Name Conversion:**
```python
VARIABLE_MAPPING = {
    'XMEAS(1)': 'A Feed',
    'XMEAS(2)': 'D Feed', 
    'XMEAS(3)': 'E Feed',
    'XMEAS(4)': 'A and C Feed',
    'XMEAS(5)': 'Recycle Flow',
    'XMEAS(6)': 'Reactor Feed Rate',
    'XMEAS(7)': 'Reactor Pressure',
    'XMEAS(8)': 'Reactor Level',
    'XMEAS(9)': 'Reactor Temperature',
    # ... continue for all 52 variables
}
```

## 🎯 **Key Insights**

### **Buffer Behavior:**
- **Initial phase:** Collecting data for 1 hour (20 samples)
- **Steady state:** PCA analysis every 3 minutes with sliding window
- **Memory efficient:** Deque automatically manages size

### **PCA Approach:**
- **Standardized features:** All variables normalized to same scale
- **Time-agnostic:** Treats samples as independent observations
- **Robust to noise:** Industrial sensor noise doesn't break analysis

### **Real-time Performance:**
- **Fast buffering:** O(1) deque operations
- **Efficient PCA:** Vectorized calculations
- **Scalable:** Can handle high-frequency data streams

### **Time Window Trade-offs:**
- **Larger window (>20):** Better statistical power, slower response
- **Smaller window (<20):** Faster response, less statistical power
- **20 samples:** Good balance for TEP process dynamics

This architecture provides real-time anomaly detection with proper statistical foundation and efficient data management!
