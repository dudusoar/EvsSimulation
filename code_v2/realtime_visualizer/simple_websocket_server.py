"""
简化的WebSocket服务器
使用更直接的方法避免事件循环问题
"""

import asyncio
import websockets
import json
import threading
import time
from typing import Set
import logging

class SimpleWebSocketServer:
    """简化的WebSocket服务器"""
    
    def __init__(self, simulation_engine, port: int = 8765):
        self.engine = simulation_engine
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.is_running = False
        self.is_paused = False
        self.speed_multiplier = 1.0
        self.server = None
        self.logger = logging.getLogger(__name__)
        
    async def register_client(self, websocket, path):
        """注册新客户端"""
        self.clients.add(websocket)
        self.logger.info(f"客户端连接: {websocket.remote_address}")
        
        # 发送初始数据
        await self.send_initial_data(websocket)
        
        try:
            async for message in websocket:
                await self.handle_client_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            self.logger.error(f"客户端处理错误: {e}")
        finally:
            self.clients.remove(websocket)
            self.logger.info(f"客户端断开: {websocket.remote_address}")
    
    async def send_initial_data(self, websocket):
        """发送初始化数据"""
        try:
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
            
            control_data = {
                'type': 'control_state',
                'is_running': self.is_running,
                'is_paused': self.is_paused,
                'speed_multiplier': self.speed_multiplier
            }
            await websocket.send(json.dumps(control_data))
        except Exception as e:
            self.logger.error(f"发送初始数据错误: {e}")
    
    async def handle_client_message(self, websocket, message):
        """处理客户端消息"""
        try:
            data = json.loads(message)
            command = data.get('command')
            
            if command == 'start':
                await self.start_simulation()
            elif command == 'pause':
                self.is_paused = True
                await self.broadcast_control_state()
            elif command == 'resume':
                self.is_paused = False
                await self.broadcast_control_state()
            elif command == 'reset':
                await self.reset_simulation()
            elif command == 'set_speed':
                self.speed_multiplier = max(0.1, min(10.0, data.get('speed', 1.0)))
                await self.broadcast_control_state()
                
        except Exception as e:
            self.logger.error(f"处理消息错误: {e}")
    
    async def start_simulation(self):
        """开始仿真"""
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            
            # 在后台任务中运行仿真循环
            asyncio.create_task(self.simulation_loop())
            await self.broadcast_control_state()
    
    async def reset_simulation(self):
        """重置仿真"""
        self.is_running = False
        self.is_paused = False
        
        # 重新初始化引擎
        config = self.engine.config
        from core.simulation_engine import SimulationEngine
        self.engine = SimulationEngine(config)
        
        await self.broadcast_control_state()
        
        # 重新发送初始数据给所有客户端
        for client in self.clients.copy():
            try:
                await self.send_initial_data(client)
            except:
                self.clients.remove(client)
    
    async def simulation_loop(self):
        """仿真循环"""
        while self.is_running:
            if not self.is_paused:
                # 运行仿真步骤
                self.engine.run_step()
                
                # 收集并广播数据
                simulation_data = self.collect_simulation_data()
                await self.broadcast_data(simulation_data)
            
            # 控制更新频率
            await asyncio.sleep(self.engine.time_step / self.speed_multiplier)
    
    def collect_simulation_data(self):
        """收集仿真数据"""
        vehicles_data = []
        for vehicle in self.engine.get_vehicles():
            vehicles_data.append({
                'id': vehicle.vehicle_id,
                'position': vehicle.position,
                'battery_percentage': vehicle.battery_percentage,
                'status': vehicle.status,
                'has_passenger': vehicle.has_passenger
            })
        
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
        
        stats = self.engine.get_current_statistics()
        
        return {
            'type': 'simulation_update',
            'timestamp': time.time(),
            'simulation_time': self.engine.current_time,
            'vehicles': vehicles_data,
            'orders': orders_data,
            'statistics': stats
        }
    
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
        
        await self.broadcast_data(control_data)
    
    async def broadcast_data(self, data):
        """广播数据到所有客户端"""
        if not self.clients:
            return
        
        message = json.dumps(data)
        disconnected_clients = set()
        
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                self.logger.error(f"发送数据错误: {e}")
                disconnected_clients.add(client)
        
        self.clients -= disconnected_clients
    
    async def start_server(self):
        """启动服务器"""
        try:
            self.server = await websockets.serve(
                self.register_client,
                "localhost",
                self.port
            )
            self.logger.info(f"WebSocket服务器启动在 ws://localhost:{self.port}")
            return self.server
        except Exception as e:
            self.logger.error(f"启动WebSocket服务器失败: {e}")
            raise
    
    async def stop_server(self):
        """停止服务器"""
        self.is_running = False
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.logger.info("WebSocket服务器已停止") 