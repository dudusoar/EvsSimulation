"""
车辆管理模块
负责车辆的创建、更新、调度和统计
整合了原有vehicle.py、vehicle_management.py和vision.py的功能
"""

import random
import numpy as np
from typing import List, Dict, Optional, Tuple
from models.vehicle import Vehicle
from core.map_manager import MapManager
from config.simulation_config import VEHICLE_STATUS
from utils.geometry import calculate_distance, calculate_direction_to_target, is_point_near_target


class VehicleManager:
    """车辆管理器类"""
    
    def __init__(self, map_manager: MapManager, config: Dict):
        """
        初始化车辆管理器
        
        参数:
            map_manager: 地图管理器
            config: 配置参数
        """
        self.map_manager = map_manager
        self.config = config
        
        # 车辆存储
        self.vehicles: Dict[str, Vehicle] = {}  # vehicle_id -> Vehicle
        
        # 速度参数
        self.vehicle_speed = config.get('vehicle_speed_mps', 50/3.6)  # m/s
        self.approach_threshold = 10.0  # 接近目标的阈值（米）
        
        # 初始化车辆
        self._initialize_vehicles()
    
    # ============= 初始化方法 =============
    def _initialize_vehicles(self):
        """初始化车辆"""
        num_vehicles = self.config.get('num_vehicles', 20)
        
        # 随机选择起始位置
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
        
        print(f"初始化了 {len(self.vehicles)} 辆车")
    
    # ============= 车辆更新方法 =============
    def update_all_vehicles(self, dt: float):
        """更新所有车辆状态"""
        for vehicle in self.vehicles.values():
            self._update_vehicle(vehicle, dt)
    
    def _update_vehicle(self, vehicle: Vehicle, dt: float):
        """更新单个车辆"""
        # 根据状态执行不同的更新逻辑
        if vehicle.status == VEHICLE_STATUS['IDLE']:
            # 空闲状态，累计空闲时间
            vehicle.add_idle_time(dt)
            
        elif vehicle.status in [VEHICLE_STATUS['TO_PICKUP'], 
                               VEHICLE_STATUS['WITH_PASSENGER'], 
                               VEHICLE_STATUS['TO_CHARGING']]:
            # 移动状态，更新位置
            self._update_vehicle_movement(vehicle, dt)
            
        elif vehicle.status == VEHICLE_STATUS['CHARGING']:
            # 充电状态，由充电管理器处理
            pass
    
    def _update_vehicle_movement(self, vehicle: Vehicle, dt: float):
        """更新车辆移动"""
        # 检查是否有路径
        if not vehicle.path_points:
            return
        
        # 获取当前目标点
        target_point = vehicle.get_next_path_point()
        if not target_point:
            return
        
        # 检查是否接近当前路径点
        if is_point_near_target(vehicle.position, target_point, self.approach_threshold):
            # 前进到下一个路径点
            vehicle.advance_path_index()
            
            # 检查是否到达终点
            if vehicle.has_reached_destination():
                self._handle_arrival(vehicle)
                return
            
            # 获取新的目标点
            target_point = vehicle.get_next_path_point()
            if not target_point:
                return
        
        # 计算移动方向和速度
        direction = calculate_direction_to_target(vehicle.position, target_point)
        velocity = (direction[0] * self.vehicle_speed, direction[1] * self.vehicle_speed)
        vehicle.update_velocity(velocity)
        
        # 计算新位置
        new_x = vehicle.position[0] + velocity[0] * dt
        new_y = vehicle.position[1] + velocity[1] * dt
        new_position = (new_x, new_y)
        
        # 更新位置（包括电量消耗）
        vehicle.update_position(new_position)
        
        # 更新当前节点（如果接近路径节点）
        if vehicle.route_nodes and vehicle.path_index < len(vehicle.route_nodes):
            current_route_node = vehicle.route_nodes[min(vehicle.path_index, len(vehicle.route_nodes)-1)]
            node_position = self.map_manager.get_node_position(current_route_node)
            if is_point_near_target(vehicle.position, node_position, 50):
                vehicle.current_node = current_route_node
    
    def _handle_arrival(self, vehicle: Vehicle):
        """处理车辆到达目的地"""
        # 这里只处理状态更新，具体业务逻辑由仿真引擎处理
        if vehicle.status == VEHICLE_STATUS['TO_PICKUP']:
            # 到达接客点，等待仿真引擎处理
            pass
        elif vehicle.status == VEHICLE_STATUS['WITH_PASSENGER']:
            # 到达目的地，等待仿真引擎处理
            pass
        elif vehicle.status == VEHICLE_STATUS['TO_CHARGING']:
            # 到达充电站，等待仿真引擎处理
            pass
    
    # ============= 车辆获取方法 =============
    def get_all_vehicles(self) -> List[Vehicle]:
        """获取所有车辆"""
        return list(self.vehicles.values())
    
    def get_vehicle_by_id(self, vehicle_id: str) -> Optional[Vehicle]:
        """根据ID获取车辆"""
        return self.vehicles.get(vehicle_id)
    
    def get_available_vehicles(self) -> List[Vehicle]:
        """获取可用车辆（空闲且电量充足）"""
        available = []
        for vehicle in self.vehicles.values():
            if vehicle.is_idle and not vehicle.needs_charging:
                available.append(vehicle)
        return available
    
    def get_vehicles_by_status(self, status: str) -> List[Vehicle]:
        """根据状态获取车辆"""
        return [v for v in self.vehicles.values() if v.status == status]
    
    def get_low_battery_vehicles(self, threshold: float = 20.0) -> List[Vehicle]:
        """获取低电量车辆"""
        return [v for v in self.vehicles.values() if v.battery_percentage <= threshold]
    
    # ============= 车辆调度方法 =============
    def dispatch_vehicle_to_order(self, vehicle: Vehicle, pickup_node: int, dropoff_node: int):
        """派遣车辆去接订单"""
        # 规划到接客点的路径
        route_nodes = self.map_manager.get_shortest_path_nodes(
            vehicle.current_node, pickup_node
        )
        path_points = self.map_manager.get_shortest_path_points(
            vehicle.current_node, pickup_node
        )
        
        # 设置路径和状态
        vehicle.set_route(route_nodes, path_points)
        vehicle.update_status(VEHICLE_STATUS['TO_PICKUP'])
        vehicle.target_node = pickup_node
    
    def dispatch_vehicle_to_charging(self, vehicle: Vehicle, station_node: int):
        """派遣车辆去充电"""
        # 规划到充电站的路径
        route_nodes = self.map_manager.get_shortest_path_nodes(
            vehicle.current_node, station_node
        )
        path_points = self.map_manager.get_shortest_path_points(
            vehicle.current_node, station_node
        )
        
        # 设置路径和状态
        vehicle.set_route(route_nodes, path_points)
        vehicle.update_status(VEHICLE_STATUS['TO_CHARGING'])
        vehicle.target_node = station_node
        vehicle.assign_task({
            'type': 'charging',
            'target_node': station_node
        })
    
    def update_vehicle_for_passenger_pickup(self, vehicle: Vehicle, dropoff_node: int):
        """更新车辆状态为载客"""
        # 规划到目的地的路径
        route_nodes = self.map_manager.get_shortest_path_nodes(
            vehicle.current_node, dropoff_node
        )
        path_points = self.map_manager.get_shortest_path_points(
            vehicle.current_node, dropoff_node
        )
        
        # 设置路径和状态
        vehicle.set_route(route_nodes, path_points)
        vehicle.update_status(VEHICLE_STATUS['WITH_PASSENGER'])
        vehicle.target_node = dropoff_node
    
    # ============= 电池管理方法 =============
    def charge_vehicle(self, vehicle_id: str, charge_amount: float):
        """给车辆充电"""
        vehicle = self.vehicles.get(vehicle_id)
        if vehicle:
            vehicle.charge_battery(charge_amount)
    
    def get_vehicles_needing_charge(self) -> List[Vehicle]:
        """获取需要充电的车辆"""
        return [v for v in self.vehicles.values() if v.needs_charging and v.is_idle]
    
    # ============= 统计方法 =============
    def get_fleet_statistics(self) -> Dict:
        """获取车队统计信息"""
        vehicles_list = list(self.vehicles.values())
        total_vehicles = len(vehicles_list)
        
        if total_vehicles == 0:
            return {}
        
        # 状态统计
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
        
        # 计算平均值
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