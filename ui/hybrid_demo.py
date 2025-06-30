#!/usr/bin/env python3
"""
Hybrid Demo: DearPyGui Control + Folium Map
"""

import dearpygui.dearpygui as dpg
import folium
import threading
import time
import webbrowser
import os

class HybridDemo:
    def __init__(self):
        self.map_file = "control_map.html"
        self.is_running = False
        self.vehicle_count = 10
        self.update_interval = 3.0
        
    def create_ui(self):
        dpg.create_context()
        
        with dpg.window(label="Hybrid Control Panel", tag="main"):
            dpg.add_text("DearPyGui Control Panel", color=[100, 200, 255])
            dpg.add_separator()
            
            # Controls
            dpg.add_slider_int(
                label="Vehicle Count", 
                default_value=10, min_value=5, max_value=30,
                callback=lambda s, v: self.update_vehicles(v)
            )
            
            dpg.add_slider_float(
                label="Update Interval (s)", 
                default_value=3.0, min_value=1.0, max_value=10.0,
                callback=lambda s, v: self.update_interval_change(v)
            )
            
            dpg.add_separator()
            
            # Buttons
            dpg.add_button(label="Create Map", callback=self.create_map, width=200)
            dpg.add_button(label="Open Map", callback=self.open_map, width=200)
            dpg.add_button(label="Start Updates", callback=self.start_updates, width=200)
            dpg.add_button(label="Stop Updates", callback=self.stop_updates, width=200)
            
            dpg.add_separator()
            dpg.add_text("Status: Ready", tag="status")
            dpg.add_text("Updates: 0", tag="update_count")
    
    def create_map(self):
        """Create initial Folium map"""
        try:
            # Simple map centered on West Lafayette
            m = folium.Map(location=[40.4259, -86.9081], zoom_start=13)
            
            # Add some sample vehicles
            for i in range(self.vehicle_count):
                lat = 40.4259 + (i * 0.001) - 0.005
                lon = -86.9081 + (i * 0.001) - 0.005
                
                folium.Marker(
                    [lat, lon],
                    popup=f"Vehicle {i+1}",
                    icon=folium.Icon(color='blue', icon='car')
                ).add_to(m)
            
            # Save map
            m.save(self.map_file)
            dpg.set_value("status", f"Map created: {self.map_file}")
            
        except Exception as e:
            dpg.set_value("status", f"Error: {e}")
    
    def update_vehicles(self, count):
        self.vehicle_count = count
        dpg.set_value("status", f"Vehicle count: {count}")
    
    def update_interval_change(self, interval):
        self.update_interval = interval
        dpg.set_value("status", f"Update interval: {interval:.1f}s")
    
    def open_map(self):
        if os.path.exists(self.map_file):
            webbrowser.open(self.map_file)
        else:
            dpg.set_value("status", "Map not created yet")
    
    def start_updates(self):
        self.is_running = True
        threading.Thread(target=self.update_loop, daemon=True).start()
        dpg.set_value("status", "Auto-update started")
    
    def stop_updates(self):
        self.is_running = False
        dpg.set_value("status", "Auto-update stopped")
    
    def update_loop(self):
        count = 0
        while self.is_running:
            # Recreate map with updated data
            self.create_map()
            count += 1
            dpg.set_value("update_count", f"Updates: {count}")
            time.sleep(self.update_interval)
    
    def run(self):
        self.create_ui()
        dpg.create_viewport(title="Hybrid Demo", width=400, height=400)
        dpg.setup_dearpygui()
        dpg.set_primary_window("main", True)
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

if __name__ == "__main__":
    HybridDemo().run() 