#!/usr/bin/env python3
"""
实时可视化测试启动脚本
用于快速测试和调试实时可视化功能
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """检查依赖项"""
    missing_deps = []
    
    try:
        import websockets
        print("✅ websockets - OK")
    except ImportError:
        missing_deps.append("websockets>=11.0.0")
        print("❌ websockets - Missing")
    
    try:
        import aiohttp
        print("✅ aiohttp - OK")
    except ImportError:
        missing_deps.append("aiohttp>=3.8.0")
        print("❌ aiohttp - Missing")
    
    try:
        import osmnx
        print("✅ osmnx - OK")
    except ImportError:
        missing_deps.append("osmnx>=1.3.0")
        print("❌ osmnx - Missing")
    
    try:
        import networkx
        print("✅ networkx - OK")
    except ImportError:
        missing_deps.append("networkx>=2.8")
        print("❌ networkx - Missing")
    
    if missing_deps:
        print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
        print("Please install them with:")
        print(f"pip install {' '.join(missing_deps)}")
        return False
    
    print("\n✅ All dependencies satisfied!")
    return True

def check_files():
    """检查必要文件是否存在"""
    required_files = [
        'realtime_visualizer/websocket_server.py',
        'realtime_visualizer/realtime_visualizer.py',
        'realtime_visualizer/web/index.html',
        'realtime_visualizer/web/js/main.js',
        'core/simulation_engine.py',
        'config/simulation_config.py'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing")
            all_exist = False
    
    return all_exist

def test_import():
    """测试导入"""
    try:
        print("\n🔄 Testing imports...")
        
        from config.simulation_config import SIMULATION_CONFIG
        print("✅ Configuration imported")
        
        from core.simulation_engine import SimulationEngine
        print("✅ SimulationEngine imported")
        
        from realtime_visualizer.websocket_server import WebSocketServer
        print("✅ WebSocketServer imported")
        
        from realtime_visualizer.realtime_visualizer import RealtimeVisualizer
        print("✅ RealtimeVisualizer imported")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    print("🚀 Real-time Visualizer Test Script")
    print("=" * 50)
    
    print("\n1. Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    print("\n2. Checking required files...")
    if not check_files():
        print("\n❌ Some required files are missing!")
        sys.exit(1)
    
    print("\n3. Testing imports...")
    if not test_import():
        sys.exit(1)
    
    print("\n✅ All tests passed!")
    print("\n4. Starting real-time visualizer...")
    
    # 创建简化的配置
    config = {
        'location': 'West Lafayette, IN',
        'num_vehicles': 10,
        'simulation_duration': 3600,
        'num_charging_stations': 3,
        'order_generation_rate': 50,
        'time_step': 0.1
    }
    
    # 启动实时可视化
    import asyncio
    from realtime_visualizer.realtime_visualizer import RealtimeVisualizer
    
    async def run_test():
        visualizer = RealtimeVisualizer(config=config)
        try:
            await visualizer.start()
            print("\n🌐 Open your browser and go to: http://localhost:8080")
            print("⌨️  Press Ctrl+C to stop")
            
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping...")
            await visualizer.stop()
            print("✅ Stopped successfully")
    
    try:
        asyncio.run(run_test())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()