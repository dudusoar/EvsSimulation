#!/usr/bin/env python3
"""
Flask API Server for Real-time Simulation
Simple HTTP API to replace WebSocket communication
"""

import json
import threading
import time
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from pathlib import Path
from typing import Dict, Any
import sys

from core.simulation_engine import SimulationEngine


class FlaskApiServer:
    """Flask API服务器 - 替代WebSocket的简单方案"""
    
    def __init__(self, simulation_engine: SimulationEngine, port: int = 8080):
        """
        初始化API服务器
        
        参数:
            simulation_engine: 仿真引擎实例
            port: HTTP端口
        """
        self.engine = simulation_engine
        self.port = port
        
        # 控制状态
        self.is_running = False
        self.is_paused = False
        self.speed_multiplier = 1.0
        
        # 仿真控制
        self.simulation_thread = None
        self.stop_event = threading.Event()
        
        # 创建Flask应用
        self.app = Flask(__name__)
        CORS(self.app)  # 允许跨域请求
        
        # 设置静态文件目录
        self.web_dir = Path(__file__).parent / "web"
        
        # 直接注册路由
        self.setup_routes()
        
        print(f"✅ API服务器初始化完成，端口: {port}")
    
    def setup_routes(self):
        """设置路由"""
        # 保存self引用
        server = self
        
        # 静态文件服务
        @self.app.route('/')
        def index():
            return send_from_directory(server.web_dir, 'index.html')
        
        @self.app.route('/<path:filename>')
        def static_files(filename):
            return send_from_directory(server.web_dir, filename)
        
        # API接口
        @self.app.route('/api/status')
        def get_status():
            """获取系统状态"""
            try:
                return jsonify({
                    'is_running': server.is_running,
                    'is_paused': server.is_paused,
                    'speed_multiplier': server.speed_multiplier,
                    'simulation_time': getattr(server.engine, 'current_time', 0)
                })
            except Exception as e:
                return jsonify({
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/initial_data')
        def get_initial_data():
            """获取初始化数据"""
            try:
                # 获取充电站数据
                charging_stations = []
                for station in server.engine.get_charging_stations():
                    charging_stations.append({
                        'id': station.station_id,
                        'position': list(station.position),
                        'capacity': station.total_slots
                    })
                
                return jsonify({
                    'success': True,
                    'charging_stations': charging_stations
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/simulation_data')
        def get_simulation_data():
            """获取当前仿真数据"""
            try:
                data = server._collect_simulation_data()
                return jsonify({
                    'success': True,
                    'data': data
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/control', methods=['POST'])
        def control_simulation():
            """控制仿真"""
            try:
                data = request.get_json()
                command = data.get('command')
                
                if command == 'start':
                    server.start_simulation()
                elif command == 'pause':
                    server.pause_simulation()
                elif command == 'resume':
                    server.resume_simulation()
                elif command == 'reset':
                    server.reset_simulation()
                elif command == 'set_speed':
                    speed = data.get('speed', 1.0)
                    server.set_speed(speed)
                else:
                    return jsonify({
                        'success': False,
                        'error': f'Unknown command: {command}'
                    }), 400
                
                return jsonify({
                    'success': True,
                    'message': f'Command {command} executed'
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/vehicle/<vehicle_id>')
        def get_vehicle_details(vehicle_id):
            """获取车辆详情"""
            try:
                vehicles = server.engine.get_vehicles()
                vehicle = next((v for v in vehicles if v.vehicle_id == vehicle_id), None)
                
                if vehicle:
                    return jsonify({
                        'success': True,
                        'data': {
                            'position': list(vehicle.position),
                            'battery_percentage': vehicle.battery_percentage,
                            'status': vehicle.status,
                            'current_task': getattr(vehicle, 'current_task', None),
                            'statistics': vehicle.get_statistics()
                        }
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': f'Vehicle {vehicle_id} not found'
                    }), 404
                    
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
    
    def _collect_simulation_data(self) -> Dict:
        """收集当前仿真数据"""
        try:
            # 获取车辆数据
            vehicles_data = []
            for vehicle in self.engine.get_vehicles():
                vehicles_data.append({
                    'id': vehicle.vehicle_id,
                    'position': list(vehicle.position),
                    'battery_percentage': vehicle.battery_percentage,
                    'status': vehicle.status,
                    'has_passenger': getattr(vehicle, 'has_passenger', False)
                })
            
            # 获取订单数据
            orders_info = self.engine.get_orders()
            orders_data = []
            
            for order in orders_info['pending'] + orders_info['active']:
                orders_data.append({
                    'id': order.order_id,
                    'pickup_position': list(order.pickup_position),
                    'dropoff_position': list(order.dropoff_position),
                    'status': order.status,
                    'assigned_vehicle': getattr(order, 'assigned_vehicle_id', None)
                })
            
            # 获取统计数据
            stats = self.engine.get_current_statistics()
            
            # 简化统计数据格式
            simplified_stats = {
                'total_vehicles': len(vehicles_data),
                'pending_orders': len(orders_info['pending']),
                'active_orders': len(orders_info['active']),
                'completed_orders': stats.get('orders', {}).get('total_orders_completed', 0),
                'total_revenue': stats.get('orders', {}).get('total_revenue', 0),
                'average_battery': stats.get('vehicles', {}).get('avg_battery_percentage', 0)
            }
            
            return {
                'timestamp': time.time(),
                'simulation_time': getattr(self.engine, 'current_time', 0),
                'vehicles': vehicles_data,
                'orders': orders_data,
                'statistics': simplified_stats
            }
            
        except Exception as e:
            print(f"收集仿真数据错误: {e}")
            return {
                'timestamp': time.time(),
                'simulation_time': 0,
                'vehicles': [],
                'orders': [],
                'statistics': {}
            }
    
    def start_simulation(self):
        """开始仿真"""
        if not self.is_running:
            print("🚀 启动仿真...")
            self.is_running = True
            self.is_paused = False
            self.stop_event.clear()
            
            # 在新线程中运行仿真
            self.simulation_thread = threading.Thread(
                target=self._run_simulation_loop,
                daemon=True
            )
            self.simulation_thread.start()
    
    def pause_simulation(self):
        """暂停仿真"""
        print("⏸️ 暂停仿真...")
        self.is_paused = True
    
    def resume_simulation(self):
        """恢复仿真"""
        print("▶️ 恢复仿真...")
        self.is_paused = False
    
    def reset_simulation(self):
        """重置仿真"""
        print("🔄 重置仿真...")
        self.is_running = False
        self.is_paused = False
        self.stop_event.set()
        
        # 等待仿真线程结束
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=3.0)
        
        # 重新初始化仿真引擎
        config = self.engine.config
        from core.simulation_engine import SimulationEngine
        self.engine = SimulationEngine(config)
    
    def set_speed(self, speed: float):
        """设置仿真速度"""
        self.speed_multiplier = max(0.1, min(10.0, speed))
        print(f"⚡ 设置速度: {self.speed_multiplier}x")
    
    def _run_simulation_loop(self):
        """仿真循环（在独立线程中运行）"""
        print("🔄 仿真循环开始...")
        
        while self.is_running and not self.stop_event.is_set():
            try:
                if not self.is_paused:
                    # 运行仿真步骤
                    self.engine.run_step()
                
                # 控制更新频率
                target_interval = getattr(self.engine, 'time_step', 0.1) / self.speed_multiplier
                time.sleep(max(0.01, target_interval))  # 最小10ms
                
            except Exception as e:
                print(f"仿真循环错误: {e}")
                break
        
        print("🛑 仿真循环结束")
    
    def start_server(self):
        """启动HTTP服务器"""
        def run_server():
            try:
                print(f"🌐 启动HTTP服务器在 http://localhost:{self.port}")
                self.app.run(
                    host='localhost',
                    port=self.port,
                    debug=False,
                    use_reloader=False,
                    threaded=True
                )
            except Exception as e:
                print(f"❌ HTTP服务器启动错误: {e}")
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        # 等待服务器启动
        time.sleep(2)
    
    def stop_server(self):
        """停止服务器"""
        print("🛑 停止API服务器...")
        self.is_running = False
        self.stop_event.set()
        
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=3.0) 