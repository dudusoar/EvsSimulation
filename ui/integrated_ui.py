#!/usr/bin/env python3
"""
Integrated EV Simulation UI
Real integration with existing simulation system
"""

import dearpygui.dearpygui as dpg
import numpy as np
import threading
import time
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.simulation_engine import SimulationEngine
    SIMULATION_AVAILABLE = True
    print("Simulation modules loaded successfully")
except ImportError as e:
    print(f"Warning: Simulation modules not available: {e}")
    SIMULATION_AVAILABLE = False


class IntegratedSimulationUI:
    """Integrated simulation UI with real backend"""
    
    def __init__(self):
        self.simulation_engine = None
        self.is_running = False
        self.is_paused = False
        self.simulation_thread = None
        
        # Simulation parameters
        self.sim_params = {
            'location': 'West Lafayette, Indiana',
            'duration': 3600,
            'num_vehicles': 20,
            'num_charging_stations': 8,
            'vehicle_speed': 15.0,
            'battery_capacity': 75.0,
            'time_step': 0.1
        }

    def setup_ui(self):
        """Setup UI interface"""
        with dpg.window(label="Integrated EV Simulation System", tag="main_window"):
            
            # Status warning if simulation not available
            if not SIMULATION_AVAILABLE:
                dpg.add_text("WARNING: Simulation modules not available", color=[255, 100, 100])
                dpg.add_separator()
            
            # Three-panel layout
            with dpg.group(horizontal=True):
                
                # Left panel: Parameters
                with dpg.child_window(label="Parameters", width=300, height=600, border=True):
                    dpg.add_text("Simulation Configuration", color=[100, 200, 255])
                    dpg.add_separator()
                    
                    dpg.add_text("Basic Parameters:")
                    dpg.add_slider_int(label="Duration (s)", default_value=3600, 
                                     min_value=300, max_value=7200, tag="duration",
                                     callback=lambda s, v: self.update_param('duration', v))
                    
                    dpg.add_slider_int(label="Vehicles", default_value=20, 
                                     min_value=5, max_value=50, tag="vehicles",
                                     callback=lambda s, v: self.update_param('num_vehicles', v))
                    
                    dpg.add_slider_int(label="Charging Stations", default_value=8, 
                                     min_value=3, max_value=20, tag="stations",
                                     callback=lambda s, v: self.update_param('num_charging_stations', v))
                    
                    dpg.add_separator()
                    dpg.add_text("Vehicle Config:")
                    dpg.add_slider_float(label="Speed (m/s)", default_value=15.0, 
                                       min_value=5.0, max_value=30.0, format="%.1f",
                                       callback=lambda s, v: self.update_param('vehicle_speed', v))
                    
                    dpg.add_slider_float(label="Battery (kWh)", default_value=75.0, 
                                       min_value=40.0, max_value=100.0, format="%.1f",
                                       callback=lambda s, v: self.update_param('battery_capacity', v))
                    
                    dpg.add_separator()
                    dpg.add_text("Map Selection:")
                    dpg.add_combo(label="Location", 
                                items=["West Lafayette, Indiana", "New York City, NY"],
                                default_value="West Lafayette, Indiana",
                                callback=lambda s, v: self.update_param('location', v))
                    
                    dpg.add_separator()
                    dpg.add_button(label="Initialize Simulation", 
                                 callback=self.initialize_simulation, 
                                 width=-1, height=50, tag="init_btn")
                
                # Center panel: Map
                with dpg.child_window(label="Map View", width=700, height=600, border=True):
                    dpg.add_text("Real-time Map Display", color=[100, 255, 100])
                    dpg.add_separator()
                    
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Zoom In", callback=lambda: print("Zoom in"))
                        dpg.add_button(label="Zoom Out", callback=lambda: print("Zoom out"))
                        dpg.add_button(label="Reset View", callback=lambda: print("Reset"))
                    
                    dpg.add_separator()
                    dpg.add_text("Map will display here after initialization", tag="map_placeholder")
                    dpg.add_text("Status: Ready", tag="map_status")
                
                # Right panel: Metrics
                with dpg.child_window(label="Metrics", width=300, height=600, border=True):
                    dpg.add_text("Performance Indicators", color=[255, 200, 100])
                    dpg.add_separator()
                    
                    dpg.add_text("Progress:")
                    dpg.add_progress_bar(tag="progress", default_value=0.0, overlay="0%")
                    dpg.add_text("00:00:00 / 01:00:00", tag="time_display")
                    
                    dpg.add_separator()
                    dpg.add_text("Fleet Status:")
                    dpg.add_text("Active Vehicles: 0", tag="active_vehicles")
                    dpg.add_text("Average Battery: 0%", tag="avg_battery")
                    dpg.add_text("Utilization: 0%", tag="utilization")
                    
                    dpg.add_separator()
                    dpg.add_text("Orders:")
                    dpg.add_text("Pending: 0", tag="pending_orders")
                    dpg.add_text("Active: 0", tag="active_orders")
                    dpg.add_text("Completed: 0", tag="completed_orders")
                    
                    dpg.add_separator()
                    dpg.add_text("Financial:")
                    dpg.add_text("Revenue: $0.00", tag="total_revenue")
                    dpg.add_text("Per Hour: $0.00", tag="hourly_revenue")
            
            dpg.add_separator()
            
            # Control panel
            with dpg.group(horizontal=True):
                dpg.add_text("Control:", color=[255, 255, 100])
                
                dpg.add_button(label="Start", callback=self.start_simulation, 
                             tag="start_btn", width=80, height=35)
                dpg.add_button(label="Pause", callback=self.pause_simulation, 
                             tag="pause_btn", width=80, height=35, enabled=False)
                dpg.add_button(label="Stop", callback=self.stop_simulation, 
                             tag="stop_btn", width=80, height=35, enabled=False)
                dpg.add_button(label="Reset", callback=self.reset_simulation, 
                             tag="reset_btn", width=80, height=35)
                
                dpg.add_text("Speed:")
                dpg.add_slider_float(label="", default_value=1.0, min_value=0.1, max_value=5.0,
                                   format="%.1fx", width=120, tag="speed_control")

    def update_param(self, param_name, value):
        """Update simulation parameter"""
        self.sim_params[param_name] = value
        print(f"Updated {param_name}: {value}")

    def initialize_simulation(self):
        """Initialize simulation"""
        try:
            dpg.configure_item("init_btn", enabled=False)
            dpg.set_value("map_status", "Initializing...")
            
            if not SIMULATION_AVAILABLE:
                dpg.set_value("map_status", "Demo mode - modules not available")
                dpg.configure_item("start_btn", enabled=True)
                dpg.configure_item("init_btn", enabled=True)
                return
            
            print(f"Initializing simulation for {self.sim_params['location']}...")
            
            # Create config for simulation engine
            config = {
                'location': self.sim_params['location'],
                'num_vehicles': self.sim_params['num_vehicles'],
                'num_charging_stations': self.sim_params['num_charging_stations'],
                'vehicle_config': {
                    'max_speed': self.sim_params['vehicle_speed'],
                    'battery_capacity': self.sim_params['battery_capacity']
                },
                'time_step': self.sim_params['time_step']
            }
            
            # Initialize simulation engine
            self.simulation_engine = SimulationEngine(config)
            
            dpg.set_value("map_status", f"Ready - {self.sim_params['location']}")
            dpg.configure_item("start_btn", enabled=True)
            dpg.configure_item("init_btn", enabled=True)
            
            print("Simulation initialized successfully!")
            
        except Exception as e:
            print(f"Initialization failed: {e}")
            dpg.set_value("map_status", f"Error: {str(e)}")
            dpg.configure_item("init_btn", enabled=True)

    def start_simulation(self):
        """Start simulation"""
        if not SIMULATION_AVAILABLE or not self.simulation_engine:
            print("Simulation not available or not initialized")
            return
        
        self.is_running = True
        self.is_paused = False
        
        dpg.configure_item("start_btn", enabled=False)
        dpg.configure_item("pause_btn", enabled=True)
        dpg.configure_item("stop_btn", enabled=True)
        
        # Start simulation thread
        self.simulation_thread = threading.Thread(target=self.simulation_loop, daemon=True)
        self.simulation_thread.start()
        
        print("Simulation started!")

    def pause_simulation(self):
        """Pause/resume simulation"""
        self.is_paused = not self.is_paused
        if self.is_paused:
            dpg.set_item_label("pause_btn", "Resume")
            print("Paused")
        else:
            dpg.set_item_label("pause_btn", "Pause")
            print("Resumed")

    def stop_simulation(self):
        """Stop simulation"""
        self.is_running = False
        dpg.configure_item("start_btn", enabled=True)
        dpg.configure_item("pause_btn", enabled=False)
        dpg.configure_item("stop_btn", enabled=False)
        dpg.set_item_label("pause_btn", "Pause")
        print("Stopped")

    def reset_simulation(self):
        """Reset simulation"""
        self.stop_simulation()
        # Reset display
        dpg.set_value("progress", 0.0)
        dpg.set_value("time_display", "00:00:00 / 01:00:00")
        print("Reset")

    def simulation_loop(self):
        """Main simulation loop"""
        while self.is_running:
            if not self.is_paused:
                try:
                    # Run simulation step
                    self.simulation_engine.run_step()
                    
                    # Update UI
                    self.update_display()
                    
                    # Check completion
                    if self.simulation_engine.current_time >= self.sim_params['duration']:
                        self.stop_simulation()
                        break
                        
                except Exception as e:
                    print(f"Simulation error: {e}")
                    self.stop_simulation()
                    break
            
            time.sleep(0.1)

    def update_display(self):
        """Update UI display with real data"""
        if not self.simulation_engine:
            return
        
        try:
            # Get statistics
            stats = self.simulation_engine.get_current_statistics()
            
            # Update progress
            progress = self.simulation_engine.current_time / self.sim_params['duration']
            dpg.set_value("progress", progress)
            dpg.configure_item("progress", overlay=f"{progress*100:.1f}%")
            
            # Update time
            current = int(self.simulation_engine.current_time)
            total = self.sim_params['duration']
            time_str = f"{current//3600:02d}:{(current%3600)//60:02d}:{current%60:02d} / {total//3600:02d}:{(total%3600)//60:02d}:{total%60:02d}"
            dpg.set_value("time_display", time_str)
            
            # Update metrics
            vehicles = len(self.simulation_engine.get_vehicles())
            dpg.set_value("active_vehicles", f"Active Vehicles: {vehicles}")
            
            if 'vehicles' in stats:
                avg_battery = stats['vehicles'].get('avg_battery_percentage', 0)
                utilization = stats['vehicles'].get('utilization_rate', 0) * 100
                dpg.set_value("avg_battery", f"Average Battery: {avg_battery:.1f}%")
                dpg.set_value("utilization", f"Utilization: {utilization:.1f}%")
            
            if 'orders' in stats:
                pending = len(stats['orders'].get('pending', []))
                active = len(stats['orders'].get('active', []))
                completed = stats['orders'].get('total_orders_completed', 0)
                revenue = stats['orders'].get('total_revenue', 0)
                
                dpg.set_value("pending_orders", f"Pending: {pending}")
                dpg.set_value("active_orders", f"Active: {active}")
                dpg.set_value("completed_orders", f"Completed: {completed}")
                dpg.set_value("total_revenue", f"Revenue: ${revenue:.2f}")
                
                if self.simulation_engine.current_time > 0:
                    hourly = revenue / (self.simulation_engine.current_time / 3600)
                    dpg.set_value("hourly_revenue", f"Per Hour: ${hourly:.2f}")
                    
        except Exception as e:
            print(f"Display update error: {e}")

    def run(self):
        """Run the application"""
        dpg.create_context()
        
        # Dark theme
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (22, 22, 22))
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (30, 30, 30))
                dpg.add_theme_color(dpg.mvThemeCol_Button, (51, 122, 183))
        
        dpg.bind_theme(theme)
        self.setup_ui()
        
        dpg.create_viewport(title="Integrated EV Simulation", width=1400, height=800)
        dpg.setup_dearpygui()
        dpg.set_primary_window("main_window", True)
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()


def main():
    """Main function"""
    print("Starting Integrated EV Simulation UI...")
    app = IntegratedSimulationUI()
    app.run()


if __name__ == "__main__":
    main() 