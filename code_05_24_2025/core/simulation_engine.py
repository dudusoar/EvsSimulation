"""
仿真引擎模块
协调所有子系统，管理仿真流程，处理业务逻辑
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
    """仿真引擎类"""
    
    def __init__(self, config: Dict):
        """
        初始化仿真引擎
        
        参数:
            config: 仿真配置参数
        """
        self.config = config
        self.current_time = 0.0
        self.time_step = config.get('time_step', 0.1)
        
        # 初始化各个管理器
        print("初始化仿真引擎...")
        
        # 1. 地图管理器
        print("加载地图...")
        self.map_manager = MapManager(
            location=config.get('location', 'West Lafayette, IN'),
            cache_dir='datasets/maps'
        )
        
        # 2. 车辆管理器
        print("初始化车辆...")
        self.vehicle_manager = VehicleManager(self.map_manager, config)
        
        # 3. 订单系统
        print("初始化订单系统...")
        self.order_system = OrderSystem(self.map_manager, config)
        
        # 4. 充电管理器
        print("初始化充电站...")
        self.charging_manager = ChargingManager(self.map_manager, config)
        
        # 统计信息
        self.statistics = {
            'start_time': time.time(),
            'simulation_time': 0.0,
            'total_steps': 0
        }
        
        print("仿真引擎初始化完成！")
    
    # ============= 仿真主循环 =============
    def run_simulation(self, duration: float) -> Dict:
        """
        运行仿真
        
        参数:
            duration: 仿真持续时间（秒）
        
        返回:
            仿真结果统计
        """
        print(f"\n开始仿真，持续时间: {duration}秒")
        steps = int(duration / self.time_step)
        
        for step in range(steps):
            self.run_step()
            
            # 定期打印进度
            if step % 100 == 0:
                progress = (step / steps) * 100
                print(f"仿真进度: {progress:.1f}%")
        
        print("仿真完成！")
        return self.get_final_statistics()
    
    def run_step(self):
        """运行一个仿真步骤"""
        # 1. 生成新订单
        new_orders = self.order_system.generate_orders(self.current_time, self.time_step)
        
        # 2. 分配订单
        self._assign_orders()
        
        # 3. 更新车辆状态
        self.vehicle_manager.update_all_vehicles(self.time_step)
        
        # 4. 处理车辆到达事件
        self._handle_vehicle_arrivals()
        
        # 5. 更新充电进度
        charging_updates = self.charging_manager.update_charging_progress(self.time_step)
        for vehicle_id, charge_amount in charging_updates.items():
            self.vehicle_manager.charge_vehicle(vehicle_id, charge_amount)
        
        # 6. 检查充电需求
        self._check_charging_needs()
        
        # 7. 取消超时订单
        self.order_system.check_and_cancel_timeout_orders(self.current_time)
        
        # 8. 更新时间
        self.current_time += self.time_step
        self.statistics['simulation_time'] = self.current_time
        self.statistics['total_steps'] += 1
    
    # ============= 订单分配逻辑 =============
    def _assign_orders(self):
        """分配待处理订单"""
        # 获取待分配订单
        pending_orders = self.order_system.get_pending_orders()
        if not pending_orders:
            return
        
        # 获取可用车辆
        available_vehicles = self.vehicle_manager.get_available_vehicles()
        if not available_vehicles:
            return
        
        # 为每个订单找最佳车辆
        for order in pending_orders:
            if not available_vehicles:
                break
            
            # 找到最佳车辆
            best_vehicle = self.order_system.find_best_vehicle_for_order(
                order.order_id, available_vehicles
            )
            
            if best_vehicle:
                # 分配订单
                success = self.order_system.assign_order_to_vehicle(
                    order.order_id, best_vehicle, self.current_time
                )
                
                if success:
                    # 从可用列表中移除
                    available_vehicles.remove(best_vehicle)
    
    # ============= 车辆到达处理 =============
    def _handle_vehicle_arrivals(self):
        """处理车辆到达目的地的事件"""
        for vehicle in self.vehicle_manager.get_all_vehicles():
            # 检查是否到达目的地
            if not vehicle.has_reached_destination():
                continue
            
            # 根据车辆状态处理
            if vehicle.status == VEHICLE_STATUS['TO_PICKUP']:
                self._handle_pickup_arrival(vehicle)
                
            elif vehicle.status == VEHICLE_STATUS['WITH_PASSENGER']:
                self._handle_dropoff_arrival(vehicle)
                
            elif vehicle.status == VEHICLE_STATUS['TO_CHARGING']:
                self._handle_charging_arrival(vehicle)
    
    def _handle_pickup_arrival(self, vehicle: Vehicle):
        """处理到达接客点"""
        if not vehicle.current_task:
            return
        
        order_id = vehicle.current_task.get('order_id')
        if not order_id:
            return
        
        # 接客
        success = self.order_system.pickup_passenger(
            order_id, vehicle, self.current_time
        )
        
        if success:
            # 更新车辆状态（已在order_system中处理）
            pass
    
    def _handle_dropoff_arrival(self, vehicle: Vehicle):
        """处理到达目的地"""
        if not vehicle.current_task:
            return
        
        order_id = vehicle.current_task.get('order_id')
        if not order_id:
            return
        
        # 完成订单
        revenue = self.order_system.complete_order(
            order_id, vehicle, self.current_time
        )
    
    def _handle_charging_arrival(self, vehicle: Vehicle):
        """处理到达充电站"""
        if not vehicle.target_node:
            return
        
        # 获取充电站
        station = self.charging_manager.get_station_by_node(vehicle.target_node)
        if not station:
            # 没有充电站，返回空闲状态
            vehicle.clear_task()
            vehicle.update_status(VEHICLE_STATUS['IDLE'])
            return
        
        # 请求充电
        success = self.charging_manager.request_charging(vehicle, station)
        if not success:
            # 充电站满了，返回空闲状态
            vehicle.clear_task()
            vehicle.update_status(VEHICLE_STATUS['IDLE'])
    
    # ============= 充电管理 =============
    def _check_charging_needs(self):
        """检查并处理充电需求"""
        # 检查所有车辆
        for vehicle in self.vehicle_manager.get_all_vehicles():
            # 判断是否需要充电
            if not self.charging_manager.should_vehicle_charge(vehicle):
                continue
            
            # 如果已经在充电或前往充电，跳过
            if vehicle.status in [VEHICLE_STATUS['CHARGING'], VEHICLE_STATUS['TO_CHARGING']]:
                continue
            
            # 如果正在执行订单，不中断
            if vehicle.has_passenger:
                continue
            
            # 找到最佳充电站
            best_station = self.charging_manager.find_optimal_charging_station(vehicle)
            if best_station:
                # 派遣去充电
                self.vehicle_manager.dispatch_vehicle_to_charging(
                    vehicle, best_station.node_id
                )
        
        # 检查充满的车辆
        for vehicle in self.vehicle_manager.get_vehicles_by_status(VEHICLE_STATUS['CHARGING']):
            if vehicle.battery_percentage >= 95:  # 充到95%就可以了
                # 停止充电
                self.charging_manager.stop_charging(vehicle)
    
    # ============= 统计方法 =============
    def get_current_statistics(self) -> Dict:
        """获取当前统计信息"""
        # 获取各子系统统计
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
        """获取最终统计结果"""
        stats = self.get_current_statistics()
        
        # 添加总体统计
        stats['summary'] = {
            'total_simulation_time': self.current_time,
            'total_revenue': stats['orders']['total_revenue'],
            'total_cost': stats['vehicles']['total_fleet_cost'],
            'total_profit': stats['vehicles']['total_fleet_profit'],
            'order_completion_rate': stats['orders']['completion_rate'],
            'vehicle_utilization_rate': stats['vehicles']['utilization_rate'],
            'charging_utilization_rate': stats['charging']['avg_utilization_rate']
        }
        
        # 计算每辆车的详细统计
        vehicle_details = []
        for vehicle in self.vehicle_manager.get_all_vehicles():
            vehicle_details.append(vehicle.get_statistics())
        stats['vehicle_details'] = vehicle_details
        
        # 计算每个充电站的详细统计
        station_details = []
        for station in self.charging_manager.get_station_list():
            station_details.append(station.get_statistics())
        stats['station_details'] = station_details
        
        return stats
    
    # ============= 数据访问方法 =============
    def get_vehicles(self) -> List[Vehicle]:
        """获取所有车辆"""
        return self.vehicle_manager.get_all_vehicles()
    
    def get_orders(self) -> Dict:
        """获取订单信息"""
        return {
            'pending': self.order_system.get_pending_orders(),
            'active': self.order_system.get_active_orders()
        }
    
    def get_charging_stations(self):
        """获取充电站列表"""
        return self.charging_manager.get_station_list()