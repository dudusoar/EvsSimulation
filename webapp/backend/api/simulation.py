"""
Simulation Control API Endpoints
"""

from fastapi import APIRouter, HTTPException
from webapp.backend.models.response import (
    APIResponse, SimulationConfig, SimulationControl, SimulationState
)
from webapp.backend.services.simulation_service import simulation_service

router = APIRouter()


@router.post("/create", response_model=APIResponse)
async def create_simulation(config: SimulationConfig):
    """Create a new simulation with given configuration"""
    try:
        success = simulation_service.create_simulation(config)
        
        if success:
            return APIResponse(
                success=True,
                message="Simulation created successfully",
                data={"config": config.dict()}
            )
        else:
            return APIResponse(
                success=False,
                message="Failed to create simulation",
                error="Unknown error during simulation creation"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/control", response_model=APIResponse)
async def control_simulation(control: SimulationControl):
    """Control simulation (start, pause, resume, stop)"""
    try:
        command = control.command.lower()
        
        if command == "start":
            success = simulation_service.start_simulation()
            message = "Simulation started" if success else "Failed to start simulation"
            
        elif command == "pause":
            success = simulation_service.pause_simulation()
            message = "Simulation paused" if success else "Failed to pause simulation"
            
        elif command == "resume":
            success = simulation_service.resume_simulation()
            message = "Simulation resumed" if success else "Failed to resume simulation"
            
        elif command == "stop":
            success = simulation_service.stop_simulation()
            message = "Simulation stopped" if success else "Failed to stop simulation"
            
        elif command == "reset":
            # Stop current simulation and clear state
            simulation_service.stop_simulation()
            success = True
            message = "Simulation reset"
            
        else:
            return APIResponse(
                success=False,
                message="Invalid command",
                error=f"Unknown command: {command}"
            )
        
        return APIResponse(
            success=success,
            message=message,
            data={"command": command}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/speed", response_model=APIResponse)
async def set_simulation_speed(speed_data: dict):
    """Set simulation speed multiplier"""
    try:
        multiplier = speed_data.get("multiplier", 1.0)
        
        success = simulation_service.set_speed_multiplier(multiplier)
        
        if success:
            return APIResponse(
                success=True,
                message=f"Speed set to {multiplier}x",
                data={"speed_multiplier": multiplier}
            )
        else:
            return APIResponse(
                success=False,
                message="Invalid speed multiplier",
                error="Speed multiplier must be between 0.1 and 10.0"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=APIResponse)
async def get_simulation_status():
    """Get current simulation status"""
    try:
        status_data = {
            "is_running": simulation_service.is_running,
            "is_paused": simulation_service.is_paused,
            "speed_multiplier": simulation_service.speed_multiplier,
            "has_engine": simulation_service.engine is not None,
            "current_time": simulation_service.engine.current_time if simulation_service.engine else 0
        }
        
        return APIResponse(
            success=True,
            message="Status retrieved successfully",
            data=status_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/state", response_model=APIResponse)
async def get_simulation_state():
    """Get current simulation state (vehicles, orders, etc.)"""
    try:
        current_state = simulation_service.get_current_state()
        
        if current_state:
            return APIResponse(
                success=True,
                message="State retrieved successfully",
                data=current_state.dict()
            )
        else:
            return APIResponse(
                success=False,
                message="No simulation state available",
                error="Simulation not running or not initialized"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 