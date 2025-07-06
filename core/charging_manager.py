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

    # Model(R): This class allows us to match each station to a unique random id. 
    # Moreover, it specifies the charging rate and threshold
    # Input: MapManager (Class), Configuration parameters (Dict)
    # Output: None
    
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
        #### add different charging rates based on vehicle type

        self.charging_threshold = config.get('charging_threshold', 20.0)  # %
        #aka this is the min battery percentage
        
        # Initialize charging stations
        self._initialize_charging_stations()
    
    # ============= Initialization Methods =============

    # Model(R): Specifies the number of charging stations and slots per station.
    # Adds the details(station number, node id, x,y position, total slots, charging rate, price)
    # to a dictionary using their station id as the key. 

    # Inputs: None
    # Outputs: None

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
            self.node_to_station[node_id] = station.station_id #Maps the node id to the station id
        
        print(f"Initialized {len(self.charging_stations)} charging stations")
    
    # ============= Charging Station Search Methods =============
    # Test: This will find the nearest station based on the distance (calculated via Distance formaula) and whether it has an available slot.

    # Input: x,y position of EV on map (Tuple)
    # Output: Closest available station to EV (Object of Charging Station class) or None

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
    
    # Test: This will find the best charging station based on distance (determined via Dijkstra), availability, and queue time
    # Input: Vehicle (class)
    # Output: Closest available station to EV (Object of Charging Station class) or None

    
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
            
            # Calculate distance
            distance = self.map_manager.calculate_route_distance(
                vehicle.current_node, station.node_id
            )
            
            # Calculate score: distance + queue penalty
            utilization_penalty = station.get_utilization_rate() * 1000
            score = distance + utilization_penalty
            
            if score < min_score:
                min_score = score
                best_station = station
        
        return best_station
    
    # ------------NEW FUNCTION 
    
    def find_extra_optimal_charging_station(self, vehicle: Vehicle) -> Optional[ChargingStation]:

        """
        Finds the best station based on different factors 
        1. Time
        2. Queue
        -- These factors depend on whether or not the charging stations will differ
        3. How fast it can charge the vehicle
        4. Sustainability factor
        5. Cost to charge

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
            
            # Calculate time
            distance = self.map_manager.get_fastest_path_nodes(
                vehicle.current_node, station.node_id
            )
            
            # Calculate score: distance + queue penalty
            utilization_penalty = station.get_utilization_rate() * 1000
            score = distance + utilization_penalty

            #
            
            if score < min_score:
                min_score = score
                best_station = station
        
        return best_station

    # Test: Gets the station based on the node id
    # Input: Node id (int)
    # Output: Best Charging Station (Object of ChargingStation class)

    
    def get_station_by_node(self, node_id: int) -> Optional[ChargingStation]:
        """Get charging station by node ID"""
        station_id = self.node_to_station.get(node_id)
        if station_id:
            return self.charging_stations.get(station_id)
        return None
    
    # ============= Charging Control Methods =============

    # Test: Checks if a certain vehicle in a specific charging station is charging
    # Input: vehicle (Object of Vehicle Class), station (Object of ChargingStation Class)
    # Output: Whether or not vehicle is charging on that station (Bool)
     
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
    
    # Test: checks if vehicle is charging, if so, it will calculate how much it has charged and the cost. 
    # It then updates the vehicle to be idle.
    # If the station is not charging, it will just return the charge cost and amount to both be zero
    # Input: vehicle (Object of Vehicle Class)
    # Output: Charge amount, charge cost (Tuple)

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
    
    # Test: Loops through each station then each of its vehicles to update how much each vehicle has charged 
    # during a given time step
    # Input: Time step (float)
    # Output: each vehicle id and its charge (Dictionary)
    
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
    
    # Test: Determines if vehicle should charge. It will charge if it doesn't have a passenger and battery below threshold
    # Input: vehicle (Object of vehicle class)
    # Output: Whether vehicle should charge or not (bool)
    
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

    # Test: Gets the statistics of the charging system (total stations, total slots, occupied slots, available slots, 
    # average utilization rate, total energy delivered, total revenue generated, total vehicles charged, average revenue per station)
    # Input: None
    # Output: Statistics (Dict)

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

    # Test: Gets a list of all charging stations
    # Input: None
    # Output: List of all charging stations (List)
    
    def get_station_list(self) -> List[ChargingStation]:
        """Get all charging station list"""
        return list(self.charging_stations.values())
    
    # Test: Gets a list of all busy charging stations (utilization rate is > 80%)
    # Input: None
    # Output: List of all busy charging stations (List)
    
    def get_busy_stations(self) -> List[ChargingStation]:
        """Get busy charging stations (utilization > 80%)"""
        busy_stations = []
        for station in self.charging_stations.values():
            if station.get_utilization_rate() > 0.8:
                busy_stations.append(station)
        return busy_stations