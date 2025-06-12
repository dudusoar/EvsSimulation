"""
Electric Vehicle Simulation System Main Program - 修复版本
Program entry point, handles command line arguments and coordinates module execution
"""

import argparse
import sys
import json
import asyncio
from datetime import datetime
import os

from config.simulation_config import SIMULATION_CONFIG
from core.simulation_engine import SimulationEngine
from visualization.visualizer import Visualizer
from data.data_manager import DataManager

# Import realtime visualizer (only when needed and available)
def import_realtime_visualizer():
    """Lazy import of realtime visualizer - optional dependency"""
    try:
        from realtime_visualizer.realtime_visualizer import RealtimeVisualizer
        return RealtimeVisualizer
    except ImportError as e:
        print(f"⚠️  Real-time visualizer not available: {e}")
        print("💡 To enable real-time web visualization, install dependencies:")
        print("   pip install websockets aiohttp")
        print("📊 You can still use traditional simulation modes")
        return None
    except Exception as e:
        print(f"⚠️  Real-time visualizer module error: {e}")
        print("📊 Falling back to traditional simulation")
        return None


def load_custom_config(config_file: str) -> dict:
    """Load custom configuration file"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            custom_config = json.load(f)
        # Merge configurations
        config = SIMULATION_CONFIG.copy()
        config.update(custom_config)
        return config
    except Exception as e:
        print(f"Failed to load configuration file: {e}")
        return SIMULATION_CONFIG


def check_dependencies():
    """检查依赖项是否安装"""
    try:
        import websockets
        import aiohttp
        return True
    except ImportError:
        return False


def run_realtime_simulation(config: dict, args):
    """运行实时可视化仿真"""
    print("\n🚀 Starting Real-time Visualization System...")
    print("=" * 60)
    
    # 尝试导入实时可视化模块
    RealtimeVisualizer = import_realtime_visualizer()
    
    if RealtimeVisualizer is None:
        print("\n❌ Real-time visualization is not available!")
        print("🔄 Falling back to traditional simulation mode...")
        print("=" * 60)
        return run_traditional_simulation(config, args)
    
    # 检查依赖
    if not check_dependencies():
        print("❌ Missing dependencies for real-time visualization!")
        print("Please install required packages:")
        print("  pip install websockets>=11.0.0 aiohttp>=3.8.0")
        print("\n🔄 Falling back to traditional simulation mode...")
        return run_traditional_simulation(config, args)
    
    # 更新配置
    if args.location:
        config['location'] = args.location
    if args.vehicles:
        config['num_vehicles'] = args.vehicles
    if args.duration:
        config['simulation_duration'] = args.duration
        
    print(f"Configuration:")
    print(f"- Location: {config.get('location', 'West Lafayette, IN')}")
    print(f"- Vehicles: {config.get('num_vehicles', 20)}")
    print(f"- Duration: {config.get('simulation_duration', 3600)} seconds")
    print(f"- Mode: Real-time Interactive Visualization")
    print()
    print("📡 Services will be available at:")
    print("   Frontend: http://localhost:8080")
    print("   WebSocket: ws://localhost:8765")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    async def run_realtime():
        visualizer = RealtimeVisualizer(config=config)
        try:
            await visualizer.start()
            print("\n✅ Real-time Visualizer started successfully!")
            print("🌐 Open your browser and go to: http://localhost:8080")
            print("⌨️  Press Ctrl+C to stop")
            
            # Keep running until interrupted
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down Real-time Visualizer...")
            await visualizer.stop()
            print("✅ Real-time Visualizer stopped successfully")
        except Exception as e:
            print(f"\n❌ Error in real-time visualizer: {e}")
            print("🔄 Falling back to traditional simulation...")
            await visualizer.stop()
            return run_traditional_simulation(config, args)
    
    # Run the realtime visualizer
    try:
        return asyncio.run(run_realtime())
    except KeyboardInterrupt:
        print("\n🛑 Real-time Visualizer interrupted by user")
    except Exception as e:
        print(f"\n❌ Failed to start real-time visualizer: {e}")
        print("🔄 Falling back to traditional simulation...")
        return run_traditional_simulation(config, args)


def run_traditional_simulation(config: dict, args):
    """运行传统仿真"""
    print("=" * 60)
    print("EV Driver Simulation System - Traditional Mode")
    print("=" * 60)
    
    # Update configuration
    if args.location:
        config['location'] = args.location
    if args.vehicles:
        config['num_vehicles'] = args.vehicles
    if args.duration:
        config['simulation_duration'] = args.duration
    if args.no_animation:
        config['enable_animation'] = False
    
    # Print configuration information
    print(f"\nSimulation Configuration:")
    print(f"- Location: {config['location']}")
    print(f"- Vehicles: {config['num_vehicles']}")
    print(f"- Duration: {config['simulation_duration']} seconds")
    print(f"- Charging stations: {config['num_charging_stations']}")
    print(f"- Order generation rate: {config['order_generation_rate']} orders/hour")
    
    # Initialize data manager
    data_manager = None
    if config.get('save_data', False) or args.save_data:
        data_manager = DataManager()
    
    # Initialize simulation engine
    print("\nInitializing simulation system...")
    engine = SimulationEngine(config)
    
    # Run simulation
    if config.get('enable_animation', True) and not args.headless:
        # Run with visualization
        print("\nStarting simulation with visualization...")
        visualizer = Visualizer(engine, config)
        
        # Save animation
        if args.output:
            output_file = visualizer.save_animation(
                filename=args.output,
                format=args.format
            )
        else:
            visualizer.save_animation(format=args.format)
    else:
        # Run in headless mode
        print("\nRunning simulation (headless mode)...")
        final_stats = engine.run_simulation(config['simulation_duration'])
    
    # Get final statistics
    final_stats = engine.get_final_statistics()
    
    # Save data
    if data_manager:
        data_manager.save_simulation_results(final_stats)
        if args.report:
            data_manager.generate_report(final_stats)
        if args.excel:
            data_manager.export_to_excel(final_stats)
    
    # Print result summary
    print("\n" + "=" * 60)
    print("Simulation Completed!")
    print("=" * 60)
    print(f"\nSimulation Results Summary:")
    print(f"- Total revenue: ${final_stats['summary']['total_revenue']:.2f}")
    print(f"- Total cost: ${final_stats['summary']['total_cost']:.2f}")
    print(f"- Total profit: ${final_stats['summary']['total_profit']:.2f}")
    print(f"- Order completion rate: {final_stats['summary']['order_completion_rate']*100:.1f}%")
    print(f"- Vehicle utilization rate: {final_stats['summary']['vehicle_utilization_rate']*100:.1f}%")
    print(f"- Charging station utilization rate: {final_stats['summary']['charging_utilization_rate']*100:.1f}%")
    
    return final_stats


def run_simulation(config: dict, args):
    """Main simulation runner"""
    # Check if realtime mode is requested
    if hasattr(args, 'realtime') and args.realtime:
        return run_realtime_simulation(config, args)
    else:
        return run_traditional_simulation(config, args)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Electric Vehicle Simulation System - Simulates electric vehicle operations in cities',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default configuration (traditional simulation)
  python main.py
  
  # Specify location and number of vehicles
  python main.py -l "Beijing, China" -v 50
  
  # Run in headless mode and generate report
  python main.py --headless --save-data --report
  
  # Use custom configuration file
  python main.py -c custom_config.json
  
  # Start real-time interactive visualization (NEW!)
  python main.py --realtime
  
  # Real-time visualization with custom settings
  python main.py --realtime -l "Manhattan, New York" -v 30
        """
    )
    
    # Basic parameters
    parser.add_argument('-l', '--location', type=str,
                      help='Simulation location (default: West Lafayette, IN)')
    parser.add_argument('-v', '--vehicles', type=int,
                      help='Number of vehicles')
    parser.add_argument('-d', '--duration', type=int,
                      help='Simulation duration (seconds)')
    parser.add_argument('-c', '--config', type=str,
                      help='Configuration file path')
    
    # Output parameters (only for traditional mode)
    parser.add_argument('-o', '--output', type=str,
                      help='Output filename (without extension)')
    parser.add_argument('-f', '--format', choices=['html', 'mp4'],
                      default='html', help='Animation format (default: html)')
    
    # Run modes
    parser.add_argument('--headless', action='store_true',
                      help='Headless mode (no visualization)')
    parser.add_argument('--no-animation', action='store_true',
                      help='Disable animation generation')
    parser.add_argument('--realtime', action='store_true',
                      help='Start real-time interactive visualization server (localhost:8080)')
    
    # Data saving (only for traditional mode)
    parser.add_argument('--save-data', action='store_true',
                      help='Save simulation data')
    parser.add_argument('--report', action='store_true',
                      help='Generate simulation report')
    parser.add_argument('--excel', action='store_true',
                      help='Export Excel file')
    
    # Debug parameters
    parser.add_argument('--debug', action='store_true',
                      help='Debug mode')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.realtime and (args.headless or args.no_animation or args.save_data or args.report or args.excel):
        print("Warning: Data saving options are not applicable in real-time mode")
    
    # Load configuration
    if args.config:
        config = load_custom_config(args.config)
    else:
        config = SIMULATION_CONFIG.copy()
    
    # Run simulation
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