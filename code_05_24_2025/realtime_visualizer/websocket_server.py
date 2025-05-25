"""
WebSocket服务器
负责实时推送仿真数据到前端客户端
"""

import asyncio
import websockets
import json
import threading
import time
from typing import Dict, List, Set, Optional
from datetime import datetime

from core.simulation_engine import SimulationEngine


class VisualizationServer:
    """实时可视化WebSocket服务器"""
    
    def __init__(self, simulation_engine: SimulationEngine, port: int = 8765):
        """
        初始化服务器
        
        参数:
            simulation_engine: 仿真引擎实例
            port: WebSocket端口
        """
        self.engine = simulation_engine
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        
        # 控制状态
        self.is_running = False
        self.is_paused = False
        self.speed_multiplier = 1.0
        self.should_reset = False
        
        # 线程控制
        self.simulation_thread = None
        self.server_thread = None
        self.loop = None
        
        print(f"可视化服务器初始化完成，端口: {port}")
    
    async def register_client(self, websocket, path):
        """注册新客户端"""
        self.clients.add(websocket)
        print(f"客户端连接: {websocket.remote_address}")
        
        # 发送初始数据
        await self.send_initial_data(websocket)
        
        try:
            # 监听客户端消息
            async for message in websocket:
                await self.handle_client_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.remove(websocket)
            print(f"客户端断开: {websocket.remote_address}")
    
    async def send_initial_data(self, websocket):
        """发送初始化数据"""
        # 发送地图数据
        map_data = {
            'type': 'map_data',
            'bounds': self.engine.map_manager.get_bounds(),
            'charging_stations': [
                {
                    'id': station.station_id,
                    'position': station.position,
                    'capacity': station.capacity
                }
                for station in self.engine.get_charging_stations()
            ]
        }
        await websocket.send(json.dumps(map_data))
        
        # 发送控制状态
        control_data = {
            'type': 'control_state',
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'speed_multiplier': self.speed_multiplier
        }
        await websocket.send(json.dumps(control_data))
    
    async def handle_client_message(self, websocket, message):
        """处理客户端消息"""
        try:
            data = json.loads(message)
            command = data.get('command')
            
            if command == 'start':
                await self.start_simulation()
            elif command == 'pause':
                await self.pause_simulation()
            elif command == 'resume':
                await self.resume_simulation()
            elif command == 'reset':
                await self.reset_simulation()
            elif command == 'set_speed':
                speed = data.get('speed', 1.0)
                await self.set_speed(speed)
            elif command == 'get_vehicle_details':
                vehicle_id = data.get('vehicle_id')
                await self.send_vehicle_details(websocket, vehicle_id)
            elif command == 'get_order_details':
                order_id = data.get('order_id')
                await self.send_order_details(websocket, order_id)
                
        except json.JSONDecodeError:
            print(f"无效的JSON消息: {message}")
        except Exception as e:
            print(f"处理客户端消息时出错: {e}")
    
    async def start_simulation(self):
        """开始仿真"""
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            
            # 在新线程中运行仿真
            self.simulation_thread = threading.Thread(
                target=self._run_simulation_loop,
                daemon=True
            )
            self.simulation_thread.start()
            
            # 通知所有客户端
            await self.broadcast_control_state()
    
    async def pause_simulation(self):
        """暂停仿真"""
        self.is_paused = True
        await self.broadcast_control_state()
    
    async def resume_simulation(self):
        """恢复仿真"""
        self.is_paused = False
        await self.broadcast_control_state()
    
    async def reset_simulation(self):
        """重置仿真"""
        self.should_reset = True
        self.is_running = False
        self.is_paused = False
        
        # 等待仿真线程结束
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=2.0)
        
        # 重新初始化仿真引擎
        config = self.engine.config
        self.engine = SimulationEngine(config)
        
        self.should_reset = False
        await self.broadcast_control_state()
        
        # 重新发送初始数据
        for client in self.clients.copy():
            try:
                await self.send_initial_data(client)
            except:
                self.clients.remove(client)
    
    async def set_speed(self, speed: float):
        """设置仿真速度"""
        self.speed_multiplier = max(0.1, min(10.0, speed))
        await self.broadcast_control_state()
    
    async def broadcast_control_state(self):
        """广播控制状态"""
        if not self.clients:
            return
        
        control_data = {
            'type': 'control_state',
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'speed_multiplier': self.speed_multiplier
        }
        
        message = json.dumps(control_data)
        disconnected_clients = set()
        
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
        
        # 移除断开的客户端
        self.clients -= disconnected_clients
    
    async def broadcast_simulation_data(self, data: Dict):
        """广播仿真数据"""
        if not self.clients:
            return
        
        message = json.dumps(data)
        disconnected_clients = set()
        
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
        
        # 移除断开的客户端
        self.clients -= disconnected_clients
    
    async def send_vehicle_details(self, websocket, vehicle_id: str):
        """发送车辆详情"""
        vehicles = self.engine.get_vehicles()
        vehicle = next((v for v in vehicles if v.vehicle_id == vehicle_id), None)
        
        if vehicle:
            details = {
                'type': 'vehicle_details',
                'vehicle_id': vehicle_id,
                'data': {
                    'position': vehicle.position,
                    'battery_percentage': vehicle.battery_percentage,
                    'status': vehicle.status,
                    'current_task': vehicle.current_task,
                    'statistics': vehicle.get_statistics()
                }
            }
            await websocket.send(json.dumps(details))
    
    async def send_order_details(self, websocket, order_id: str):
        """发送订单详情"""
        orders_info = self.engine.get_orders()
        all_orders = orders_info['pending'] + orders_info['active']
        order = next((o for o in all_orders if o.order_id == order_id), None)
        
        if order:
            details = {
                'type': 'order_details',
                'order_id': order_id,
                'data': {
                    'pickup_position': order.pickup_position,
                    'dropoff_position': order.dropoff_position,
                    'status': order.status,
                    'creation_time': order.creation_time,
                    'assigned_vehicle': order.assigned_vehicle
                }
            }
            await websocket.send(json.dumps(details))
    
    def _run_simulation_loop(self):
        """仿真循环（在独立线程中运行）"""
        last_update_time = time.time()
        
        while self.is_running and not self.should_reset:
            if not self.is_paused:
                # 运行仿真步骤
                self.engine.run_step()
                
                # 收集数据
                simulation_data = self._collect_simulation_data()
                
                # 异步发送数据
                if self.loop and not self.loop.is_closed():
                    asyncio.run_coroutine_threadsafe(
                        self.broadcast_simulation_data(simulation_data),
                        self.loop
                    )
            
            # 控制更新频率
            current_time = time.time()
            elapsed = current_time - last_update_time
            target_interval = self.engine.time_step / self.speed_multiplier
            
            if elapsed < target_interval:
                time.sleep(target_interval - elapsed)
            
            last_update_time = time.time()
    
    def _collect_simulation_data(self) -> Dict:
        """收集当前仿真数据"""
        # 获取车辆数据
        vehicles_data = []
        for vehicle in self.engine.get_vehicles():
            vehicles_data.append({
                'id': vehicle.vehicle_id,
                'position': vehicle.position,
                'battery_percentage': vehicle.battery_percentage,
                'status': vehicle.status,
                'has_passenger': vehicle.has_passenger
            })
        
        # 获取订单数据
        orders_info = self.engine.get_orders()
        orders_data = []
        
        for order in orders_info['pending'] + orders_info['active']:
            orders_data.append({
                'id': order.order_id,
                'pickup_position': order.pickup_position,
                'dropoff_position': order.dropoff_position,
                'status': order.status,
                'assigned_vehicle': order.assigned_vehicle
            })
        
        # 获取统计数据
        stats = self.engine.get_current_statistics()
        
        return {
            'type': 'simulation_update',
            'timestamp': datetime.now().isoformat(),
            'simulation_time': self.engine.current_time,
            'vehicles': vehicles_data,
            'orders': orders_data,
            'statistics': stats
        }
    
    def start_server(self):
        """启动WebSocket服务器"""
        def run_server():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            start_server = websockets.serve(
                self.register_client,
                "localhost",
                self.port
            )
            
            print(f"WebSocket服务器启动在 ws://localhost:{self.port}")
            self.loop.run_until_complete(start_server)
            self.loop.run_forever()
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        # 等待服务器启动
        time.sleep(1)
    
    def stop_server(self):
        """停止服务器"""
        self.is_running = False
        
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)
        
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=2.0)
        
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=2.0)
        
        print("WebSocket服务器已停止") 