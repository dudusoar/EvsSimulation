"""
电车司机仿真系统主程序
程序入口，处理命令行参数，协调各模块运行
"""

import argparse
import sys
import json
from datetime import datetime

from config.simulation_config import SIMULATION_CONFIG
from core.simulation_engine import SimulationEngine
from visualization.visualizer import Visualizer
from data.data_manager import DataManager


def load_custom_config(config_file: str) -> dict:
    """加载自定义配置文件"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            custom_config = json.load(f)
        # 合并配置
        config = SIMULATION_CONFIG.copy()
        config.update(custom_config)
        return config
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        return SIMULATION_CONFIG


def run_simulation(config: dict, args):
    """运行仿真"""
    print("=" * 60)
    print("EV Driver Simulation System")
    print("=" * 60)
    
    # 更新配置
    if args.location:
        config['location'] = args.location
    if args.vehicles:
        config['num_vehicles'] = args.vehicles
    if args.duration:
        config['simulation_duration'] = args.duration
    if args.no_animation:
        config['enable_animation'] = False
    
    # 打印配置信息
    print(f"\nSimulation Configuration:")
    print(f"- Location: {config['location']}")
    print(f"- Vehicles: {config['num_vehicles']}")
    print(f"- Duration: {config['simulation_duration']} seconds")
    print(f"- Charging stations: {config['num_charging_stations']}")
    print(f"- Order generation rate: {config['order_generation_rate']} orders/hour")
    
    # 初始化数据管理器
    data_manager = None
    if config.get('save_data', False) or args.save_data:
        data_manager = DataManager()
    
    # 初始化仿真引擎
    print("\nInitializing simulation system...")
    engine = SimulationEngine(config)
    
    # 运行仿真
    if config.get('enable_animation', True) and not args.headless:
        # 带可视化运行
        print("\nStarting simulation with visualization...")
        visualizer = Visualizer(engine, config)
        
        # 保存动画
        if args.output:
            output_file = visualizer.save_animation(
                filename=args.output,
                format=args.format
            )
        else:
            visualizer.save_animation(format=args.format)
    else:
        # 无头模式运行
        print("\nRunning simulation (headless mode)...")
        final_stats = engine.run_simulation(config['simulation_duration'])
    
    # 获取最终统计
    final_stats = engine.get_final_statistics()
    
    # 保存数据
    if data_manager:
        data_manager.save_simulation_results(final_stats)
        if args.report:
            data_manager.generate_report(final_stats)
        if args.excel:
            data_manager.export_to_excel(final_stats)
    
    # 打印结果摘要
    print("\n" + "=" * 60)
    print("Simulation Completed!")
    print("=" * 60)
    print(f"\nSimulation Results Summary:")
    print(f"- Total revenue: ¥{final_stats['summary']['total_revenue']:.2f}")
    print(f"- Total cost: ¥{final_stats['summary']['total_cost']:.2f}")
    print(f"- Total profit: ¥{final_stats['summary']['total_profit']:.2f}")
    print(f"- Order completion rate: {final_stats['summary']['order_completion_rate']*100:.1f}%")
    print(f"- Vehicle utilization rate: {final_stats['summary']['vehicle_utilization_rate']*100:.1f}%")
    print(f"- Charging station utilization rate: {final_stats['summary']['charging_utilization_rate']*100:.1f}%")
    
    return final_stats


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='电车司机仿真系统 - 模拟电动车辆在城市中的运营',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用默认配置运行
  python main.py
  
  # 指定地点和车辆数
  python main.py -l "Beijing, China" -v 50
  
  # 无头模式运行并生成报告
  python main.py --headless --save-data --report
  
  # 使用自定义配置文件
  python main.py -c custom_config.json
        """
    )
    
    # 基本参数
    parser.add_argument('-l', '--location', type=str,
                      help='仿真地点（默认: West Lafayette, IN）')
    parser.add_argument('-v', '--vehicles', type=int,
                      help='车辆数量')
    parser.add_argument('-d', '--duration', type=int,
                      help='仿真时长（秒）')
    parser.add_argument('-c', '--config', type=str,
                      help='配置文件路径')
    
    # 输出参数
    parser.add_argument('-o', '--output', type=str,
                      help='输出文件名（不含扩展名）')
    parser.add_argument('-f', '--format', choices=['html', 'mp4'],
                      default='html', help='动画格式（默认: html）')
    
    # 运行模式
    parser.add_argument('--headless', action='store_true',
                      help='无头模式（无可视化）')
    parser.add_argument('--no-animation', action='store_true',
                      help='禁用动画生成')
    
    # 数据保存
    parser.add_argument('--save-data', action='store_true',
                      help='保存仿真数据')
    parser.add_argument('--report', action='store_true',
                      help='生成仿真报告')
    parser.add_argument('--excel', action='store_true',
                      help='导出Excel文件')
    
    # 调试参数
    parser.add_argument('--debug', action='store_true',
                      help='调试模式')
    
    args = parser.parse_args()
    
    # 加载配置
    if args.config:
        config = load_custom_config(args.config)
    else:
        config = SIMULATION_CONFIG.copy()
    
    # 运行仿真
    try:
        run_simulation(config, args)
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()