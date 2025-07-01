"""
Simulation Service Layer
Wraps existing simulation engine for web application
"""

import asyncio
import threading
import time
from typing import Dict, List, Optional, Callable
from datetime import datetime

# Import existing simulation system
from core.simulation_engine import SimulationEngine
from config.simulation_config import SIMULATION_CONFIG
from webapp.backend.models.response import (
    VehicleData, ChargingStationData, OrderData, 
    SimulationStats, SimulationState, SimulationConfig
)


class SimulationService:
    """Service layer for simulation management"""
    
    def __init__(self):
        """Initialize simulation service"""
        self.engine: Optional[SimulationEngine] = None
        self.config: Dict = SIMULATION_CONFIG.copy()
        self.is_running: bool = False
        self.is_paused: bool = False
        self.simulation_thread: Optional[threading.Thread] = None
        self.current_state: Optional[SimulationState] = None
        self.subscribers: List[Callable] = []  # WebSocket subscribers
        self.speed_multiplier: float = 1.0
        
    def subscribe(self, callback: Callable):
        """Subscribe to simulation state updates"""
        self.subscribers.append(callback)
        
    def unsubscribe(self, callback: Callable):
        """Unsubscribe from simulation state updates"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    async def notify_subscribers(self, state: SimulationState):
        """Notify all subscribers of state update"""
        for callback in self.subscribers:
            try:
                await callback(state)
            except Exception as e:
                print(f"Error notifying subscriber: {e}")
    
    def create_simulation(self, config: SimulationConfig) -> bool:
        """Create new simulation with given config"""
        try:
            # Update internal config
            self.config.update({
                'location': config.location,
                'num_vehicles': config.num_vehicles,
                'num_charging_stations': config.num_charging_stations,
                'simulation_duration': config.simulation_duration,
                'vehicle_speed': config.vehicle_speed,
                'order_generation_rate': config.order_generation_rate
            })
            
            # Create simulation engine
            self.engine = SimulationEngine(self.config)
            return True
            
        except Exception as e:
            print(f"Error creating simulation: {e}")
            return False
    
    def start_simulation(self) -> bool:
        """Start simulation in background thread"""
        if self.is_running:
            return False
            
        if not self.engine:
            return False
            
        self.is_running = True
        self.is_paused = False
        
        # Start simulation in background thread
        self.simulation_thread = threading.Thread(
            target=self._simulation_loop, 
            daemon=True
        )
        self.simulation_thread.start()
        return True
    
    def pause_simulation(self) -> bool:
        """Pause simulation"""
        if not self.is_running:
            return False
        self.is_paused = True
        return True
    
    def resume_simulation(self) -> bool:
        """Resume simulation"""
        if not self.is_running:
            return False
        self.is_paused = False
        return True
    
    def stop_simulation(self) -> bool:
        """Stop simulation"""
        self.is_running = False
        self.is_paused = False
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=2.0)
        return True
    
    def set_speed_multiplier(self, multiplier: float) -> bool:
        """Set simulation speed multiplier"""
        if 0.1 <= multiplier <= 10.0:
            self.speed_multiplier = multiplier
            return True
        return False
    
    def get_current_state(self) -> Optional[SimulationState]:
        """Get current simulation state"""
        return self.current_state
    
    def _simulation_loop(self):
        """Main simulation loop running in background thread"""
        if not self.engine:
            return
            
        try:
            duration = self.config['simulation_duration']
            base_time_step = self.config.get('time_step', 0.1)
            
            while self.engine.current_time < duration and self.is_running:
                if not self.is_paused:
                    # Run simulation step
                    self.engine.run_step()
                    
                    # Update current state
                    self.current_state = self._build_current_state()
                    
                    # Notify subscribers asynchronously
                    if self.subscribers:
                        asyncio.run(self.notify_subscribers(self.current_state))
                
                # Control simulation speed
                sleep_time = base_time_step / self.speed_multiplier
                time.sleep(sleep_time)
            
            # Simulation completed
            self.is_running = False
            print("Simulation completed")
            
        except Exception as e:
            print(f"Error in simulation loop: {e}")
            self.is_running = False
    
    def _build_current_state(self) -> SimulationState:
        """Build current simulation state from engine data"""
        if not self.engine:
            return None
            
        # Get vehicles data
        vehicles = []
        for vehicle in self.engine.get_vehicles():
            vehicles.append(VehicleData(
                vehicle_id=vehicle.vehicle_id,
                position=[vehicle.position[0], vehicle.position[1]],  # [lon, lat]
                status=vehicle.status,
                battery_percentage=vehicle.battery_percentage,
                current_order_id=getattr(vehicle, 'current_order_id', None),
                destination=None  # TODO: add destination if available
            ))
        
        # Get charging stations data
        charging_stations = []
        for station in self.engine.get_charging_stations():
            charging_stations.append(ChargingStationData(
                station_id=station.station_id,
                position=[station.position[0], station.position[1]],  # [lon, lat]
                total_slots=station.total_slots,
                available_slots=station.available_slots,
                utilization_rate=(station.total_slots - station.available_slots) / station.total_slots
            ))
        
        # Get orders data
        orders = []
        orders_info = self.engine.get_orders()
        all_orders = orders_info.get('pending', []) + orders_info.get('active', [])
        
        for order in all_orders:
            orders.append(OrderData(
                order_id=order.order_id,
                pickup_position=[order.pickup_position[0], order.pickup_position[1]],
                dropoff_position=[order.dropoff_position[0], order.dropoff_position[1]],
                status=order.status,
                assigned_vehicle_id=getattr(order, 'assigned_vehicle_id', None),
                creation_time=getattr(order, 'creation_time', 0),
                completion_time=getattr(order, 'completion_time', None)
            ))
        
        # Get statistics
        current_stats = self.engine.get_current_statistics()
        stats = SimulationStats(
            current_time=self.engine.current_time,
            total_revenue=current_stats.get('orders', {}).get('total_revenue', 0),
            total_cost=current_stats.get('vehicles', {}).get('total_cost', 0),
            total_profit=current_stats.get('orders', {}).get('total_revenue', 0) - 
                        current_stats.get('vehicles', {}).get('total_cost', 0),
            order_completion_rate=current_stats.get('orders', {}).get('completion_rate', 0),
            vehicle_utilization_rate=current_stats.get('vehicles', {}).get('utilization_rate', 0),
            charging_utilization_rate=current_stats.get('charging', {}).get('utilization_rate', 0),
            total_orders_completed=current_stats.get('orders', {}).get('total_orders_completed', 0),
            total_orders_pending=current_stats.get('orders', {}).get('pending_orders', 0)
        )
        
        return SimulationState(
            vehicles=vehicles,
            charging_stations=charging_stations,
            orders=orders,
            stats=stats,
            timestamp=time.time()
        )


# Global simulation service instance
simulation_service = SimulationService() 