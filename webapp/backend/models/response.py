"""
Response Models for API Data Transfer
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel


class VehicleData(BaseModel):
    """Vehicle data model"""
    vehicle_id: str
    position: List[float]  # [longitude, latitude]
    status: str
    battery_percentage: float
    current_order_id: Optional[str] = None
    destination: Optional[List[float]] = None


class ChargingStationData(BaseModel):
    """Charging station data model"""
    station_id: str
    position: List[float]  # [longitude, latitude]
    total_slots: int
    available_slots: int
    utilization_rate: float


class OrderData(BaseModel):
    """Order data model"""
    order_id: str
    pickup_position: List[float]  # [longitude, latitude]
    dropoff_position: List[float]  # [longitude, latitude]
    status: str
    assigned_vehicle_id: Optional[str] = None
    creation_time: float
    assignment_time: Optional[float] = None
    pickup_time: Optional[float] = None
    completion_time: Optional[float] = None
    estimated_distance: float = 0.0
    final_price: float = 0.0
    pickup_completed: bool = False


class SimulationStats(BaseModel):
    """Simulation statistics model"""
    current_time: float
    total_revenue: float
    total_cost: float
    total_profit: float
    order_completion_rate: float
    vehicle_utilization_rate: float
    charging_utilization_rate: float
    total_orders_completed: int
    total_orders_pending: int


class SimulationState(BaseModel):
    """Complete simulation state for real-time updates"""
    vehicles: List[VehicleData]
    charging_stations: List[ChargingStationData]
    orders: List[OrderData]
    stats: SimulationStats
    timestamp: float


class SimulationConfig(BaseModel):
    """Simulation configuration model"""
    location: str
    num_vehicles: int
    num_charging_stations: int
    simulation_duration: float
    vehicle_speed: float
    order_generation_rate: int


class SimulationControl(BaseModel):
    """Simulation control commands"""
    command: str  # "start", "pause", "resume", "stop", "reset"
    config: Optional[SimulationConfig] = None
    speed_multiplier: Optional[float] = None


class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None


class WebSocketMessage(BaseModel):
    """WebSocket message model"""
    type: str  # "simulation_state", "control", "error"
    data: Optional[Any] = None
    timestamp: float 