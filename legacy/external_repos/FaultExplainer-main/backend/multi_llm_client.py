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
import logging
from datetime import datetime, timedelta
from collections import defaultdict
import threading

logger = logging.getLogger(__name__)

# Optional RAG system import
try:
    from rag_system import TEPKnowledgeRAG
    RAG_AVAILABLE = True
    logger.info("RAG system available")
except ImportError as e:
    RAG_AVAILABLE = False
    logger.warning(f"RAG system not available: {str(e)}")
    logger.info("Backend will run without RAG capabilities")

class MultiLLMClient:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.clients = {}
        self.enabled_models = []
        self.runtime_enabled_models = set()  # Models enabled at runtime
        self.usage_stats = defaultdict(int)  # Track API usage
        self.cost_tracking = defaultdict(float)  # Track estimated costs

        # Cost protection system
        self.premium_session_start = None  # When premium models were first enabled
        self.premium_session_duration = 30 * 60  # 30 minutes in seconds
        self.auto_shutdown_enabled = True
        self.shutdown_callbacks = []  # Callbacks to execute on auto-shutdown
        self.shutdown_timer = None

        # Initialize RAG system (optional)
        self.rag_system = None
        if RAG_AVAILABLE:
            try:
                self.rag_system = TEPKnowledgeRAG(
                    knowledge_folder="log_materials",
                    db_path="knowledge_db"
                )
                logger.info("RAG system initialized successfully")
            except Exception as e:
                logger.warning(f"RAG system initialization failed: {str(e)}")
                self.rag_system = None
        else:
            logger.info("RAG system not available - running without knowledge base")
        
        # Initialize ALL clients (regardless of enabled status) for runtime toggling
        for model_name, model_config in config["models"].items():
            # Always initialize the client
            if model_name == "gemini":
                self.clients[model_name] = self._init_gemini(model_config)
            elif model_name == "anthropic":
                self.clients[model_name] = self._init_claude(model_config)

            # Add to enabled list only if enabled in config
            if model_config.get("enabled", False):
                self.enabled_models.append(model_name)

        # Always initialize LMStudio client (regardless of enabled status)
        lmstudio_config = config.get("lmstudio", {})
        if lmstudio_config:
            self.clients["lmstudio"] = self._init_lmstudio(lmstudio_config)
            # Add to enabled list only if enabled in config
            if lmstudio_config.get("enabled", False):
                self.enabled_models.append("lmstudio")

        print(f"✅ Initialized LLM clients: {list(self.clients.keys())}")
        print(f"📊 Config-enabled models: {self.enabled_models}")

        # Auto-enable Gemini as default runtime model (if available)
        if "gemini" in self.clients and "gemini" not in self.enabled_models:
            self.runtime_enabled_models.add("gemini")
            print(f"🎯 Auto-enabled Gemini as default runtime model")
    
    def _init_lmstudio(self, config: Dict[str, Any]) -> OpenAI:
        """Initialize LMStudio client"""
        return OpenAI(
            base_url=config["base_url"],
            api_key=config["api_key"]
        )
    
    def _init_gemini(self, config: Dict[str, Any]) -> Any:
        """Initialize Google Gemini client with failover support"""
        # Store both API keys for failover
        self.gemini_config = config
        self.gemini_primary_key = config["api_key"]
        self.gemini_backup_key = config.get("backup_api_key")
        self.gemini_current_key = self.gemini_primary_key

        # Configure with primary key initially
        genai.configure(api_key=self.gemini_primary_key)
        return genai.GenerativeModel(config["model_name"])
    
    def _init_claude(self, config: Dict[str, Any]) -> Anthropic:
        """Initialize Claude client"""
        return Anthropic(api_key=config["api_key"])

    def enhance_prompt_with_rag(self, user_prompt: str, fault_features: List[str] = None,
                               fault_data: Dict[str, Any] = None) -> str:
        """
        Enhance user prompt with RAG knowledge retrieval

        Args:
            user_prompt: Original prompt
            fault_features: List of top contributing features
            fault_data: Additional fault context data

        Returns:
            Enhanced prompt with knowledge context
        """
        if self.rag_system is None:
            logger.debug("RAG system not available, using original prompt")
            return user_prompt

        try:
            enhanced_prompt = self.rag_system.enhance_prompt_with_knowledge(
                original_prompt=user_prompt,
                fault_features=fault_features or [],
                fault_data=fault_data or {}
            )
            logger.info("Prompt enhanced with RAG knowledge")
            return enhanced_prompt
        except Exception as e:
            logger.error(f"RAG enhancement failed: {str(e)}")
            return user_prompt

    async def get_analysis_from_all_models(self, system_message: str, user_prompt: str,
                                         fault_features: List[str] = None,
                                         fault_data: Dict[str, Any] = None) -> Dict[str, Dict[str, Any]]:
        """Get fault analysis from all enabled models with RAG enhancement"""
        # Enhance prompt with RAG knowledge
        enhanced_prompt = self.enhance_prompt_with_rag(
            user_prompt=user_prompt,
            fault_features=fault_features,
            fault_data=fault_data
        )

        results = {}

        # Use active models (config + runtime enabled)
        active_models = self.get_active_models()

        for model_name in active_models:
            try:
                start_time = time.time()
                print(f"🤖 Querying {model_name}...")
                
                if model_name == "lmstudio":
                    response = await self._query_lmstudio(system_message, enhanced_prompt)
                elif model_name == "gemini":
                    response = await self._query_gemini(system_message, enhanced_prompt)
                elif model_name == "anthropic":
                    response = await self._query_claude(system_message, enhanced_prompt)
                
                end_time = time.time()
                
                results[model_name] = {
                    "response": response,
                    "response_time": round(end_time - start_time, 2),
                    "status": "success"
                }
                print(f"✅ {model_name} completed in {results[model_name]['response_time']}s")

                # Track usage and estimated costs
                estimated_cost = self._estimate_cost(model_name, response)
                self.track_usage(model_name, estimated_cost=estimated_cost)
                
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
        """Query Google Gemini with automatic failover"""
        client = self.clients["gemini"]

        # Combine system message and user prompt for Gemini
        full_prompt = f"{system_message}\n\n{user_prompt}"

        # Try primary API key first
        try:
            print(f"🔑 Using Gemini primary API key: {self.gemini_current_key[:20]}...")

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

        except Exception as e:
            print(f"❌ Primary Gemini API key failed: {str(e)}")

            # Try backup API key if available and auto_failover is enabled
            if (hasattr(self, 'gemini_backup_key') and
                self.gemini_backup_key and
                self.gemini_config.get("auto_failover", False) and
                self.gemini_current_key != self.gemini_backup_key):

                print(f"🔄 Switching to backup Gemini API key: {self.gemini_backup_key[:20]}...")

                try:
                    # Switch to backup key
                    self.gemini_current_key = self.gemini_backup_key
                    genai.configure(api_key=self.gemini_backup_key)

                    # Recreate client with backup key
                    client = genai.GenerativeModel(self.gemini_config["model_name"])
                    self.clients["gemini"] = client

                    # Retry with backup key
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

                    print(f"✅ Backup Gemini API key working!")
                    return response.text

                except Exception as backup_error:
                    print(f"❌ Backup Gemini API key also failed: {str(backup_error)}")
                    raise Exception(f"Both Gemini API keys failed. Primary: {str(e)}, Backup: {str(backup_error)}")
            else:
                # No backup available or auto_failover disabled
                raise e
    
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

    def initialize_knowledge_base(self, force_reindex: bool = False) -> Dict[str, Any]:
        """
        Initialize or update the RAG knowledge base

        Args:
            force_reindex: If True, reprocess all documents

        Returns:
            Status information about the indexing process
        """
        if self.rag_system is None:
            return {"error": "RAG system not available"}

        try:
            new_docs = self.rag_system.index_documents(force_reindex=force_reindex)
            status = self.rag_system.get_system_status()

            return {
                "success": True,
                "new_documents_processed": new_docs,
                "total_documents": status["total_documents"],
                "knowledge_folder": status["knowledge_folder"],
                "last_updated": status["last_updated"]
            }
        except Exception as e:
            logger.error(f"Knowledge base initialization failed: {str(e)}")
            return {"error": str(e)}

    def search_knowledge_base(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Search the knowledge base for relevant information

        Args:
            query: Search query
            n_results: Maximum number of results

        Returns:
            Search results with metadata
        """
        if self.rag_system is None:
            return {"error": "RAG system not available"}

        try:
            results = self.rag_system.search_knowledge(query, n_results=n_results)
            return {
                "success": True,
                "query": query,
                "results_count": len(results),
                "results": results
            }
        except Exception as e:
            logger.error(f"Knowledge base search failed: {str(e)}")
            return {"error": str(e)}

    def get_rag_status(self) -> Dict[str, Any]:
        """Get RAG system status and statistics"""
        if self.rag_system is None:
            return {"available": False, "error": "RAG system not initialized"}

        try:
            status = self.rag_system.get_system_status()
            status["available"] = True
            return status
        except Exception as e:
            return {"available": False, "error": str(e)}

    def toggle_model(self, model_name: str, enabled: bool) -> Dict[str, Any]:
        """
        Dynamically enable/disable a model at runtime

        Args:
            model_name: Name of the model to toggle
            enabled: Whether to enable or disable the model

        Returns:
            Status of the operation
        """
        try:
            if model_name not in self.clients:
                return {"error": f"Model {model_name} not available"}

            # Check if model is config-enabled
            is_config_enabled = model_name in self.enabled_models

            if enabled:
                # If not config-enabled, add to runtime-enabled
                if not is_config_enabled:
                    self.runtime_enabled_models.add(model_name)
                # If config-enabled, remove from runtime-disabled (if it was disabled)
                self.runtime_enabled_models.discard(f"disabled_{model_name}")
                logger.info(f"Enabled {model_name} for runtime use")

                # Start premium session timer if this is a premium model
                if self._is_premium_model(model_name):
                    self._start_premium_session_timer()

            else:
                # If config-enabled, mark as runtime-disabled
                if is_config_enabled:
                    self.runtime_enabled_models.add(f"disabled_{model_name}")
                # If not config-enabled, remove from runtime-enabled
                else:
                    self.runtime_enabled_models.discard(model_name)
                logger.info(f"Disabled {model_name} for runtime use")

                # Check if any premium models are still active
                active_premium = any(self._is_premium_model(m) for m in self.runtime_enabled_models)
                if not active_premium and self.premium_session_start is not None:
                    # No premium models active, cancel timer
                    self.cancel_auto_shutdown()
                    logger.info("🛡️ All premium models disabled - session timer cancelled")

            # Update current enabled models list
            self._update_active_models()

            return {
                "success": True,
                "model": model_name,
                "enabled": enabled,
                "active_models": list(self.get_active_models())
            }

        except Exception as e:
            logger.error(f"Error toggling model {model_name}: {str(e)}")
            return {"error": str(e)}

    def get_active_models(self) -> set:
        """Get currently active models (config enabled + runtime enabled - runtime disabled)"""
        config_enabled = set(self.enabled_models)
        runtime_enabled = {m for m in self.runtime_enabled_models if not m.startswith('disabled_')}
        runtime_disabled = {m.replace('disabled_', '') for m in self.runtime_enabled_models if m.startswith('disabled_')}

        # Start with config-enabled models, add runtime-enabled, remove runtime-disabled
        active = config_enabled.union(runtime_enabled)
        active = active - runtime_disabled

        return active

    def _update_active_models(self):
        """Update the enabled_models list based on config and runtime settings"""
        # Keep original config-enabled models and add runtime-enabled ones
        original_enabled = [model for model in self.enabled_models]
        active_models = self.get_active_models()

        # Update enabled_models to reflect current active state
        self.enabled_models = list(active_models)

    def get_model_status(self) -> Dict[str, Any]:
        """Get detailed status of all models"""
        status = {
            "config_enabled": [],
            "runtime_enabled": list(self.runtime_enabled_models),
            "active_models": list(self.get_active_models()),
            "available_models": list(self.clients.keys()),
            "usage_stats": dict(self.usage_stats),
            "cost_tracking": dict(self.cost_tracking)
        }

        # Add model details
        for model_name in self.clients.keys():
            model_config = self.config.get('models', {}).get(model_name, {})
            if not model_config and model_name == 'lmstudio':
                model_config = self.config.get('lmstudio', {})

            status["config_enabled"].append({
                "name": model_name,
                "enabled": model_name in self.enabled_models,
                "premium": model_config.get("premium", False),
                "description": model_config.get("description", ""),
                "runtime_enabled": model_name in self.runtime_enabled_models
            })

        return status

    def track_usage(self, model_name: str, tokens_used: int = 0, estimated_cost: float = 0.0):
        """Track usage statistics for cost management"""
        self.usage_stats[model_name] += 1
        self.cost_tracking[model_name] += estimated_cost

        logger.info(f"Usage tracked - {model_name}: calls={self.usage_stats[model_name]}, "
                   f"estimated_cost=${self.cost_tracking[model_name]:.4f}")

    def reset_usage_stats(self) -> Dict[str, Any]:
        """Reset usage statistics"""
        old_stats = {
            "usage_stats": dict(self.usage_stats),
            "cost_tracking": dict(self.cost_tracking)
        }

        self.usage_stats.clear()
        self.cost_tracking.clear()

        logger.info("Usage statistics reset")
        return {"success": True, "previous_stats": old_stats}

    def _estimate_cost(self, model_name: str, response: str) -> float:
        """Estimate API cost based on model and response length"""
        if model_name == "lmstudio":
            return 0.0  # Local model, no cost

        # Rough token estimation (4 chars per token average)
        estimated_tokens = len(response) / 4

        # Estimated costs per 1K tokens (as of 2024)
        cost_per_1k_tokens = {
            "anthropic": 0.015,  # Claude 3.5 Sonnet output tokens
            "gemini": 0.0075,    # Gemini 1.5 Pro output tokens
        }

        rate = cost_per_1k_tokens.get(model_name, 0.01)
        return (estimated_tokens / 1000) * rate

    def _is_premium_model(self, model_name: str) -> bool:
        """Check if a model is premium (costs money)"""
        if model_name == "lmstudio":
            return False

        model_config = self.config.get('models', {}).get(model_name, {})
        return model_config.get('premium', True)  # Default to premium for safety

    def _start_premium_session_timer(self):
        """Start the premium session timer"""
        if not self.auto_shutdown_enabled:
            return

        if self.premium_session_start is None:
            self.premium_session_start = datetime.now()
            logger.info(f"🛡️ Premium session started - auto-shutdown in {self.premium_session_duration/60:.0f} minutes")

            # Start shutdown timer
            if self.shutdown_timer:
                self.shutdown_timer.cancel()

            self.shutdown_timer = threading.Timer(
                self.premium_session_duration,
                self._execute_auto_shutdown
            )
            self.shutdown_timer.start()

    def _execute_auto_shutdown(self):
        """Execute automatic shutdown of premium models"""
        logger.warning("🛡️ AUTO-SHUTDOWN: 30-minute premium session limit reached")

        # Disable all premium models
        premium_models = [name for name in self.runtime_enabled_models
                         if self._is_premium_model(name)]

        for model_name in premium_models:
            self.runtime_enabled_models.discard(model_name)
            logger.warning(f"🛡️ Auto-disabled premium model: {model_name}")

        # Update active models
        self._update_active_models()

        # Execute shutdown callbacks (for stopping simulation)
        for callback in self.shutdown_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Shutdown callback error: {str(e)}")

        # Reset session
        self.premium_session_start = None
        if self.shutdown_timer:
            self.shutdown_timer.cancel()
            self.shutdown_timer = None

        logger.warning("🛡️ Premium models auto-disabled. System returned to cost-optimized mode.")

    def get_session_status(self) -> Dict[str, Any]:
        """Get current session status and remaining time"""
        if self.premium_session_start is None:
            return {
                "premium_session_active": False,
                "remaining_time_seconds": None,
                "remaining_time_minutes": None,
                "auto_shutdown_enabled": self.auto_shutdown_enabled
            }

        elapsed = datetime.now() - self.premium_session_start
        remaining_seconds = max(0, self.premium_session_duration - elapsed.total_seconds())

        return {
            "premium_session_active": True,
            "session_start": self.premium_session_start.isoformat(),
            "elapsed_seconds": int(elapsed.total_seconds()),
            "remaining_time_seconds": int(remaining_seconds),
            "remaining_time_minutes": round(remaining_seconds / 60, 1),
            "auto_shutdown_enabled": self.auto_shutdown_enabled,
            "will_shutdown_at": (self.premium_session_start + timedelta(seconds=self.premium_session_duration)).isoformat()
        }

    def register_shutdown_callback(self, callback):
        """Register a callback to be executed on auto-shutdown"""
        self.shutdown_callbacks.append(callback)

    def cancel_auto_shutdown(self):
        """Cancel the auto-shutdown timer (for manual control)"""
        if self.shutdown_timer:
            self.shutdown_timer.cancel()
            self.shutdown_timer = None
        self.premium_session_start = None
        logger.info("🛡️ Auto-shutdown cancelled")

    def set_auto_shutdown_enabled(self, enabled: bool):
        """Enable or disable auto-shutdown feature"""
        self.auto_shutdown_enabled = enabled
        if not enabled and self.shutdown_timer:
            self.cancel_auto_shutdown()
        logger.info(f"🛡️ Auto-shutdown {'enabled' if enabled else 'disabled'}")

    def extend_premium_session(self, additional_minutes: int = 30):
        """Extend the premium session by additional minutes"""
        if self.premium_session_start is None:
            return {"error": "No active premium session"}

        if self.shutdown_timer:
            self.shutdown_timer.cancel()

        # Extend the session duration
        self.premium_session_duration += additional_minutes * 60
        remaining_time = self.premium_session_duration - (datetime.now() - self.premium_session_start).total_seconds()

        if remaining_time > 0:
            self.shutdown_timer = threading.Timer(remaining_time, self._execute_auto_shutdown)
            self.shutdown_timer.start()

            logger.info(f"🛡️ Premium session extended by {additional_minutes} minutes")
            return {
                "success": True,
                "extended_by_minutes": additional_minutes,
                "new_remaining_minutes": round(remaining_time / 60, 1)
            }
        else:
            # Session already expired
            self._execute_auto_shutdown()
            return {"error": "Session already expired"}

    def force_shutdown_premium(self):
        """Manually force shutdown of premium models"""
        logger.info("🛡️ Manual premium shutdown requested")
        self._execute_auto_shutdown()
        return {"success": True, "message": "Premium models manually disabled"}
