"""
Vehicle Data Model
Defines vehicle data structure and basic operations
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
import numpy as np
from config.simulation_config import VEHICLE_STATUS


@dataclass
class Vehicle:
    """Vehicle class containing all vehicle state information"""
    
    # ============= Basic Properties =============
    vehicle_id: str
    position: Tuple[float, float]  # (x, y) coordinates
    velocity: Tuple[float, float] = (0.0, 0.0)  # (vx, vy) velocity
    
    # ============= Battery Related =============
    battery_capacity: float = 100.0  # Maximum battery (%)
    current_battery: float = 100.0   # Current battery (%)
    consumption_rate: float = 0.2    # Energy consumption rate (%/km)
    
    # ============= Status Related =============
    status: str = VEHICLE_STATUS['IDLE']  # Current status
    current_task: Optional[Dict] = None   # Current task
    
    # ============= Route Related =============
    current_node: Optional[int] = None      # Current node
    target_node: Optional[int] = None       # Target node
    route_nodes: List[int] = field(default_factory=list)      # Route node list
    path_points: List[Tuple[float, float]] = field(default_factory=list)  # Detailed path points
    path_index: int = 0                     # Current path point index
    
    # ============= Statistical Data =============
    total_distance: float = 0.0        # Total distance traveled
    total_orders: int = 0              # Number of completed orders
    total_revenue: float = 0.0         # Total revenue
    total_charging_cost: float = 0.0   # Total charging cost
    idle_time: float = 0.0             # Idle time
    
    # ============= Property Methods =============
    @property
    def battery_percentage(self) -> float:
        """Return battery percentage"""
        return (self.current_battery / self.battery_capacity) * 100.0
    
    @property
    def is_idle(self) -> bool:
        """Check if idle"""
        return self.status == VEHICLE_STATUS['IDLE']
    
    @property
    def is_charging(self) -> bool:
        """Check if charging"""
        return self.status == VEHICLE_STATUS['CHARGING']
    
    @property
    def needs_charging(self) -> bool:
        """Check if needs charging"""
        return self.battery_percentage <= 20.0  # Need charging below 20%
    
    @property
    def has_passenger(self) -> bool:
        """Check if carrying passenger"""
        return self.status == VEHICLE_STATUS['WITH_PASSENGER']
    
    # ============= Position Update Methods =============
    def update_position(self, new_position: Tuple[float, float]):
        """Update position"""
        # Calculate movement distance
        dx = new_position[0] - self.position[0]
        dy = new_position[1] - self.position[1]
        distance = np.sqrt(dx**2 + dy**2) / 1000  # Convert to kilometers
        
        # Update position
        self.position = new_position
        
        # Update statistics
        self.total_distance += distance
        
        # Consume battery
        self.consume_battery(distance)
    
    def update_velocity(self, new_velocity: Tuple[float, float]):
        """Update velocity"""
        self.velocity = new_velocity
    
    # ============= Battery Management Methods =============
    def consume_battery(self, distance_km: float):
        """Consume battery"""
        consumption = distance_km * self.consumption_rate
        self.current_battery = max(0.0, self.current_battery - consumption)
    
    def charge_battery(self, amount: float):
        """Charge battery"""
        self.current_battery = min(self.battery_capacity, self.current_battery + amount)
    
    def calculate_range(self) -> float:
        """Calculate remaining range (kilometers)"""
        if self.consumption_rate > 0:
            return self.current_battery / self.consumption_rate
        return float('inf')
    
    # ============= Task Management Methods =============
    def assign_task(self, task: Dict):
        """Assign task"""
        self.current_task = task
        
    def clear_task(self):
        """Clear task"""
        self.current_task = None
        self.target_node = None
        self.route_nodes = []
        self.path_points = []
        self.path_index = 0
    
    def update_status(self, new_status: str):
        """Update status"""
        self.status = new_status
        
    # ============= Route Management Methods =============
    def set_route(self, route_nodes: List[int], path_points: List[Tuple[float, float]]):
        """Set route"""
        self.route_nodes = route_nodes
        self.path_points = path_points
        self.path_index = 0
        if route_nodes:
            self.target_node = route_nodes[-1]
    
    def get_next_path_point(self) -> Optional[Tuple[float, float]]:
        """Get next path point"""
        if self.path_index < len(self.path_points):
            return self.path_points[self.path_index]
        return None
    
    def advance_path_index(self):
        """Advance to next path point"""
        if self.path_index < len(self.path_points) - 1:
            self.path_index += 1
    
    def has_reached_destination(self) -> bool:
        """Check if reached destination"""
        return self.path_index >= len(self.path_points) - 1
    
    # ============= Statistics Methods =============
    def complete_order(self, revenue: float):
        """Complete order"""
        self.total_orders += 1
        self.total_revenue += revenue
    
    def add_charging_cost(self, cost: float):
        """Add charging cost"""
        self.total_charging_cost += cost
    
    def add_idle_time(self, time: float):
        """Add idle time"""
        self.idle_time += time
    
    def get_profit(self) -> float:
        """Calculate profit"""
        return self.total_revenue - self.total_charging_cost
    
    def get_statistics(self) -> Dict:
        """Get statistics"""
        return {
            'vehicle_id': self.vehicle_id,
            'total_distance': self.total_distance,
            'total_orders': self.total_orders,
            'total_revenue': self.total_revenue,
            'total_charging_cost': self.total_charging_cost,
            'profit': self.get_profit(),
            'idle_time': self.idle_time,
            'battery_percentage': self.battery_percentage
        }