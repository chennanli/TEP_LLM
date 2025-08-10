"""
TEP Simulation Service - Adapted from your existing unified_tep_control_panel.py
Simplified for immediate development without database dependency
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
import asyncio
import logging
from datetime import datetime
import os
import sys

# Add the current directory to Python path to import your existing modules
sys.path.append('/app')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TEP Simulation Service",
    description="Tennessee Eastman Process Dynamic Simulator",
    version="1.0.0"
)

# Global simulation state
simulation_state = {
    "is_running": False,
    "current_step": 0,
    "total_steps": 0,
    "current_data": None,
    "simulation_id": None,
    "config": None,
    "anomaly_score": 0.0,
    "is_anomaly": False
}

# Try to import your existing TEP modules
try:
    # Import your existing tep2py or simulation code
    # Adjust these imports based on your actual file structure
    from tep_bridge import TEPBridge  # Your existing bridge
    logger.info("✅ Successfully imported existing TEP modules")
    tep_bridge = TEPBridge()
except ImportError as e:
    logger.warning(f"⚠️ Could not import existing TEP modules: {e}")
    tep_bridge = None

class SimpleTEPSimulator:
    """Simplified TEP simulator for immediate development"""
    
    def __init__(self):
        self.is_running = False
        self.current_step = 0
        self.data_history = []
        
    def start_simulation(self, config: Dict[str, Any]):
        """Start TEP simulation with given configuration"""
        self.is_running = True
        self.current_step = 0
        self.config = config
        
        # Generate simulation ID
        simulation_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Starting TEP simulation: {simulation_id}")
        logger.info(f"Configuration: {config}")
        
        return {
            "simulation_id": simulation_id,
            "status": "started",
            "config": config,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_current_data(self):
        """Generate current simulation data"""
        if not self.is_running:
            return None
            
        # Generate mock TEP data (replace with your actual simulation)
        data = {
            "step": self.current_step,
            "timestamp": datetime.now().isoformat(),
            "variables": self._generate_tep_variables(),
            "anomaly_score": self._calculate_anomaly_score(),
            "is_anomaly": False
        }
        
        # Simple anomaly detection logic
        data["is_anomaly"] = data["anomaly_score"] > 2.0
        
        self.current_step += 1
        self.data_history.append(data)
        
        # Keep only last 100 data points
        if len(self.data_history) > 100:
            self.data_history = self.data_history[-100:]
            
        return data
    
    def _generate_tep_variables(self):
        """Generate mock TEP variables (replace with actual simulation)"""
        # Mock data - replace with your actual TEP simulation
        base_values = {
            "xmeas_1": 0.25 + np.random.normal(0, 0.05),
            "xmeas_2": 3654.0 + np.random.normal(0, 100),
            "xmeas_3": 4509.3 + np.random.normal(0, 50),
            "xmeas_4": 9.35 + np.random.normal(0, 0.5),
            "xmeas_5": 26.9 + np.random.normal(0, 1),
            "reactor_temperature": 120.4 + np.random.normal(0, 2),
            "reactor_pressure": 2705.0 + np.random.normal(0, 50),
            "reactor_level": 75.0 + np.random.normal(0, 5),
        }
        
        # Add fault effects if configured
        if hasattr(self, 'config') and self.config and 'faults' in self.config:
            for fault_id, fault_params in self.config['faults'].items():
                start_time = fault_params.get('start_time', 0)
                magnitude = fault_params.get('magnitude', 0)
                
                if self.current_step >= start_time and magnitude > 0:
                    # Apply fault effects (simplified)
                    if fault_id == 'idv1':
                        base_values["reactor_temperature"] += magnitude * 10
                    elif fault_id == 'idv2':
                        base_values["reactor_pressure"] += magnitude * 100
        
        return base_values
    
    def _calculate_anomaly_score(self):
        """Calculate simple anomaly score"""
        if len(self.data_history) < 10:
            return 0.0
            
        # Simple anomaly detection based on recent data
        recent_data = self.data_history[-10:]
        current_temp = self._generate_tep_variables()["reactor_temperature"]
        
        # Calculate deviation from recent average
        recent_temps = [d["variables"]["reactor_temperature"] for d in recent_data if "variables" in d]
        if recent_temps:
            avg_temp = np.mean(recent_temps)
            deviation = abs(current_temp - avg_temp)
            return deviation / 10.0  # Normalize
        
        return 0.0
    
    def stop_simulation(self):
        """Stop the simulation"""
        self.is_running = False
        logger.info("TEP simulation stopped")
        
        return {
            "status": "stopped",
            "final_step": self.current_step,
            "timestamp": datetime.now().isoformat()
        }

# Initialize simulator
if tep_bridge:
    # Use your existing TEP bridge if available
    simulator = tep_bridge
    logger.info("✅ Using existing TEP bridge")
else:
    # Use simplified simulator for development
    simulator = SimpleTEPSimulator()
    logger.info("✅ Using simplified TEP simulator")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "tep-simulation",
        "timestamp": datetime.now().isoformat(),
        "simulation_running": simulation_state["is_running"]
    }

@app.post("/start")
async def start_simulation(config: Dict[str, Any]):
    """Start TEP simulation"""
    try:
        if hasattr(simulator, 'start_simulation'):
            result = simulator.start_simulation(config)
        else:
            # Fallback for existing code
            result = {
                "simulation_id": f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "status": "started",
                "config": config
            }
        
        # Update global state
        simulation_state.update({
            "is_running": True,
            "current_step": 0,
            "total_steps": config.get("duration", 1000),
            "simulation_id": result.get("simulation_id"),
            "config": config
        })
        
        return result
        
    except Exception as e:
        logger.error(f"Error starting simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def get_simulation_status():
    """Get current simulation status and data"""
    try:
        if hasattr(simulator, 'get_current_data'):
            current_data = simulator.get_current_data()
        else:
            # Fallback mock data
            current_data = {
                "step": simulation_state["current_step"],
                "variables": {"reactor_temperature": 120.4, "reactor_pressure": 2705.0},
                "anomaly_score": 0.5,
                "is_anomaly": False
            }
        
        # Update global state
        if current_data:
            simulation_state.update({
                "current_data": current_data,
                "current_step": current_data.get("step", simulation_state["current_step"]),
                "anomaly_score": current_data.get("anomaly_score", 0.0),
                "is_anomaly": current_data.get("is_anomaly", False)
            })
        
        return {
            "status": "running" if simulation_state["is_running"] else "stopped",
            "data": current_data,
            "simulation_state": simulation_state,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting simulation status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stop")
async def stop_simulation():
    """Stop TEP simulation"""
    try:
        if hasattr(simulator, 'stop_simulation'):
            result = simulator.stop_simulation()
        else:
            result = {"status": "stopped"}
        
        # Update global state
        simulation_state.update({
            "is_running": False,
            "current_data": None
        })
        
        return result
        
    except Exception as e:
        logger.error(f"Error stopping simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/configure")
async def configure_simulation(config: Dict[str, Any]):
    """Update simulation configuration"""
    try:
        simulation_state["config"] = config
        
        # Apply configuration to simulator if method exists
        if hasattr(simulator, 'configure'):
            simulator.configure(config)
        
        return {
            "status": "configured",
            "config": config,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error configuring simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
