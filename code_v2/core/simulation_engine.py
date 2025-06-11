<<<<<<< HEAD
"""
Simulation Engine Module
Coordinates all subsystems, manages simulation flow, and handles business logic
"""

import time
from typing import Dict, List, Optional
from core.map_manager import MapManager
from core.vehicle_manager import VehicleManager
from core.order_system import OrderSystem
from core.charging_manager import ChargingManager
from models.vehicle import Vehicle
from config.simulation_config import VEHICLE_STATUS
from utils.geometry import is_point_near_target


class SimulationEngine:
    """Simulation Engine Class"""
    
    def __init__(self, config: Dict):
        """
        Initialize simulation engine
        
        Args:
            config: Simulation configuration parameters
        """
        self.config = config
        self.current_time = 0.0
        self.time_step = config.get('time_step', 0.1)
        
        # Initialize all managers
        print("Initializing simulation engine...")
        
        # 1. Map manager
        print("Loading map...")
        self.map_manager = MapManager(
            location=config.get('location', 'West Lafayette, IN'),
            cache_dir='datasets/maps'
        )
        
        # 2. Vehicle manager
        print("Initializing vehicles...")
        self.vehicle_manager = VehicleManager(self.map_manager, config)
        
        # 3. Order system
        print("Initializing order system...")
        self.order_system = OrderSystem(self.map_manager, config)
        
        # 4. Charging manager
        print("Initializing charging stations...")
        self.charging_manager = ChargingManager(self.map_manager, config)
        
        # Statistics
        self.statistics = {
            'start_time': time.time(),
            'simulation_time': 0.0,
            'total_steps': 0
        }
        
        print("Simulation engine initialization completed!")
    
    # ============= Simulation Main Loop =============
    def run_simulation(self, duration: float) -> Dict:
        """
        Run simulation
        
        Args:
            duration: Simulation duration (seconds)
        
        Returns:
            Simulation result statistics
        """
        print(f"\nStarting simulation, duration: {duration} seconds")
        steps = int(duration / self.time_step)
        
        for step in range(steps):
            self.run_step()
            
            # Print progress periodically
            if step % 100 == 0:
                progress = (step / steps) * 100
                print(f"Simulation progress: {progress:.1f}%")
        
        print("Simulation completed!")
        return self.get_final_statistics()
    
    def run_step(self):
        """Run one simulation step"""
        # 1. Generate new orders
        new_orders = self.order_system.generate_orders(self.current_time, self.time_step)
        
        # 2. Assign orders
        self._assign_orders()
        
        # 3. Update vehicle status
        self.vehicle_manager.update_all_vehicles(self.time_step)
        
        # 4. Handle vehicle arrival events
        self._handle_vehicle_arrivals()
        
        # 5. Update charging progress
        charging_updates = self.charging_manager.update_charging_progress(self.time_step)
        for vehicle_id, charge_amount in charging_updates.items():
            self.vehicle_manager.charge_vehicle(vehicle_id, charge_amount)
        
        # 6. Check charging needs
        self._check_charging_needs()
        
        # 7. Cancel timeout orders
        self.order_system.check_and_cancel_timeout_orders(self.current_time)
        
        # 8. Update time
        self.current_time += self.time_step
        self.statistics['simulation_time'] = self.current_time
        self.statistics['total_steps'] += 1
    
    # ============= Order Assignment Logic =============
    def _assign_orders(self):
        """Assign pending orders"""
        # Get pending orders
        pending_orders = self.order_system.get_pending_orders()
        if not pending_orders:
            return
        
        # Get available vehicles
        available_vehicles = self.vehicle_manager.get_available_vehicles()
        if not available_vehicles:
            return
        
        # Find best vehicle for each order
        for order in pending_orders:
            if not available_vehicles:
                break
            
            # Find best vehicle
            best_vehicle = self.order_system.find_best_vehicle_for_order(
                order.order_id, available_vehicles
            )
            
            if best_vehicle:
                # Assign order
                success = self.order_system.assign_order_to_vehicle(
                    order.order_id, best_vehicle, self.current_time
                )
                
                if success:
                    # Remove from available list
                    available_vehicles.remove(best_vehicle)
    
    # ============= Vehicle Arrival Handling =============
    def _handle_vehicle_arrivals(self):
        """Handle vehicle arrival at destination events"""
        for vehicle in self.vehicle_manager.get_all_vehicles():
            # Check if reached destination
            if not vehicle.has_reached_destination():
                continue
            
            # Handle based on vehicle status
            if vehicle.status == VEHICLE_STATUS['TO_PICKUP']:
                self._handle_pickup_arrival(vehicle)
                
            elif vehicle.status == VEHICLE_STATUS['WITH_PASSENGER']:
                self._handle_dropoff_arrival(vehicle)
                
            elif vehicle.status == VEHICLE_STATUS['TO_CHARGING']:
                self._handle_charging_arrival(vehicle)
    
    def _handle_pickup_arrival(self, vehicle: Vehicle):
        """Handle arrival at pickup point"""
        if not vehicle.current_task:
            return
        
        order_id = vehicle.current_task.get('order_id')
        if not order_id:
            return
        
        # Pickup passenger
        success = self.order_system.pickup_passenger(
            order_id, vehicle, self.current_time
        )
        
        if success:
            # Update vehicle status (already handled in order_system)
            pass
    
    def _handle_dropoff_arrival(self, vehicle: Vehicle):
        """Handle arrival at destination"""
        if not vehicle.current_task:
            return
        
        order_id = vehicle.current_task.get('order_id')
        if not order_id:
            return
        
        # Complete order
        revenue = self.order_system.complete_order(
            order_id, vehicle, self.current_time
        )
    
    def _handle_charging_arrival(self, vehicle: Vehicle):
        """Handle arrival at charging station"""
        if not vehicle.target_node:
            return
        
        # Get charging station
        station = self.charging_manager.get_station_by_node(vehicle.target_node)
        if not station:
            # No charging station, return to idle status
            vehicle.clear_task()
            vehicle.update_status(VEHICLE_STATUS['IDLE'])
            return
        
        # Request charging
        success = self.charging_manager.request_charging(vehicle, station)
        if not success:
            # Charging station full, return to idle status
            vehicle.clear_task()
            vehicle.update_status(VEHICLE_STATUS['IDLE'])
    
    # ============= Charging Management =============
    def _check_charging_needs(self):
        """Check and handle charging needs"""
        # Check all vehicles
        for vehicle in self.vehicle_manager.get_all_vehicles():
            # Determine if charging is needed
            if not self.charging_manager.should_vehicle_charge(vehicle):
                continue
            
            # Skip if already charging or going to charge
            if vehicle.status in [VEHICLE_STATUS['CHARGING'], VEHICLE_STATUS['TO_CHARGING']]:
                continue
            
            # Don't interrupt if carrying passenger
            if vehicle.has_passenger:
                continue
            
            # Find optimal charging station
            best_station = self.charging_manager.find_optimal_charging_station(vehicle)
            if best_station:
                # Dispatch to charging
                self.vehicle_manager.dispatch_vehicle_to_charging(
                    vehicle, best_station.node_id
                )
        
        # Check fully charged vehicles
        for vehicle in self.vehicle_manager.get_vehicles_by_status(VEHICLE_STATUS['CHARGING']):
            if vehicle.battery_percentage >= 95:  # Stop charging at 95%
                # Stop charging
                self.charging_manager.stop_charging(vehicle)
    
    # ============= Statistics Methods =============
    def get_current_statistics(self) -> Dict:
        """Get current statistics"""
        # Get subsystem statistics
        vehicle_stats = self.vehicle_manager.get_fleet_statistics()
        order_stats = self.order_system.get_statistics()
        charging_stats = self.charging_manager.get_statistics()
        
        return {
            'simulation_time': self.current_time,
            'vehicles': vehicle_stats,
            'orders': order_stats,
            'charging': charging_stats
        }
    
    def get_final_statistics(self) -> Dict:
        """Get final statistics"""
        stats = self.get_current_statistics()
        
        # Add overall statistics
        stats['summary'] = {
            'total_simulation_time': self.current_time,
            'total_revenue': stats['orders']['total_revenue'],
            'total_cost': stats['vehicles']['total_fleet_cost'],
            'total_profit': stats['vehicles']['total_fleet_profit'],
            'order_completion_rate': stats['orders']['completion_rate'],
            'vehicle_utilization_rate': stats['vehicles']['utilization_rate'],
            'charging_utilization_rate': stats['charging']['avg_utilization_rate']
        }
        
        # Calculate detailed statistics for each vehicle
        vehicle_details = []
        for vehicle in self.vehicle_manager.get_all_vehicles():
            vehicle_details.append(vehicle.get_statistics())
        stats['vehicle_details'] = vehicle_details
        
        # Calculate detailed statistics for each charging station
        station_details = []
        for station in self.charging_manager.get_station_list():
            station_details.append(station.get_statistics())
        stats['station_details'] = station_details
        
        return stats
    
    # ============= Data Access Methods =============
    def get_vehicles(self) -> List[Vehicle]:
        """Get all vehicles"""
        return self.vehicle_manager.get_all_vehicles()
    
    def get_orders(self) -> Dict:
        """Get order information"""
        return {
            'pending': self.order_system.get_pending_orders(),
            'active': self.order_system.get_active_orders()
        }
    
    def get_charging_stations(self):
        """Get charging station list"""
=======
"""
Simulation Engine Module
Coordinates all subsystems, manages simulation flow, and handles business logic
"""

import time
from typing import Dict, List, Optional
from core.map_manager import MapManager
from core.vehicle_manager import VehicleManager
from core.order_system import OrderSystem
from core.charging_manager import ChargingManager
from models.vehicle import Vehicle
from config.simulation_config import VEHICLE_STATUS
from utils.geometry import is_point_near_target


class SimulationEngine:
    """Simulation Engine Class"""
    
    def __init__(self, config: Dict):
        """
        Initialize simulation engine
        
        Args:
            config: Simulation configuration parameters
        """
        self.config = config
        self.current_time = 0.0
        self.time_step = config.get('time_step', 0.1)
        
        # Initialize all managers
        print("Initializing simulation engine...")
        
        # 1. Map manager
        print("Loading map...")
        self.map_manager = MapManager(
            location=config.get('location', 'West Lafayette, IN'),
            cache_dir='datasets/maps'
        )
        
        # 2. Vehicle manager
        print("Initializing vehicles...")
        self.vehicle_manager = VehicleManager(self.map_manager, config)
        
        # 3. Order system
        print("Initializing order system...")
        self.order_system = OrderSystem(self.map_manager, config)
        
        # 4. Charging manager
        print("Initializing charging stations...")
        self.charging_manager = ChargingManager(self.map_manager, config)
        
        # Statistics
        self.statistics = {
            'start_time': time.time(),
            'simulation_time': 0.0,
            'total_steps': 0
        }
        
        print("Simulation engine initialization completed!")
    
    # ============= Simulation Main Loop =============
    def run_simulation(self, duration: float) -> Dict:
        """
        Run simulation
        
        Args:
            duration: Simulation duration (seconds)
        
        Returns:
            Simulation result statistics
        """
        print(f"\nStarting simulation, duration: {duration} seconds")
        steps = int(duration / self.time_step)
        
        for step in range(steps):
            self.run_step()
            
            # Print progress periodically
            if step % 100 == 0:
                progress = (step / steps) * 100
                print(f"Simulation progress: {progress:.1f}%")
        
        print("Simulation completed!")
        return self.get_final_statistics()
    
    def run_step(self):
        """Run one simulation step"""
        # 1. Generate new orders
        new_orders = self.order_system.generate_orders(self.current_time, self.time_step)
        
        # 2. Assign orders
        self._assign_orders()
        
        # 3. Update vehicle status
        self.vehicle_manager.update_all_vehicles(self.time_step)
        
        # 4. Handle vehicle arrival events
        self._handle_vehicle_arrivals()
        
        # 5. Update charging progress
        charging_updates = self.charging_manager.update_charging_progress(self.time_step)
        for vehicle_id, charge_amount in charging_updates.items():
            self.vehicle_manager.charge_vehicle(vehicle_id, charge_amount)
        
        # 6. Check charging needs
        self._check_charging_needs()
        
        # 7. Cancel timeout orders
        self.order_system.check_and_cancel_timeout_orders(self.current_time)
        
        # 8. Update time
        self.current_time += self.time_step
        self.statistics['simulation_time'] = self.current_time
        self.statistics['total_steps'] += 1
    
    # ============= Order Assignment Logic =============
    def _assign_orders(self):
        """Assign pending orders"""
        # Get pending orders
        pending_orders = self.order_system.get_pending_orders()
        if not pending_orders:
            return
        
        # Get available vehicles
        available_vehicles = self.vehicle_manager.get_available_vehicles()
        if not available_vehicles:
            return
        
        # Find best vehicle for each order
        for order in pending_orders:
            if not available_vehicles:
                break
            
            # Find best vehicle
            best_vehicle = self.order_system.find_best_vehicle_for_order(
                order.order_id, available_vehicles
            )
            
            if best_vehicle:
                # Assign order
                success = self.order_system.assign_order_to_vehicle(
                    order.order_id, best_vehicle, self.current_time
                )
                
                if success:
                    # Remove from available list
                    available_vehicles.remove(best_vehicle)
    
    # ============= Vehicle Arrival Handling =============
    def _handle_vehicle_arrivals(self):
        """Handle vehicle arrival at destination events"""
        for vehicle in self.vehicle_manager.get_all_vehicles():
            # Check if reached destination
            if not vehicle.has_reached_destination():
                continue
            
            # Handle based on vehicle status
            if vehicle.status == VEHICLE_STATUS['TO_PICKUP']:
                self._handle_pickup_arrival(vehicle)
                
            elif vehicle.status == VEHICLE_STATUS['WITH_PASSENGER']:
                self._handle_dropoff_arrival(vehicle)
                
            elif vehicle.status == VEHICLE_STATUS['TO_CHARGING']:
                self._handle_charging_arrival(vehicle)
    
    def _handle_pickup_arrival(self, vehicle: Vehicle):
        """Handle arrival at pickup point"""
        if not vehicle.current_task:
            return
        
        order_id = vehicle.current_task.get('order_id')
        if not order_id:
            return
        
        # Pickup passenger
        success = self.order_system.pickup_passenger(
            order_id, vehicle, self.current_time
        )
        
        if success:
            # Update vehicle status (already handled in order_system)
            pass
    
    def _handle_dropoff_arrival(self, vehicle: Vehicle):
        """Handle arrival at destination"""
        if not vehicle.current_task:
            return
        
        order_id = vehicle.current_task.get('order_id')
        if not order_id:
            return
        
        # Complete order
        revenue = self.order_system.complete_order(
            order_id, vehicle, self.current_time
        )
    
    def _handle_charging_arrival(self, vehicle: Vehicle):
        """Handle arrival at charging station"""
        if not vehicle.target_node:
            return
        
        # Get charging station
        station = self.charging_manager.get_station_by_node(vehicle.target_node)
        if not station:
            # No charging station, return to idle status
            vehicle.clear_task()
            vehicle.update_status(VEHICLE_STATUS['IDLE'])
            return
        
        # Request charging
        success = self.charging_manager.request_charging(vehicle, station)
        if not success:
            # Charging station full, return to idle status
            vehicle.clear_task()
            vehicle.update_status(VEHICLE_STATUS['IDLE'])
    
    # ============= Charging Management =============
    def _check_charging_needs(self):
        """Check and handle charging needs"""
        # Check all vehicles
        for vehicle in self.vehicle_manager.get_all_vehicles():
            # Determine if charging is needed
            if not self.charging_manager.should_vehicle_charge(vehicle):
                continue
            
            # Skip if already charging or going to charge
            if vehicle.status in [VEHICLE_STATUS['CHARGING'], VEHICLE_STATUS['TO_CHARGING']]:
                continue
            
            # Don't interrupt if carrying passenger
            if vehicle.has_passenger:
                continue
            
            # Find optimal charging station
            best_station = self.charging_manager.find_optimal_charging_station(vehicle)
            if best_station:
                # Dispatch to charging
                self.vehicle_manager.dispatch_vehicle_to_charging(
                    vehicle, best_station.node_id
                )
        
        # Check fully charged vehicles
        for vehicle in self.vehicle_manager.get_vehicles_by_status(VEHICLE_STATUS['CHARGING']):
            if vehicle.battery_percentage >= 95:  # Stop charging at 95%
                # Stop charging
                self.charging_manager.stop_charging(vehicle)
    
    # ============= Statistics Methods =============
    def get_current_statistics(self) -> Dict:
        """Get current statistics"""
        # Get subsystem statistics
        vehicle_stats = self.vehicle_manager.get_fleet_statistics()
        order_stats = self.order_system.get_statistics()
        charging_stats = self.charging_manager.get_statistics()
        
        return {
            'simulation_time': self.current_time,
            'vehicles': vehicle_stats,
            'orders': order_stats,
            'charging': charging_stats
        }
    
    def get_final_statistics(self) -> Dict:
        """Get final statistics"""
        stats = self.get_current_statistics()
        
        # Add overall statistics
        stats['summary'] = {
            'total_simulation_time': self.current_time,
            'total_revenue': stats['orders']['total_revenue'],
            'total_cost': stats['vehicles']['total_fleet_cost'],
            'total_profit': stats['vehicles']['total_fleet_profit'],
            'order_completion_rate': stats['orders']['completion_rate'],
            'vehicle_utilization_rate': stats['vehicles']['utilization_rate'],
            'charging_utilization_rate': stats['charging']['avg_utilization_rate']
        }
        
        # Calculate detailed statistics for each vehicle
        vehicle_details = []
        for vehicle in self.vehicle_manager.get_all_vehicles():
            vehicle_details.append(vehicle.get_statistics())
        stats['vehicle_details'] = vehicle_details
        
        # Calculate detailed statistics for each charging station
        station_details = []
        for station in self.charging_manager.get_station_list():
            station_details.append(station.get_statistics())
        stats['station_details'] = station_details
        
        return stats
    
    # ============= Data Access Methods =============
    def get_vehicles(self) -> List[Vehicle]:
        """Get all vehicles"""
        return self.vehicle_manager.get_all_vehicles()
    
    def get_orders(self) -> Dict:
        """Get order information"""
        return {
            'pending': self.order_system.get_pending_orders(),
            'active': self.order_system.get_active_orders()
        }
    
    def get_charging_stations(self):
        """Get charging station list"""
>>>>>>> b9bd6771fbd7f2273a429016a9b2c009e69bada8
        return self.charging_manager.get_station_list()