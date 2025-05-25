"""
充电站数据模型
定义充电站的数据结构
"""

from dataclasses import dataclass, field
from typing import Tuple, List, Set
import uuid


@dataclass
class ChargingStation:
    """充电站类，包含充电站的所有信息"""
    
    # ============= 基本信息 =============
    station_id: str = None
    node_id: int = None                      # 所在节点ID
    position: Tuple[float, float] = None     # 位置坐标
    
    # ============= 充电参数 =============
    total_slots: int = 3                     # 总充电位数
    charging_power: float = 50.0             # 充电功率（kW）
    charging_rate: float = 1.0               # 充电速率（%/秒）
    electricity_price: float = 0.8           # 电价（元/kWh）
    
    # ============= 状态信息 =============
    occupied_slots: int = 0                  # 已占用充电位数
    charging_vehicles: Set[str] = field(default_factory=set)  # 正在充电的车辆ID集合
    
    # ============= 统计信息 =============
    total_energy_delivered: float = 0.0      # 总供电量（kWh）
    total_revenue: float = 0.0               # 总收入
    total_vehicles_served: int = 0           # 服务车辆总数
    
    def __post_init__(self):
        """初始化后处理"""
        if self.station_id is None:
            self.station_id = f"STATION_{uuid.uuid4().hex[:8]}"
    
    # ============= 充电位管理方法 =============
    @property
    def available_slots(self) -> int:
        """获取可用充电位数"""
        return self.total_slots - self.occupied_slots
    
    def has_available_slot(self) -> bool:
        """是否有可用充电位"""
        return self.available_slots > 0
    
    def is_full(self) -> bool:
        """是否已满"""
        return self.occupied_slots >= self.total_slots
    
    def get_utilization_rate(self) -> float:
        """获取利用率"""
        if self.total_slots > 0:
            return self.occupied_slots / self.total_slots
        return 0.0
    
    # ============= 车辆充电管理方法 =============
    def start_charging(self, vehicle_id: str) -> bool:
        """开始充电"""
        if self.has_available_slot() and vehicle_id not in self.charging_vehicles:
            self.charging_vehicles.add(vehicle_id)
            self.occupied_slots += 1
            self.total_vehicles_served += 1
            return True
        return False
    
    def stop_charging(self, vehicle_id: str) -> bool:
        """停止充电"""
        if vehicle_id in self.charging_vehicles:
            self.charging_vehicles.remove(vehicle_id)
            self.occupied_slots -= 1
            return True
        return False
    
    def is_vehicle_charging(self, vehicle_id: str) -> bool:
        """检查车辆是否在充电"""
        return vehicle_id in self.charging_vehicles
    
    # ============= 充电计算方法 =============
    def calculate_charge_amount(self, duration: float) -> float:
        """计算充电量（电池百分比）"""
        return self.charging_rate * duration
    
    def calculate_energy_consumed(self, charge_percentage: float, battery_capacity: float = 100.0) -> float:
        """计算消耗的电能（kWh）"""
        # 假设100%电池容量对应50kWh
        kwh_per_percent = 0.5
        return charge_percentage * kwh_per_percent
    
    def calculate_charging_cost(self, charge_percentage: float, battery_capacity: float = 100.0) -> float:
        """计算充电费用"""
        energy_kwh = self.calculate_energy_consumed(charge_percentage, battery_capacity)
        cost = energy_kwh * self.electricity_price
        
        # 更新统计信息
        self.total_energy_delivered += energy_kwh
        self.total_revenue += cost
        
        return cost
    
    # ============= 信息获取方法 =============
    def get_info(self) -> dict:
        """获取充电站信息"""
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
        """获取统计信息"""
        return {
            'station_id': self.station_id,
            'utilization_rate': self.get_utilization_rate(),
            'total_energy_delivered': self.total_energy_delivered,
            'total_revenue': self.total_revenue,
            'total_vehicles_served': self.total_vehicles_served,
            'average_revenue_per_vehicle': self.total_revenue / max(1, self.total_vehicles_served)
        }