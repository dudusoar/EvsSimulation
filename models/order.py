"""
Order Data Model
Defines order data structure
"""

from dataclasses import dataclass
from typing import Tuple, Optional
import uuid
from config.simulation_config import ORDER_STATUS


@dataclass
class Order:
    """Order class containing all order information"""
    
    # ============= Basic Information =============
    order_id: str = None
    pickup_node: int = None           # Pickup point node ID
    dropoff_node: int = None          # Dropoff point node ID
    pickup_position: Tuple[float, float] = None   # Pickup point coordinates
    dropoff_position: Tuple[float, float] = None  # Dropoff point coordinates
    
    # ============= Time Information =============
    creation_time: float = 0.0        # Creation time
    assignment_time: float = None     # Assignment time
    pickup_time: float = None         # Pickup time
    completion_time: float = None     # Completion time
    
    # ============= Status Information =============
    status: str = ORDER_STATUS['PENDING']  # Order status
    assigned_vehicle_id: Optional[str] = None  # Assigned vehicle ID
    
    # ============= Price Information =============
    estimated_distance: float = 0.0   # Estimated distance (kilometers)
    base_price: float = 0.0          # Base price
    surge_multiplier: float = 1.0    # Dynamic price multiplier
    final_price: float = 0.0         # Final price
    
    def __post_init__(self):
        """Post-initialization processing"""
        if self.order_id is None:
            self.order_id = f"ORDER_{uuid.uuid4().hex[:8]}"
    
    # ============= Status Management Methods =============
    def assign_to_vehicle(self, vehicle_id: str, current_time: float):
        """Assign to vehicle"""
        self.assigned_vehicle_id = vehicle_id
        self.assignment_time = current_time
        self.status = ORDER_STATUS['ASSIGNED']
    
    def pickup_passenger(self, current_time: float):
        """Pick up passenger"""
        self.pickup_time = current_time
        self.status = ORDER_STATUS['PICKED_UP']
    
    def complete_order(self, current_time: float):
        """Complete order"""
        self.completion_time = current_time
        self.status = ORDER_STATUS['COMPLETED']
    
    def cancel_order(self, current_time: float):
        """Cancel order"""
        self.completion_time = current_time
        self.status = ORDER_STATUS['CANCELLED']
    
    # ============= Price Calculation Methods =============
    def calculate_price(self, base_rate: float = 2.0):
        """Calculate price"""
        self.base_price = self.estimated_distance * base_rate
        self.final_price = self.base_price * self.surge_multiplier
        return self.final_price
    
    # ============= Time Calculation Methods =============
    def get_waiting_time(self, current_time: float) -> float:
        """Get waiting time"""
        if self.assignment_time:
            return self.assignment_time - self.creation_time
        return current_time - self.creation_time
    
    def get_pickup_time(self) -> float:
        """Get pickup time duration"""
        if self.pickup_time and self.assignment_time:
            return self.pickup_time - self.assignment_time
        return 0.0
    
    def get_trip_time(self) -> float:
        """Get trip time"""
        if self.completion_time and self.pickup_time:
            return self.completion_time - self.pickup_time
        return 0.0
    
    def get_total_time(self) -> float:
        """Get total time"""
        if self.completion_time:
            return self.completion_time - self.creation_time
        return 0.0
    
    # ============= Information Getter Methods =============
    def is_pending(self) -> bool:
        """Whether waiting for assignment"""
        return self.status == ORDER_STATUS['PENDING']
    
    def is_assigned(self) -> bool:
        """Whether assigned"""
        return self.status == ORDER_STATUS['ASSIGNED']
    
    def is_completed(self) -> bool:
        """Whether completed"""
        return self.status == ORDER_STATUS['COMPLETED']
    
    def get_info(self) -> dict:
        """Get order information"""
        return {
            'order_id': self.order_id,
            'status': self.status,
            'pickup_node': self.pickup_node,
            'dropoff_node': self.dropoff_node,
            'estimated_distance': self.estimated_distance,
            'final_price': self.final_price,
            'waiting_time': self.get_waiting_time(self.completion_time or 0),
            'pickup_time': self.get_pickup_time(),
            'trip_time': self.get_trip_time(),
            'total_time': self.get_total_time()
        }