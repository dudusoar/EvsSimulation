"""
Data Query API Endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from webapp.backend.models.response import APIResponse
from webapp.backend.services.simulation_service import simulation_service

router = APIRouter()


@router.get("/vehicles", response_model=APIResponse)
async def get_vehicles(vehicle_id: Optional[str] = Query(None)):
    """Get vehicles data"""
    try:
        current_state = simulation_service.get_current_state()
        
        if not current_state:
            return APIResponse(
                success=False,
                message="No simulation data available",
                error="Simulation not running"
            )
        
        vehicles = current_state.vehicles
        
        if vehicle_id:
            # Filter specific vehicle
            vehicle = next((v for v in vehicles if v.vehicle_id == vehicle_id), None)
            if not vehicle:
                return APIResponse(
                    success=False,
                    message=f"Vehicle {vehicle_id} not found",
                    error="Vehicle not found"
                )
            vehicles = [vehicle]
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(vehicles)} vehicle(s)",
            data={"vehicles": [v.dict() for v in vehicles]}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/charging-stations", response_model=APIResponse)
async def get_charging_stations(station_id: Optional[str] = Query(None)):
    """Get charging stations data"""
    try:
        current_state = simulation_service.get_current_state()
        
        if not current_state:
            return APIResponse(
                success=False,
                message="No simulation data available",
                error="Simulation not running"
            )
        
        stations = current_state.charging_stations
        
        if station_id:
            # Filter specific station
            station = next((s for s in stations if s.station_id == station_id), None)
            if not station:
                return APIResponse(
                    success=False,
                    message=f"Charging station {station_id} not found",
                    error="Station not found"
                )
            stations = [station]
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(stations)} charging station(s)",
            data={"charging_stations": [s.dict() for s in stations]}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders", response_model=APIResponse)
async def get_orders(status: Optional[str] = Query(None), limit: int = Query(100)):
    """Get orders data"""
    try:
        current_state = simulation_service.get_current_state()
        
        if not current_state:
            return APIResponse(
                success=False,
                message="No simulation data available",
                error="Simulation not running"
            )
        
        orders = current_state.orders
        
        if status:
            # Filter by status
            orders = [o for o in orders if o.status.lower() == status.lower()]
        
        # Apply limit
        orders = orders[:limit]
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(orders)} order(s)",
            data={"orders": [o.dict() for o in orders]}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics", response_model=APIResponse)
async def get_statistics():
    """Get simulation statistics"""
    try:
        current_state = simulation_service.get_current_state()
        
        if not current_state:
            return APIResponse(
                success=False,
                message="No simulation data available",
                error="Simulation not running"
            )
        
        return APIResponse(
            success=True,
            message="Statistics retrieved successfully",
            data={"statistics": current_state.stats.dict()}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/map-bounds", response_model=APIResponse)
async def get_map_bounds():
    """Get map bounds for the current simulation location"""
    try:
        # This would require extending the simulation service to provide map bounds
        # For now, return default bounds for West Lafayette
        bounds = {
            "north": 40.4500,
            "south": 40.4000,
            "east": -86.8500,
            "west": -86.9500,
            "center": [40.4259, -86.9081]  # [lat, lon]
        }
        
        return APIResponse(
            success=True,
            message="Map bounds retrieved successfully",
            data={"bounds": bounds}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 