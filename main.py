"""
Electric Vehicle Simulation System Main Program
Program entry point, handles command line arguments and coordinates module execution
"""

import argparse
import sys
import json
from datetime import datetime
import os

from config.simulation_config import SIMULATION_CONFIG
from core.simulation_engine import SimulationEngine
from visualization.visualizer import Visualizer
from data.data_manager import DataManager


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


def run_simulation(config: dict, args):
    """Run simulation with different visualization modes"""
    print("=" * 60)
    print("EV Driver Simulation System")
    print("=" * 60)
    
    # Update configuration
    if args.location:
        config['location'] = args.location
    if args.vehicles:
        config['num_vehicles'] = args.vehicles
    if args.duration:
        config['simulation_duration'] = args.duration
    
    # Determine mode
    if args.headless:
        mode = "Headless Mode"
    else:
        mode = "Live Visualization Mode"
    
    # Print configuration information
    print(f"\nSimulation Configuration ({mode}):")
    print(f"- Location: {config['location']}")
    print(f"- Vehicles: {config['num_vehicles']}")
    print(f"- Duration: {config['simulation_duration']} seconds")
    print(f"- Charging stations: {config['num_charging_stations']}")
    print(f"- Order generation rate: {config['order_generation_rate']} orders/hour")
    
    # Initialize data manager (only if data saving is requested)
    data_manager = None
    if config.get('save_data', False) or args.save_data:
        data_manager = DataManager(
            location=config['location'],
            num_vehicles=config['num_vehicles'],
            duration=config['simulation_duration']
        )
        print(f"- Data saving: Enabled")
    else:
        print(f"- Data saving: Disabled (add --save-data to enable)")
    
    # Initialize simulation engine
    print("\nInitializing simulation system...")
    engine = SimulationEngine(config)
    
    # Run simulation based on mode
    if args.headless:
        # Run in headless mode
        print("\nRunning simulation (headless mode)...")
        final_stats = engine.run_simulation(config['simulation_duration'])
    else:
        # Run with live visualization (default mode)
        print("\nStarting live simulation visualization...")
        visualizer = Visualizer(engine, config)
        final_stats = visualizer.run_live_simulation(config['simulation_duration'])
    
    # Save data and generate reports (only if requested)
    if data_manager:
        print("\nSaving simulation data...")
        data_manager.save_simulation_results(final_stats)
        
        if args.report:
            print("Generating detailed report...")
            data_manager.generate_report(final_stats)
            
        if args.excel:
            print("Exporting to Excel...")
            data_manager.export_to_excel(final_stats)
    
    # Print result summary (only for headless mode as others show detailed stats)
    if args.headless:
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


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Electric Vehicle Simulation System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Live visualization (default) - matplotlib visualization with real-time updates
  python main.py
  
  # Live visualization with data saving
  python main.py --save-data
  
  # Live visualization with full report and Excel export
  python main.py --save-data --report --excel
  
  # Specify location and number of vehicles  
  python main.py -l "Beijing, China" -v 50
  
  # Run in headless mode for batch processing
  python main.py --headless --save-data --report
  
  # Use custom configuration file
  python main.py -c custom_config.json
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
    
    # Run modes  
    parser.add_argument('--headless', action='store_true',
                      help='Headless mode (no visualization, for batch processing)')
    
    # Data saving options (optional for both modes)
    parser.add_argument('--save-data', action='store_true',
                      help='Save simulation data (JSON + CSV files)')
    parser.add_argument('--report', action='store_true',
                      help='Generate detailed simulation report (requires --save-data)')
    parser.add_argument('--excel', action='store_true',
                      help='Export results to Excel file (requires --save-data)')
    
    # Debug parameters
    parser.add_argument('--debug', action='store_true',
                      help='Debug mode')
    
    args = parser.parse_args()
    
    # Validate arguments  
    # No validation needed - only headless or live mode
    
    if (args.report or args.excel) and not args.save_data:
        print("Warning: --report and --excel require --save-data to be enabled")
        print("         Adding --save-data automatically")
        args.save_data = True
    
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