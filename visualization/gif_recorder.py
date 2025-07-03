"""
GIF Recorder for Python Simulation
Automatically captures frames during simulation and generates GIF
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image
import io
import os
from pathlib import Path
from typing import List, Optional
import time

from visualization.visualizer import Visualizer


class GifRecorder(Visualizer):
    """Extended Visualizer that can record simulation as GIF"""
    
    def __init__(self, simulation_engine, config: dict):
        """Initialize GIF recorder"""
        super().__init__(simulation_engine, config)
        
        # Recording parameters
        self.recording = False
        self.frames = []
        self.max_frames = config.get('gif_max_frames', 150)  # Limit frames to keep file size reasonable
        self.frame_interval = config.get('gif_frame_interval', 5)  # Capture every N steps
        self.step_counter = 0
        
        # Output settings
        self.output_path = config.get('gif_output_path', 'assets/demo-python-simulation.gif')
        self.gif_duration = config.get('gif_frame_duration', 200)  # ms per frame
        
        # Frame management options
        self.save_individual_frames = config.get('save_individual_frames', False)
        self.frames_dir = config.get('frames_output_dir', 'assets/frames')
        self.auto_cleanup = config.get('auto_cleanup_frames', True)
        
    def start_recording(self):
        """Start recording frames"""
        self.recording = True
        self.frames = []
        self.step_counter = 0
        print(f"🎬 Started GIF recording - will capture max {self.max_frames} frames")
        
    def stop_recording(self):
        """Stop recording and generate GIF"""
        self.recording = False
        print(f"🎬 Stopped recording - captured {len(self.frames)} frames")
        
    def capture_frame(self):
        """Capture current matplotlib figure as frame"""
        if not self.recording or len(self.frames) >= self.max_frames:
            return
            
        # Capture current figure
        buf = io.BytesIO()
        self.fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        
        # Convert to PIL Image and load data immediately
        frame = Image.open(buf)
        frame.load()  # Load the image data into memory
        
        # Now safe to close buffer
        buf.close()
        
        # Save individual frame if requested
        if self.save_individual_frames:
            self._save_individual_frame(frame, len(self.frames))
        
        # Store in memory for GIF creation
        self.frames.append(frame)
    
    def _save_individual_frame(self, frame: Image.Image, frame_number: int):
        """Save individual frame to disk"""
        try:
            # Ensure frames directory exists
            frames_path = Path(self.frames_dir)
            frames_path.mkdir(parents=True, exist_ok=True)
            
            # Save frame with zero-padded number
            frame_file = frames_path / f"frame_{frame_number:04d}.png"
            frame.save(frame_file, format='PNG', optimize=True)
            
        except Exception as e:
            print(f"⚠️ Failed to save frame {frame_number}: {e}")
    
    def cleanup_frames(self):
        """Clear frames from memory and optionally delete frame files"""
        # Clear memory
        memory_frames = len(self.frames)
        self.frames.clear()
        
        if memory_frames > 0:
            print(f"🧹 Cleaned up {memory_frames} frames from memory")
        
        # Optionally remove frame files
        if self.auto_cleanup and self.save_individual_frames:
            try:
                frames_path = Path(self.frames_dir)
                if frames_path.exists():
                    frame_files = list(frames_path.glob("frame_*.png"))
                    for frame_file in frame_files:
                        frame_file.unlink()
                    if frame_files:
                        print(f"🗑️ Removed {len(frame_files)} frame files from disk")
                    # Remove empty directory
                    if not any(frames_path.iterdir()):
                        frames_path.rmdir()
            except Exception as e:
                print(f"⚠️ Failed to cleanup frame files: {e}")
    
    def export_frames(self, export_dir: str = None) -> bool:
        """Export current frames to individual PNG files"""
        if not self.frames:
            print("❌ No frames to export")
            return False
        
        if export_dir is None:
            export_dir = self.frames_dir
            
        try:
            export_path = Path(export_dir)
            export_path.mkdir(parents=True, exist_ok=True)
            
            print(f"📤 Exporting {len(self.frames)} frames to {export_dir}")
            
            for i, frame in enumerate(self.frames):
                frame_file = export_path / f"frame_{i:04d}.png"
                frame.save(frame_file, format='PNG', optimize=True)
            
            print(f"✅ Frames exported successfully to {export_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to export frames: {e}")
            return False
        
    def save_gif(self) -> bool:
        """Save recorded frames as GIF"""
        if not self.frames:
            print("❌ No frames recorded")
            return False
            
        try:
            # Ensure output directory exists
            output_path = Path(self.output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"💾 Saving GIF with {len(self.frames)} frames to {self.output_path}")
            
            # Save as GIF
            self.frames[0].save(
                self.output_path,
                save_all=True,
                append_images=self.frames[1:],
                duration=self.gif_duration,
                loop=0,
                optimize=True
            )
            
            # Get file size
            file_size = os.path.getsize(self.output_path)
            print(f"✅ GIF saved successfully!")
            print(f"   📁 Path: {self.output_path}")
            print(f"   📏 Size: {file_size / 1024 / 1024:.2f} MB")
            print(f"   🎞️ Frames: {len(self.frames)}")
            print(f"   ⏱️ Duration: ~{len(self.frames) * self.gif_duration / 1000:.1f} seconds")
            
            # Auto cleanup if enabled
            if self.auto_cleanup:
                self.cleanup_frames()
            else:
                print(f"💡 Call cleanup_frames() to free memory, or export_frames() to save individual frames")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to save GIF: {e}")
            return False
    
    def run_gif_simulation(self, duration: float = 60, auto_record: bool = True):
        """
        Run simulation optimized for GIF recording
        
        Args:
            duration: Simulation duration in seconds (shorter for GIF)
            auto_record: Automatically start/stop recording
        """
        print(f"🎬 Starting GIF Recording Simulation")
        print(f"⏱️ Duration: {duration}s")
        print(f"🎞️ Max frames: {self.max_frames}")
        print(f"📈 Frame interval: every {self.frame_interval} steps")
        print("=" * 50)
        
        # Enable interactive mode
        plt.ion()
        plt.show()
        
        # Start recording if auto mode
        if auto_record:
            self.start_recording()
        
        # Initialize display
        self._clear_dynamic_elements()
        
        try:
            while self.engine.current_time < duration and len(self.frames) < self.max_frames:
                # Run simulation step
                self.engine.run_step()
                self.step_counter += 1
                
                # Update display
                self._update_live_display()
                
                # Capture frame at intervals
                if self.recording and self.step_counter % self.frame_interval == 0:
                    self.capture_frame()
                
                # Refresh display
                self.fig.canvas.draw()
                self.fig.canvas.flush_events()
                
                # Check if window was closed
                if not plt.get_fignums():
                    print("\n🛑 Window closed")
                    break
                
                # Fast simulation for GIF
                plt.pause(0.01)
                
                # Progress update
                if self.step_counter % 50 == 0:
                    progress = (self.engine.current_time / duration) * 100
                    frames_captured = len(self.frames)
                    print(f"Progress: {progress:.1f}% | Frames: {frames_captured}/{self.max_frames}")
        
        except KeyboardInterrupt:
            print("\n🛑 Recording interrupted")
        
        finally:
            # Stop recording and save GIF
            if auto_record and self.recording:
                self.stop_recording()
                success = self.save_gif()
                
                if success:
                    print(f"\n🎉 GIF recording completed!")
                    print(f"📁 File saved: {self.output_path}")
                else:
                    print(f"\n❌ GIF recording failed")
            
            plt.ioff()
            
            return self.engine.get_final_statistics()


def create_demo_gif(config_file: str = "west_lafayette_demo.yaml", 
                   output_file: str = "assets/demo-python-simulation.gif"):
    """
    Create a demo GIF from simulation
    
    Args:
        config_file: YAML config file to use
        output_file: Output GIF file path
    """
    print("🎬 Creating Demo GIF for Python Simulation")
    print("=" * 50)
    
    try:
        # Load configuration
        from config.yaml_config_manager import config_manager
        yaml_config = config_manager.load_config(config_file)
        
        # Convert to legacy format
        legacy_config = config_manager.to_legacy_format(yaml_config)
        
        # Add GIF recording settings
        legacy_config['gif_max_frames'] = 100
        legacy_config['gif_frame_interval'] = 3
        legacy_config['gif_output_path'] = output_file
        legacy_config['gif_frame_duration'] = 150  # ms
        
        # Frame management settings
        legacy_config['save_individual_frames'] = False  # Don't save individual frames by default
        legacy_config['frames_output_dir'] = 'assets/frames'
        legacy_config['auto_cleanup_frames'] = True  # Clean up memory after GIF creation
        
        # Create simulation engine
        from core.simulation_engine import SimulationEngine
        engine = SimulationEngine(legacy_config)
        
        # Create GIF recorder
        recorder = GifRecorder(engine, legacy_config)
        
        # Run simulation (shorter duration for demo)
        recorder.run_gif_simulation(duration=45)
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create demo GIF: {e}")
        return False


if __name__ == "__main__":
    """Run this script directly to create a demo GIF"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Create demo GIF from Python simulation')
    parser.add_argument('-c', '--config', default='west_lafayette_demo.yaml',
                       help='Config file to use')
    parser.add_argument('-o', '--output', default='assets/demo-python-simulation.gif',
                       help='Output GIF file path')
    
    args = parser.parse_args()
    
    success = create_demo_gif(args.config, args.output)
    if success:
        print("🎉 Demo GIF creation completed!")
    else:
        print("❌ Demo GIF creation failed!") 