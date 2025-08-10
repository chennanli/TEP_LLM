# 🤖 Project 2: FaultExplainer AI Analysis System

## 📍 **Project Location**
- **Root Directory**: `external_repos/FaultExplainer-main/`
- **Backend**: `external_repos/FaultExplainer-main/backend/`
- **Frontend**: `external_repos/FaultExplainer-main/frontend/`

## 🎯 **Project Purpose**
AI-powered fault detection and diagnosis system using PCA anomaly detection combined with Multi-LLM analysis for industrial process monitoring.

## 🏗️ **Architecture**

### **Full-Stack Web Application**
```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   React Frontend    │    │   FastAPI Backend   │    │   AI/ML Services    │
│   (TypeScript)      │◄──►│   (Python)          │◄──►│   (Claude/LMStudio) │
│                     │    │                     │    │                     │
│ • Mantine UI        │    │ • PCA Analysis      │    │ • Multi-LLM         │
│ • D3.js Charts      │    │ • Data Processing   │    │ • Fault Diagnosis   │
│ • Real-time Updates │    │ • API Endpoints     │    │ • Natural Language  │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

## 🛠️ **Technology Stack**

### **Frontend (React + TypeScript)**
```json
{
  "core": {
    "react": "^18.2.0",
    "typescript": "^5.2.2",
    "vite": "^5.2.0"
  },
  "ui_framework": {
    "@mantine/core": "^7.11.2",
    "@mantine/charts": "^7.11.2",
    "@tabler/icons-react": "^3.6.0"
  },
  "visualization": {
    "d3": "^7.9.0",
    "recharts": "^2.13.0-alpha.4"
  },
  "utilities": {
    "react-router-dom": "^6.23.1",
    "papaparse": "^5.4.1",
    "marked": "^13.0.0"
  }
}
```

### **Backend (FastAPI + Python)**
```python
# Core Framework
fastapi>=0.111.0
uvicorn>=0.30.1
pydantic>=2.7.4

# AI/ML Stack
scikit-learn>=1.5.0  # PCA analysis
numpy>=2.0.0
pandas>=2.2.2

# LLM Integration
anthropic>=0.61.0    # Claude API
openai>=1.34.0       # LMStudio/OpenAI
google-generativeai>=0.8.3  # Gemini (disabled)

# Data Processing
matplotlib>=3.9.0
plotly>=5.22.0

# Web Framework
starlette>=0.37.2
python-multipart>=0.0.9
```

## 📊 **Backend Architecture**

### **Core Components**

#### **1. FastAPI Application**
**File**: `backend/app.py`
```python
# Main API server
app = FastAPI(title="FaultExplainer Backend")

# Key endpoints
@app.post("/explain")      # LLM fault analysis
@app.get("/health")        # System status
@app.post("/analyze")      # PCA analysis
@app.get("/config")        # Configuration
```

#### **2. PCA Fault Detection Model**
**File**: `backend/model.py`
```python
class FaultDetectionModel:
    def __init__(self, n_components=0.9, alpha=0.01):
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=n_components)
        self.t2_threshold = None
    
    def fit(self, training_data):
        # Train on normal operation data (fault0.csv)
        Z = self.scaler.fit_transform(training_data)
        self.pca.fit(Z)
        self.set_t2_threshold()
    
    def process_data_point(self, data_point):
        # Real-time anomaly detection
        anomaly, t2_stat = self.is_anomaly(data_point)
        return anomaly
```

#### **3. Multi-LLM Client**
**File**: `backend/multi_llm_client.py`
```python
class MultiLLMClient:
    def __init__(self, config):
        self.clients = {}
        # Initialize enabled LLM clients
        for model_name, model_config in config["models"].items():
            if model_config.get("enabled", False):
                if model_name == "claude":
                    self.clients[model_name] = self._init_claude(model_config)
                elif model_name == "lmstudio":
                    self.clients[model_name] = self._init_lmstudio(model_config)
    
    async def get_analysis_from_all_models(self, system_message, user_prompt):
        # Query all enabled LLMs concurrently
        results = {}
        for model_name in self.enabled_models:
            results[model_name] = await self._query_model(model_name, system_message, user_prompt)
        return results
```

#### **4. Prompt Engineering**
**File**: `backend/prompts.py`
```python
# System context for LLMs
INTRO_MESSAGE = """Tennessee Eastman Process description..."""
SYSTEM_MESSAGE = f"Process description:\n{INTRO_MESSAGE}"

# Analysis prompts
EXPLAIN_PROMPT = "Open-ended fault analysis"
EXPLAIN_ROOT = "Constrained to 15 known root causes"
```

### **Configuration Management**
**File**: `config.json`
```json
{
    "models": {
        "claude": {
            "enabled": true,
            "api_key": "sk-ant-api03-...",
            "model_name": "claude-3-5-sonnet-20241022"
        },
        "lmstudio": {
            "enabled": true,
            "base_url": "http://localhost:1234/v1",
            "model_name": "local-model",
            "api_key": "lm-studio"
        }
    },
    "fault_trigger_consecutive_step": 6,
    "topkfeatures": 6,
    "prompt": "explain",
    "pca_window_size": 20,
    "anomaly_threshold": 0.01
}
```

## 🎨 **Frontend Architecture**

### **Component Structure**
```
src/
├── App.tsx                    # Main application router
├── main.tsx                   # Application entry point
├── pages/
│   ├── PlotPage.tsx          # Real-time monitoring charts
│   ├── FaultReports.tsx      # T² statistics & fault history
│   ├── ChatPage.tsx          # LLM chat interface
│   └── ComparativeLLMResults.tsx  # Multi-LLM comparison
└── assets/
    └── intro.json            # TEP process description
```

### **Key Components**

#### **1. Main Navigation**
**File**: `src/App.tsx`
```tsx
// Three main tabs
<Tabs defaultValue="plot">
  <Tabs.List>
    <Tabs.Tab value="plot" leftSection={<IconChartLine />}>
      Monitoring
    </Tabs.Tab>
    <Tabs.Tab value="reports" leftSection={<IconReportAnalytics />}>
      Fault History
    </Tabs.Tab>
    <Tabs.Tab value="chat" leftSection={<IconRobot />}>
      Assistant
    </Tabs.Tab>
  </Tabs.List>
</Tabs>
```

#### **2. Real-time Monitoring**
**File**: `src/pages/PlotPage.tsx`
```tsx
// Interactive charts with D3.js
const PlotPage = () => {
  const [data, setData] = useState([]);
  const [selectedFile, setSelectedFile] = useState('fault0.csv');
  
  // Real-time data loading
  useEffect(() => {
    loadCSVData(selectedFile);
  }, [selectedFile]);
  
  return (
    <div>
      <Select data={faultFiles} onChange={setSelectedFile} />
      <LineChart data={data} />
      <ScatterPlot data={data} />
    </div>
  );
};
```

#### **3. LLM Chat Interface**
**File**: `src/pages/ChatPage.tsx`
```tsx
// Multi-LLM fault analysis
const ChatPage = () => {
  const [messages, setMessages] = useState([]);
  const [selectedFile, setSelectedFile] = useState('fault1.csv');
  
  const handleExplain = async () => {
    const response = await fetch('/api/explain', {
      method: 'POST',
      body: JSON.stringify({ file: selectedFile, data: currentData })
    });
    
    const result = await response.json();
    setMessages(prev => [...prev, result]);
  };
  
  return (
    <div>
      <Select data={faultFiles} onChange={setSelectedFile} />
      <Button onClick={handleExplain}>Explain Fault</Button>
      <ChatMessages messages={messages} />
    </div>
  );
};
```

#### **4. Fault History Dashboard**
**File**: `src/pages/FaultReports.tsx`
```tsx
// T² statistics and anomaly detection
const FaultReports = () => {
  const [t2Stats, setT2Stats] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  
  return (
    <div>
      <T2StatisticsChart data={t2Stats} />
      <AnomalyTable data={anomalies} />
      <ContributionAnalysis />
    </div>
  );
};
```

## 🔄 **Data Flow**

### **1. Data Input**
```python
# CSV files in frontend/public/
fault0.csv   # Normal operation (training data)
fault1.csv   # A/C Feed Ratio fault
fault4.csv   # Cooling water fault
# ... (fault2.csv through fault20.csv)
```

### **2. PCA Analysis Pipeline**
```python
# 1. Load training data (fault0.csv)
training_data = pd.read_csv("fault0.csv")
model.fit(training_data)

# 2. Process new data point-by-point
for data_point in new_data:
    anomaly = model.process_data_point(data_point)
    if anomaly:
        trigger_llm_analysis()
```

### **3. LLM Analysis Flow**
```python
# 1. Feature comparison
comparison_result = generate_feature_comparison(fault_data, normal_data)

# 2. Prompt construction
user_prompt = f"{EXPLAIN_PROMPT}\n{comparison_result}"

# 3. Multi-LLM query
llm_results = await multi_llm_client.get_analysis_from_all_models(
    system_message=SYSTEM_MESSAGE,
    user_prompt=user_prompt
)

# 4. Format results
formatted_results = multi_llm_client.format_comparative_results(
    results=llm_results,
    feature_comparison=comparison_result
)
```

## 🚀 **Startup Commands**

### **Backend Server**
```bash
cd external_repos/FaultExplainer-main/backend
source ../../../tep_env/bin/activate
python app.py
# Runs on: http://localhost:8000
```

### **Frontend Development**
```bash
cd external_repos/FaultExplainer-main/frontend
npm run dev
# Runs on: http://localhost:5173
```

### **Production Build**
```bash
cd external_repos/FaultExplainer-main/frontend
npm run build
npm run preview
```

## 📁 **File Structure**
```
FaultExplainer-main/
├── backend/
│   ├── app.py                 # FastAPI main application
│   ├── model.py               # PCA fault detection
│   ├── multi_llm_client.py    # LLM integration
│   ├── prompts.py             # LLM prompts
│   ├── analysis.py            # Feature analysis
│   ├── requirements.txt       # Python dependencies
│   └── data/                  # Training data
├── frontend/
│   ├── src/
│   │   ├── App.tsx           # Main application
│   │   ├── main.tsx          # Entry point
│   │   └── pages/            # React components
│   ├── public/               # Static files & CSV data
│   ├── package.json          # Node.js dependencies
│   └── vite.config.ts        # Build configuration
├── config.json               # System configuration
└── README.md                 # Project documentation
```

## 🎯 **Key Features**

### **AI Analysis Capabilities**
- **PCA Anomaly Detection**: T² statistics with 90% variance retention
- **Multi-LLM Comparison**: Claude 3.5 Sonnet + LMStudio local models
- **Feature Ranking**: Identifies top contributing variables to faults
- **Natural Language**: Industrial-grade fault diagnosis reports

### **Web Interface Features**
- **Real-time Monitoring**: Live charts with D3.js visualization
- **Interactive Analysis**: Click-to-analyze fault data
- **Multi-LLM Chat**: Compare responses from different AI models
- **Fault History**: T² statistics and anomaly timeline

### **Professional Integration**
- **RESTful API**: FastAPI with automatic documentation
- **Configurable Models**: Easy LLM provider switching
- **Industrial Data**: Supports TEP 52-variable format
- **Scalable Architecture**: Async processing with proper error handling

This project provides **professional-grade AI fault analysis** with modern web interfaces and multi-LLM capabilities.
