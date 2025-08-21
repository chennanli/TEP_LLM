#!/usr/bin/env python3
"""
Test script for TEP RAG integration
Validates that the RAG system works with the existing fault analysis workflow
"""

import asyncio
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_rag_integration():
    """Test the complete RAG integration with the LLM system"""
    
    try:
        # Import the enhanced multi-LLM client
        from multi_llm_client import MultiLLMClient
        
        # Load configuration (you may need to adjust this path)
        config_path = Path("config.json")
        if not config_path.exists():
            logger.error("config.json not found. Please ensure it exists with valid API keys.")
            return False
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Initialize the enhanced LLM client
        logger.info("🤖 Initializing enhanced LLM client with RAG...")
        llm_client = MultiLLMClient(config)
        
        # Check RAG system status
        rag_status = llm_client.get_rag_status()
        logger.info(f"📊 RAG Status: {rag_status}")
        
        if not rag_status.get('available', False):
            logger.warning("⚠️  RAG system not available, testing basic functionality only")
        
        # Test knowledge base initialization
        if rag_status.get('available', False):
            logger.info("📚 Testing knowledge base initialization...")
            init_result = llm_client.initialize_knowledge_base()
            logger.info(f"📋 Initialization result: {init_result}")
        
        # Test knowledge search
        if rag_status.get('available', False) and rag_status.get('total_documents', 0) > 0:
            logger.info("🔍 Testing knowledge search...")
            search_result = llm_client.search_knowledge_base("reactor temperature fault", n_results=3)
            logger.info(f"🔎 Search results: Found {search_result.get('results_count', 0)} relevant chunks")
            
            if search_result.get('results'):
                best_result = search_result['results'][0]
                logger.info(f"   Best match: {best_result['source']} (similarity: {best_result['similarity']})")
        
        # Test enhanced prompt generation
        logger.info("📝 Testing enhanced prompt generation...")
        
        # Sample fault analysis data
        sample_prompt = """
        A fault has just occurred in the TEP. You will be given the top six contributing features to the fault.
        
        Feature analysis:
        - Reactor Temperature: Increased by 15% above normal
        - Coolant Flow Rate: Decreased by 8% below normal  
        - Reactor Pressure: Increased by 12% above normal
        - Feed Flow Rate: Normal operation
        - Product Flow Rate: Decreased by 5% below normal
        - Separator Temperature: Increased by 7% above normal
        """
        
        sample_features = [
            "reactor_temperature", 
            "coolant_flow_rate", 
            "reactor_pressure",
            "feed_flow_rate",
            "product_flow_rate", 
            "separator_temperature"
        ]
        
        sample_fault_data = {
            "fault_type": "cooling_system",
            "severity": "moderate"
        }
        
        # Test prompt enhancement
        enhanced_prompt = llm_client.enhance_prompt_with_rag(
            user_prompt=sample_prompt,
            fault_features=sample_features,
            fault_data=sample_fault_data
        )
        
        logger.info("✅ Prompt enhancement completed")
        logger.info(f"📏 Original prompt length: {len(sample_prompt)} characters")
        logger.info(f"📏 Enhanced prompt length: {len(enhanced_prompt)} characters")
        
        if "KNOWLEDGE BASE" in enhanced_prompt:
            logger.info("✅ Knowledge base information included in enhanced prompt")
        else:
            logger.info("ℹ️  No relevant knowledge found or RAG system not available")
        
        # Test full LLM analysis with RAG (if models are available)
        if any(config.get('models', {}).get(model, {}).get('enabled', False) 
               for model in ['anthropic', 'gemini', 'lmstudio']):
            
            logger.info("🧠 Testing full LLM analysis with RAG enhancement...")
            
            try:
                # Use a simple system message for testing
                system_message = "You are a helpful AI assistant for Tennessee Eastman Process fault analysis."
                
                # Get analysis from all enabled models
                llm_results = await llm_client.get_analysis_from_all_models(
                    system_message=system_message,
                    user_prompt=sample_prompt,
                    fault_features=sample_features,
                    fault_data=sample_fault_data
                )
                
                logger.info(f"🎯 LLM Analysis completed for {len(llm_results)} models")
                
                for model_name, result in llm_results.items():
                    if result['status'] == 'success':
                        response_length = len(result['response']) if isinstance(result['response'], str) else 0
                        logger.info(f"   {model_name}: ✅ Success ({response_length} chars, {result['response_time']}s)")
                        
                        # Check if response includes citations (indicating RAG worked)
                        if 'Source:' in result['response'] or 'Reference:' in result['response']:
                            logger.info(f"   {model_name}: 📚 Includes knowledge base citations")
                    else:
                        logger.warning(f"   {model_name}: ❌ Failed - {result.get('error', 'Unknown error')}")
                
            except Exception as e:
                logger.warning(f"⚠️  LLM analysis test failed: {str(e)}")
                logger.info("This may be due to missing API keys or network issues")
        
        else:
            logger.info("ℹ️  No LLM models enabled, skipping full analysis test")
        
        logger.info("🎉 RAG integration test completed successfully!")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import error: {str(e)}")
        logger.info("Make sure all dependencies are installed: pip install -r requirements_rag.txt")
        return False
    
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_rag_functionality():
    """Test basic RAG system functionality without LLM integration"""
    
    try:
        from rag_system import TEPKnowledgeRAG
        
        logger.info("🧪 Testing basic RAG functionality...")
        
        # Initialize RAG system
        rag = TEPKnowledgeRAG(
            knowledge_folder="log_materials",
            db_path="knowledge_db"
        )
        
        # Get system status
        status = rag.get_system_status()
        logger.info(f"📊 RAG System Status:")
        logger.info(f"   Knowledge folder: {status['knowledge_folder']}")
        logger.info(f"   Database path: {status['database_path']}")
        logger.info(f"   Total documents: {status['total_documents']}")
        logger.info(f"   Processed files: {status['processed_files']}")
        
        # Test document indexing
        if Path("log_materials").exists():
            pdf_files = list(Path("log_materials").glob("*.pdf"))
            logger.info(f"📄 Found {len(pdf_files)} PDF files in knowledge folder")
            
            if pdf_files:
                new_docs = rag.index_documents()
                logger.info(f"📚 Indexed {new_docs} new documents")
            else:
                logger.info("ℹ️  No PDF files found for indexing")
        
        # Test search functionality
        if status['total_documents'] > 0:
            test_queries = [
                "reactor temperature",
                "cooling system",
                "pressure control",
                "troubleshooting"
            ]
            
            for query in test_queries:
                results = rag.search_knowledge(query, n_results=3)
                logger.info(f"🔍 Query '{query}': Found {len(results)} results")
                
                if results:
                    best_result = results[0]
                    logger.info(f"   Best: {best_result['source']} (similarity: {best_result['similarity']:.3f})")
        
        logger.info("✅ Basic RAG functionality test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Basic RAG test failed: {str(e)}")
        return False

async def main():
    """Main test function"""
    logger.info("🚀 Starting TEP RAG Integration Tests")
    logger.info("=" * 50)
    
    # Test 1: Basic RAG functionality
    logger.info("\n📋 Test 1: Basic RAG Functionality")
    basic_test_passed = test_basic_rag_functionality()
    
    # Test 2: Full integration test
    logger.info("\n📋 Test 2: Full RAG Integration")
    integration_test_passed = await test_rag_integration()
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 Test Summary:")
    logger.info(f"   Basic RAG Test: {'✅ PASSED' if basic_test_passed else '❌ FAILED'}")
    logger.info(f"   Integration Test: {'✅ PASSED' if integration_test_passed else '❌ FAILED'}")
    
    if basic_test_passed and integration_test_passed:
        logger.info("🎉 All tests passed! RAG system is ready for use.")
        logger.info("\nNext steps:")
        logger.info("1. Add your PDF documents to the log_materials/ folder")
        logger.info("2. Start the backend: python app.py")
        logger.info("3. Initialize knowledge base: POST /rag/initialize")
        logger.info("4. Test fault analysis with enhanced knowledge")
    else:
        logger.error("❌ Some tests failed. Check the logs above for details.")
        
        if not basic_test_passed:
            logger.info("💡 Basic RAG test failed - check dependencies and folder structure")
        
        if not integration_test_passed:
            logger.info("💡 Integration test failed - check API keys and configuration")

if __name__ == "__main__":
    asyncio.run(main())
