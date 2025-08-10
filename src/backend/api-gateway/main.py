"""
TEP Industrial Intelligence Platform - API Gateway
Simplified version for immediate development without database dependency
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio
import json
import redis
from typing import Dict, Any, List
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TEP Industrial Intelligence API Gateway",
    description="Unified API for TEP simulation, anomaly detection, and LLM analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
SIMULATION_SERVICE = os.getenv("SIMULATION_SERVICE_URL", "http://localhost:8001")
LLM_SERVICE = os.getenv("LLM_SERVICE_URL", "http://localhost:8002")
USE_DATABASE = os.getenv("USE_DATABASE", "false").lower() == "true"

# Redis for real-time data
try:
    redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)
    redis_client.ping()
    logger.info("✅ Connected to Redis")
except:
    redis_client = None
    logger.warning("⚠️ Redis not available, using in-memory storage")

# In-memory storage for development
memory_store = {
    "current_simulation": None,
    "anomaly_history": [],
    "llm_analyses": []
}

# WebSocket connections
active_connections: List[WebSocket] = []

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        if self.active_connections:
            disconnected = []
            for connection in self.active_connections:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected.append(connection)
            
            # Remove disconnected clients
            for conn in disconnected:
                self.disconnect(conn)

manager = ConnectionManager()

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    services_status = {}
    
    # Check simulation service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{SIMULATION_SERVICE}/health")
            services_status["simulation"] = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        services_status["simulation"] = "unhealthy"
    
    # Check LLM service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{LLM_SERVICE}/health")
            services_status["llm_analysis"] = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        services_status["llm_analysis"] = "unhealthy"
    
    # Check Redis
    services_status["redis"] = "healthy" if redis_client else "unavailable"
    
    overall_status = "healthy" if all(
        status in ["healthy", "unavailable"] for status in services_status.values()
    ) else "degraded"
    
    return {
        "status": overall_status,
        "services": services_status,
        "timestamp": datetime.now().isoformat(),
        "database_mode": "enabled" if USE_DATABASE else "disabled"
    }

# Simulation endpoints
@app.post("/api/v1/simulation/start")
async def start_simulation(config: Dict[str, Any]):
    """Start TEP simulation"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{SIMULATION_SERVICE}/start", json=config)
            
            if response.status_code == 200:
                result = response.json()
                memory_store["current_simulation"] = result
                
                # Broadcast to WebSocket clients
                await manager.broadcast({
                    "type": "simulation_started",
                    "data": result,
                    "timestamp": datetime.now().isoformat()
                })
                
                return result
            else:
                raise HTTPException(status_code=response.status_code, detail=response.text)
                
    except httpx.RequestError as e:
        logger.error(f"Simulation service error: {e}")
        raise HTTPException(status_code=503, detail="Simulation service unavailable")

@app.get("/api/v1/simulation/status")
async def get_simulation_status():
    """Get current simulation status"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{SIMULATION_SERVICE}/status")
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code, detail=response.text)
                
    except httpx.RequestError as e:
        logger.error(f"Simulation service error: {e}")
        raise HTTPException(status_code=503, detail="Simulation service unavailable")

@app.post("/api/v1/simulation/stop")
async def stop_simulation():
    """Stop TEP simulation"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{SIMULATION_SERVICE}/stop")
            
            if response.status_code == 200:
                result = response.json()
                memory_store["current_simulation"] = None
                
                # Broadcast to WebSocket clients
                await manager.broadcast({
                    "type": "simulation_stopped",
                    "data": result,
                    "timestamp": datetime.now().isoformat()
                })
                
                return result
            else:
                raise HTTPException(status_code=response.status_code, detail=response.text)
                
    except httpx.RequestError as e:
        logger.error(f"Simulation service error: {e}")
        raise HTTPException(status_code=503, detail="Simulation service unavailable")

# LLM Analysis endpoints
@app.post("/api/v1/llm/analyze")
async def analyze_fault(data: Dict[str, Any]):
    """Trigger LLM analysis for fault diagnosis"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{LLM_SERVICE}/explain", json=data)
            
            if response.status_code == 200:
                result = response.json()
                
                # Store analysis result
                analysis_record = {
                    "timestamp": datetime.now().isoformat(),
                    "input_data": data,
                    "result": result
                }
                memory_store["llm_analyses"].append(analysis_record)
                
                # Keep only last 50 analyses
                if len(memory_store["llm_analyses"]) > 50:
                    memory_store["llm_analyses"] = memory_store["llm_analyses"][-50:]
                
                # Broadcast to WebSocket clients
                await manager.broadcast({
                    "type": "llm_analysis_complete",
                    "data": result,
                    "timestamp": datetime.now().isoformat()
                })
                
                return result
            else:
                raise HTTPException(status_code=response.status_code, detail=response.text)
                
    except httpx.RequestError as e:
        logger.error(f"LLM service error: {e}")
        raise HTTPException(status_code=503, detail="LLM service unavailable")

@app.get("/api/v1/llm/history")
async def get_llm_history(limit: int = 10):
    """Get recent LLM analysis history"""
    analyses = memory_store["llm_analyses"][-limit:]
    return {
        "analyses": analyses,
        "total": len(memory_store["llm_analyses"]),
        "timestamp": datetime.now().isoformat()
    }

# WebSocket endpoint for real-time data
@app.websocket("/ws/realtime")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for client messages
            try:
                data = await websocket.receive_text()
                # Handle client messages if needed
                logger.info(f"Received WebSocket message: {data}")
            except WebSocketDisconnect:
                break
            except:
                # Send periodic updates
                await asyncio.sleep(1)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Background task to stream simulation data
@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    asyncio.create_task(stream_simulation_data())

async def stream_simulation_data():
    """Background task to stream real-time simulation data"""
    while True:
        try:
            # Get current simulation status
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{SIMULATION_SERVICE}/status")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Broadcast to WebSocket clients
                    await manager.broadcast({
                        "type": "simulation_data",
                        "data": data,
                        "timestamp": datetime.now().isoformat()
                    })
                    
        except Exception as e:
            logger.error(f"Error streaming simulation data: {e}")
        
        await asyncio.sleep(3)  # Update every 3 seconds

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
