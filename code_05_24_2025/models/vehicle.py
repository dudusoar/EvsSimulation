"""
车辆数据模型
定义车辆的数据结构和基本操作
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
import numpy as np
from config.simulation_config import VEHICLE_STATUS


@dataclass
class Vehicle:
    """车辆类，包含车辆的所有状态信息"""
    
    # ============= 基本属性 =============
    vehicle_id: str
    position: Tuple[float, float]  # (x, y) 坐标
    velocity: Tuple[float, float] = (0.0, 0.0)  # (vx, vy) 速度
    
    # ============= 电池相关 =============
    battery_capacity: float = 100.0  # 最大电量（%）
    current_battery: float = 100.0   # 当前电量（%）
    consumption_rate: float = 0.2    # 能耗率（%/km）
    
    # ============= 状态相关 =============
    status: str = VEHICLE_STATUS['IDLE']  # 当前状态
    current_task: Optional[Dict] = None   # 当前任务
    
    # ============= 路径相关 =============
    current_node: Optional[int] = None      # 当前所在节点
    target_node: Optional[int] = None       # 目标节点
    route_nodes: List[int] = field(default_factory=list)      # 路径节点列表
    path_points: List[Tuple[float, float]] = field(default_factory=list)  # 详细路径点
    path_index: int = 0                     # 当前路径点索引
    
    # ============= 统计数据 =============
    total_distance: float = 0.0        # 总行驶距离
    total_orders: int = 0              # 完成订单数
    total_revenue: float = 0.0         # 总收入
    total_charging_cost: float = 0.0   # 总充电成本
    idle_time: float = 0.0             # 空闲时间
    
    # ============= 属性方法 =============
    @property
    def battery_percentage(self) -> float:
        """返回电池百分比"""
        return (self.current_battery / self.battery_capacity) * 100.0
    
    @property
    def is_idle(self) -> bool:
        """判断是否空闲"""
        return self.status == VEHICLE_STATUS['IDLE']
    
    @property
    def is_charging(self) -> bool:
        """判断是否在充电"""
        return self.status == VEHICLE_STATUS['CHARGING']
    
    @property
    def needs_charging(self) -> bool:
        """判断是否需要充电"""
        return self.battery_percentage <= 20.0  # 低于20%需要充电
    
    @property
    def has_passenger(self) -> bool:
        """判断是否载客"""
        return self.status == VEHICLE_STATUS['WITH_PASSENGER']
    
    # ============= 位置更新方法 =============
    def update_position(self, new_position: Tuple[float, float]):
        """更新位置"""
        # 计算移动距离
        dx = new_position[0] - self.position[0]
        dy = new_position[1] - self.position[1]
        distance = np.sqrt(dx**2 + dy**2) / 1000  # 转换为公里
        
        # 更新位置
        self.position = new_position
        
        # 更新统计数据
        self.total_distance += distance
        
        # 消耗电量
        self.consume_battery(distance)
    
    def update_velocity(self, new_velocity: Tuple[float, float]):
        """更新速度"""
        self.velocity = new_velocity
    
    # ============= 电池管理方法 =============
    def consume_battery(self, distance_km: float):
        """消耗电量"""
        consumption = distance_km * self.consumption_rate
        self.current_battery = max(0.0, self.current_battery - consumption)
    
    def charge_battery(self, amount: float):
        """充电"""
        self.current_battery = min(self.battery_capacity, self.current_battery + amount)
    
    def calculate_range(self) -> float:
        """计算剩余续航里程（公里）"""
        if self.consumption_rate > 0:
            return self.current_battery / self.consumption_rate
        return float('inf')
    
    # ============= 任务管理方法 =============
    def assign_task(self, task: Dict):
        """分配任务"""
        self.current_task = task
        
    def clear_task(self):
        """清除任务"""
        self.current_task = None
        self.target_node = None
        self.route_nodes = []
        self.path_points = []
        self.path_index = 0
    
    def update_status(self, new_status: str):
        """更新状态"""
        self.status = new_status
        
    # ============= 路径管理方法 =============
    def set_route(self, route_nodes: List[int], path_points: List[Tuple[float, float]]):
        """设置路径"""
        self.route_nodes = route_nodes
        self.path_points = path_points
        self.path_index = 0
        if route_nodes:
            self.target_node = route_nodes[-1]
    
    def get_next_path_point(self) -> Optional[Tuple[float, float]]:
        """获取下一个路径点"""
        if self.path_index < len(self.path_points):
            return self.path_points[self.path_index]
        return None
    
    def advance_path_index(self):
        """前进到下一个路径点"""
        if self.path_index < len(self.path_points) - 1:
            self.path_index += 1
    
    def has_reached_destination(self) -> bool:
        """判断是否到达目的地"""
        return self.path_index >= len(self.path_points) - 1
    
    # ============= 统计方法 =============
    def complete_order(self, revenue: float):
        """完成订单"""
        self.total_orders += 1
        self.total_revenue += revenue
    
    def add_charging_cost(self, cost: float):
        """添加充电成本"""
        self.total_charging_cost += cost
    
    def add_idle_time(self, time: float):
        """添加空闲时间"""
        self.idle_time += time
    
    def get_profit(self) -> float:
        """计算利润"""
        return self.total_revenue - self.total_charging_cost
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
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