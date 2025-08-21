#!/usr/bin/env python3
"""
Test script to verify LLM analysis is working and results are displayed in UI
"""

import requests
import json
import time

def test_backend_connection():
    """Test if backend is running"""
    try:
        response = requests.get('http://localhost:8000/', timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {str(e)}")
        return False

def get_model_status():
    """Get current model status"""
    try:
        response = requests.get('http://localhost:8000/models/status', timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get model status: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Model status request failed: {str(e)}")
        return None

def enable_lmstudio():
    """Enable LMStudio for testing"""
    try:
        response = requests.post(
            'http://localhost:8000/models/toggle',
            json={"model_name": "lmstudio", "enabled": True},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to enable LMStudio: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Enable LMStudio request failed: {str(e)}")
        return None

def test_llm_analysis():
    """Test LLM analysis with sample data"""
    test_data = {
        'id': 'ui_test_001',
        'file': 'test_fault.csv',
        'data': {
            'A Feed': [0.25, 0.26, 0.24, 0.25, 0.26],
            'D Feed': [3664, 3670, 3660, 3665, 3668],
            'E Feed': [4509, 4515, 4505, 4510, 4512],
            'A and C Feed': [9.35, 9.40, 9.30, 9.35, 9.38],
            'Recycle Flow': [26.9, 27.1, 26.8, 26.9, 27.0],
            'Reactor Feed Rate': [42.3, 42.5, 42.1, 42.3, 42.4],
            'Reactor Pressure': [2634, 2640, 2630, 2635, 2638],
            'Reactor Level': [75.7, 75.9, 75.5, 75.7, 75.8],
            'Reactor Temperature': [145.4, 146.2, 144.8, 145.5, 146.0],  # Elevated
            'Purge Rate': [0.337, 0.340, 0.335, 0.338, 0.339],
            'Product Sep Temp': [55.0, 55.5, 54.8, 55.2, 55.3],  # Elevated
            'Product Sep Level': [50.0, 50.2, 49.8, 50.1, 50.0],
            'Product Sep Pressure': [3102, 3108, 3098, 3105, 3106],
            'Product Sep Underflow': [25.16, 25.20, 25.12, 25.18, 25.19],
            'Stripper Level': [22.95, 23.00, 22.90, 22.95, 22.98],
            'Stripper Pressure': [2634, 2640, 2630, 2635, 2638],
            'Stripper Underflow': [25.16, 25.20, 25.12, 25.18, 25.19],
            'Stripper Temp': [65.73, 66.00, 65.50, 65.80, 65.90],
            'Stripper Steam Flow': [53.98, 54.20, 53.80, 54.00, 54.10],
            'Compressor Work': [24.52, 24.60, 24.45, 24.55, 24.58],
            'Reactor Coolant Temp': [69.3, 70.1, 68.8, 69.5, 69.8],  # Elevated
            'Separator Coolant Temp': [85.3, 86.0, 84.8, 85.5, 85.8],  # Elevated
        }
    }
    
    try:
        print("🔍 Sending test analysis request...")
        response = requests.post(
            'http://localhost:8000/explain',
            json=test_data,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Analysis completed successfully!")
            
            # Check LLM analyses
            llm_analyses = result.get('llm_analyses', {})
            print(f"📊 LLM Analyses returned: {len(llm_analyses)} models")
            
            for model, analysis in llm_analyses.items():
                status = analysis.get('status', 'unknown')
                response_time = analysis.get('response_time', 0)
                print(f"   🤖 {model.upper()}: {status} ({response_time}s)")
                
                if status == 'success':
                    analysis_text = analysis.get('analysis', '')
                    print(f"      📝 Response length: {len(analysis_text)} chars")
                    print(f"      📝 Preview: {analysis_text[:100]}...")
                else:
                    error = analysis.get('error', 'Unknown error')
                    print(f"      ❌ Error: {error}")
            
            return result
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Analysis request failed: {str(e)}")
        return None

def main():
    """Main test function"""
    print("🧪 Testing LLM Analysis UI Integration")
    print("=" * 50)
    
    # Test 1: Backend connection
    if not test_backend_connection():
        print("❌ Cannot proceed without backend connection")
        return
    
    # Test 2: Check model status
    print("\n📊 Checking model status...")
    status = get_model_status()
    if status:
        print(f"   Available models: {status['available_models']}")
        print(f"   Active models: {status['active_models']}")
        
        if not status['active_models']:
            print("⚠️  No models are currently active")
            print("   Attempting to enable LMStudio...")
            
            enable_result = enable_lmstudio()
            if enable_result and enable_result.get('success'):
                print("✅ LMStudio enabled")
            else:
                print("❌ Failed to enable LMStudio")
                return
    else:
        print("❌ Failed to get model status")
        return
    
    # Test 3: Run LLM analysis
    print("\n🔍 Testing LLM analysis...")
    result = test_llm_analysis()
    
    if result:
        print("\n✅ LLM Analysis Test Results:")
        print(f"   Timestamp: {result.get('timestamp', 'N/A')}")
        print(f"   Feature Analysis: {len(result.get('feature_analysis', ''))} chars")
        print(f"   LLM Models: {list(result.get('llm_analyses', {}).keys())}")
        
        # Check if results would show in UI
        llm_analyses = result.get('llm_analyses', {})
        if llm_analyses:
            print("\n🎯 UI Display Check:")
            print("   ✅ Results available for frontend display")
            print("   ✅ Navigate to 'Multi-LLM Analysis' tab to see results")
            
            for model, analysis in llm_analyses.items():
                if analysis.get('status') == 'success':
                    print(f"   ✅ {model}: Ready for display")
                else:
                    print(f"   ❌ {model}: Error - {analysis.get('error', 'Unknown')}")
        else:
            print("   ❌ No LLM analyses in result")
    else:
        print("❌ LLM analysis test failed")
    
    # Test 4: Instructions for user
    print("\n" + "=" * 50)
    print("📋 Next Steps:")
    print("1. ✅ Backend is running and models are configured")
    print("2. 🌐 Open frontend: http://localhost:5173")
    print("3. 🎛️ Use the model checkboxes in the header to select LLMs:")
    print("   • ☑️ LMStudio (Local, Free)")
    print("   • ☐ Claude (Premium, Paid)")
    print("   • ☐ Gemini (Premium, Paid)")
    print("4. 📊 Load fault data and trigger analysis")
    print("5. 📱 Check 'Multi-LLM Analysis' tab for results")
    
    print("\n💡 Troubleshooting:")
    print("   • If no results appear, check browser console for errors")
    print("   • Ensure at least one model is enabled via checkboxes")
    print("   • LMStudio must be running on localhost:1234 for local analysis")
    print("   • Premium models require valid API keys")

if __name__ == "__main__":
    main()
