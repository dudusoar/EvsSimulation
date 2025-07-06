"""
Order System Module
Responsible for order generation, assignment, management and statistics
"""

import random
import numpy as np
from typing import List, Dict, Optional, Tuple
from models.order import Order
from models.vehicle import Vehicle
from core.map_manager import MapManager
from config.simulation_config import ORDER_STATUS, VEHICLE_STATUS
from utils.geometry import calculate_distance


class OrderSystem:
    """Order System Class"""

    # Model (R): Initializes the OrderSystem class by creating a dictionary to map order ids to the order, a list for pending orders, 
    # and stats to indentify the orders created, completed, cancelled, and total revenue. Moreover, it to generate the orders, this 
    # function specifies the order generation rate, price/km, surge multiplier and max waiting time.
    #
    # Inputs: map_manager (Object of MapManager class) -> Provides map info
    # Outputs: None
    
    def __init__(self, map_manager: MapManager, config: Dict):
        """
        Initialize order system
        
        Args:
            map_manager: Map manager
            config: Configuration parameters
        """
        self.map_manager = map_manager
        self.config = config
        
        # Order storage
        self.orders: Dict[str, Order] = {}  # order_id -> Order
        self.pending_orders: List[str] = []  # List of pending order IDs
        
        # Statistics
        self.total_orders_created = 0
        self.total_orders_completed = 0
        self.total_orders_cancelled = 0
        self.total_revenue = 0.0
        
        # Order generation parameters
        self.base_generation_rate = config.get('order_generation_rate', 5) / 3600  # Convert to per second
        self.base_price_per_km = config.get('base_price_per_km', 2.0)
        self.surge_multiplier = config.get('surge_multiplier', 1.5) #During high traffic time
        self.max_waiting_time = config.get('max_waiting_time', 600)
        
        # Pre-generate initial orders to ensure simulation starts with orders!
        self._generate_initial_orders()

    # Model (R): Generates orders that will be found at the start of the simulation. 
    #
    # Inputs: None
    # Outputs: None
    
    def _generate_initial_orders(self):
        """Pre-generate initial orders to ensure simulation starts with available orders"""
        print("Pre-generating initial orders...")
        # Reset global order counter for new simulation
        from models.order import _global_order_counter
        import models.order
        models.order._global_order_counter = 0
        
        # Generate initial orders based on vehicle count to ensure sufficient workload
        num_vehicles = self.config.get('num_vehicles', 20)
        initial_order_count = min(num_vehicles // 2, 10)  # Generate half the number of vehicles, max 10
        
        orders_generated = 0
        attempts = 0
        max_attempts = initial_order_count * 3  # Avoid infinite loop
        
        while orders_generated < initial_order_count and attempts < max_attempts:
            attempts += 1
            order = self._create_random_order(0.0)  # Set time to 0
            if order:
                self.orders[order.order_id] = order
                self.pending_orders.append(order.order_id)
                self.total_orders_created += 1
                orders_generated += 1
        
        print(f"Pre-generated {orders_generated} initial orders")
    
    # ============= Order Generation Methods =============

    # Model (R): Generates orders additional to the initialized orders. Creates an expected number of orders based on the time step
    # to then draw an int using a poisson distribution 
    #
    # Input: current_time (float), dt(float) -> time step 
    # Output: new_orders (List[Orders])

    def generate_orders(self, current_time: float, dt: float) -> List[Order]:
        """
        Generate new orders based on current time and demand
        
        Args:
            current_time: Current simulation time
            dt: Time step
        
        Returns:
            List of newly generated orders
        """
        # Calculate number of orders to generate for this time step (Poisson process)
        expected_orders = self.base_generation_rate * dt
        num_orders = np.random.poisson(expected_orders)
        
        new_orders = []
        for _ in range(num_orders):
            order = self._create_random_order(current_time)
            if order:
                self.orders[order.order_id] = order
                self.pending_orders.append(order.order_id)
                self.total_orders_created += 1
                new_orders.append(order)
        
        return new_orders
    
    # Model: Creates a random order by drawing two random nodes to traverse across from the map and specifies order details:
    # pickup node and pos, dropoff node and pos, distance, current time, surge multiplier, and finally calculates total price.
    #
    # Input: current_time (float)
    # Output: order (object of Order Class) or None
    
    def _create_random_order(self, current_time: float) -> Optional[Order]:
        """Create a random order"""
        # Randomly select origin and destination
        nodes = self.map_manager.get_random_nodes(2)
        if len(nodes) < 2: #if less than 2 nodes in map, not possible to create an order
            return None
        
        pickup_node = nodes[0]
        dropoff_node = nodes[1]
        
        # Get position coordinates
        pickup_pos = self.map_manager.get_node_position(pickup_node)
        dropoff_pos = self.map_manager.get_node_position(dropoff_node)
        
        # Calculate distance
        distance_km = self.map_manager.calculate_route_distance(pickup_node, dropoff_node) / 1000
        
        # Skip orders that are too short
        if distance_km < 0.5:
            return None
        
        # Create order
        order = Order(
            pickup_node=pickup_node,
            dropoff_node=dropoff_node,
            pickup_position=pickup_pos,
            dropoff_position=dropoff_pos,
            creation_time=current_time,
            estimated_distance=distance_km,
            surge_multiplier=self._calculate_surge_multiplier(current_time) #higher price for high traffic time
        )
        
        # Calculate price
        order.calculate_price(self.base_price_per_km)
        
        return order
    
    # Model (R): Calculates how much more the bas price is based on the time
    # 
    # Input: current_time(float)
    # Output: self.surge_multiplier(float) or 1.0
    
    def _calculate_surge_multiplier(self, current_time: float) -> float:
        """
        Calculate dynamic price multiplier
        Can be adjusted based on time, supply-demand relationship, etc.
        """
        # Simple time-based surge pricing
        hour = (current_time / 3600) % 24
        
        # Peak hours surcharge
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            return self.surge_multiplier
        
        return 1.0
    
    # ============= Order Assignment Methods =============

    # Test: assigns the order to an EV by getting the vehicle closest by distance to the pick up point. No assignmnent if the order
    # does not have an id in the orders list, not pending, or <0.5 km
    #
    # Inputs: order_id (str), vehicle (object of Vehicle Class), current_time (float)
    # Outputs: Whether or not the order was successfully assigned to an EV (bool)
    def assign_order_to_vehicle(self, order_id: str, vehicle: Vehicle, current_time: float) -> bool:
        """
        Assign order to vehicle
        
        Args:
            order_id: Order ID
            vehicle: Vehicle object
            current_time: Current time
        
        Returns:
            Whether assignment was successful
        """
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        
        # Check order status
        if not order.is_pending(): #if not pending then no need to assign
            return False
        
        # Assign order
        order.assign_to_vehicle(vehicle.vehicle_id, current_time)
        
        # Remove from pending list
        if order_id in self.pending_orders:
            self.pending_orders.remove(order_id)
        
        # Update vehicle task
        vehicle.assign_task({
            'type': 'order',
            'order_id': order_id,
            'target_node': order.pickup_node,
            'pickup_node': order.pickup_node,
            'dropoff_node': order.dropoff_node
        })
        
        # Plan route to pickup point
        route_nodes = self.map_manager.get_shortest_path_nodes(
            vehicle.current_node, order.pickup_node
        )
        path_points = self.map_manager.get_shortest_path_points(
            vehicle.current_node, order.pickup_node
        )
        
        vehicle.set_route(route_nodes, path_points)
        vehicle.update_status(VEHICLE_STATUS['TO_PICKUP'])
        
        return True
    
    
    
    def find_best_vehicle_for_order(self, order_id: str, available_vehicles: List[Vehicle]) -> Optional[Vehicle]:
        """
        Find best vehicle for order
        Based on distance, battery level and other factors
        """
        if order_id not in self.orders or not available_vehicles:
            return None
        
        order = self.orders[order_id]
        best_vehicle = None
        min_score = float('inf')
        
        for vehicle in available_vehicles:
            # Calculate distance to pickup point
            distance = self.map_manager.calculate_route_distance(
                vehicle.current_node, order.pickup_node
            )
            
            # Calculate score (considering distance and battery)
            # Vehicles with insufficient battery get higher score (less priority)
            battery_penalty = 0 if vehicle.battery_percentage > 50 else 1000
            score = distance + battery_penalty
            
            if score < min_score:
                min_score = score
                best_vehicle = vehicle
        
        return best_vehicle
    
    # ============= Order Status Update Methods =============
    def pickup_passenger(self, order_id: str, vehicle: Vehicle, current_time: float) -> bool:
        """
        Handle passenger pickup
        
        Args:
            order_id: Order ID
            vehicle: Vehicle object
            current_time: Current time
        
        Returns:
            Whether successful
        """
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        
        # Update order status
        order.pickup_passenger(current_time)
        
        # Update vehicle status and route (to destination)
        vehicle.update_status(VEHICLE_STATUS['WITH_PASSENGER'])
        
        # Plan route to destination
        route_nodes = self.map_manager.get_shortest_path_nodes(
            order.pickup_node, order.dropoff_node
        )
        path_points = self.map_manager.get_shortest_path_points(
            order.pickup_node, order.dropoff_node
        )
        
        vehicle.set_route(route_nodes, path_points)
        vehicle.current_task['target_node'] = order.dropoff_node
        
        return True
    
    def complete_order(self, order_id: str, vehicle: Vehicle, current_time: float) -> float:
        """
        Complete order
        
        Args:
            order_id: Order ID
            vehicle: Vehicle object
            current_time: Current time
        
        Returns:
            Order revenue
        """
        if order_id not in self.orders:
            return 0.0
        
        order = self.orders[order_id]
        
        # Update order status
        order.complete_order(current_time)
        
        # Update statistics
        self.total_orders_completed += 1
        self.total_revenue += order.final_price
        
        # Update vehicle statistics
        vehicle.complete_order(order.final_price)
        
        # Clear vehicle task
        vehicle.clear_task()
        vehicle.update_status(VEHICLE_STATUS['IDLE'])
        
        return order.final_price
    
    def cancel_order(self, order_id: str, current_time: float):
        """Cancel order (timeout without pickup)"""
        if order_id not in self.orders:
            return
        
        order = self.orders[order_id]
        order.cancel_order(current_time)
        
        # Remove from pending list
        if order_id in self.pending_orders:
            self.pending_orders.remove(order_id)
        
        self.total_orders_cancelled += 1
    
    # ============= Order Management Methods =============
    def check_and_cancel_timeout_orders(self, current_time: float):
        """Check and cancel timeout orders"""
        timeout_orders = []
        
        for order_id in self.pending_orders[:]:  # Copy list to avoid modification during iteration
            order = self.orders[order_id]
            waiting_time = current_time - order.creation_time
            
            if waiting_time > self.max_waiting_time:
                timeout_orders.append(order_id)
                self.cancel_order(order_id, current_time)
        
        return timeout_orders
    
    def get_pending_orders(self) -> List[Order]:
        """Get all pending orders"""
        return [self.orders[order_id] for order_id in self.pending_orders]
    
    def get_order_by_id(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        return self.orders.get(order_id)
    
    def get_active_orders(self) -> List[Order]:
        """Get all active orders (assigned but not completed)"""
        active_orders = []
        for order in self.orders.values():
            if order.status in [ORDER_STATUS['ASSIGNED'], ORDER_STATUS['PICKED_UP']]:
                active_orders.append(order)
        return active_orders
    
    # ============= Statistics Methods =============
    def get_statistics(self) -> Dict:
        """Get order system statistics"""
        completed_orders = [o for o in self.orders.values() if o.is_completed()]
        
        if completed_orders:
            avg_waiting_time = np.mean([o.get_waiting_time(o.completion_time) for o in completed_orders])
            avg_pickup_time = np.mean([o.get_pickup_time() for o in completed_orders])
            avg_trip_time = np.mean([o.get_trip_time() for o in completed_orders])
            avg_total_time = np.mean([o.get_total_time() for o in completed_orders])
            avg_price = np.mean([o.final_price for o in completed_orders])
        else:
            avg_waiting_time = avg_pickup_time = avg_trip_time = avg_total_time = avg_price = 0
        
        return {
            'total_orders_created': self.total_orders_created,
            'total_orders_completed': self.total_orders_completed,
            'total_orders_cancelled': self.total_orders_cancelled,
            'pending_orders': len(self.pending_orders),
            'active_orders': len(self.get_active_orders()),
            'total_revenue': self.total_revenue,
            'completion_rate': self.total_orders_completed / max(1, self.total_orders_created),
            'cancellation_rate': self.total_orders_cancelled / max(1, self.total_orders_created),
            'avg_waiting_time': avg_waiting_time,
            'avg_pickup_time': avg_pickup_time,
            'avg_trip_time': avg_trip_time,
            'avg_total_time': avg_total_time,
            'avg_price': avg_price
        }
    
    def get_order_distribution(self) -> Dict[str, int]:
        """Get order status distribution"""
        distribution = {
            'pending': 0,
            'assigned': 0,
            'picked_up': 0,
            'completed': 0,
            'cancelled': 0
        }
        
        for order in self.orders.values():
            if order.status == ORDER_STATUS['PENDING']:
                distribution['pending'] += 1
            elif order.status == ORDER_STATUS['ASSIGNED']:
                distribution['assigned'] += 1
            elif order.status == ORDER_STATUS['PICKED_UP']:
                distribution['picked_up'] += 1
            elif order.status == ORDER_STATUS['COMPLETED']:
                distribution['completed'] += 1
            elif order.status == ORDER_STATUS['CANCELLED']:
                distribution['cancelled'] += 1
        
        return distribution