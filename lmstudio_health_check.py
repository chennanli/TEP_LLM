#!/usr/bin/env python3
"""
LMStudio Health Check and Recovery Tool
Monitors LMStudio status and provides recovery options
"""

import requests
import time
import json
import subprocess
import sys
from typing import Dict, Any, Optional

class LMStudioHealthChecker:
    def __init__(self, base_url: str = "http://localhost:1234"):
        self.base_url = base_url
        self.models_endpoint = f"{base_url}/v1/models"
        self.chat_endpoint = f"{base_url}/v1/chat/completions"
        
    def check_connection(self, timeout: int = 5) -> Dict[str, Any]:
        """Check if LMStudio is reachable"""
        try:
            start_time = time.time()
            response = requests.get(self.models_endpoint, timeout=timeout)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                models = response.json().get("data", [])
                return {
                    "status": "connected",
                    "response_time": round(response_time, 3),
                    "models_count": len(models),
                    "models": [m["id"] for m in models]
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}",
                    "response_time": round(response_time, 3)
                }
        except requests.exceptions.Timeout:
            return {"status": "timeout", "error": "Connection timeout"}
        except requests.exceptions.ConnectionError:
            return {"status": "disconnected", "error": "Cannot connect to LMStudio"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def test_chat_completion(self, timeout: int = 30) -> Dict[str, Any]:
        """Test a simple chat completion"""
        try:
            start_time = time.time()
            
            payload = {
                "model": "mistralai_mistral-small-3.1-24b-instruct-2503",
                "messages": [{"role": "user", "content": "Respond with just: HEALTHY"}],
                "max_tokens": 10,
                "temperature": 0.1
            }
            
            response = requests.post(
                self.chat_endpoint, 
                json=payload, 
                timeout=timeout,
                headers={"Content-Type": "application/json"}
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"].strip()
                
                return {
                    "status": "healthy" if "HEALTHY" in content.upper() else "responding",
                    "response_time": round(response_time, 3),
                    "content": content,
                    "tokens_used": data.get("usage", {}).get("total_tokens", 0)
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}",
                    "response_time": round(response_time, 3)
                }
                
        except requests.exceptions.Timeout:
            return {"status": "timeout", "error": "Chat completion timeout"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def full_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        print("🔍 Checking LMStudio health...")
        
        # Check connection
        print("  📡 Testing connection...")
        connection_result = self.check_connection()
        print(f"     Status: {connection_result['status']}")
        
        if connection_result["status"] != "connected":
            return {
                "overall_status": "unhealthy",
                "connection": connection_result,
                "chat": {"status": "skipped", "reason": "No connection"}
            }
        
        # Test chat completion
        print("  🤖 Testing chat completion...")
        chat_result = self.test_chat_completion()
        print(f"     Status: {chat_result['status']}")
        print(f"     Response time: {chat_result.get('response_time', 'N/A')}s")
        
        overall_status = "healthy" if chat_result["status"] in ["healthy", "responding"] else "unhealthy"
        
        return {
            "overall_status": overall_status,
            "connection": connection_result,
            "chat": chat_result
        }
    
    def restart_lmstudio_suggestion(self):
        """Provide restart suggestions"""
        print("\n🔧 LMStudio Recovery Suggestions:")
        print("1. 📱 Open LMStudio application")
        print("2. 🔄 Restart the local server (Server tab)")
        print("3. 🤖 Ensure a model is loaded")
        print("4. 🌐 Check server is running on localhost:1234")
        print("5. 💾 Try loading a smaller/different model if memory issues")
        
        print("\n🖥️  Manual restart commands:")
        print("   • Close LMStudio completely")
        print("   • Reopen LMStudio")
        print("   • Go to Server tab")
        print("   • Select model and click 'Start Server'")

def main():
    checker = LMStudioHealthChecker()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        # Continuous monitoring mode
        print("🔄 Starting continuous monitoring (Ctrl+C to stop)...")
        try:
            while True:
                result = checker.full_health_check()
                if result["overall_status"] == "unhealthy":
                    print("❌ LMStudio is unhealthy!")
                    checker.restart_lmstudio_suggestion()
                else:
                    print("✅ LMStudio is healthy")
                
                print(f"⏰ Next check in 30 seconds...\n")
                time.sleep(30)
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
    else:
        # Single check
        result = checker.full_health_check()
        
        print(f"\n📊 Overall Status: {result['overall_status'].upper()}")
        
        if result["overall_status"] == "unhealthy":
            print("❌ Issues detected!")
            checker.restart_lmstudio_suggestion()
        else:
            print("✅ LMStudio is working properly")
            
        # Print detailed results
        print(f"\n📋 Detailed Results:")
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
