#!/usr/bin/env python3
"""
Test script to diagnose Claude integration and root cause analysis issues
"""

import asyncio
import json
import sys
import traceback
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from multi_llm_client import MultiLLMClient
        print("✅ MultiLLMClient imported successfully")
    except Exception as e:
        print(f"❌ MultiLLMClient import failed: {str(e)}")
        return False
    
    try:
        from prompts import SYSTEM_MESSAGE, EXPLAIN_PROMPT
        print("✅ Prompts imported successfully")
    except Exception as e:
        print(f"❌ Prompts import failed: {str(e)}")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\n📋 Testing configuration...")
    
    config_path = Path("../config.json")
    if not config_path.exists():
        print("❌ Config file not found")
        return None
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print("✅ Config loaded successfully")
        
        # Check Claude configuration
        claude_config = config.get('models', {}).get('anthropic', {})
        if claude_config.get('enabled', False):
            api_key = claude_config.get('api_key', '')
            if api_key and api_key != 'YOUR_ANTHROPIC_API_KEY_HERE':
                print("✅ Claude API key configured")
            else:
                print("❌ Claude API key not configured")
                return None
        else:
            print("❌ Claude not enabled in config")
            return None
        
        return config
        
    except Exception as e:
        print(f"❌ Config loading failed: {str(e)}")
        return None

async def test_claude_client(config):
    """Test Claude client initialization and basic functionality"""
    print("\n🤖 Testing Claude client...")
    
    try:
        from multi_llm_client import MultiLLMClient
        
        # Initialize client
        client = MultiLLMClient(config)
        print(f"✅ Client initialized with models: {client.enabled_models}")
        
        if 'anthropic' not in client.enabled_models:
            print("❌ Claude not in enabled models")
            return False
        
        # Test simple query
        system_msg = "You are a helpful assistant for Tennessee Eastman Process fault analysis."
        user_msg = "Test: Please confirm you can analyze TEP faults and provide a brief response."
        
        print("🔍 Testing Claude API call...")
        results = await client.get_analysis_from_all_models(system_msg, user_msg)
        
        if 'anthropic' in results:
            result = results['anthropic']
            if result['status'] == 'success':
                print(f"✅ Claude responded successfully in {result['response_time']}s")
                print(f"📝 Response preview: {result['response'][:150]}...")
                return True
            else:
                print(f"❌ Claude query failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print("❌ No Claude result returned")
            return False
            
    except Exception as e:
        print(f"❌ Claude client test failed: {str(e)}")
        traceback.print_exc()
        return False

async def test_fault_analysis(config):
    """Test fault analysis with sample data"""
    print("\n🔬 Testing fault analysis...")
    
    try:
        from multi_llm_client import MultiLLMClient
        from prompts import SYSTEM_MESSAGE, EXPLAIN_PROMPT
        
        client = MultiLLMClient(config)
        
        # Create sample fault analysis prompt
        sample_fault_data = """
        A fault has just occurred in the TEP. Here are the top six contributing features:
        
        Feature: Reactor Temperature
        - Fault Value: 115.5°C (15% above normal)
        - Normal Mean: 100.0°C
        - Analysis: Significant temperature increase indicates cooling system issue
        
        Feature: Coolant Flow Rate  
        - Fault Value: 85.2 L/min (10% below normal)
        - Normal Mean: 95.0 L/min
        - Analysis: Reduced coolant flow correlates with temperature rise
        
        Feature: Reactor Pressure
        - Fault Value: 112.8 kPa (12% above normal) 
        - Normal Mean: 100.5 kPa
        - Analysis: Pressure increase follows temperature rise pattern
        
        Please provide a detailed root cause analysis identifying the most likely fault cause 
        and recommended corrective actions.
        """
        
        user_prompt = f"{EXPLAIN_PROMPT}\n\n{sample_fault_data}"
        
        print("🧠 Running fault analysis with Claude...")
        results = await client.get_analysis_from_all_models(SYSTEM_MESSAGE, user_prompt)
        
        if 'anthropic' in results:
            result = results['anthropic']
            if result['status'] == 'success':
                response = result['response']
                print(f"✅ Fault analysis completed in {result['response_time']}s")
                print(f"📊 Response length: {len(response)} characters")
                
                # Check for key elements of good root cause analysis
                response_lower = response.lower()
                analysis_quality = []
                
                if 'root cause' in response_lower:
                    analysis_quality.append("✅ Contains root cause identification")
                else:
                    analysis_quality.append("⚠️  Missing explicit root cause identification")
                
                if 'cooling' in response_lower or 'coolant' in response_lower:
                    analysis_quality.append("✅ Identifies cooling system issues")
                else:
                    analysis_quality.append("⚠️  May not identify cooling system connection")
                
                if 'recommend' in response_lower or 'action' in response_lower:
                    analysis_quality.append("✅ Includes recommendations")
                else:
                    analysis_quality.append("⚠️  Missing corrective action recommendations")
                
                if 'temperature' in response_lower and 'pressure' in response_lower:
                    analysis_quality.append("✅ Addresses multiple fault indicators")
                else:
                    analysis_quality.append("⚠️  May not comprehensively address all indicators")
                
                print("\n📋 Analysis Quality Assessment:")
                for item in analysis_quality:
                    print(f"   {item}")
                
                print(f"\n📝 Full Response:\n{'-'*50}")
                print(response)
                print('-'*50)
                
                return True
            else:
                print(f"❌ Fault analysis failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print("❌ No fault analysis result returned")
            return False
            
    except Exception as e:
        print(f"❌ Fault analysis test failed: {str(e)}")
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🏭 TEP Claude Integration Diagnostic Test")
    print("=" * 50)
    
    # Test 1: Imports
    if not test_imports():
        print("\n❌ Import test failed - cannot proceed")
        sys.exit(1)
    
    # Test 2: Configuration
    config = test_config()
    if config is None:
        print("\n❌ Configuration test failed - cannot proceed")
        sys.exit(1)
    
    # Test 3: Claude client
    claude_works = await test_claude_client(config)
    if not claude_works:
        print("\n❌ Claude client test failed")
        sys.exit(1)
    
    # Test 4: Fault analysis
    fault_analysis_works = await test_fault_analysis(config)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print("✅ Imports: PASSED")
    print("✅ Configuration: PASSED") 
    print("✅ Claude Client: PASSED")
    print(f"{'✅' if fault_analysis_works else '❌'} Fault Analysis: {'PASSED' if fault_analysis_works else 'FAILED'}")
    
    if fault_analysis_works:
        print("\n🎉 All tests passed! Claude integration is working correctly.")
        print("\n💡 If you're still having issues:")
        print("   1. Check that the backend is running: python app.py")
        print("   2. Verify the unified control panel can reach the backend")
        print("   3. Check that data is being sent in the correct format")
    else:
        print("\n❌ Fault analysis test failed - check the error messages above")

if __name__ == "__main__":
    asyncio.run(main())
