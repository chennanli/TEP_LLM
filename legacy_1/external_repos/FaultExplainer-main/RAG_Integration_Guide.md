# TEP RAG Integration Guide

## 🎯 Overview

This guide explains how to integrate RAG (Retrieval-Augmented Generation) capabilities with the existing TEP fault analysis system. The RAG system enhances LLM responses by incorporating relevant knowledge from PDF documents.

## 🏗️ Architecture Overview

### **Enhanced System Flow:**

```
1. TEP Simulation → 2. PCA Anomaly Detection → 3. Feature Analysis
                                                        ↓
4. RAG Knowledge Search ← 5. Enhanced LLM Prompt ← 6. Original Prompt
                                                        ↓
7. Knowledge-Enhanced Analysis → 8. Cited Recommendations → 9. User Interface
```

### **Key Components Added:**

1. **`rag_system.py`** - Core RAG functionality
2. **Enhanced `multi_llm_client.py`** - RAG-integrated LLM client
3. **Updated `app.py`** - RAG management endpoints
4. **`log_materials/`** - Knowledge base folder for PDFs

## 🚀 Quick Start

### **1. Install Dependencies**

```bash
# Navigate to backend directory
cd legacy/external_repos/FaultExplainer-main/backend

# Install RAG dependencies
pip install chromadb sentence-transformers PyPDF2

# Or install from requirements file
pip install -r requirements_rag.txt
```

### **2. Setup Knowledge Base**

```bash
# Run setup script
python setup_rag.py

# Or manually create folder and add PDFs
mkdir log_materials
# Add your PDF files to log_materials/
```

### **3. Start Enhanced System**

```bash
# Start the backend with RAG capabilities
python app.py
```

### **4. Initialize Knowledge Base**

```bash
# Via API call
curl -X POST "http://localhost:8000/rag/initialize"

# Or via Python
import requests
response = requests.post("http://localhost:8000/rag/initialize")
print(response.json())
```

## 📋 Current System Analysis

### **What Makes Your TEP LLM System Effective:**

1. **🎯 Domain-Specific Prompting:**
   - Detailed TEP process descriptions in system prompts
   - Structured top-6 feature analysis with statistical comparisons
   - Chemical engineering context and technical language

2. **📊 Data-Driven Analysis:**
   - PCA-based anomaly detection with T² statistics
   - Feature contribution analysis identifying key variables
   - Statistical comparisons (fault vs. normal operation)

3. **🔄 Multi-LLM Architecture:**
   - Comparative analysis across Claude, Gemini, and LMStudio
   - Robust error handling with timeout management
   - Performance tracking and response time monitoring

4. **⚡ Real-Time Integration:**
   - Live data processing with time-windowed analysis
   - Automated fault callbacks when anomalies detected
   - Background processing for non-blocking analysis

### **RAG Enhancements Preserve These Strengths:**

- ✅ **All existing functionality maintained**
- ✅ **Statistical analysis workflow unchanged**
- ✅ **Multi-LLM comparison preserved**
- ✅ **Real-time processing capabilities intact**
- ✅ **Added knowledge-based context and citations**

## 🔧 RAG System Features

### **1. Intelligent Knowledge Retrieval**

```python
# Searches based on fault characteristics
fault_features = ["reactor_temperature", "coolant_flow", "pressure"]
knowledge = rag.search_knowledge("reactor temperature fault troubleshooting")

# Returns relevant document chunks with similarity scores
# Example result:
{
    "text": "Check coolant flow rates and heat exchanger performance...",
    "source": "TEP_Troubleshooting_Guide.pdf",
    "page": 15,
    "similarity": 0.87
}
```

### **2. Enhanced LLM Prompts**

**Before RAG:**
```
You have been provided with the descriptions of the Tennessee Eastman process (TEP). 
A fault has just occurred, and you are tasked with diagnosing its root cause.

Feature analysis shows reactor temperature increased by 15%...
```

**After RAG:**
```
You have been provided with the descriptions of the Tennessee Eastman process (TEP). 
A fault has just occurred, and you are tasked with diagnosing its root cause.

Feature analysis shows reactor temperature increased by 15%...

## RELEVANT KNOWLEDGE BASE INFORMATION:
**Source 1:** TEP_Troubleshooting_Guide.pdf (Page 15, Similarity: 0.87)
Check coolant flow rates and heat exchanger performance. Verify reactor 
temperature sensor calibration. Inspect cooling system for blockages...

## ANALYSIS INSTRUCTIONS:
- Consider the above knowledge base information in your analysis
- If relevant information is found, cite the source in your response
- If no relevant information is available, explicitly state this limitation
```

### **3. Source Citation in Responses**

**Enhanced LLM Response:**
```
Based on the statistical analysis and relevant documentation (Source: 
TEP_Troubleshooting_Guide.pdf, Page 15), the reactor temperature increase 
suggests a cooling system issue. The troubleshooting guide recommends 
checking coolant flow rates and heat exchanger performance as first steps.

Recommended actions:
1. Verify coolant flow rates (Reference: Maintenance_Manual.pdf, Page 23)
2. Inspect heat exchanger for fouling or blockages
3. Check temperature sensor calibration
```

## 🛠️ Implementation Details

### **1. Vector Database (ChromaDB)**

- **Local Storage**: No external dependencies
- **Persistent**: Data survives application restarts
- **Efficient**: Fast similarity search with embeddings
- **Scalable**: Handles large document collections

### **2. Document Processing**

```python
# Automatic PDF text extraction
chunks = rag.extract_text_from_pdf("troubleshooting_guide.pdf")

# Smart chunking by paragraphs
# Metadata tracking (source, page, chunk number)
# Duplicate detection and version management
```

### **3. Embedding Model**

- **Model**: `all-MiniLM-L6-v2` (384 dimensions)
- **Fast**: Optimized for speed and accuracy
- **Multilingual**: Supports various languages
- **Local**: No external API calls required

## 📊 API Endpoints

### **RAG Management Endpoints:**

```bash
# Initialize/update knowledge base
POST /rag/initialize?force_reindex=false

# Get system status
GET /rag/status

# Search knowledge base
POST /rag/search?query="reactor temperature"&n_results=5
```

### **Enhanced Fault Analysis:**

```bash
# Existing endpoint now includes RAG enhancement
POST /explain
{
    "id": "fault_123",
    "file": "fault1.csv",
    "data": [...] 
}
```

## 🔄 Integration with Existing Workflow

### **Legacy Folder Integration:**

1. **Preserve Current System**: All existing functionality maintained
2. **Add RAG Layer**: Knowledge enhancement without disruption
3. **Gradual Adoption**: Can be enabled/disabled as needed
4. **Backward Compatibility**: Works with existing data and APIs

### **Integration Folder Migration:**

When ready to update the integration folder:

1. **Copy RAG Components**:
   ```bash
   cp legacy/external_repos/FaultExplainer-main/backend/rag_system.py integration/src/backend/services/llm-analysis/
   cp -r legacy/external_repos/FaultExplainer-main/log_materials integration/
   ```

2. **Update Integration LLM Client**:
   - Add RAG imports and initialization
   - Enhance prompt generation with knowledge retrieval
   - Add RAG management endpoints

3. **Frontend Enhancements**:
   - Add knowledge base status display
   - Include source citations in analysis results
   - Add RAG management interface

## 📈 Performance Considerations

### **Optimization Strategies:**

1. **Chunking Strategy**: Paragraph-based for optimal context
2. **Similarity Threshold**: Configurable minimum relevance (default: 0.3)
3. **Result Limiting**: Top-N results to control prompt size
4. **Caching**: Document embeddings cached for fast retrieval
5. **Incremental Updates**: Only reprocess changed documents

### **Resource Usage:**

- **Memory**: ~200MB for embedding model + document vectors
- **Storage**: ~10MB per 100 PDF pages (varies by content)
- **CPU**: Minimal during search, moderate during indexing
- **Network**: None (fully local operation)

## 🧪 Testing and Validation

### **Test Scenarios:**

1. **Knowledge Retrieval Accuracy**:
   ```python
   # Test search relevance
   results = rag.search_knowledge("reactor temperature fault")
   assert len(results) > 0
   assert results[0]['similarity'] > 0.5
   ```

2. **Prompt Enhancement**:
   ```python
   # Test prompt augmentation
   enhanced = rag.enhance_prompt_with_knowledge(
       original_prompt="Analyze reactor fault",
       fault_features=["reactor_temp", "coolant_flow"]
   )
   assert "KNOWLEDGE BASE" in enhanced
   ```

3. **End-to-End Integration**:
   ```bash
   # Test full workflow
   curl -X POST "http://localhost:8000/explain" \
        -H "Content-Type: application/json" \
        -d '{"id": "test", "file": "fault1.csv", "data": [...]}'
   ```

## 🎯 Best Practices

### **Document Management:**

1. **Naming Convention**: Use descriptive, versioned names
2. **Content Quality**: Ensure PDFs contain searchable text
3. **Regular Updates**: Remove obsolete documents, add new ones
4. **Organization**: Use subfolders for different document types

### **Knowledge Base Maintenance:**

1. **Regular Reindexing**: After significant document changes
2. **Performance Monitoring**: Track search relevance and response times
3. **Content Review**: Ensure knowledge base stays current and accurate
4. **User Feedback**: Monitor LLM citation accuracy and usefulness

### **System Integration:**

1. **Gradual Rollout**: Test with subset of documents first
2. **Fallback Handling**: System works even if RAG fails
3. **Monitoring**: Log RAG usage and performance metrics
4. **Documentation**: Keep knowledge base content documented

## 🚀 Future Enhancements

### **Planned Improvements:**

1. **Advanced Chunking**: Semantic chunking based on content structure
2. **Multi-Modal**: Support for images and diagrams in PDFs
3. **Knowledge Graphs**: Relationship mapping between concepts
4. **Active Learning**: Improve retrieval based on user feedback
5. **Integration Folder**: Full migration to modern architecture

### **Scalability Options:**

1. **External Vector DB**: Migrate to Pinecone/Weaviate for large scale
2. **Distributed Processing**: Multi-node document processing
3. **Advanced Embeddings**: Domain-specific embedding models
4. **Real-Time Updates**: Live document monitoring and indexing

## 📚 Additional Resources

- **RAG System Code**: `backend/rag_system.py`
- **Setup Script**: `backend/setup_rag.py`
- **Requirements**: `backend/requirements_rag.txt`
- **Knowledge Folder**: `log_materials/README.md`
- **API Documentation**: Available at `/docs` when server is running

The RAG system is designed to enhance, not replace, your existing fault analysis capabilities while providing a foundation for future knowledge-driven improvements.
