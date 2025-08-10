# TEP Dynamic Simulator → PCA → LLM Data Flow

## 🎯 **Complete Data Flow Explanation**

### **Step 1: Dynamic Simulator Output (Point-by-Point)**
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

### **Step 2: Time Window Buffer (Matrix Formation)**
```python
# FaultExplainer needs a sliding window of data points
class DataBuffer:
    def __init__(self, window_size=20):
        self.window_size = window_size
        self.buffer = deque(maxlen=window_size)
        self.feature_columns = [
            'A Feed', 'D Feed', 'E Feed', 'A and C Feed', 'Recycle Flow',
            'Reactor Feed Rate', 'Reactor Pressure', 'Reactor Level', 
            'Reactor Temperature', 'Purge Rate', 'Product Sep Temp',
            # ... all 52 variables mapped to FaultExplainer names
        ]
    
    def add_point(self, tep_data_point):
        # Convert TEP variable names to FaultExplainer names
        mapped_point = self.map_tep_to_faultexplainer(tep_data_point)
        self.buffer.append(mapped_point)
        
        # When buffer is full, we have a time window matrix
        if len(self.buffer) == self.window_size:
            return self.create_matrix()
        return None
    
    def create_matrix(self):
        # Convert buffer to DataFrame (time window matrix)
        df = pd.DataFrame(list(self.buffer))
        return df[self.feature_columns]  # Only feature columns, no time
```

### **Step 3: PCA Analysis (T² Calculation)**
```python
# FaultExplainer PCA Model (already trained on normal data)
class FaultDetectionModel:
    def __init__(self):
        self.pca = PCA(n_components=0.9)
        self.scaler = StandardScaler()
        self.t2_threshold = 11.345  # Pre-calculated threshold
        
    def detect_anomaly(self, data_matrix):
        """
        Input: DataFrame with shape (window_size, n_features)
        Output: T² statistic for anomaly detection
        """
        # Take the latest data point from the window
        latest_point = data_matrix.iloc[-1:].copy()
        
        # Standardize using pre-fitted scaler
        z = self.scaler.transform(latest_point)
        
        # Calculate T² statistic using PCA components
        t2_stat = z @ self.P @ np.diag(self.lamda**-1) @ self.P.T @ z.T
        
        return {
            't2_statistic': t2_stat.item(),
            'is_anomaly': t2_stat.item() > self.t2_threshold,
            'threshold': self.t2_threshold,
            'data_window': data_matrix  # Keep window for LLM analysis
        }
```

### **Step 4: LLM Analysis (Context Window)**
```python
def trigger_llm_analysis(self, pca_result):
    """
    Send time window data to LLM when anomaly detected
    """
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
        
        return response.json()
```

## 📊 **Data Format Mapping**

### **TEP2PY Output → FaultExplainer Input:**
```python
# TEP2PY variable names → FaultExplainer expected names
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
    'XMEAS(10)': 'Purge Rate',
    'XMEAS(11)': 'Product Sep Temp',
    'XMEAS(12)': 'Product Sep Level',
    'XMEAS(13)': 'Product Sep Pressure',
    'XMEAS(14)': 'Product Sep Underflow',
    'XMEAS(15)': 'Stripper Level',
    'XMEAS(16)': 'Stripper Pressure',
    'XMEAS(17)': 'Stripper Underflow',
    'XMEAS(18)': 'Stripper Temp',
    'XMEAS(19)': 'Stripper Steam Flow',
    'XMEAS(20)': 'Compressor Work',
    'XMEAS(21)': 'Reactor Coolant Temp',
    'XMEAS(22)': 'Separator Coolant Temp',
    # ... continue for all 52 variables
}

def map_tep_to_faultexplainer(tep_data):
    """Convert TEP variable names to FaultExplainer format"""
    mapped_data = {}
    for tep_name, fe_name in VARIABLE_MAPPING.items():
        if tep_name in tep_data:
            mapped_data[fe_name] = tep_data[tep_name]
    return mapped_data
```

## 🔄 **Complete Integration Flow:**

### **Real-Time Processing:**
```python
class TEPFaultExplainerIntegration:
    def __init__(self):
        self.data_buffer = DataBuffer(window_size=20)
        self.pca_model = FaultDetectionModel()  # Pre-trained
        self.llm_client = FaultExplainerLLM()
        
    def process_tep_output(self, tep_data_point):
        """Process each TEP simulation output"""
        
        # Step 1: Add to time window buffer
        window_matrix = self.data_buffer.add_point(tep_data_point)
        
        if window_matrix is not None:  # Buffer is full
            
            # Step 2: PCA anomaly detection
            pca_result = self.pca_model.detect_anomaly(window_matrix)
            
            # Step 3: LLM analysis if anomaly detected
            if pca_result['is_anomaly']:
                llm_analysis = self.trigger_llm_analysis(pca_result)
                
                return {
                    'anomaly_detected': True,
                    't2_statistic': pca_result['t2_statistic'],
                    'llm_explanation': llm_analysis['explanation'],
                    'fault_diagnosis': llm_analysis['fault_type']
                }
        
        return {'anomaly_detected': False}
```

## 🎯 **Timeline Example:**

### **Time Window Processing:**
```
Time 0: TEP → Point A₀ → Buffer [A₀] (size 1)
Time 1: TEP → Point A₁ → Buffer [A₀, A₁] (size 2)
Time 2: TEP → Point A₂ → Buffer [A₀, A₁, A₂] (size 3)
...
Time 19: TEP → Point A₁₉ → Buffer [A₀...A₁₉] (size 20) → PCA Analysis
Time 20: TEP → Point A₂₀ → Buffer [A₁...A₂₀] (size 20) → PCA Analysis
```

### **PCA Window Analysis:**
```
Window Matrix (20×52):
    A Feed  D Feed  Reactor Temp  Reactor Pressure  ...
t₀  0.250   3674.0     120.41        2704.3       ...
t₁  0.251   3659.4     120.41        2705.0       ...
t₂  0.250   3660.3     120.42        2706.2       ...
...
t₁₉ 0.294   3654.3     120.37        2703.2       ...

PCA → T² = 2.34 (< threshold 11.345) → Normal
```

### **Anomaly Detection:**
```
Window Matrix (20×52):
    A Feed  D Feed  Reactor Temp  Reactor Pressure  ...
t₀  0.250   3674.0     120.41        2704.3       ...
t₁  0.251   3659.4     120.41        2705.0       ...
...
t₁₉ 0.294   3654.3     125.87        2850.2       ... ← Fault effects

PCA → T² = 15.67 (> threshold 11.345) → ANOMALY!
LLM → "Temperature spike detected. Pattern suggests A/C feed ratio fault..."
```

## 🔧 **Key Implementation Points:**

### **1. Buffer Management:**
- **Sliding window** of 20 data points (configurable)
- **FIFO queue** - oldest point removed when new point added
- **Feature alignment** - TEP variables mapped to FaultExplainer names

### **2. PCA Integration:**
- **Pre-trained model** on normal operation data (fault0.csv)
- **Standardization** using pre-fitted scaler
- **T² calculation** using PCA components and eigenvalues

### **3. LLM Context:**
- **Time series context** - entire window sent to LLM
- **Process state** - current IDV inputs included
- **Anomaly metrics** - T² statistic and threshold provided

### **4. Real-Time Performance:**
- **Efficient buffering** using deque with maxlen
- **Vectorized PCA** calculations
- **Asynchronous LLM** calls to avoid blocking

This is exactly how the professor's FaultExplainer system works - it takes time windows of process data, applies PCA for anomaly detection, and sends the context to LLM for fault diagnosis!
