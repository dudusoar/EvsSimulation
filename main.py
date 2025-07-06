#!/usr/bin/env python3
"""
Electric Vehicle Simulation System - YAML配置驱动版本
统一的程序入口，完全由YAML配置文件控制所有参数
"""

import argparse
import sys
import time
import traceback
from pathlib import Path

<<<<<<< HEAD
from config.simulation_config import SIMULATION_CONFIG
from core.simulation_engine import SimulationEngine
from visualization.visualizer import Visualizer
from data.data_manager import DataManager
from core.map_manager import MapManager
=======
# 添加项目路径
sys.path.append(str(Path(__file__).parent))
>>>>>>> 766c210061aa23c5f87b6e98d504d6541d584f19

def run_live_simulation(engine, yaml_config):
    """运行实时可视化仿真"""
    from visualization.visualizer import Visualizer
    
    print("🎨 初始化可视化系统...")
    # 转换为传统配置格式给Visualizer使用
    from config.yaml_config_manager import config_manager
    legacy_config = config_manager.to_legacy_format(yaml_config)
    
    visualizer = Visualizer(
        simulation_engine=engine,
        config=legacy_config
    )
    
    print("▶️ 开始实时仿真...")
    print(f"⏱️ 目标时长: {yaml_config.simulation.duration}秒")
    print(f"📊 进度报告间隔: {yaml_config.data.save_interval}秒")
    print("\n按 Ctrl+C 可以提前停止仿真")
    
    try:
        final_stats = visualizer.run_live_simulation(
            duration=yaml_config.simulation.duration
        )
        print("\n🎉 实时仿真完成！")
        print("✅ 详细统计信息已在可视化窗口中显示")
        return final_stats
        
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断仿真")
        return None
    except Exception as e:
        print(f"\n❌ 仿真过程中出错: {e}")
        return None

def run_headless_simulation(engine, yaml_config):
    """运行无界面仿真"""
    print("⚡ 开始无界面仿真...")
    print(f"⏱️ 目标时长: {yaml_config.simulation.duration}秒")
    print(f"📊 进度报告间隔: {yaml_config.data.save_interval}秒")
    
    duration = yaml_config.simulation.duration
    progress_interval = yaml_config.data.save_interval
    
    start_time = time.time()
    next_progress_time = progress_interval
    
    try:
        while engine.current_time < duration:
            # 批量运行直到下一个进度报告点
            target_time = min(next_progress_time, duration)
            
            while engine.current_time < target_time:
                engine.run_step()
            
            # 输出进度报告
            if engine.current_time >= next_progress_time:
                elapsed_real = time.time() - start_time
                progress = (engine.current_time / duration) * 100
                stats = engine.get_current_statistics()
                
                print(f"\n📈 进度报告 ({progress:.1f}%):")
                print(f"   - 仿真时间: {engine.current_time:.1f}s / {duration:.1f}s")
                print(f"   - 实际用时: {elapsed_real:.1f}s")
                print(f"   - 完成订单: {stats.get('orders', {}).get('total_orders_completed', 0)}")
                print(f"   - 当前收入: ${stats.get('orders', {}).get('total_revenue', 0):.2f}")
                
                next_progress_time += progress_interval
        
        print(f"\n🎉 无界面仿真完成！")
        
        # 最终统计
        total_time = time.time() - start_time
        final_stats = engine.get_final_statistics()
        print(f"\n📊 最终统计:")
        print(f"   - 仿真时长: {duration}秒")
        print(f"   - 实际用时: {total_time:.2f}秒")
        print(f"   - 加速比: {duration/total_time:.1f}x")
        
        # 显示详细结果
        summary = final_stats.get('summary', {})
        print(f"   - 总收入: ${summary.get('total_revenue', 0):.2f}")
        print(f"   - 总成本: ${summary.get('total_cost', 0):.2f}")
        print(f"   - 总利润: ${summary.get('total_profit', 0):.2f}")
        print(f"   - 完成订单: {final_stats.get('orders', {}).get('total_orders_completed', 0)}")
        print(f"   - 订单完成率: {summary.get('order_completion_rate', 0)*100:.1f}%")
        print(f"   - 车辆利用率: {summary.get('vehicle_utilization_rate', 0)*100:.1f}%")
        
        return final_stats
        
    except KeyboardInterrupt:
        print(f"\n⏹️ 用户中断仿真")
        return None
    except Exception as e:
        print(f"\n❌ 仿真过程中出错: {e}")
        return None

def save_simulation_data(final_stats, yaml_config):
    """保存仿真数据（如果配置了数据保存）"""
    if yaml_config.data.save_data and final_stats:
        print("\n💾 保存仿真数据...")
        try:
            from data.data_manager import DataManager
            
            data_manager = DataManager(
                location=yaml_config.simulation.location,
                num_vehicles=yaml_config.vehicles.count,
                duration=yaml_config.simulation.duration
            )
            
            data_manager.save_simulation_results(final_stats)
            print("✅ 仿真数据保存成功")
            
            # 可以在这里添加更多数据处理逻辑
            # 比如生成报告、导出Excel等
            
        except Exception as e:
            print(f"❌ 保存仿真数据失败: {e}")

def list_available_configs():
    """列出可用的配置文件"""
    from config.yaml_config_manager import config_manager
    
    print("📁 可用的YAML配置文件:")
    configs = config_manager.list_configs()
    
    if not configs:
        print("   (没有找到配置文件)")
        return
    
    for i, config_file in enumerate(configs, 1):
        try:
            config = config_manager.load_config(config_file)
            print(f"   {i}. {config_file}")
            print(f"      名称: {config.simulation.name}")
            print(f"      位置: {config.simulation.location}")
            print(f"      模式: {config.visualization.mode}")
            print(f"      车辆: {config.vehicles.count}辆")
            print(f"      时长: {config.simulation.duration}秒")
            print(f"      数据保存: {'是' if config.data.save_data else '否'}")
        except Exception as e:
            print(f"   {i}. {config_file} (读取失败: {e})")

def run_simulation(config_file: str = "default.yaml"):
    """运行仿真的主函数"""
    print(f"🚀 EV仿真系统 - YAML配置驱动")
    print(f"📁 配置文件: {config_file}")
    print("=" * 60)
    
    try:
        # 1. 加载YAML配置
        from config.yaml_config_manager import config_manager
        print(f"📋 正在加载配置文件: {config_file}")
        yaml_config = config_manager.load_config(config_file)
        
        # 显示配置信息
        print(f"✅ 配置加载成功:")
        print(f"   - 仿真名称: {yaml_config.simulation.name}")
        print(f"   - 地点: {yaml_config.simulation.location}")
        print(f"   - 运行模式: {yaml_config.visualization.mode}")
        print(f"   - 车辆数: {yaml_config.vehicles.count}")
        print(f"   - 时长: {yaml_config.simulation.duration}秒")
        print(f"   - 数据保存: {'开启' if yaml_config.data.save_data else '关闭'}")
        if yaml_config.data.save_data:
            print(f"   - 保存间隔: {yaml_config.data.save_interval}秒")
        
        # 2. 转换为传统格式（兼容现有引擎）
        legacy_config = config_manager.to_legacy_format(yaml_config)
        
        # 3. 初始化仿真引擎
        print("\n🔧 初始化仿真引擎...")
        from core.simulation_engine import SimulationEngine
        engine = SimulationEngine(legacy_config)
        
        # 4. 根据配置的模式运行仿真
        mode = yaml_config.visualization.mode.lower()
        final_stats = None
        
        if mode == "live":
            print("\n🎮 启动实时可视化模式...")
            final_stats = run_live_simulation(engine, yaml_config)
        elif mode == "headless":
            print("\n🖥️ 启动无界面模式...")
            final_stats = run_headless_simulation(engine, yaml_config)
        else:
            print(f"❌ 未知的运行模式: {mode}")
            print("   支持的模式: live, headless")
            return False
        
        # 5. 保存数据（如果配置了）
        save_simulation_data(final_stats, yaml_config)
        
        return True
        
    except FileNotFoundError as e:
        print(f"❌ 配置文件不存在: {e}")
        print("💡 使用 --list 查看可用的配置文件")
        return False
    except Exception as e:
        print(f"❌ 运行失败: {e}")
        print(f"错误详情: {traceback.format_exc()}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='EV仿真系统 - YAML配置驱动版本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用方法:
  # 使用默认配置运行
  python main.py
  
  # 使用指定配置文件
  python main.py -c config/examples/west_lafayette_demo.yaml
  
  # 列出所有可用配置
  python main.py --list
  
配置文件说明:
  所有参数都在YAML配置文件中设置，包括：
  - 运行模式 (live/headless)
  - 车辆数量、仿真时长
  - 数据保存设置
  - 可视化参数等
  
  参考配置文件: config/default.yaml
        """
    )
    
    # 基本参数
    parser.add_argument(
        '-c', '--config', 
        default='default.yaml',
        help='YAML配置文件路径 (默认: default.yaml)'
    )
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='列出所有可用的配置文件'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )
    
    args = parser.parse_args()
    
    # 列出配置文件
    if args.list:
        list_available_configs()
        return 0
    
    # 运行仿真
    try:
        success = run_simulation(args.config)
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断程序")
        return 0
    except Exception as e:
        print(f"\n❌ 程序错误: {e}")
        if args.debug:
            traceback.print_exc()
<<<<<<< HEAD
        sys.exit(1)

    #mm = MapManager("Manhattan, New York, NY, USA",'datasets/maps')
    #mm.calculate_travel_time_weights(50.0)
    #mm.get_shortest_path_points(36,45)
    #mm.get_all_nodes()

=======
        return 1
>>>>>>> 766c210061aa23c5f87b6e98d504d6541d584f19

if __name__ == '__main__':
    exit(main())