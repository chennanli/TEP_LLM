"""
Multi-LLM Client for FaultExplainer
Supports LMStudio, Google Gemini, and Claude API
"""

import json
import requests
import google.generativeai as genai
from anthropic import Anthropic
from openai import OpenAI
from typing import Dict, List, Any, Optional
import asyncio
import time

class MultiLLMClient:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.clients = {}
        self.enabled_models = []
        
        # Initialize enabled clients
        for model_name, model_config in config["models"].items():
            if model_config.get("enabled", False):
                self.enabled_models.append(model_name)
                if model_name == "lmstudio":
                    self.clients[model_name] = self._init_lmstudio(model_config)
                elif model_name == "gemini":
                    self.clients[model_name] = self._init_gemini(model_config)
                elif model_name == "anthropic":
                    self.clients[model_name] = self._init_claude(model_config)
        
        print(f"✅ Initialized LLM clients: {self.enabled_models}")
    
    def _init_lmstudio(self, config: Dict[str, Any]) -> OpenAI:
        """Initialize LMStudio client"""
        return OpenAI(
            base_url=config["base_url"],
            api_key=config["api_key"]
        )
    
    def _init_gemini(self, config: Dict[str, Any]) -> Any:
        """Initialize Google Gemini client"""
        genai.configure(api_key=config["api_key"])
        return genai.GenerativeModel(config["model_name"])
    
    def _init_claude(self, config: Dict[str, Any]) -> Anthropic:
        """Initialize Claude client"""
        return Anthropic(api_key=config["api_key"])
    
    async def get_analysis_from_all_models(self, system_message: str, user_prompt: str) -> Dict[str, Dict[str, Any]]:
        """Get fault analysis from all enabled models"""
        results = {}
        
        for model_name in self.enabled_models:
            try:
                start_time = time.time()
                print(f"🤖 Querying {model_name}...")
                
                if model_name == "lmstudio":
                    response = await self._query_lmstudio(system_message, user_prompt)
                elif model_name == "gemini":
                    response = await self._query_gemini(system_message, user_prompt)
                elif model_name == "anthropic":
                    response = await self._query_claude(system_message, user_prompt)
                
                end_time = time.time()
                
                results[model_name] = {
                    "response": response,
                    "response_time": round(end_time - start_time, 2),
                    "status": "success"
                }
                print(f"✅ {model_name} completed in {results[model_name]['response_time']}s")
                
            except Exception as e:
                results[model_name] = {
                    "response": f"Error: {str(e)}",
                    "response_time": 0,
                    "status": "error"
                }
                print(f"❌ {model_name} failed: {str(e)}")
        
        return results
    
    async def _query_lmstudio(self, system_message: str, user_prompt: str) -> str:
        """Query LMStudio with timeout and retry logic"""
        client = self.clients["lmstudio"]

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt}
        ]

        # Retry logic for LMStudio (can get stuck)
        max_retries = 2
        timeout = 120  # 2 minutes timeout

        for attempt in range(max_retries):
            try:
                print(f"🤖 LMStudio attempt {attempt + 1}/{max_retries}")

                # Run in thread pool with timeout
                loop = asyncio.get_event_loop()
                response = await asyncio.wait_for(
                    loop.run_in_executor(
                        None,
                        lambda: client.chat.completions.create(
                            model=self.config["models"]["lmstudio"]["model_name"],
                            messages=messages,
                            temperature=0.7,
                            max_tokens=2000,
                            timeout=timeout
                        )
                    ),
                    timeout=timeout
                )

                return response.choices[0].message.content

            except asyncio.TimeoutError:
                print(f"⏰ LMStudio timeout on attempt {attempt + 1}")
                if attempt == max_retries - 1:
                    raise Exception(f"LMStudio timeout after {max_retries} attempts")
                await asyncio.sleep(2)  # Wait before retry

            except Exception as e:
                print(f"❌ LMStudio error on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    raise Exception(f"LMStudio failed after {max_retries} attempts: {str(e)}")
                await asyncio.sleep(2)  # Wait before retry
    
    async def _query_gemini(self, system_message: str, user_prompt: str) -> str:
        """Query Google Gemini"""
        client = self.clients["gemini"]

        # Combine system message and user prompt for Gemini
        full_prompt = f"{system_message}\n\n{user_prompt}"

        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=2000,
                )
            )
        )

        return response.text
    
    async def _query_claude(self, system_message: str, user_prompt: str) -> str:
        """Query Claude"""
        client = self.clients["anthropic"]

        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.messages.create(
                model=self.config["models"]["anthropic"]["model_name"],
                max_tokens=2000,
                temperature=0.7,
                system=system_message,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
        )

        return response.content[0].text
    
    def format_comparative_results(self, results: Dict[str, Dict[str, Any]], feature_comparison: str) -> Dict[str, Any]:
        """Format results for comparative display"""
        
        formatted_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "feature_analysis": feature_comparison,
            "llm_analyses": {},
            "performance_summary": {}
        }
        
        for model_name, result in results.items():
            formatted_results["llm_analyses"][model_name] = {
                "analysis": result["response"],
                "response_time": result["response_time"],
                "status": result["status"]
            }
            
            # Performance summary
            if result["status"] == "success":
                formatted_results["performance_summary"][model_name] = {
                    "response_time": result["response_time"],
                    "word_count": len(result["response"].split()) if isinstance(result["response"], str) else 0
                }
        
        return formatted_results
