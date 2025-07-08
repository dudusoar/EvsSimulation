"""
Charging Management Module
Responsible for charging station management, charging scheduling and charging process control
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
from models.charging_station import ChargingStation
from models.vehicle import Vehicle
from core.map_manager import MapManager
from config.simulation_config import VEHICLE_STATUS
from utils.geometry import calculate_distance


class ChargingManager:
    """Charging Manager Class"""
    
    def __init__(self, map_manager: MapManager, config: Dict):
        """
        Initialize charging manager
        
        Args:
            map_manager: Map manager
            config: Configuration parameters
        """
        self.map_manager = map_manager
        self.config = config
        
        # Charging stations
        self.charging_stations: Dict[str, ChargingStation] = {}  # station_id -> ChargingStation
        self.node_to_station: Dict[int, str] = {}  # node_id -> station_id mapping
        
        # Charging parameters
        self.charging_rate = config.get('charging_rate', 1.0)  # %/second
        self.charging_threshold = config.get('charging_threshold', 20.0)  # %
        
        # Initialize charging stations
        self._initialize_charging_stations()
    
    # ============= Initialization Methods =============
    def _initialize_charging_stations(self):
        """Initialize charging stations"""
        num_stations = self.config.get('num_charging_stations', 5)
        slots_per_station = self.config.get('charging_slots_per_station', 3)
        
        # Select charging station locations
        station_nodes = self.map_manager.select_charging_station_nodes(num_stations)
        
        # Create charging stations
        for i, node_id in enumerate(station_nodes):
            position = self.map_manager.get_node_position(node_id)
            
            station = ChargingStation(
                station_id=f"STATION_{i+1}",
                node_id=node_id,
                position=position,
                total_slots=slots_per_station,
                charging_rate=self.charging_rate,
                electricity_price=self.config.get('electricity_price', 0.8)
            )
            
            self.charging_stations[station.station_id] = station
            self.node_to_station[node_id] = station.station_id
        
        print(f"Initialized {len(self.charging_stations)} charging stations")
    
    # ============= Charging Station Search Methods =============
    def find_nearest_available_station(self, position: Tuple[float, float]) -> Optional[ChargingStation]:
        """Find nearest available charging station"""
        best_station = None
        min_distance = float('inf')
        
        for station in self.charging_stations.values():
            if station.has_available_slot():
                distance = calculate_distance(position, station.position)
                if distance < min_distance:
                    min_distance = distance
                    best_station = station
        
        return best_station
    
    def find_optimal_charging_station(self, vehicle: Vehicle) -> Optional[ChargingStation]:
        """
        Find optimal charging station for vehicle
        Consider distance, availability and queuing situation
        """
        if not vehicle.current_node:
            return None
        
        vehicle_pos = self.map_manager.get_node_position(vehicle.current_node)
        
        # Calculate score for each charging station
        best_station = None
        min_score = float('inf')
        
        for station in self.charging_stations.values():
            if not station.has_available_slot():
                continue
            
            #----------------------------
            # uses time now instead of distance
            # Calculate time
            time = self.map_manager.calculate_route_time(
                vehicle.current_node, station.node_id
            )
            
            # Calculate score: distance + queue penalty
            utilization_penalty = station.get_utilization_rate() * 1000
            score = time + utilization_penalty
            
            if score < min_score:
                min_score = score
                best_station = station
        
        return best_station
    
    def get_station_by_node(self, node_id: int) -> Optional[ChargingStation]:
        """Get charging station by node ID"""
        station_id = self.node_to_station.get(node_id)
        if station_id:
            return self.charging_stations.get(station_id)
        return None
    
    # ============= Charging Control Methods =============
    def request_charging(self, vehicle: Vehicle, station: ChargingStation) -> bool:
        """
        Request charging
        
        Args:
            vehicle: Vehicle object
            station: Charging station object
        
        Returns:
            Whether charging started successfully
        """
        # Check if charging station has available slot
        if not station.has_available_slot():
            return False
        
        # Start charging
        if station.start_charging(vehicle.vehicle_id):
            vehicle.update_status(VEHICLE_STATUS['CHARGING'])
            return True
        
        return False
    
    def stop_charging(self, vehicle: Vehicle) -> Tuple[float, float]:
        """
        Stop charging
        
        Args:
            vehicle: Vehicle object
        
        Returns:
            (charge_amount, charging_cost)
        """
        # Find charging station where vehicle is charging
        station = None
        for s in self.charging_stations.values():
            if s.is_vehicle_charging(vehicle.vehicle_id):
                station = s
                break
        
        if not station:
            return 0.0, 0.0
        
        # Calculate charge amount and cost
        charge_amount = vehicle.current_battery - (vehicle.battery_capacity - 100.0)  # How much charged
        if charge_amount < 0:
            charge_amount = 0
        
        # Calculate cost
        cost = station.calculate_charging_cost(charge_amount)
        
        # Stop charging
        station.stop_charging(vehicle.vehicle_id)
        
        # Update vehicle status
        vehicle.update_status(VEHICLE_STATUS['IDLE'])
        vehicle.add_charging_cost(cost)
        
        return charge_amount, cost
    
    def update_charging_progress(self, dt: float) -> Dict[str, float]:
        """
        Update charging progress for all vehicles currently charging
        
        Args:
            dt: Time step
        
        Returns:
            {vehicle_id: charge_amount} dictionary
        """
        charging_updates = {}
        
        for station in self.charging_stations.values():
            # Calculate charge amount for this time step
            charge_amount = station.calculate_charge_amount(dt)
            
            # Update each vehicle currently charging
            for vehicle_id in list(station.charging_vehicles):  # Copy list to avoid modification errors
                charging_updates[vehicle_id] = charge_amount
        
        return charging_updates
    
    def should_vehicle_charge(self, vehicle: Vehicle) -> bool:
        """
        Determine if vehicle should go charging
        
        Args:
            vehicle: Vehicle object
        
        Returns:
            Whether should charge
        """
        # Don't charge if carrying passenger
        if vehicle.has_passenger:
            return False
        
        # Should charge if battery below threshold
        if vehicle.battery_percentage <= self.charging_threshold:
            return True
        
        # Consider charging if battery low and currently idle
        if vehicle.is_idle and vehicle.battery_percentage <= 40:
            return True
        
        return False
    
    # ============= Statistics Methods =============
    def get_statistics(self) -> Dict:
        """Get charging system statistics"""
        total_stations = len(self.charging_stations)
        total_slots = sum(s.total_slots for s in self.charging_stations.values())
        occupied_slots = sum(s.occupied_slots for s in self.charging_stations.values())
        total_energy = sum(s.total_energy_delivered for s in self.charging_stations.values())
        total_revenue = sum(s.total_revenue for s in self.charging_stations.values())
        total_vehicles_served = sum(s.total_vehicles_served for s in self.charging_stations.values())
        
        # Calculate average utilization rate
        avg_utilization = occupied_slots / max(1, total_slots)
        
        return {
            'total_stations': total_stations,
            'total_slots': total_slots,
            'occupied_slots': occupied_slots,
            'available_slots': total_slots - occupied_slots,
            'avg_utilization_rate': avg_utilization,
            'total_energy_delivered': total_energy,
            'total_revenue': total_revenue,
            'total_vehicles_served': total_vehicles_served,
            'avg_revenue_per_station': total_revenue / max(1, total_stations)
        }
    
    def get_station_list(self) -> List[ChargingStation]:
        """Get all charging station list"""
        return list(self.charging_stations.values())
    
    def get_busy_stations(self) -> List[ChargingStation]:
        """Get busy charging stations (utilization > 80%)"""
        busy_stations = []
        for station in self.charging_stations.values():
            if station.get_utilization_rate() > 0.8:
                busy_stations.append(station)
        return busy_stations