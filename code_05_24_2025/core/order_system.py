"""
订单系统模块
负责订单的生成、分配、管理和统计
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
    """订单系统类"""
    
    def __init__(self, map_manager: MapManager, config: Dict):
        """
        初始化订单系统
        
        参数:
            map_manager: 地图管理器
            config: 配置参数
        """
        self.map_manager = map_manager
        self.config = config
        
        # 订单存储
        self.orders: Dict[str, Order] = {}  # order_id -> Order
        self.pending_orders: List[str] = []  # 等待分配的订单ID列表
        
        # 统计信息
        self.total_orders_created = 0
        self.total_orders_completed = 0
        self.total_orders_cancelled = 0
        self.total_revenue = 0.0
        
        # 订单生成参数
        self.base_generation_rate = config.get('order_generation_rate', 5) / 3600  # 转换为每秒
        self.base_price_per_km = config.get('base_price_per_km', 2.0)
        self.surge_multiplier = config.get('surge_multiplier', 1.5)
        self.max_waiting_time = config.get('max_waiting_time', 600)
        
        # 预生成初始订单，确保仿真开始就有订单！
        self._generate_initial_orders()
    
    def _generate_initial_orders(self):
        """预生成初始订单，确保仿真开始就有订单可用"""
        print("预生成初始订单...")
        # 根据车辆数量生成初始订单，确保有足够的工作量
        num_vehicles = self.config.get('num_vehicles', 20)
        initial_order_count = min(num_vehicles // 2, 10)  # 生成车辆数一半的订单，最多10个
        
        orders_generated = 0
        attempts = 0
        max_attempts = initial_order_count * 3  # 避免无限循环
        
        while orders_generated < initial_order_count and attempts < max_attempts:
            attempts += 1
            order = self._create_random_order(0.0)  # 时间设为0
            if order:
                self.orders[order.order_id] = order
                self.pending_orders.append(order.order_id)
                self.total_orders_created += 1
                orders_generated += 1
        
        print(f"预生成了 {orders_generated} 个初始订单")
    
    # ============= 订单生成方法 =============
    def generate_orders(self, current_time: float, dt: float) -> List[Order]:
        """
        根据当前时间和需求生成新订单
        
        参数:
            current_time: 当前仿真时间
            dt: 时间步长
        
        返回:
            新生成的订单列表
        """
        # 计算这个时间步应该生成的订单数（泊松过程）
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
    
    def _create_random_order(self, current_time: float) -> Optional[Order]:
        """创建一个随机订单"""
        # 随机选择起点和终点
        nodes = self.map_manager.get_random_nodes(2)
        if len(nodes) < 2:
            return None
        
        pickup_node = nodes[0]
        dropoff_node = nodes[1]
        
        # 获取位置坐标
        pickup_pos = self.map_manager.get_node_position(pickup_node)
        dropoff_pos = self.map_manager.get_node_position(dropoff_node)
        
        # 计算距离
        distance_km = self.map_manager.calculate_route_distance(pickup_node, dropoff_node) / 1000
        
        # 跳过太短的订单
        if distance_km < 0.5:
            return None
        
        # 创建订单
        order = Order(
            pickup_node=pickup_node,
            dropoff_node=dropoff_node,
            pickup_position=pickup_pos,
            dropoff_position=dropoff_pos,
            creation_time=current_time,
            estimated_distance=distance_km,
            surge_multiplier=self._calculate_surge_multiplier(current_time)
        )
        
        # 计算价格
        order.calculate_price(self.base_price_per_km)
        
        return order
    
    def _calculate_surge_multiplier(self, current_time: float) -> float:
        """
        计算动态价格倍数
        可以根据时间、供需关系等因素调整
        """
        # 简单的时间based surge pricing
        hour = (current_time / 3600) % 24
        
        # 早晚高峰时段加价
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            return self.surge_multiplier
        
        return 1.0
    
    # ============= 订单分配方法 =============
    def assign_order_to_vehicle(self, order_id: str, vehicle: Vehicle, current_time: float) -> bool:
        """
        将订单分配给车辆
        
        参数:
            order_id: 订单ID
            vehicle: 车辆对象
            current_time: 当前时间
        
        返回:
            是否分配成功
        """
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        
        # 检查订单状态
        if not order.is_pending():
            return False
        
        # 分配订单
        order.assign_to_vehicle(vehicle.vehicle_id, current_time)
        
        # 从待分配列表中移除
        if order_id in self.pending_orders:
            self.pending_orders.remove(order_id)
        
        # 更新车辆任务
        vehicle.assign_task({
            'type': 'order',
            'order_id': order_id,
            'target_node': order.pickup_node,
            'pickup_node': order.pickup_node,
            'dropoff_node': order.dropoff_node
        })
        
        # 规划路径到接客点
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
        为订单找到最佳车辆
        基于距离、电量等因素
        """
        if order_id not in self.orders or not available_vehicles:
            return None
        
        order = self.orders[order_id]
        best_vehicle = None
        min_score = float('inf')
        
        for vehicle in available_vehicles:
            # 计算到接客点的距离
            distance = self.map_manager.calculate_route_distance(
                vehicle.current_node, order.pickup_node
            )
            
            # 计算评分（考虑距离和电量）
            # 电量不足的车辆得分更高（不优先选择）
            battery_penalty = 0 if vehicle.battery_percentage > 50 else 1000
            score = distance + battery_penalty
            
            if score < min_score:
                min_score = score
                best_vehicle = vehicle
        
        return best_vehicle
    
    # ============= 订单状态更新方法 =============
    def pickup_passenger(self, order_id: str, vehicle: Vehicle, current_time: float) -> bool:
        """
        接客处理
        
        参数:
            order_id: 订单ID
            vehicle: 车辆对象
            current_time: 当前时间
        
        返回:
            是否成功
        """
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        
        # 更新订单状态
        order.pickup_passenger(current_time)
        
        # 更新车辆状态和路径（前往目的地）
        vehicle.update_status(VEHICLE_STATUS['WITH_PASSENGER'])
        
        # 规划到目的地的路径
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
        完成订单
        
        参数:
            order_id: 订单ID
            vehicle: 车辆对象
            current_time: 当前时间
        
        返回:
            订单收入
        """
        if order_id not in self.orders:
            return 0.0
        
        order = self.orders[order_id]
        
        # 更新订单状态
        order.complete_order(current_time)
        
        # 更新统计信息
        self.total_orders_completed += 1
        self.total_revenue += order.final_price
        
        # 更新车辆统计
        vehicle.complete_order(order.final_price)
        
        # 清空车辆任务
        vehicle.clear_task()
        vehicle.update_status(VEHICLE_STATUS['IDLE'])
        
        return order.final_price
    
    def cancel_order(self, order_id: str, current_time: float):
        """取消订单（超时未接客）"""
        if order_id not in self.orders:
            return
        
        order = self.orders[order_id]
        order.cancel_order(current_time)
        
        # 从待分配列表中移除
        if order_id in self.pending_orders:
            self.pending_orders.remove(order_id)
        
        self.total_orders_cancelled += 1
    
    # ============= 订单管理方法 =============
    def check_and_cancel_timeout_orders(self, current_time: float):
        """检查并取消超时的订单"""
        timeout_orders = []
        
        for order_id in self.pending_orders[:]:  # 复制列表以避免迭代时修改
            order = self.orders[order_id]
            waiting_time = current_time - order.creation_time
            
            if waiting_time > self.max_waiting_time:
                timeout_orders.append(order_id)
                self.cancel_order(order_id, current_time)
        
        return timeout_orders
    
    def get_pending_orders(self) -> List[Order]:
        """获取所有待分配订单"""
        return [self.orders[order_id] for order_id in self.pending_orders]
    
    def get_order_by_id(self, order_id: str) -> Optional[Order]:
        """根据ID获取订单"""
        return self.orders.get(order_id)
    
    def get_active_orders(self) -> List[Order]:
        """获取所有活跃订单（已分配但未完成）"""
        active_orders = []
        for order in self.orders.values():
            if order.status in [ORDER_STATUS['ASSIGNED'], ORDER_STATUS['PICKED_UP']]:
                active_orders.append(order)
        return active_orders
    
    # ============= 统计方法 =============
    def get_statistics(self) -> Dict:
        """获取订单系统统计信息"""
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
        """获取订单状态分布"""
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