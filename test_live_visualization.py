#!/usr/bin/env python3
"""
Test live visualization functionality
"""

import sys
import os

# Add project root directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.simulation_config import SIMULATION_CONFIG
from core.simulation_engine import SimulationEngine
from visualization.visualizer import Visualizer


def test_live_visualization():
    """Test live visualization functionality"""
    print("🚀 Testing Live Visualization Functionality")
    print("=" * 50)
    
    # Use shorter simulation time for testing
    config = SIMULATION_CONFIG.copy()
    config.update({
        'simulation_duration': 300,  # 5 minutes
        'num_vehicles': 10,          # Fewer vehicles
        'location': 'West Lafayette, IN',
        'animation_fps': 15,         # Lower frame rate to reduce CPU usage
        'order_generation_rate': 300 # Moderate order generation rate
    })
    
    print(f"Configuration:")
    print(f"- Location: {config['location']}")
    print(f"- Number of vehicles: {config['num_vehicles']}")
    print(f"- Simulation time: {config['simulation_duration']} seconds")
    print(f"- Frame rate: {config['animation_fps']} FPS")
    print()
    
    try:
        # Initialize simulation engine
        print("Initializing simulation engine...")
        engine = SimulationEngine(config)
        
        # Initialize visualizer
        print("Initializing visualizer...")
        visualizer = Visualizer(engine, config)
        
        # Start live visualization
        print("Starting live visualization...")
        print("💡 Close matplotlib window or press Ctrl+C to stop simulation")
        print()
        
        final_stats = visualizer.run_live_simulation()
        
        # Test completed successfully
        print("\n✅ Live visualization test completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️ User interrupted test")
    except Exception as e:
        print(f"\n❌ Error occurred during test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_live_visualization() 