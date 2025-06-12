#!/usr/bin/env python3
"""
简单的Flask API测试
独立测试API服务器功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

def test_flask_simple():
    """简单测试Flask服务器"""
    try:
        print("🧪 Testing Flask API server...")
        
        # 创建基本配置
        config = {
            'location': 'West Lafayette, IN',
            'num_vehicles': 3,
            'simulation_duration': 60,
            'num_charging_stations': 2,
            'order_generation_rate': 10,
            'time_step': 0.1
        }
        
        # 创建仿真引擎
        from core.simulation_engine import SimulationEngine
        engine = SimulationEngine(config)
        print("✅ Simulation engine created")
        
        # 创建API服务器
        from realtime_visualizer.flask_api_server import FlaskApiServer
        api_server = FlaskApiServer(engine, port=8080)
        print("✅ API server created")
        
        # 手动注册路由和测试
        print("📋 Available routes:")
        with api_server.app.app_context():
            for rule in api_server.app.url_map.iter_rules():
                print(f"   {rule.methods} {rule.rule}")
        
        # 启动服务器
        print("\n🚀 Starting Flask server...")
        api_server.start_server()
        
        print("\n✅ Server should be running at http://localhost:8080")
        print("📡 API endpoints:")
        print("   http://localhost:8080/api/status")
        print("   http://localhost:8080/api/initial_data")
        print("   http://localhost:8080/api/simulation_data")
        print("\n⌨️  Press Ctrl+C to stop")
        
        # 保持运行
        import time
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_flask_simple() 