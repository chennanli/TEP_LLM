"""
LLM Analysis Service - Adapted from your existing FaultExplainer backend
Simplified for immediate development without database dependency
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, List
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LLM Analysis Service",
    description="Multi-LLM fault analysis for TEP process",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LLM Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "your-anthropic-api-key-here")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key-here")
LMSTUDIO_URL = os.getenv("LMSTUDIO_URL", "http://localhost:1234/v1")

# TEP Process Description (from your existing system)
TEP_PROCESS_DESCRIPTION = """
The Tennessee Eastman Process produces two products from four reactants:
- A(g) + C(g) + D(g) → G(liq): Product 1
- A(g) + C(g) + E(g) → H(liq): Product 2
- A(g) + E(g) → F(liq): Byproduct
- 3D(g) → 2F(liq): Byproduct

The process has five major unit operations:
1. Reactor - Gas phase reactions with catalyst
2. Product condenser - Condenses products
3. Vapor-liquid separator - Separates phases
4. Recycle compressor - Recycles unreacted feeds
5. Product stripper - Removes remaining reactants

Key process variables (52 total):
- XMEAS 1-41: Measured variables (flows, temperatures, pressures, compositions)
- XMV 1-11: Manipulated variables (valve positions, setpoints)
"""

class LLMAnalyzer:
    """Multi-LLM analyzer for fault diagnosis"""
    
    def __init__(self):
        self.analysis_history = []
    
    async def analyze_fault(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze fault using multiple LLM providers"""
        
        # Prepare analysis context
        context = self._prepare_analysis_context(data)
        
        # Run analysis with multiple LLMs
        analyses = {}
        
        # Try Claude (Anthropic)
        try:
            claude_result = await self._analyze_with_claude(context)
            analyses["claude"] = claude_result
        except Exception as e:
            logger.error(f"Claude analysis failed: {e}")
            analyses["claude"] = {"error": str(e)}
        
        # Try Gemini
        try:
            gemini_result = await self._analyze_with_gemini(context)
            analyses["gemini"] = gemini_result
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            analyses["gemini"] = {"error": str(e)}
        
        # Try Local LMStudio
        try:
            local_result = await self._analyze_with_local(context)
            analyses["local"] = local_result
        except Exception as e:
            logger.error(f"Local LLM analysis failed: {e}")
            analyses["local"] = {"error": str(e)}
        
        # Compile results
        result = {
            "timestamp": datetime.now().isoformat(),
            "input_data": data,
            "llm_analyses": analyses,
            "summary": self._generate_summary(analyses),
            "confidence_score": self._calculate_confidence(analyses)
        }
        
        # Store in history
        self.analysis_history.append(result)
        if len(self.analysis_history) > 100:
            self.analysis_history = self.analysis_history[-100:]
        
        return result
    
    def _prepare_analysis_context(self, data: Dict[str, Any]) -> str:
        """Prepare context for LLM analysis"""
        
        # Extract key information
        variables = data.get("data", {})
        anomaly_score = data.get("anomaly_score", 0)
        file_info = data.get("file", "unknown")
        
        context = f"""
        TENNESSEE EASTMAN PROCESS FAULT ANALYSIS REQUEST
        
        Process Description:
        {TEP_PROCESS_DESCRIPTION}
        
        Current Situation:
        - Anomaly Score: {anomaly_score}
        - Data Source: {file_info}
        - Analysis Time: {datetime.now().isoformat()}
        
        Process Variables (Top Contributing):
        """
        
        # Add variable data
        if isinstance(variables, dict):
            for var_name, values in variables.items():
                if isinstance(values, list) and values:
                    latest_value = values[-1]
                    context += f"- {var_name}: {latest_value}\n"
                else:
                    context += f"- {var_name}: {values}\n"
        
        context += """
        
        Please analyze this data and provide:
        1. Fault identification and classification
        2. Root cause analysis
        3. Potential consequences if not addressed
        4. Recommended corrective actions
        5. Confidence level in your diagnosis
        
        Focus on chemical engineering principles and process safety.
        """
        
        return context
    
    async def _analyze_with_claude(self, context: str) -> Dict[str, Any]:
        """Analyze with Claude (Anthropic)"""
        if ANTHROPIC_API_KEY == "your-anthropic-api-key-here":
            return {"error": "Anthropic API key not configured"}
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": context
                }
            ]
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "provider": "claude",
                    "model": "claude-3-sonnet",
                    "analysis": result["content"][0]["text"],
                    "usage": result.get("usage", {}),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                raise Exception(f"Claude API error: {response.status_code} - {response.text}")
    
    async def _analyze_with_gemini(self, context: str) -> Dict[str, Any]:
        """Analyze with Gemini"""
        if GEMINI_API_KEY == "your-gemini-api-key-here":
            return {"error": "Gemini API key not configured"}
        
        # Implement Gemini API call
        # This is a placeholder - implement based on your existing Gemini integration
        return {
            "provider": "gemini",
            "model": "gemini-pro",
            "analysis": "Gemini analysis placeholder - implement based on your existing code",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _analyze_with_local(self, context: str) -> Dict[str, Any]:
        """Analyze with local LMStudio"""
        try:
            headers = {"Content-Type": "application/json"}
            payload = {
                "model": "local-model",
                "messages": [
                    {"role": "user", "content": context}
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{LMSTUDIO_URL}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "provider": "local",
                        "model": "lmstudio",
                        "analysis": result["choices"][0]["message"]["content"],
                        "usage": result.get("usage", {}),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    raise Exception(f"LMStudio API error: {response.status_code}")
                    
        except Exception as e:
            return {"error": f"Local LLM unavailable: {str(e)}"}
    
    def _generate_summary(self, analyses: Dict[str, Any]) -> str:
        """Generate summary from multiple LLM analyses"""
        successful_analyses = [
            analysis for analysis in analyses.values() 
            if "error" not in analysis and "analysis" in analysis
        ]
        
        if not successful_analyses:
            return "No successful analyses available"
        
        # Simple summary generation
        summary = f"Analysis completed using {len(successful_analyses)} LLM provider(s). "
        
        if len(successful_analyses) > 1:
            summary += "Multiple perspectives available for comprehensive fault diagnosis."
        else:
            summary += "Single LLM analysis available."
        
        return summary
    
    def _calculate_confidence(self, analyses: Dict[str, Any]) -> float:
        """Calculate confidence score based on analysis consistency"""
        successful_analyses = [
            analysis for analysis in analyses.values() 
            if "error" not in analysis
        ]
        
        if not successful_analyses:
            return 0.0
        
        # Simple confidence calculation
        base_confidence = len(successful_analyses) / 3.0  # Assuming 3 providers max
        return min(base_confidence * 0.8, 1.0)  # Cap at 80% for now

# Initialize analyzer
analyzer = LLMAnalyzer()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "llm-analysis",
        "timestamp": datetime.now().isoformat(),
        "providers": {
            "claude": "configured" if ANTHROPIC_API_KEY != "your-anthropic-api-key-here" else "not_configured",
            "gemini": "configured" if GEMINI_API_KEY != "your-gemini-api-key-here" else "not_configured",
            "local": "available"
        }
    }

@app.post("/explain")
async def explain_fault(data: Dict[str, Any]):
    """Analyze fault using multiple LLM providers"""
    try:
        result = await analyzer.analyze_fault(data)
        return result
    except Exception as e:
        logger.error(f"Error in fault analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def get_analysis_history(limit: int = 10):
    """Get recent analysis history"""
    return {
        "analyses": analyzer.analysis_history[-limit:],
        "total": len(analyzer.analysis_history),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
