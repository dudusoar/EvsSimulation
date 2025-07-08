"""
Vehicle Management Module
Responsible for vehicle creation, updating, dispatching and statistics
Integrates functionality from original vehicle.py, vehicle_management.py and vision.py
"""

import random
import numpy as np
from typing import List, Dict, Optional, Tuple
from models.vehicle import Vehicle
from core.map_manager import MapManager
from config.simulation_config import VEHICLE_STATUS
from utils.geometry import calculate_distance, calculate_direction_to_target, is_point_near_target


class VehicleManager:
    """Vehicle Manager Class"""
    
    def __init__(self, map_manager: MapManager, config: Dict):
        """
        Initialize vehicle manager
        
        Args:
            map_manager: Map manager
            config: Configuration parameters
        """
        self.map_manager = map_manager
        self.config = config
        
        # Vehicle storage
        self.vehicles: Dict[str, Vehicle] = {}  # vehicle_id -> Vehicle
        
        # Speed parameters
        self.vehicle_speed = config.get('vehicle_speed_mps', 50/3.6)  # m/s
        self.approach_threshold = 10.0  # Target approach threshold (meters)
        
        # Initialize vehicles
        self._initialize_vehicles()
    
    # ============= Initialization Methods =============
    def _initialize_vehicles(self):
        """Initialize vehicles"""
        num_vehicles = self.config.get('num_vehicles', 20)
        
        # Randomly select starting positions
        start_nodes = self.map_manager.get_random_nodes(num_vehicles)
        
        for i in range(num_vehicles):
            vehicle_id = f"V{i+1:03d}"
            position = self.map_manager.get_node_position(start_nodes[i])
            
            vehicle = Vehicle(
                vehicle_id=vehicle_id,
                position=position,
                battery_capacity=self.config.get('battery_capacity', 100.0),
                current_battery=self.config.get('battery_capacity', 100.0),
                consumption_rate=self.config.get('energy_consumption', 0.2),
                current_node=start_nodes[i]
            )
            
            self.vehicles[vehicle_id] = vehicle
        
        print(f"Initialized {len(self.vehicles)} vehicles")
    
    # ============= Vehicle Update Methods =============
    def update_all_vehicles(self, dt: float):
        """Update all vehicle states"""
        for vehicle in self.vehicles.values():
            self._update_vehicle(vehicle, dt)
    
    def _update_vehicle(self, vehicle: Vehicle, dt: float):
        """Update single vehicle"""
        # Execute different update logic based on status
        if vehicle.status == VEHICLE_STATUS['IDLE']:
            # Idle state, accumulate idle time
            vehicle.add_idle_time(dt)
            
        elif vehicle.status in [VEHICLE_STATUS['TO_PICKUP'], 
                               VEHICLE_STATUS['WITH_PASSENGER'], 
                               VEHICLE_STATUS['TO_CHARGING']]:
            # Moving state, update position
            self._update_vehicle_movement(vehicle, dt)
            
        elif vehicle.status == VEHICLE_STATUS['CHARGING']:
            # Charging state, handled by charging manager
            pass
    
    def _update_vehicle_movement(self, vehicle: Vehicle, dt: float):
        """Update vehicle movement"""
        # Check if there's a path
        dt_hours = dt / 3600  # Convert seconds to hours
    
        #-------------NEW FIX (consistent units?)
        # Calculate movement based on vehicle speed (km/h)
        distance_km = self.vehicle_speed * dt_hours  # km
        distance_m = distance_km * 1000  # meters
        #----------------------------------------
        if not vehicle.path_points:
            return
        
        # Get current target point
        target_point = vehicle.get_next_path_point()
        if not target_point:
            return
        
        # Check if approaching current path point
        if is_point_near_target(vehicle.position, target_point, self.approach_threshold):
            # Advance to next path point
            vehicle.advance_path_index()
            
            # Check if reached destination
            if vehicle.has_reached_destination():
                self._handle_arrival(vehicle)
                return
            
            # Get new target point
            target_point = vehicle.get_next_path_point()
            if not target_point:
                return
        
        # Calculate movement direction and speed
        direction = calculate_direction_to_target(vehicle.position, target_point)
        velocity = (direction[0] * self.vehicle_speed, direction[1] * self.vehicle_speed)
        vehicle.update_velocity(velocity)
        
        # Calculate new position
        new_x = vehicle.position[0] + velocity[0] * dt
        new_y = vehicle.position[1] + velocity[1] * dt
        new_position = (new_x, new_y)
        
        # Update position (including battery consumption)
        vehicle.update_position(new_position)
        
        # Update current node (if close to route node)
        if vehicle.route_nodes and vehicle.path_index < len(vehicle.route_nodes):
            current_route_node = vehicle.route_nodes[min(vehicle.path_index, len(vehicle.route_nodes)-1)]
            node_position = self.map_manager.get_node_position(current_route_node)
            if is_point_near_target(vehicle.position, node_position, 50):
                vehicle.current_node = current_route_node
    
    def _handle_arrival(self, vehicle: Vehicle):
        """Handle vehicle arrival at destination"""
        # Only handle status updates here, specific business logic handled by simulation engine
        if vehicle.status == VEHICLE_STATUS['TO_PICKUP']:
            # Arrived at pickup point, wait for simulation engine to handle
            pass
        elif vehicle.status == VEHICLE_STATUS['WITH_PASSENGER']:
            # Arrived at destination, wait for simulation engine to handle
            pass
        elif vehicle.status == VEHICLE_STATUS['TO_CHARGING']:
            # Arrived at charging station, wait for simulation engine to handle
            pass
    
    # ============= Vehicle Getter Methods =============
    def get_all_vehicles(self) -> List[Vehicle]:
        """Get all vehicles"""
        return list(self.vehicles.values())
    
    def get_vehicle_by_id(self, vehicle_id: str) -> Optional[Vehicle]:
        """Get vehicle by ID"""
        return self.vehicles.get(vehicle_id)
    
    def get_available_vehicles(self) -> List[Vehicle]:
        """Get available vehicles (idle and sufficient battery)"""
        available = []
        for vehicle in self.vehicles.values():
            if vehicle.is_idle and not vehicle.needs_charging:
                available.append(vehicle)
        return available
    
    def get_vehicles_by_status(self, status: str) -> List[Vehicle]:
        """Get vehicles by status"""
        return [v for v in self.vehicles.values() if v.status == status]
    
    def get_low_battery_vehicles(self, threshold: float = 20.0) -> List[Vehicle]:
        """Get low battery vehicles"""
        return [v for v in self.vehicles.values() if v.battery_percentage <= threshold]
    
    # ============= Vehicle Dispatch Methods =============
    def dispatch_vehicle_to_order(self, vehicle: Vehicle, pickup_node: int, dropoff_node: int):
        """Dispatch vehicle to pick up order"""
        # Plan route to pickup point
        route_nodes = self.map_manager.get_shortest_path_nodes(
            vehicle.current_node, pickup_node
        )
        path_points = self.map_manager.get_shortest_path_points(
            vehicle.current_node, pickup_node
        )
        
        # Set route and status
        vehicle.set_route(route_nodes, path_points)
        vehicle.update_status(VEHICLE_STATUS['TO_PICKUP'])
        vehicle.target_node = pickup_node
    
    def dispatch_vehicle_to_charging(self, vehicle: Vehicle, station_node: int):
        """Dispatch vehicle to charging"""
        # Plan route to charging station
        route_nodes = self.map_manager.get_shortest_path_nodes(
            vehicle.current_node, station_node
        )
        path_points = self.map_manager.get_shortest_path_points(
            vehicle.current_node, station_node
        )
        
        # Set route and status
        vehicle.set_route(route_nodes, path_points)
        vehicle.update_status(VEHICLE_STATUS['TO_CHARGING'])
        vehicle.target_node = station_node
        vehicle.assign_task({
            'type': 'charging',
            'target_node': station_node
        })
    
    def update_vehicle_for_passenger_pickup(self, vehicle: Vehicle, dropoff_node: int):
        """Update vehicle status to carrying passenger"""
        # Plan route to destination
        route_nodes = self.map_manager.get_shortest_path_nodes(
            vehicle.current_node, dropoff_node
        )
        path_points = self.map_manager.get_shortest_path_points(
            vehicle.current_node, dropoff_node
        )
        
        # Set route and status
        vehicle.set_route(route_nodes, path_points)
        vehicle.update_status(VEHICLE_STATUS['WITH_PASSENGER'])
        vehicle.target_node = dropoff_node
    
    # ============= Battery Management Methods =============
    def charge_vehicle(self, vehicle_id: str, charge_amount: float):
        """Charge vehicle"""
        vehicle = self.vehicles.get(vehicle_id)
        if vehicle:
            vehicle.charge_battery(charge_amount)
    
    def get_vehicles_needing_charge(self) -> List[Vehicle]:
        """Get vehicles needing charge"""
        return [v for v in self.vehicles.values() if v.needs_charging and v.is_idle]
    
    # ============= Statistics Methods =============
    def get_fleet_statistics(self) -> Dict:
        """Get fleet statistics"""
        vehicles_list = list(self.vehicles.values())
        total_vehicles = len(vehicles_list)
        
        if total_vehicles == 0:
            return {}
        
        # Status statistics
        status_counts = {
            'idle': 0,
            'to_pickup': 0,
            'with_passenger': 0,
            'to_charging': 0,
            'charging': 0
        }
        
        for vehicle in vehicles_list:
            if vehicle.status == VEHICLE_STATUS['IDLE']:
                status_counts['idle'] += 1
            elif vehicle.status == VEHICLE_STATUS['TO_PICKUP']:
                status_counts['to_pickup'] += 1
            elif vehicle.status == VEHICLE_STATUS['WITH_PASSENGER']:
                status_counts['with_passenger'] += 1
            elif vehicle.status == VEHICLE_STATUS['TO_CHARGING']:
                status_counts['to_charging'] += 1
            elif vehicle.status == VEHICLE_STATUS['CHARGING']:
                status_counts['charging'] += 1
        
        # Calculate averages
        avg_battery = np.mean([v.battery_percentage for v in vehicles_list])
        avg_distance = np.mean([v.total_distance for v in vehicles_list])
        avg_orders = np.mean([v.total_orders for v in vehicles_list])
        avg_revenue = np.mean([v.total_revenue for v in vehicles_list])
        avg_profit = np.mean([v.get_profit() for v in vehicles_list])
        total_revenue = sum(v.total_revenue for v in vehicles_list)
        total_cost = sum(v.total_charging_cost for v in vehicles_list)
        
        return {
            'total_vehicles': total_vehicles,
            'status_distribution': status_counts,
            'avg_battery_percentage': avg_battery,
            'avg_distance_traveled': avg_distance,
            'avg_orders_completed': avg_orders,
            'avg_revenue_per_vehicle': avg_revenue,
            'avg_profit_per_vehicle': avg_profit,
            'total_fleet_revenue': total_revenue,
            'total_fleet_cost': total_cost,
            'total_fleet_profit': total_revenue - total_cost,
            'utilization_rate': 1 - (status_counts['idle'] / total_vehicles)
        }