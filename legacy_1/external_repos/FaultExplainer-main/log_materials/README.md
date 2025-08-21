# TEP Knowledge Base - Log Materials

## 📋 Overview

This folder contains PDF documents that serve as the knowledge base for the TEP (Tennessee Eastman Process) fault analysis RAG (Retrieval-Augmented Generation) system.

## 📁 Folder Structure

```
log_materials/
├── README.md                          # This file
├── process_manuals/                   # Process operation manuals
├── troubleshooting_guides/            # Fault diagnosis procedures
├── maintenance_procedures/            # Equipment maintenance docs
├── safety_protocols/                  # Safety and emergency procedures
├── historical_cases/                  # Past fault analysis reports
└── technical_specifications/          # Equipment and process specs
```

## 📄 Document Types

### **Recommended Document Categories:**

1. **Process Operation Manuals**
   - TEP process flow diagrams
   - Normal operating procedures
   - Control system documentation
   - Process variable descriptions

2. **Troubleshooting Guides**
   - Fault diagnosis procedures
   - Root cause analysis methodologies
   - Corrective action procedures
   - Emergency response protocols

3. **Historical Case Studies**
   - Past fault analysis reports
   - Lessons learned documents
   - Incident investigation reports
   - Best practices documentation

4. **Technical Specifications**
   - Equipment specifications
   - Instrumentation calibration procedures
   - Process design parameters
   - Safety system documentation

5. **Maintenance Procedures**
   - Preventive maintenance schedules
   - Equipment replacement procedures
   - Calibration protocols
   - Inspection checklists

## 🔧 Usage Instructions

### **Adding New Documents:**

1. **Place PDF files** in this folder or appropriate subfolders
2. **Run indexing** to add documents to the vector database:
   ```python
   from rag_system import TEPKnowledgeRAG
   
   rag = TEPKnowledgeRAG(knowledge_folder="log_materials")
   rag.index_documents()
   ```

3. **Verify indexing** by checking the system status:
   ```python
   status = rag.get_system_status()
   print(f"Indexed {status['total_documents']} document chunks")
   ```

### **Document Naming Convention:**

Use descriptive names that indicate content and version:
- `TEP_Process_Manual_v2.1.pdf`
- `Fault_Diagnosis_Procedures_2024.pdf`
- `Reactor_Troubleshooting_Guide.pdf`
- `Historical_Fault_Analysis_2023.pdf`

### **Document Quality Guidelines:**

1. **Text-Based PDFs**: Ensure PDFs contain searchable text (not just images)
2. **Clear Structure**: Use headings and sections for better chunk extraction
3. **Relevant Content**: Focus on TEP-specific or chemical process content
4. **Current Information**: Keep documents up-to-date and remove obsolete versions

## 🤖 RAG Integration

### **How RAG Enhances Fault Analysis:**

1. **Knowledge Retrieval**: When a fault is detected, the system searches for relevant troubleshooting procedures
2. **Context Enhancement**: LLM prompts are enhanced with relevant knowledge base content
3. **Source Citation**: LLM responses include references to specific documents and pages
4. **Knowledge Gaps**: System explicitly states when no relevant information is found

### **Search Capabilities:**

The RAG system searches based on:
- **Fault Features**: Top contributing variables (e.g., "reactor temperature pressure")
- **Fault Types**: Specific fault classifications
- **Process Context**: General TEP troubleshooting information
- **Semantic Similarity**: Content meaning rather than exact keyword matches

## 📊 System Integration

### **Current Workflow Enhancement:**

```
1. TEP Simulation → 2. PCA Anomaly Detection → 3. Feature Analysis
                                                        ↓
4. RAG Knowledge Search ← 5. Enhanced LLM Prompt ← 6. Original Prompt
                                                        ↓
7. Knowledge-Enhanced Analysis → 8. Cited Recommendations → 9. User Interface
```

### **Example Enhanced Analysis:**

**Without RAG:**
> "Based on the statistical analysis, the reactor temperature increase suggests a cooling system issue..."

**With RAG:**
> "Based on the statistical analysis and relevant documentation (Source: Reactor_Troubleshooting_Guide.pdf, Page 15), the reactor temperature increase suggests a cooling system issue. The troubleshooting guide recommends checking coolant flow rates and heat exchanger performance as first steps..."

## 🔍 Monitoring and Maintenance

### **Regular Tasks:**

1. **Update Documents**: Add new procedures and remove outdated ones
2. **Reindex Database**: Run `rag.index_documents(force_reindex=True)` after major updates
3. **Monitor Performance**: Check search relevance and adjust similarity thresholds
4. **Review Citations**: Ensure LLM responses properly cite knowledge sources

### **Performance Metrics:**

- **Document Coverage**: Number of indexed documents vs. available PDFs
- **Search Relevance**: Similarity scores for retrieved knowledge chunks
- **Citation Accuracy**: Proper source attribution in LLM responses
- **Knowledge Utilization**: Frequency of knowledge base usage in analyses

## 🚀 Getting Started

### **Quick Setup:**

1. **Add Sample Documents**: Place a few relevant PDFs in this folder
2. **Initialize RAG System**:
   ```bash
   cd legacy/external_repos/FaultExplainer-main/backend
   python -c "from rag_system import TEPKnowledgeRAG; rag = TEPKnowledgeRAG(); rag.index_documents()"
   ```
3. **Test Search**:
   ```python
   results = rag.search_knowledge("reactor temperature fault")
   print(f"Found {len(results)} relevant chunks")
   ```

### **Integration with Existing System:**

The RAG system is designed to enhance, not replace, the current fault analysis workflow. It preserves all existing capabilities while adding knowledge-based context to improve analysis quality and provide actionable recommendations.

## 📚 Additional Resources

- **RAG System Code**: `backend/rag_system.py`
- **Integration Guide**: See implementation examples in updated `multi_llm_client.py`
- **Vector Database**: ChromaDB storage in `backend/knowledge_db/`
- **Processing Logs**: Check application logs for indexing and search activities
