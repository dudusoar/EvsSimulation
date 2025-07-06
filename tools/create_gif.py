#!/usr/bin/env python3
"""
GIF Creator for Python Simulation
Create demonstration GIFs with customizable options
"""

import sys
import argparse
from pathlib import Path

# Add project path
sys.path.append(str(Path(__file__).parent.parent))

def create_demo_gif(config_file="yaml_config/gif_demos/west_lafayette_high_density.yaml", 
                   output_file="assets/demo-python-simulation.gif",
                   save_frames=False,
                   frames_dir="assets/frames",
                   max_frames=80,
                   frame_interval=3,
                   duration=15):
    """
    Create a demo GIF with customizable options
    
    Args:
        config_file: YAML config file to use
        output_file: Output GIF file path
        save_frames: Whether to save individual frame files
        frames_dir: Directory for individual frames
        max_frames: Maximum number of frames to capture
        frame_interval: Capture every N simulation steps
        duration: Simulation duration in seconds
    """
    print("🎬 EV Simulation GIF Creator")
    print("=" * 40)
    print(f"📁 Config: {config_file}")
    print(f"📁 Output: {output_file}")
    print(f"🎞️ Frames: {max_frames} (every {frame_interval} steps)")
    print(f"⏱️ Duration: {duration}s")
    print("=" * 40)
    
    try:
        # Load configuration
        from config.yaml_config_manager import config_manager
        yaml_config = config_manager.load_config(config_file)
        
        # Convert to legacy format
        legacy_config = config_manager.to_legacy_format(yaml_config)
        
        # Add GIF recording settings
        legacy_config['gif_max_frames'] = max_frames
        legacy_config['gif_frame_interval'] = frame_interval
        legacy_config['gif_output_path'] = output_file
        legacy_config['gif_frame_duration'] = 150  # ms
        
        # Frame management settings
        legacy_config['save_individual_frames'] = save_frames
        legacy_config['frames_output_dir'] = frames_dir
        legacy_config['auto_cleanup_frames'] = not save_frames
        
        # Create simulation engine
        from core.simulation_engine import SimulationEngine
        engine = SimulationEngine(legacy_config)
        
        # Create GIF recorder
        from visualization.gif_recorder import GifRecorder
        recorder = GifRecorder(engine, legacy_config)
        
        # Run simulation
        recorder.run_gif_simulation(duration=duration)
        
        print(f"\n🎉 GIF created successfully: {output_file}")
        if save_frames:
            print(f"📁 Frames saved to: {frames_dir}/")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create GIF: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Create demonstration GIFs for EV Simulation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # High density demo (default)
  python tools/create_gif.py
  
  # Light traffic demo
  python tools/create_gif.py -c yaml_config/gif_demos/west_lafayette_light_traffic.yaml
  
  # Charging focus demo  
  python tools/create_gif.py -c yaml_config/gif_demos/west_lafayette_charging_focus.yaml
  
  # Custom settings
  python tools/create_gif.py --duration 20 --max-frames 100
  
  # Save individual frames
  python tools/create_gif.py --save-frames
        """
    )
    
    parser.add_argument('-c', '--config', 
                       default='yaml_config/gif_demos/west_lafayette_high_density.yaml',
                       help='YAML config file to use')
    parser.add_argument('-o', '--output', 
                       default='assets/demo-python-simulation.gif',
                       help='Output GIF file path')
    parser.add_argument('--save-frames', action='store_true',
                       help='Save individual frame files')
    parser.add_argument('--frames-dir', default='assets/frames',
                       help='Directory for individual frames')
    parser.add_argument('--max-frames', type=int, default=80,
                       help='Maximum number of frames (default: 80)')
    parser.add_argument('--frame-interval', type=int, default=3,
                       help='Capture every N simulation steps (default: 3)')
    parser.add_argument('--duration', type=float, default=15,
                       help='Simulation duration in seconds (default: 15)')
    
    args = parser.parse_args()
    
    # Create GIF
    success = create_demo_gif(
        config_file=args.config,
        output_file=args.output,
        save_frames=args.save_frames,
        frames_dir=args.frames_dir,
        max_frames=args.max_frames,
        frame_interval=args.frame_interval,
        duration=args.duration
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 