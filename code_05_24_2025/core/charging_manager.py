"""
充电管理模块
负责充电站的管理、充电调度和充电过程控制
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
from models.charging_station import ChargingStation
from models.vehicle import Vehicle
from core.map_manager import MapManager
from config.simulation_config import VEHICLE_STATUS
from utils.geometry import calculate_distance


class ChargingManager:
    """充电管理器类"""
    
    def __init__(self, map_manager: MapManager, config: Dict):
        """
        初始化充电管理器
        
        参数:
            map_manager: 地图管理器
            config: 配置参数
        """
        self.map_manager = map_manager
        self.config = config
        
        # 充电站
        self.charging_stations: Dict[str, ChargingStation] = {}  # station_id -> ChargingStation
        self.node_to_station: Dict[int, str] = {}  # node_id -> station_id 映射
        
        # 充电参数
        self.charging_rate = config.get('charging_rate', 1.0)  # %/秒
        self.charging_threshold = config.get('charging_threshold', 20.0)  # %
        
        # 初始化充电站
        self._initialize_charging_stations()
    
    # ============= 初始化方法 =============
    def _initialize_charging_stations(self):
        """初始化充电站"""
        num_stations = self.config.get('num_charging_stations', 5)
        slots_per_station = self.config.get('charging_slots_per_station', 3)
        
        # 选择充电站位置
        station_nodes = self.map_manager.select_charging_station_nodes(num_stations)
        
        # 创建充电站
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
        
        print(f"初始化了 {len(self.charging_stations)} 个充电站")
    
    # ============= 充电站查找方法 =============
    def find_nearest_available_station(self, position: Tuple[float, float]) -> Optional[ChargingStation]:
        """找到最近的可用充电站"""
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
        为车辆找到最优充电站
        考虑距离、可用性和排队情况
        """
        if not vehicle.current_node:
            return None
        
        vehicle_pos = self.map_manager.get_node_position(vehicle.current_node)
        
        # 计算每个充电站的评分
        best_station = None
        min_score = float('inf')
        
        for station in self.charging_stations.values():
            if not station.has_available_slot():
                continue
            
            # 计算距离
            distance = self.map_manager.calculate_route_distance(
                vehicle.current_node, station.node_id
            )
            
            # 计算评分：距离 + 排队惩罚
            utilization_penalty = station.get_utilization_rate() * 1000
            score = distance + utilization_penalty
            
            if score < min_score:
                min_score = score
                best_station = station
        
        return best_station
    
    def get_station_by_node(self, node_id: int) -> Optional[ChargingStation]:
        """根据节点ID获取充电站"""
        station_id = self.node_to_station.get(node_id)
        if station_id:
            return self.charging_stations.get(station_id)
        return None
    
    # ============= 充电控制方法 =============
    def request_charging(self, vehicle: Vehicle, station: ChargingStation) -> bool:
        """
        请求充电
        
        参数:
            vehicle: 车辆对象
            station: 充电站对象
        
        返回:
            是否成功开始充电
        """
        # 检查充电站是否有空位
        if not station.has_available_slot():
            return False
        
        # 开始充电
        if station.start_charging(vehicle.vehicle_id):
            vehicle.update_status(VEHICLE_STATUS['CHARGING'])
            return True
        
        return False
    
    def stop_charging(self, vehicle: Vehicle) -> Tuple[float, float]:
        """
        停止充电
        
        参数:
            vehicle: 车辆对象
        
        返回:
            (充电量, 充电费用)
        """
        # 找到车辆所在的充电站
        station = None
        for s in self.charging_stations.values():
            if s.is_vehicle_charging(vehicle.vehicle_id):
                station = s
                break
        
        if not station:
            return 0.0, 0.0
        
        # 计算充电量和费用
        charge_amount = vehicle.current_battery - (vehicle.battery_capacity - 100.0)  # 充了多少
        if charge_amount < 0:
            charge_amount = 0
        
        # 计算费用
        cost = station.calculate_charging_cost(charge_amount)
        
        # 停止充电
        station.stop_charging(vehicle.vehicle_id)
        
        # 更新车辆状态
        vehicle.update_status(VEHICLE_STATUS['IDLE'])
        vehicle.add_charging_cost(cost)
        
        return charge_amount, cost
    
    def update_charging_progress(self, dt: float) -> Dict[str, float]:
        """
        更新所有充电中车辆的充电进度
        
        参数:
            dt: 时间步长
        
        返回:
            {vehicle_id: charge_amount} 字典
        """
        charging_updates = {}
        
        for station in self.charging_stations.values():
            # 计算这个时间步的充电量
            charge_amount = station.calculate_charge_amount(dt)
            
            # 更新每辆充电中的车辆
            for vehicle_id in list(station.charging_vehicles):  # 复制列表以避免修改时出错
                charging_updates[vehicle_id] = charge_amount
        
        return charging_updates
    
    def should_vehicle_charge(self, vehicle: Vehicle) -> bool:
        """
        判断车辆是否应该去充电
        
        参数:
            vehicle: 车辆对象
        
        返回:
            是否应该充电
        """
        # 如果正在执行订单，不充电
        if vehicle.has_passenger:
            return False
        
        # 如果电量低于阈值，应该充电
        if vehicle.battery_percentage <= self.charging_threshold:
            return True
        
        # 如果电量较低且当前空闲，考虑充电
        if vehicle.is_idle and vehicle.battery_percentage <= 40:
            return True
        
        return False
    
    # ============= 统计方法 =============
    def get_statistics(self) -> Dict:
        """获取充电系统统计信息"""
        total_stations = len(self.charging_stations)
        total_slots = sum(s.total_slots for s in self.charging_stations.values())
        occupied_slots = sum(s.occupied_slots for s in self.charging_stations.values())
        total_energy = sum(s.total_energy_delivered for s in self.charging_stations.values())
        total_revenue = sum(s.total_revenue for s in self.charging_stations.values())
        total_vehicles_served = sum(s.total_vehicles_served for s in self.charging_stations.values())
        
        # 计算平均利用率
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
        """获取所有充电站列表"""
        return list(self.charging_stations.values())
    
    def get_busy_stations(self) -> List[ChargingStation]:
        """获取繁忙的充电站（利用率>80%）"""
        busy_stations = []
        for station in self.charging_stations.values():
            if station.get_utilization_rate() > 0.8:
                busy_stations.append(station)
        return busy_stations