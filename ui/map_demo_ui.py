#!/usr/bin/env python3
"""
DearPyGui with Real OSMnx Map Display
Shows actual road network from OpenStreetMap
"""

import dearpygui.dearpygui as dpg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import threading
import time
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import osmnx as ox
    from core.map_manager import MapManager
    MAP_AVAILABLE = True
    print("OSMnx and map modules loaded successfully")
except ImportError as e:
    print(f"Warning: Map modules not available: {e}")
    MAP_AVAILABLE = False


class MapDemoUI:
    """Demo UI with real OSMnx map display"""
    
    def __init__(self):
        self.map_manager = None
        self.map_figure = None
        self.map_ax = None
        self.map_texture = None
        
        # UI configuration
        self.config = {
            'window_width': 1400,
            'window_height': 800,
            'map_width': 800,
            'map_height': 600
        }
        
        # Map parameters
        self.map_params = {
            'location': 'West Lafayette, Indiana',
            'show_vehicles': True,
            'show_stations': True,
            'num_vehicles': 10,
            'num_stations': 5
        }

    def create_placeholder_texture(self):
        """Create placeholder texture"""
        # Create a gray placeholder
        placeholder = np.ones((400, 600, 3), dtype=np.float32) * 0.3
        placeholder[180:220, 280:320] = [0.5, 0.5, 0.8]  # Blue rectangle
        
        with dpg.texture_registry():
            dpg.add_raw_texture(
                width=600,
                height=400,
                default_value=placeholder.flatten(),
                format=dpg.mvFormat_Float_rgb,
                tag="map_texture"
            )

    def setup_ui(self):
        """Setup UI interface"""
        with dpg.window(label="OSMnx Map Demo", tag="main_window"):
            
            # Status
            if not MAP_AVAILABLE:
                dpg.add_text("WARNING: OSMnx not available", color=[255, 100, 100])
                dpg.add_separator()
            
            with dpg.group(horizontal=True):
                
                # Left panel: Controls
                with dpg.child_window(label="Map Controls", width=300, height=700, border=True):
                    dpg.add_text("Map Configuration", color=[100, 200, 255])
                    dpg.add_separator()
                    
                    dpg.add_text("Location:")
                    dpg.add_combo(
                        label="City",
                        items=[
                            "West Lafayette, Indiana", 
                            "New York City, NY",
                            "San Francisco, CA",
                            "Chicago, IL"
                        ],
                        default_value="West Lafayette, Indiana",
                        tag="location_combo",
                        callback=lambda s, v: self.update_location(v)
                    )
                    
                    dpg.add_separator()
                    dpg.add_text("Display Options:")
                    
                    dpg.add_checkbox(
                        label="Show Vehicles", 
                        default_value=True,
                        tag="show_vehicles_cb",
                        callback=lambda s, v: self.update_display_option('show_vehicles', v)
                    )
                    
                    dpg.add_checkbox(
                        label="Show Charging Stations", 
                        default_value=True,
                        tag="show_stations_cb",
                        callback=lambda s, v: self.update_display_option('show_stations', v)
                    )
                    
                    dpg.add_separator()
                    dpg.add_text("Simulation Elements:")
                    
                    dpg.add_slider_int(
                        label="Vehicles", 
                        default_value=10,
                        min_value=5,
                        max_value=30,
                        tag="vehicles_slider",
                        callback=lambda s, v: self.update_param('num_vehicles', v)
                    )
                    
                    dpg.add_slider_int(
                        label="Charging Stations", 
                        default_value=5,
                        min_value=3,
                        max_value=15,
                        tag="stations_slider",
                        callback=lambda s, v: self.update_param('num_stations', v)
                    )
                    
                    dpg.add_separator()
                    
                    # Map loading button
                    dpg.add_button(
                        label="Load Map",
                        callback=self.load_map,
                        tag="load_map_btn",
                        width=-1,
                        height=50
                    )
                    
                    dpg.add_separator()
                    
                    # Map controls
                    dpg.add_text("Map Controls:")
                    dpg.add_button(label="Refresh Display", callback=self.refresh_map, width=-1)
                    dpg.add_button(label="Add Random Vehicles", callback=self.add_vehicles, width=-1)
                    dpg.add_button(label="Add Charging Stations", callback=self.add_stations, width=-1)
                    
                    dpg.add_separator()
                    
                    # Status
                    dpg.add_text("Map Status:")
                    dpg.add_text("Ready", tag="map_status", color=[100, 255, 100])
                
                # Right panel: Map display
                with dpg.child_window(label="Map Display", width=800, height=700, border=True):
                    dpg.add_text("Real OpenStreetMap Display", color=[100, 255, 100])
                    dpg.add_separator()
                    
                    # Map toolbar
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Reset View", callback=self.reset_view)
                        dpg.add_button(label="Export Image", callback=self.export_image)
                    
                    dpg.add_separator()
                    
                    # Create placeholder texture first
                    self.create_placeholder_texture()
                    
                    # Map image display
                    dpg.add_image(
                        "map_texture",
                        width=750,
                        height=550,
                        tag="map_image"
                    )

    def update_location(self, location):
        """Update map location"""
        self.map_params['location'] = location
        print(f"Location updated to: {location}")

    def update_display_option(self, option, value):
        """Update display option"""
        self.map_params[option] = value
        print(f"Display option {option}: {value}")
        # Refresh map if loaded
        if self.map_manager:
            self.refresh_map()

    def update_param(self, param, value):
        """Update parameter"""
        self.map_params[param] = value
        print(f"Parameter {param}: {value}")

    def load_map(self):
        """Load map from OpenStreetMap"""
        if not MAP_AVAILABLE:
            dpg.set_value("map_status", "OSMnx not available")
            return
        
        try:
            # Disable button and show loading
            dpg.configure_item("load_map_btn", enabled=False)
            dpg.set_value("map_status", "Loading map...")
            
            location = self.map_params['location']
            print(f"Loading map for: {location}")
            
            # Create map manager
            self.map_manager = MapManager(location)
            
            # Setup matplotlib plot
            self.map_figure, self.map_ax = self.map_manager.setup_plot(show_preview=False)
            self.map_figure.set_size_inches(10, 8)
            
            # Set title
            self.map_ax.set_title(f"Road Network: {location}", fontsize=14)
            
            # Add simulation elements
            self.add_simulation_elements()
            
            # Convert to texture
            self.update_map_texture()
            
            # Update status
            dpg.set_value("map_status", f"Loaded: {location}")
            dpg.configure_item("load_map_btn", enabled=True)
            
            print("Map loaded successfully!")
            
        except Exception as e:
            print(f"Map loading failed: {e}")
            dpg.set_value("map_status", f"Error: {str(e)}")
            dpg.configure_item("load_map_btn", enabled=True)

    def add_simulation_elements(self):
        """Add vehicles and charging stations to map"""
        if not self.map_manager or not self.map_ax:
            return
        
        try:
            # Clear previous elements (keep the map)
            # Remove any existing scatter plots
            for collection in self.map_ax.collections:
                if hasattr(collection, '_original_facecolor'):
                    collection.remove()
            
            # Add vehicles if enabled
            if self.map_params['show_vehicles']:
                vehicle_nodes = self.map_manager.get_random_nodes(self.map_params['num_vehicles'])
                if vehicle_nodes:
                    vehicle_positions = [self.map_manager.get_node_position(node) for node in vehicle_nodes]
                    x_coords = [pos[0] for pos in vehicle_positions]
                    y_coords = [pos[1] for pos in vehicle_positions]
                    
                    self.map_ax.scatter(
                        x_coords, y_coords, 
                        c='blue', s=80, alpha=0.8, 
                        marker='o', label='Vehicles',
                        zorder=5
                    )
            
            # Add charging stations if enabled
            if self.map_params['show_stations']:
                station_nodes = self.map_manager.select_charging_station_nodes(self.map_params['num_stations'])
                if station_nodes:
                    station_positions = [self.map_manager.get_node_position(node) for node in station_nodes]
                    x_coords = [pos[0] for pos in station_positions]
                    y_coords = [pos[1] for pos in station_positions]
                    
                    self.map_ax.scatter(
                        x_coords, y_coords, 
                        c='red', s=120, alpha=0.9,
                        marker='s', label='Charging Stations',
                        zorder=5
                    )
            
            # Add legend
            if self.map_params['show_vehicles'] or self.map_params['show_stations']:
                self.map_ax.legend(loc='upper right', fontsize=10)
            
        except Exception as e:
            print(f"Failed to add simulation elements: {e}")

    def update_map_texture(self):
        """Update map texture for DearPyGui"""
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
            
            # Convert to RGB (DearPyGui format)
            img_rgb = img_array[:, :, :3]
            
            # Normalize to 0-1 range
            img_normalized = img_rgb.astype(np.float32) / 255.0
            
            # Update texture
            dpg.set_value("map_texture", img_normalized.flatten())
            
            print("Map texture updated successfully")
            
        except Exception as e:
            print(f"Map texture update failed: {e}")

    def refresh_map(self):
        """Refresh map display"""
        if not self.map_manager:
            print("No map loaded")
            return
        
        try:
            # Clear and redraw
            self.map_ax.clear()
            
            # Redraw base map
            self.map_figure, self.map_ax = self.map_manager.setup_plot(show_preview=False)
            self.map_ax.set_title(f"Road Network: {self.map_params['location']}", fontsize=14)
            
            # Add simulation elements
            self.add_simulation_elements()
            
            # Update texture
            self.update_map_texture()
            
            print("Map refreshed")
            
        except Exception as e:
            print(f"Map refresh failed: {e}")

    def add_vehicles(self):
        """Add random vehicles"""
        self.map_params['num_vehicles'] = min(30, self.map_params['num_vehicles'] + 5)
        dpg.set_value("vehicles_slider", self.map_params['num_vehicles'])
        self.refresh_map()

    def add_stations(self):
        """Add charging stations"""
        self.map_params['num_stations'] = min(15, self.map_params['num_stations'] + 2)
        dpg.set_value("stations_slider", self.map_params['num_stations'])
        self.refresh_map()

    def reset_view(self):
        """Reset map view"""
        if self.map_manager:
            self.refresh_map()

    def export_image(self):
        """Export map as image"""
        if not self.map_figure:
            print("No map to export")
            return
        
        try:
            filename = f"map_export_{int(time.time())}.png"
            self.map_figure.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"Map exported as: {filename}")
        except Exception as e:
            print(f"Export failed: {e}")

    def run(self):
        """Run the application"""
        dpg.create_context()
        
        # Dark theme
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (25, 25, 25))
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (35, 35, 35))
                dpg.add_theme_color(dpg.mvThemeCol_Button, (51, 122, 183))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (71, 142, 203))
        
        dpg.bind_theme(theme)
        self.setup_ui()
        
        dpg.create_viewport(
            title="DearPyGui OSMnx Map Demo", 
            width=self.config['window_width'], 
            height=self.config['window_height']
        )
        dpg.setup_dearpygui()
        dpg.set_primary_window("main_window", True)
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()


def main():
    """Main function"""
    print("Starting OSMnx Map Demo...")
    demo = MapDemoUI()
    demo.run()


if __name__ == "__main__":
    main() 