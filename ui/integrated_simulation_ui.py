#!/usr/bin/env python3
"""
Integrated EV Simulation UI with DearPyGui
Real integration with existing simulation system
"""

import dearpygui.dearpygui as dpg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import threading
import time
from typing import Dict, Any, List, Tuple
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.simulation_engine import SimulationEngine
    from core.map_manager import MapManager
    from config.simulation_config import VEHICLE_STATUS
    SIMULATION_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Simulation modules not available: {e}")
    SIMULATION_AVAILABLE = False


class IntegratedSimulationUI:
    """Integrated simulation UI with real backend"""
    
    def __init__(self):
        """Initialize UI"""
        self.simulation_engine = None
        self.map_manager = None
        
        # Simulation control state
        self.is_running = False
        self.is_paused = False
        self.simulation_thread = None
        self.speed_multiplier = 1.0
        
        # UI configuration
        self.config = {
            'window_width': 1600,
            'window_height': 1000,
            'map_width': 800,
            'map_height': 600,
            'panel_width': 300
        }
        
        # Map visualization
        self.map_texture = None
        self.map_figure = None
        self.map_ax = None
        
        # Simulation parameters
        self.sim_params = {
            'location': 'West Lafayette, Indiana',
            'duration': 3600,
            'num_vehicles': 20,
            'num_charging_stations': 8,
            'vehicle_speed': 15.0,
            'charging_power': 50.0,
            'battery_capacity': 75.0,
            'time_step': 0.1
        }
        
        # Metrics data
        self.metrics = {
            'simulation_time': 0.0,
            'active_vehicles': 0,
            'pending_orders': 0,
            'active_orders': 0,
            'completed_orders': 0,
            'total_revenue': 0.0,
            'avg_battery': 0.0,
            'vehicle_utilization': 0.0
        }

    def create_context(self):
        """Create DearPyGui context"""
        dpg.create_context()
        dpg.create_viewport(
            title="Integrated EV Simulation System",
            width=self.config['window_width'],
            height=self.config['window_height'],
            resizable=True
        )
        dpg.setup_dearpygui()

    def setup_ui(self):
        """Setup UI layout"""
        # Main window
        with dpg.window(label="EV Simulation System", tag="main_window"):
            
            # Status bar
            if not SIMULATION_AVAILABLE:
                dpg.add_text("WARNING: Simulation modules not available - Running in demo mode", 
                           color=[255, 100, 100])
                dpg.add_separator()
            
            # Horizontal layout
            with dpg.group(horizontal=True):
                
                # Left panel: Parameter control
                self.create_parameter_panel()
                
                # Center panel: Map display
                self.create_map_area()
                
                # Right panel: Metrics monitoring
                self.create_metrics_panel()
            
            # Bottom panel: Simulation control
            self.create_control_panel()

    def create_parameter_panel(self):
        """Create parameter control panel"""
        with dpg.child_window(
            label="Simulation Parameters",
            width=self.config['panel_width'],
            height=700,
            border=True
        ):
            dpg.add_text("Simulation Configuration", color=[100, 200, 255])
            dpg.add_separator()
            
            # Basic parameters
            dpg.add_text("Basic Parameters:")
            
            dpg.add_slider_int(
                label="Duration (s)",
                default_value=self.sim_params['duration'],
                min_value=300,
                max_value=7200,
                tag="duration_slider",
                callback=lambda s, v: self.update_param('duration', v)
            )
            
            dpg.add_slider_int(
                label="Vehicles",
                default_value=self.sim_params['num_vehicles'],
                min_value=5,
                max_value=50,
                tag="vehicles_slider",
                callback=lambda s, v: self.update_param('num_vehicles', v)
            )
            
            dpg.add_slider_int(
                label="Charging Stations",
                default_value=self.sim_params['num_charging_stations'],
                min_value=3,
                max_value=20,
                tag="stations_slider",
                callback=lambda s, v: self.update_param('num_charging_stations', v)
            )
            
            dpg.add_separator()
            dpg.add_text("Vehicle Configuration:")
            
            dpg.add_slider_float(
                label="Speed (m/s)",
                default_value=self.sim_params['vehicle_speed'],
                min_value=5.0,
                max_value=30.0,
                format="%.1f",
                tag="speed_slider",
                callback=lambda s, v: self.update_param('vehicle_speed', v)
            )
            
            dpg.add_slider_float(
                label="Battery (kWh)",
                default_value=self.sim_params['battery_capacity'],
                min_value=40.0,
                max_value=100.0,
                format="%.1f",
                tag="battery_slider",
                callback=lambda s, v: self.update_param('battery_capacity', v)
            )
            
            dpg.add_slider_float(
                label="Charging (kW)",
                default_value=self.sim_params['charging_power'],
                min_value=25.0,
                max_value=150.0,
                format="%.1f",
                tag="charging_slider",
                callback=lambda s, v: self.update_param('charging_power', v)
            )
            
            dpg.add_separator()
            
            # Map configuration
            dpg.add_text("Map Configuration:")
            dpg.add_combo(
                label="Location",
                items=["West Lafayette, Indiana", "New York City, NY", "San Francisco, CA"],
                default_value="West Lafayette, Indiana",
                tag="location_combo",
                callback=lambda s, v: self.update_param('location', v)
            )
            
            dpg.add_separator()
            
            # Initialize button
            dpg.add_button(
                label="Initialize Simulation",
                callback=self.initialize_simulation,
                tag="init_button",
                width=-1,
                height=50
            )

    def create_map_area(self):
        """Create map display area"""
        with dpg.child_window(
            label="Real-time Map",
            width=self.config['map_width'],
            height=700,
            border=True
        ):
            dpg.add_text("Real-time Map View", color=[100, 255, 100])
            dpg.add_separator()
            
            # Map toolbar
            with dpg.group(horizontal=True):
                dpg.add_button(label="Zoom In", callback=self.zoom_in)
                dpg.add_button(label="Zoom Out", callback=self.zoom_out)
                dpg.add_button(label="Reset View", callback=self.reset_view)
                dpg.add_button(label="Update Map", callback=self.update_map_display)
            
            dpg.add_separator()
            
            # Map image display area
            # Create placeholder texture first
            self.create_placeholder_texture()
            
            dpg.add_image(
                "map_texture",
                width=self.config['map_width'] - 20,
                height=self.config['map_height'] - 100,
                tag="map_image"
            )
            
            # Map status
            dpg.add_text("Map Status: Ready", tag="map_status")

    def create_placeholder_texture(self):
        """Create placeholder texture for map"""
        # Create a simple placeholder image
        placeholder = np.ones((400, 600, 3), dtype=np.float32) * 0.2
        placeholder[180:220, 280:320] = [0.5, 0.5, 0.8]  # Blue rectangle
        
        with dpg.texture_registry():
            dpg.add_raw_texture(
                width=600,
                height=400,
                default_value=placeholder.flatten(),
                format=dpg.mvFormat_Float_rgb,
                tag="map_texture"
            )

    def create_metrics_panel(self):
        """Create metrics monitoring panel"""
        with dpg.child_window(
            label="Real-time Metrics",
            width=self.config['panel_width'],
            height=700,
            border=True
        ):
            dpg.add_text("Performance Indicators", color=[255, 200, 100])
            dpg.add_separator()
            
            # Simulation progress
            dpg.add_text("Simulation Progress:")
            dpg.add_progress_bar(tag="sim_progress", default_value=0.0, overlay="0%")
            dpg.add_text("00:00:00 / 01:00:00", tag="time_display")
            
            dpg.add_separator()
            dpg.add_text("Fleet Status:")
            
            # Vehicle metrics
            dpg.add_text("Active Vehicles: 0", tag="active_vehicles")
            dpg.add_text("Average Battery: 0%", tag="avg_battery")
            dpg.add_text("Vehicle Utilization: 0%", tag="vehicle_util")
            
            dpg.add_separator()
            dpg.add_text("Order Management:")
            
            # Order metrics
            dpg.add_text("Pending Orders: 0", tag="pending_orders")
            dpg.add_text("Active Orders: 0", tag="active_orders")
            dpg.add_text("Completed Orders: 0", tag="completed_orders")
            
            dpg.add_separator()
            dpg.add_text("Financial Performance:")
            
            # Financial metrics
            dpg.add_text("Total Revenue: $0.00", tag="total_revenue")
            dpg.add_text("Revenue/Hour: $0.00", tag="revenue_hour")
            
            dpg.add_separator()
            
            # Real-time chart
            dpg.add_text("Performance Charts:")
            with dpg.plot(
                label="Real-time Metrics",
                height=200,
                width=-1,
                tag="metrics_plot"
            ):
                dpg.add_plot_axis(dpg.mvXAxis, label="Time", tag="x_axis")
                dpg.add_plot_axis(dpg.mvYAxis, label="Value", tag="y_axis")

    def create_control_panel(self):
        """Create simulation control panel"""
        dpg.add_separator()
        
        with dpg.group(horizontal=True):
            dpg.add_text("Simulation Control:", color=[255, 255, 100])
            
            # Control buttons
            dpg.add_button(
                label="Start",
                callback=self.start_simulation,
                tag="start_button",
                width=100,
                height=40
            )
            
            dpg.add_button(
                label="Pause",
                callback=self.pause_simulation,
                tag="pause_button",
                width=100,
                height=40,
                enabled=False
            )
            
            dpg.add_button(
                label="Stop",
                callback=self.stop_simulation,
                tag="stop_button",
                width=100,
                height=40,
                enabled=False
            )
            
            dpg.add_button(
                label="Reset",
                callback=self.reset_simulation,
                tag="reset_button",
                width=100,
                height=40
            )
            
            # Speed control
            dpg.add_text("Speed:")
            dpg.add_slider_float(
                label="",
                default_value=1.0,
                min_value=0.1,
                max_value=10.0,
                format="%.1fx",
                width=150,
                tag="speed_control",
                callback=self.adjust_speed
            )

    def update_param(self, param_name: str, value: Any):
        """Update simulation parameter"""
        self.sim_params[param_name] = value
        print(f"Parameter updated: {param_name} = {value}")

    def initialize_simulation(self):
        """Initialize simulation system"""
        try:
            # Disable button
            dpg.configure_item("init_button", enabled=False)
            
            # Update status
            dpg.set_value("map_status", "Initializing simulation...")
            
            if not SIMULATION_AVAILABLE:
                dpg.set_value("map_status", "Demo mode - Simulation modules not available")
                dpg.configure_item("start_button", enabled=True)
                dpg.configure_item("init_button", enabled=True)
                return
            
            print(f"Initializing simulation for {self.sim_params['location']}...")
            
            # Create simulation configuration
            config = {
                'location': self.sim_params['location'],
                'num_vehicles': self.sim_params['num_vehicles'],
                'num_charging_stations': self.sim_params['num_charging_stations'],
                'vehicle_config': {
                    'max_speed': self.sim_params['vehicle_speed'],
                    'battery_capacity': self.sim_params['battery_capacity']
                },
                'charging_config': {
                    'charging_power': self.sim_params['charging_power']
                },
                'time_step': self.sim_params['time_step']
            }
            
            # Initialize simulation engine
            self.simulation_engine = SimulationEngine(config)
            self.map_manager = self.simulation_engine.map_manager
            
            # Setup map display
            self.setup_map_display()
            
            # Update UI state
            dpg.set_value("map_status", f"Ready - {self.sim_params['location']}")
            dpg.configure_item("start_button", enabled=True)
            dpg.configure_item("init_button", enabled=True)
            
            print("Simulation initialized successfully!")
            
        except Exception as e:
            print(f"Initialization failed: {e}")
            dpg.set_value("map_status", f"Error: {str(e)}")
            dpg.configure_item("init_button", enabled=True)

    def setup_map_display(self):
        """Setup map display"""
        if not self.map_manager:
            return
        
        try:
            # Create matplotlib figure
            self.map_figure, self.map_ax = self.map_manager.setup_plot(show_preview=False)
            self.map_figure.set_size_inches(8, 6)
            
            # Add initial elements
            self.add_simulation_elements_to_map()
            
            # Convert to texture
            self.update_map_texture()
            
        except Exception as e:
            print(f"Map display setup failed: {e}")

    def add_simulation_elements_to_map(self):
        """Add simulation elements to map"""
        if not self.simulation_engine or not self.map_ax:
            return
        
        try:
            # Get vehicles
            vehicles = self.simulation_engine.get_vehicles()
            if vehicles:
                vehicle_positions = []
                for vehicle in vehicles:
                    if vehicle.current_node:
                        pos = self.map_manager.get_node_position(vehicle.current_node)
                        vehicle_positions.append(pos)
                
                if vehicle_positions:
                    x_coords = [pos[0] for pos in vehicle_positions]
                    y_coords = [pos[1] for pos in vehicle_positions]
                    self.map_ax.scatter(x_coords, y_coords, c='blue', s=50, alpha=0.8, label='Vehicles')
            
            # Get charging stations
            charging_stations = self.simulation_engine.get_charging_stations()
            if charging_stations:
                station_positions = []
                for station in charging_stations:
                    pos = self.map_manager.get_node_position(station.node_id)
                    station_positions.append(pos)
                
                if station_positions:
                    x_coords = [pos[0] for pos in station_positions]
                    y_coords = [pos[1] for pos in station_positions]
                    self.map_ax.scatter(x_coords, y_coords, c='red', s=100, alpha=0.8, 
                                      marker='s', label='Charging Stations')
            
            # Add legend
            self.map_ax.legend()
            
        except Exception as e:
            print(f"Failed to add simulation elements: {e}")

    def update_map_texture(self):
        """Update map texture"""
        if not self.map_figure:
            return
        
        try:
            # Render matplotlib figure to memory
            canvas = FigureCanvasAgg(self.map_figure)
            canvas.draw()
            
            # Get image data
            buf = canvas.buffer_rgba()
            w, h = canvas.get_width_height()
            
            # Convert to numpy array
            img_array = np.frombuffer(buf, dtype=np.uint8).reshape((h, w, 4))
            
            # Convert to RGB (DearPyGui needs RGB format)
            img_rgb = img_array[:, :, :3]
            
            # Normalize to 0-1 range
            img_normalized = img_rgb.astype(np.float32) / 255.0
            
            # Update texture
            dpg.set_value("map_texture", img_normalized.flatten())
            
        except Exception as e:
            print(f"Map texture update failed: {e}")

    def start_simulation(self):
        """Start simulation"""
        if not SIMULATION_AVAILABLE:
            print("Demo mode - simulation not available")
            return
        
        if not self.simulation_engine:
            print("Please initialize simulation first!")
            return
        
        self.is_running = True
        self.is_paused = False
        
        # Update button states
        dpg.configure_item("start_button", enabled=False)
        dpg.configure_item("pause_button", enabled=True)
        dpg.configure_item("stop_button", enabled=True)
        
        # Start simulation thread
        self.simulation_thread = threading.Thread(target=self.simulation_loop)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
        
        print("Simulation started!")

    def pause_simulation(self):
        """Pause/resume simulation"""
        if self.is_running:
            self.is_paused = not self.is_paused
            if self.is_paused:
                dpg.set_item_label("pause_button", "Resume")
                print("Simulation paused")
            else:
                dpg.set_item_label("pause_button", "Pause")
                print("Simulation resumed")

    def stop_simulation(self):
        """Stop simulation"""
        self.is_running = False
        self.is_paused = False
        
        # Update button states
        dpg.configure_item("start_button", enabled=True)
        dpg.configure_item("pause_button", enabled=False)
        dpg.configure_item("stop_button", enabled=False)
        dpg.set_item_label("pause_button", "Pause")
        
        print("Simulation stopped")

    def reset_simulation(self):
        """Reset simulation"""
        self.stop_simulation()
        
        # Reset metrics
        for key in self.metrics:
            self.metrics[key] = 0.0
        
        self.update_metrics_display()
        print("Simulation reset")

    def adjust_speed(self, sender, value):
        """Adjust simulation speed"""
        self.speed_multiplier = value
        print(f"Simulation speed: {value:.1f}x")

    def simulation_loop(self):
        """Simulation main loop"""
        while self.is_running:
            if not self.is_paused:
                try:
                    # Run simulation step
                    self.simulation_engine.run_step()
                    
                    # Update metrics
                    self.update_metrics()
                    
                    # Update map display (less frequently)
                    if int(self.simulation_engine.current_time * 10) % 10 == 0:
                        self.update_map_display()
                    
                    # Check if simulation complete
                    if self.simulation_engine.current_time >= self.sim_params['duration']:
                        self.stop_simulation()
                        break
                        
                except Exception as e:
                    print(f"Simulation error: {e}")
                    self.stop_simulation()
                    break
            
            # Control update frequency based on speed
            sleep_time = 0.1 / self.speed_multiplier
            time.sleep(max(0.01, sleep_time))

    def update_metrics(self):
        """Update metrics data"""
        if not self.simulation_engine:
            return
        
        try:
            # Get current statistics
            stats = self.simulation_engine.get_current_statistics()
            
            # Update metrics dictionary
            self.metrics.update({
                'simulation_time': stats.get('simulation_time', 0.0),
                'active_vehicles': len(self.simulation_engine.get_vehicles()),
                'pending_orders': len(stats.get('orders', {}).get('pending', [])),
                'active_orders': len(stats.get('orders', {}).get('active', [])),
                'completed_orders': stats.get('orders', {}).get('total_orders_completed', 0),
                'total_revenue': stats.get('orders', {}).get('total_revenue', 0.0),
                'avg_battery': stats.get('vehicles', {}).get('avg_battery_percentage', 0.0),
                'vehicle_utilization': stats.get('vehicles', {}).get('utilization_rate', 0.0) * 100
            })
            
            # Update UI display
            self.update_metrics_display()
            
        except Exception as e:
            print(f"Metrics update failed: {e}")

    def update_metrics_display(self):
        """Update metrics display"""
        # Progress bar
        progress = self.metrics['simulation_time'] / self.sim_params['duration']
        dpg.set_value("sim_progress", progress)
        dpg.configure_item("sim_progress", overlay=f"{progress*100:.1f}%")
        
        # Time display
        current_time = int(self.metrics['simulation_time'])
        total_time = self.sim_params['duration']
        time_str = f"{current_time//3600:02d}:{(current_time%3600)//60:02d}:{current_time%60:02d} / {total_time//3600:02d}:{(total_time%3600)//60:02d}:{total_time%60:02d}"
        dpg.set_value("time_display", time_str)
        
        # Metrics text
        dpg.set_value("active_vehicles", f"Active Vehicles: {self.metrics['active_vehicles']}")
        dpg.set_value("avg_battery", f"Average Battery: {self.metrics['avg_battery']:.1f}%")
        dpg.set_value("vehicle_util", f"Vehicle Utilization: {self.metrics['vehicle_utilization']:.1f}%")
        
        dpg.set_value("pending_orders", f"Pending Orders: {self.metrics['pending_orders']}")
        dpg.set_value("active_orders", f"Active Orders: {self.metrics['active_orders']}")
        dpg.set_value("completed_orders", f"Completed Orders: {self.metrics['completed_orders']}")
        
        dpg.set_value("total_revenue", f"Total Revenue: ${self.metrics['total_revenue']:.2f}")
        
        # Calculate revenue per hour
        if self.metrics['simulation_time'] > 0:
            revenue_per_hour = self.metrics['total_revenue'] / (self.metrics['simulation_time'] / 3600)
            dpg.set_value("revenue_hour", f"Revenue/Hour: ${revenue_per_hour:.2f}")

    def update_map_display(self):
        """Update map display"""
        if not self.map_ax or not self.simulation_engine:
            return
        
        try:
            # Clear dynamic elements
            self.map_ax.clear()
            
            # Redraw base map
            self.map_manager.setup_plot(show_preview=False)
            
            # Add updated simulation elements
            self.add_simulation_elements_to_map()
            
            # Update texture
            self.update_map_texture()
            
        except Exception as e:
            print(f"Map display update failed: {e}")

    def zoom_in(self):
        """Zoom in map"""
        print("Zoom in")

    def zoom_out(self):
        """Zoom out map"""
        print("Zoom out")

    def reset_view(self):
        """Reset map view"""
        print("Reset view")

    def run(self):
        """Run UI"""
        self.create_context()
        self.setup_ui()
        
        # Set primary window
        dpg.set_primary_window("main_window", True)
        
        # Show viewport
        dpg.show_viewport()
        
        # Start DearPyGui
        dpg.start_dearpygui()
        
        # Cleanup
        dpg.destroy_context()


def main():
    """Main function"""
    print("Starting Integrated EV Simulation UI...")
    
    app = IntegratedSimulationUI()
    app.run()


if __name__ == "__main__":
    main() 