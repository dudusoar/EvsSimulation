"""
订单数据模型
定义订单的数据结构
"""

from dataclasses import dataclass
from typing import Tuple, Optional
import uuid
from config.simulation_config import ORDER_STATUS


@dataclass
class Order:
    """订单类，包含订单的所有信息"""
    
    # ============= 基本信息 =============
    order_id: str = None
    pickup_node: int = None           # 上车点节点ID
    dropoff_node: int = None          # 下车点节点ID
    pickup_position: Tuple[float, float] = None   # 上车点坐标
    dropoff_position: Tuple[float, float] = None  # 下车点坐标
    
    # ============= 时间信息 =============
    creation_time: float = 0.0        # 创建时间
    assignment_time: float = None     # 分配时间
    pickup_time: float = None         # 上车时间
    completion_time: float = None     # 完成时间
    
    # ============= 状态信息 =============
    status: str = ORDER_STATUS['PENDING']  # 订单状态
    assigned_vehicle_id: Optional[str] = None  # 分配的车辆ID
    
    # ============= 价格信息 =============
    estimated_distance: float = 0.0   # 预估距离（公里）
    base_price: float = 0.0          # 基础价格
    surge_multiplier: float = 1.0    # 动态价格倍数
    final_price: float = 0.0         # 最终价格
    
    def __post_init__(self):
        """初始化后处理"""
        if self.order_id is None:
            self.order_id = f"ORDER_{uuid.uuid4().hex[:8]}"
    
    # ============= 状态管理方法 =============
    def assign_to_vehicle(self, vehicle_id: str, current_time: float):
        """分配给车辆"""
        self.assigned_vehicle_id = vehicle_id
        self.assignment_time = current_time
        self.status = ORDER_STATUS['ASSIGNED']
    
    def pickup_passenger(self, current_time: float):
        """接到乘客"""
        self.pickup_time = current_time
        self.status = ORDER_STATUS['PICKED_UP']
    
    def complete_order(self, current_time: float):
        """完成订单"""
        self.completion_time = current_time
        self.status = ORDER_STATUS['COMPLETED']
    
    def cancel_order(self, current_time: float):
        """取消订单"""
        self.completion_time = current_time
        self.status = ORDER_STATUS['CANCELLED']
    
    # ============= 价格计算方法 =============
    def calculate_price(self, base_rate: float = 2.0):
        """计算价格"""
        self.base_price = self.estimated_distance * base_rate
        self.final_price = self.base_price * self.surge_multiplier
        return self.final_price
    
    # ============= 时间计算方法 =============
    def get_waiting_time(self, current_time: float) -> float:
        """获取等待时间"""
        if self.assignment_time:
            return self.assignment_time - self.creation_time
        return current_time - self.creation_time
    
    def get_pickup_time(self) -> float:
        """获取接客用时"""
        if self.pickup_time and self.assignment_time:
            return self.pickup_time - self.assignment_time
        return 0.0
    
    def get_trip_time(self) -> float:
        """获取行程时间"""
        if self.completion_time and self.pickup_time:
            return self.completion_time - self.pickup_time
        return 0.0
    
    def get_total_time(self) -> float:
        """获取总时间"""
        if self.completion_time:
            return self.completion_time - self.creation_time
        return 0.0
    
    # ============= 信息获取方法 =============
    def is_pending(self) -> bool:
        """是否等待分配"""
        return self.status == ORDER_STATUS['PENDING']
    
    def is_assigned(self) -> bool:
        """是否已分配"""
        return self.status == ORDER_STATUS['ASSIGNED']
    
    def is_completed(self) -> bool:
        """是否已完成"""
        return self.status == ORDER_STATUS['COMPLETED']
    
    def get_info(self) -> dict:
        """获取订单信息"""
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