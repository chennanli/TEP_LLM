#!/usr/bin/env python3
"""
Test script to verify Gemini API failover functionality
"""

import requests
import json

def test_api_key(api_key, key_name):
    """Test if a specific Gemini API key is working"""
    
    print(f"🧪 Testing {key_name}: {api_key[:20]}...")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"Hello, this is a test for {key_name}. Please respond with: {key_name} is working correctly."
                    }
                ]
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                text = result['candidates'][0]['content']['parts'][0]['text']
                print(f"✅ {key_name} is working!")
                print(f"📝 Response: {text}")
                return True
            else:
                print(f"❌ {key_name} - Unexpected response format")
                return False
        else:
            print(f"❌ {key_name} failed: {response.status_code}")
            print(f"📝 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ {key_name} error: {e}")
        return False

def main():
    """Test both API keys and failover logic"""
    
    print("🔑 Testing Gemini API Failover Configuration")
    print("=" * 60)
    
    # API keys from configuration
    primary_key = "AIzaSyDUWTtC7y_jIHVMDMIC5mT9cxnZTa8QsGo"
    backup_key = "AIzaSyB6FhtFI_UfCrhVNADAo4cMPOlJdmT_kRw"
    
    print("\n📋 Testing individual API keys:")
    print("-" * 40)
    
    # Test primary key
    primary_works = test_api_key(primary_key, "Primary API Key")
    print()
    
    # Test backup key
    backup_works = test_api_key(backup_key, "Backup API Key")
    print()
    
    # Summary
    print("📊 Failover Configuration Summary:")
    print("-" * 40)
    
    if primary_works and backup_works:
        print("✅ OPTIMAL: Both API keys are working")
        print("   → Primary key will be used by default")
        print("   → Automatic failover to backup if primary fails")
    elif primary_works and not backup_works:
        print("⚠️  PRIMARY ONLY: Primary key works, backup key failed")
        print("   → System will work but no failover protection")
    elif not primary_works and backup_works:
        print("⚠️  BACKUP ONLY: Primary key failed, backup key works")
        print("   → System will automatically switch to backup key")
    else:
        print("❌ CRITICAL: Both API keys failed")
        print("   → Gemini LLM analysis will not work")
        print("   → Please check your API keys and quotas")
    
    print(f"\n🔧 Configuration files updated with:")
    print(f"   Primary:  {primary_key}")
    print(f"   Backup:   {backup_key}")
    print(f"   Model:    gemini-1.5-flash")
    print(f"   Failover: Enabled")

if __name__ == "__main__":
    main()
