#!/usr/bin/env python3
"""
Setup script for TEP RAG (Retrieval-Augmented Generation) system
Initializes the knowledge base and tests the system
"""

import os
import sys
import json
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'chromadb',
        'sentence_transformers',
        'PyPDF2'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            logger.info(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"❌ {package} is missing")
    
    if missing_packages:
        logger.error(f"Missing packages: {', '.join(missing_packages)}")
        logger.info("Install missing packages with:")
        logger.info(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def create_sample_pdf():
    """Create a sample PDF document for testing"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        sample_pdf_path = Path("log_materials/sample_tep_guide.pdf")
        sample_pdf_path.parent.mkdir(exist_ok=True)
        
        if sample_pdf_path.exists():
            logger.info(f"Sample PDF already exists: {sample_pdf_path}")
            return str(sample_pdf_path)
        
        # Create a simple PDF with TEP troubleshooting content
        c = canvas.Canvas(str(sample_pdf_path), pagesize=letter)
        width, height = letter
        
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "TEP Fault Analysis Guide")
        
        # Content
        c.setFont("Helvetica", 12)
        y_position = height - 100
        
        content = [
            "Tennessee Eastman Process Troubleshooting Procedures",
            "",
            "Reactor Temperature Faults:",
            "- Check coolant flow rates and heat exchanger performance",
            "- Verify reactor temperature sensor calibration",
            "- Inspect cooling system for blockages or leaks",
            "",
            "Pressure System Issues:",
            "- Monitor compressor performance and discharge pressure",
            "- Check for valve malfunctions or control system errors",
            "- Verify pressure relief system operation",
            "",
            "Flow Rate Anomalies:",
            "- Inspect pumps and flow control valves",
            "- Check for pipe blockages or restrictions",
            "- Verify flow meter calibration and operation",
            "",
            "Composition Control Problems:",
            "- Review analyzer calibration and maintenance",
            "- Check feed composition and quality",
            "- Verify control system setpoints and tuning",
        ]
        
        for line in content:
            if y_position < 50:  # Start new page if needed
                c.showPage()
                y_position = height - 50
                c.setFont("Helvetica", 12)
            
            c.drawString(50, y_position, line)
            y_position -= 20
        
        c.save()
        logger.info(f"✅ Created sample PDF: {sample_pdf_path}")
        return str(sample_pdf_path)
        
    except ImportError:
        logger.warning("reportlab not installed, cannot create sample PDF")
        logger.info("Install with: pip install reportlab")
        return None
    except Exception as e:
        logger.error(f"Error creating sample PDF: {str(e)}")
        return None

def create_sample_text_pdf():
    """Create a simple text-based PDF using basic methods"""
    sample_content = """TEP Fault Analysis Guide

Tennessee Eastman Process Troubleshooting Procedures

Reactor Temperature Faults:
- Check coolant flow rates and heat exchanger performance
- Verify reactor temperature sensor calibration
- Inspect cooling system for blockages or leaks

Pressure System Issues:
- Monitor compressor performance and discharge pressure
- Check for valve malfunctions or control system errors
- Verify pressure relief system operation

Flow Rate Anomalies:
- Inspect pumps and flow control valves
- Check for pipe blockages or restrictions
- Verify flow meter calibration and operation

Composition Control Problems:
- Review analyzer calibration and maintenance
- Check feed composition and quality
- Verify control system setpoints and tuning
"""
    
    # Create a simple text file that can be manually converted to PDF
    sample_txt_path = Path("log_materials/sample_tep_guide.txt")
    sample_txt_path.parent.mkdir(exist_ok=True)
    
    with open(sample_txt_path, 'w') as f:
        f.write(sample_content)
    
    logger.info(f"✅ Created sample text file: {sample_txt_path}")
    logger.info("Convert this to PDF manually or use online tools for testing")
    return str(sample_txt_path)

def test_rag_system():
    """Test the RAG system functionality"""
    try:
        from rag_system import TEPKnowledgeRAG
        
        logger.info("🧪 Testing RAG system...")
        
        # Initialize RAG system
        rag = TEPKnowledgeRAG(
            knowledge_folder="log_materials",
            db_path="knowledge_db"
        )
        
        # Index documents
        logger.info("📚 Indexing documents...")
        new_docs = rag.index_documents()
        logger.info(f"✅ Indexed {new_docs} new documents")
        
        # Get system status
        status = rag.get_system_status()
        logger.info(f"📊 System status: {status['total_documents']} total document chunks")
        
        # Test search
        test_queries = [
            "reactor temperature fault",
            "pressure system issues",
            "flow rate problems",
            "composition control"
        ]
        
        for query in test_queries:
            logger.info(f"🔍 Testing search: '{query}'")
            results = rag.search_knowledge(query, n_results=3)
            logger.info(f"   Found {len(results)} relevant chunks")
            
            if results:
                best_result = results[0]
                logger.info(f"   Best match: {best_result['source']} (similarity: {best_result['similarity']})")
        
        logger.info("✅ RAG system test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ RAG system test failed: {str(e)}")
        return False

def main():
    """Main setup function"""
    logger.info("🚀 Setting up TEP RAG system...")
    
    # Check dependencies
    if not check_dependencies():
        logger.error("❌ Dependency check failed")
        sys.exit(1)
    
    # Create log_materials directory
    log_materials_dir = Path("log_materials")
    log_materials_dir.mkdir(exist_ok=True)
    logger.info(f"✅ Created knowledge folder: {log_materials_dir}")
    
    # Check for existing PDFs
    pdf_files = list(log_materials_dir.glob("*.pdf"))
    if pdf_files:
        logger.info(f"📄 Found {len(pdf_files)} existing PDF files:")
        for pdf_file in pdf_files:
            logger.info(f"   - {pdf_file.name}")
    else:
        logger.info("📄 No PDF files found in log_materials folder")
        
        # Try to create a sample PDF
        sample_pdf = create_sample_pdf()
        if not sample_pdf:
            # Fallback to text file
            create_sample_text_pdf()
            logger.warning("⚠️  No PDF files available for testing")
            logger.info("Add PDF files to log_materials/ folder and run again")
    
    # Test RAG system
    if pdf_files or create_sample_pdf():
        if test_rag_system():
            logger.info("🎉 RAG system setup completed successfully!")
            logger.info("")
            logger.info("Next steps:")
            logger.info("1. Add your PDF documents to the log_materials/ folder")
            logger.info("2. Run the FaultExplainer backend: python app.py")
            logger.info("3. Initialize knowledge base via API: POST /rag/initialize")
            logger.info("4. Test search via API: POST /rag/search")
        else:
            logger.error("❌ RAG system setup failed")
            sys.exit(1)
    else:
        logger.warning("⚠️  Setup completed but no documents available for indexing")
        logger.info("Add PDF files to log_materials/ folder and run: python setup_rag.py")

if __name__ == "__main__":
    main()
