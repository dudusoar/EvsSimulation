"""
Charging Station Data Model
Defines charging station data structure
"""

from dataclasses import dataclass, field
from typing import Tuple, List, Set
import uuid


@dataclass
class ChargingStation:
    """Charging station class containing all charging station information"""
    
    # ============= Basic Information =============
    station_id: str = None
    node_id: int = None                      # Node ID where located
    position: Tuple[float, float] = None     # Position coordinates
    
    # ============= Charging Parameters =============
    total_slots: int = 3                     # Total number of charging slots
    charging_power: float = 50.0             # Charging power (kW)
    charging_rate: float = 1.0               # Charging rate (%/second)
    electricity_price: float = 0.8           # Electricity price (USD/kWh)
    
    # ============= Status Information =============
    occupied_slots: int = 0                  # Number of occupied charging slots
    charging_vehicles: Set[str] = field(default_factory=set)  # Set of vehicle IDs currently charging
    
    # ============= Statistical Information =============
    total_energy_delivered: float = 0.0      # Total energy delivered (kWh)
    total_revenue: float = 0.0               # Total revenue
    total_vehicles_served: int = 0           # Total number of vehicles served
    
    def __post_init__(self):
        """Post-initialization processing"""
        if self.station_id is None:
            self.station_id = f"STATION_{uuid.uuid4().hex[:8]}"
    
    # ============= Charging Slot Management Methods =============
    @property
    def available_slots(self) -> int:
        """Get number of available charging slots"""
        return self.total_slots - self.occupied_slots
    
    def has_available_slot(self) -> bool:
        """Whether has available charging slot"""
        return self.available_slots > 0
    
    def is_full(self) -> bool:
        """Whether is full"""
        return self.occupied_slots >= self.total_slots
    
    def get_utilization_rate(self) -> float:
        """Get utilization rate"""
        if self.total_slots > 0:
            return self.occupied_slots / self.total_slots
        return 0.0
    
    # ============= Vehicle Charging Management Methods =============
    def start_charging(self, vehicle_id: str) -> bool:
        """Start charging"""
        if self.has_available_slot() and vehicle_id not in self.charging_vehicles:
            self.charging_vehicles.add(vehicle_id)
            self.occupied_slots += 1
            self.total_vehicles_served += 1
            return True
        return False
    
    def stop_charging(self, vehicle_id: str) -> bool:
        """Stop charging"""
        if vehicle_id in self.charging_vehicles:
            self.charging_vehicles.remove(vehicle_id)
            self.occupied_slots -= 1
            return True
        return False
    
    def is_vehicle_charging(self, vehicle_id: str) -> bool:
        """Check if vehicle is charging"""
        return vehicle_id in self.charging_vehicles
    
    # ============= Charging Calculation Methods =============
    def calculate_charge_amount(self, duration: float) -> float:
        """Calculate charge amount (battery percentage)"""
        return self.charging_rate * duration
    
    def calculate_energy_consumed(self, charge_percentage: float, battery_capacity: float = 100.0) -> float:
        """Calculate energy consumed (kWh)"""
        # Assume 100% battery capacity corresponds to 50kWh
        kwh_per_percent = 0.5
        return charge_percentage * kwh_per_percent
    
    def calculate_charging_cost(self, charge_percentage: float, battery_capacity: float = 100.0) -> float:
        """Calculate charging cost"""
        energy_kwh = self.calculate_energy_consumed(charge_percentage, battery_capacity)
        cost = energy_kwh * self.electricity_price
        
        # Update statistics
        self.total_energy_delivered += energy_kwh
        self.total_revenue += cost
        
        return cost
    
    # ============= Information Getter Methods =============
    def get_info(self) -> dict:
        """Get charging station information"""
        return {
            'station_id': self.station_id,
            'node_id': self.node_id,
            'position': self.position,
            'available_slots': self.available_slots,
            'occupied_slots': self.occupied_slots,
            'utilization_rate': self.get_utilization_rate(),
            'charging_vehicles': list(self.charging_vehicles),
            'total_energy_delivered': self.total_energy_delivered,
            'total_revenue': self.total_revenue,
            'total_vehicles_served': self.total_vehicles_served
        }
    
    def get_statistics(self) -> dict:
        """Get statistics"""
        return {
            'station_id': self.station_id,
            'utilization_rate': self.get_utilization_rate(),
            'total_energy_delivered': self.total_energy_delivered,
            'total_revenue': self.total_revenue,
            'total_vehicles_served': self.total_vehicles_served,
            'average_revenue_per_vehicle': self.total_revenue / max(1, self.total_vehicles_served)
        }