#!/usr/bin/env python3
"""
Clear OSMnx Map Display with DearPyGui
Fixed blurry image issues
"""

import dearpygui.dearpygui as dpg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import sys
import os
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import osmnx as ox
    from core.map_manager import MapManager
    MAP_AVAILABLE = True
    print("OSMnx modules loaded successfully")
except ImportError as e:
    print(f"Warning: Map modules not available: {e}")
    MAP_AVAILABLE = False


class ClearMapUI:
    """Clear map display UI with fixed resolution"""
    
    def __init__(self):
        self.map_manager = None
        self.map_figure = None
        self.map_ax = None
        
        # Fixed sizes for crisp display
        self.map_width = 800
        self.map_height = 600
        self.dpi = 100  # High DPI for clear images
        
        self.map_params = {
            'location': 'West Lafayette, Indiana',
            'show_vehicles': True,
            'show_stations': True,
            'num_vehicles': 10,
            'num_stations': 5
        }

    def create_placeholder_texture(self):
        """Create high-quality placeholder texture"""
        # Create placeholder with exact dimensions
        w, h = self.map_width, self.map_height
        placeholder = np.ones((h, w, 3), dtype=np.float32) * 0.3
        
        # Add a border and center text area
        placeholder[10:-10, 10:-10] = [0.4, 0.4, 0.4]
        placeholder[h//2-50:h//2+50, w//2-100:w//2+100] = [0.5, 0.5, 0.8]
        
        with dpg.texture_registry():
            dpg.add_raw_texture(
                width=w,
                height=h,
                default_value=placeholder.flatten(),
                format=dpg.mvFormat_Float_rgb,
                tag="map_texture"
            )

    def setup_ui(self):
        """Setup UI interface"""
        with dpg.window(label="Clear OSMnx Map Display", tag="main_window"):
            
            if not MAP_AVAILABLE:
                dpg.add_text("WARNING: OSMnx not available", color=[255, 100, 100])
                dpg.add_separator()
            
            with dpg.group(horizontal=True):
                
                # Left panel: Controls (reduced width)
                with dpg.child_window(label="Controls", width=250, height=650, border=True):
                    dpg.add_text("Map Controls", color=[100, 200, 255])
                    dpg.add_separator()
                    
                    dpg.add_text("Location:")
                    dpg.add_combo(
                        label="",
                        items=[
                            "West Lafayette, Indiana", 
                            "New York City, NY",
                            "Chicago, IL"
                        ],
                        default_value="West Lafayette, Indiana",
                        tag="location_combo",
                        callback=lambda s, v: self.update_location(v),
                        width=-1
                    )
                    
                    dpg.add_separator()
                    
                    # Load map button
                    dpg.add_button(
                        label="Load Map",
                        callback=self.load_map,
                        tag="load_map_btn",
                        width=-1,
                        height=40
                    )
                    
                    dpg.add_separator()
                    dpg.add_text("Display:")
                    
                    dpg.add_checkbox(
                        label="Vehicles", 
                        default_value=True,
                        tag="show_vehicles_cb",
                        callback=lambda s, v: self.toggle_vehicles(v)
                    )
                    
                    dpg.add_checkbox(
                        label="Stations", 
                        default_value=True,
                        tag="show_stations_cb",
                        callback=lambda s, v: self.toggle_stations(v)
                    )
                    
                    dpg.add_slider_int(
                        label="Vehicles", 
                        default_value=10,
                        min_value=5,
                        max_value=25,
                        tag="vehicles_slider",
                        callback=lambda s, v: self.update_vehicles(v)
                    )
                    
                    dpg.add_slider_int(
                        label="Stations", 
                        default_value=5,
                        min_value=3,
                        max_value=12,
                        tag="stations_slider",
                        callback=lambda s, v: self.update_stations(v)
                    )
                    
                    dpg.add_separator()
                    dpg.add_button(label="Refresh", callback=self.refresh_map, width=-1)
                    dpg.add_button(label="Export PNG", callback=self.export_image, width=-1)
                    
                    dpg.add_separator()
                    dpg.add_text("Status:", color=[255, 255, 100])
                    dpg.add_text("Ready", tag="status", color=[100, 255, 100])
                
                # Right panel: Map display (exact size)
                with dpg.child_window(label="Map", width=850, height=650, border=True):
                    dpg.add_text("OpenStreetMap Display", color=[100, 255, 100])
                    dpg.add_separator()
                    
                    # Create placeholder texture
                    self.create_placeholder_texture()
                    
                    # Map image display with exact dimensions
                    dpg.add_image(
                        "map_texture",
                        width=self.map_width,
                        height=self.map_height,
                        tag="map_image"
                    )

    def update_location(self, location):
        """Update location"""
        self.map_params['location'] = location
        print(f"Location: {location}")

    def toggle_vehicles(self, show):
        """Toggle vehicle display"""
        self.map_params['show_vehicles'] = show
        if self.map_manager:
            self.refresh_map()

    def toggle_stations(self, show):
        """Toggle station display"""
        self.map_params['show_stations'] = show
        if self.map_manager:
            self.refresh_map()

    def update_vehicles(self, count):
        """Update vehicle count"""
        self.map_params['num_vehicles'] = count
        if self.map_manager:
            self.refresh_map()

    def update_stations(self, count):
        """Update station count"""
        self.map_params['num_stations'] = count
        if self.map_manager:
            self.refresh_map()

    def load_map(self):
        """Load map with high quality settings"""
        if not MAP_AVAILABLE:
            dpg.set_value("status", "OSMnx not available")
            return
        
        try:
            dpg.configure_item("load_map_btn", enabled=False)
            dpg.set_value("status", "Loading...")
            
            location = self.map_params['location']
            print(f"Loading map for: {location}")
            
            # Create map manager
            self.map_manager = MapManager(location)
            
            # Create high-quality matplotlib figure
            plt.style.use('default')  # Reset style
            self.map_figure = plt.figure(
                figsize=(self.map_width/self.dpi, self.map_height/self.dpi), 
                dpi=self.dpi,
                facecolor='white'
            )
            
            # Plot the graph with OSMnx
            self.map_ax = ox.plot_graph(
                self.map_manager.projected_graph,
                ax=None,
                figsize=(self.map_width/self.dpi, self.map_height/self.dpi),
                bgcolor='white',
                node_color='lightblue',
                node_size=0,
                edge_color='gray',
                edge_linewidth=0.8,
                show=False,
                close=False
            )[1]
            
            # Get the figure from the axis
            self.map_figure = self.map_ax.figure
            
            # Set title
            self.map_ax.set_title(f"{location} Road Network", fontsize=12, pad=10)
            
            # Add simulation elements
            self.add_simulation_elements()
            
            # Convert to texture
            self.update_map_texture()
            
            dpg.set_value("status", f"Loaded: {location}")
            dpg.configure_item("load_map_btn", enabled=True)
            
            print("Map loaded successfully!")
            
        except Exception as e:
            print(f"Map loading failed: {e}")
            dpg.set_value("status", f"Error: {str(e)}")
            dpg.configure_item("load_map_btn", enabled=True)

    def add_simulation_elements(self):
        """Add vehicles and stations to map"""
        if not self.map_manager or not self.map_ax:
            return
        
        try:
            # Remove existing scatter plots
            collections_to_remove = []
            for collection in self.map_ax.collections:
                if hasattr(collection, '_sizes'):  # This is a scatter plot
                    collections_to_remove.append(collection)
            
            for collection in collections_to_remove:
                collection.remove()
            
            # Add vehicles
            if self.map_params['show_vehicles']:
                vehicle_nodes = self.map_manager.get_random_nodes(self.map_params['num_vehicles'])
                if vehicle_nodes:
                    positions = [self.map_manager.get_node_position(node) for node in vehicle_nodes]
                    x_coords = [pos[0] for pos in positions]
                    y_coords = [pos[1] for pos in positions]
                    
                    self.map_ax.scatter(
                        x_coords, y_coords, 
                        c='blue', s=60, alpha=0.8, 
                        marker='o', label='Vehicles',
                        zorder=10, edgecolors='darkblue', linewidth=1
                    )
            
            # Add charging stations
            if self.map_params['show_stations']:
                station_nodes = self.map_manager.select_charging_station_nodes(self.map_params['num_stations'])
                if station_nodes:
                    positions = [self.map_manager.get_node_position(node) for node in station_nodes]
                    x_coords = [pos[0] for pos in positions]
                    y_coords = [pos[1] for pos in positions]
                    
                    self.map_ax.scatter(
                        x_coords, y_coords, 
                        c='red', s=100, alpha=0.9,
                        marker='s', label='Charging Stations',
                        zorder=10, edgecolors='darkred', linewidth=1
                    )
            
            # Add legend if elements exist
            if self.map_params['show_vehicles'] or self.map_params['show_stations']:
                self.map_ax.legend(loc='upper right', fontsize=9, framealpha=0.9)
            
        except Exception as e:
            print(f"Failed to add elements: {e}")

    def update_map_texture(self):
        """Update map texture with high quality"""
        if not self.map_figure:
            return
        
        try:
            # Set exact size
            self.map_figure.set_size_inches(
                self.map_width/self.dpi, 
                self.map_height/self.dpi
            )
            
            # Tight layout
            self.map_figure.tight_layout(pad=1.0)
            
            # Render with exact dimensions
            canvas = FigureCanvasAgg(self.map_figure)
            canvas.draw()
            
            # Get raw image data
            buf = canvas.buffer_rgba()
            w, h = canvas.get_width_height()
            
            # Convert to numpy array
            img_array = np.frombuffer(buf, dtype=np.uint8).reshape((h, w, 4))
            
            # Convert RGBA to RGB
            img_rgb = img_array[:, :, :3]
            
            # Ensure exact dimensions
            if w != self.map_width or h != self.map_height:
                print(f"Warning: Size mismatch - got {w}x{h}, expected {self.map_width}x{self.map_height}")
                # Resize if needed
                from PIL import Image
                pil_img = Image.fromarray(img_rgb)
                pil_img = pil_img.resize((self.map_width, self.map_height), Image.LANCZOS)
                img_rgb = np.array(pil_img)
            
            # Normalize to 0-1 range
            img_normalized = img_rgb.astype(np.float32) / 255.0
            
            # Update texture
            dpg.set_value("map_texture", img_normalized.flatten())
            
            print(f"Map texture updated: {img_rgb.shape}")
            
        except Exception as e:
            print(f"Texture update failed: {e}")

    def refresh_map(self):
        """Refresh map display"""
        if not self.map_manager:
            return
        
        try:
            # Add simulation elements
            self.add_simulation_elements()
            
            # Update texture
            self.update_map_texture()
            
            print("Map refreshed")
            
        except Exception as e:
            print(f"Refresh failed: {e}")

    def export_image(self):
        """Export high-quality image"""
        if not self.map_figure:
            print("No map to export")
            return
        
        try:
            filename = f"clear_map_export_{int(time.time())}.png"
            self.map_figure.savefig(
                filename, 
                dpi=150, 
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none'
            )
            print(f"Exported: {filename}")
            dpg.set_value("status", f"Exported: {filename}")
        except Exception as e:
            print(f"Export failed: {e}")

    def run(self):
        """Run application"""
        dpg.create_context()
        
        # Clean theme
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (240, 240, 240))
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (250, 250, 250))
                dpg.add_theme_color(dpg.mvThemeCol_Button, (70, 130, 180))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (100, 150, 200))
        
        dpg.bind_theme(theme)
        self.setup_ui()
        
        dpg.create_viewport(title="Clear OSMnx Map Display", width=1150, height=750)
        dpg.setup_dearpygui()
        dpg.set_primary_window("main_window", True)
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()


def main():
    """Main function"""
    print("Starting Clear Map Display...")
    app = ClearMapUI()
    app.run()


if __name__ == "__main__":
    main() 