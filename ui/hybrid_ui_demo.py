#!/usr/bin/env python3
"""
Hybrid UI Demo: DearPyGui Control Panel + Folium Map
Demonstrates real-time control with high-quality map visualization
"""

import dearpygui.dearpygui as dpg
import folium
import json
import threading
import time
import webbrowser
import os
import sys
from typing import Dict, List

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.map_manager import MapManager
    MAP_AVAILABLE = True
    print("Map modules loaded successfully")
except ImportError as e:
    print(f"Warning: Map modules not available: {e}")
    MAP_AVAILABLE = False


class HybridSimulationUI:
    """Hybrid UI: DearPyGui controls + Folium map"""
    
    def __init__(self):
        self.map_manager = None
        self.folium_map = None
        self.map_filename = "realtime_map.html"
        
        # Simulation state
        self.is_running = False
        self.is_paused = False
        self.simulation_thread = None
        self.map_update_thread = None
        
        # Simulation parameters
        self.sim_params = {
            'location': 'West Lafayette, Indiana',
            'duration': 3600,
            'num_vehicles': 20,
            'num_charging_stations': 8,
            'update_interval': 2.0,  # seconds
            'simulation_speed': 1.0
        }
        
        # Real-time data
        self.simulation_data = {
            'vehicles': [],
            'charging_stations': [],
            'current_time': 0.0,
            'metrics': {
                'active_vehicles': 0,
                'completed_orders': 0,
                'total_revenue': 0.0
            }
        }

    def create_control_panel(self):
        """Create DearPyGui control panel"""
        dpg.create_context()
        
        with dpg.window(label="EV Simulation Control Panel", tag="main_window"):
            
            # Header
            dpg.add_text("Hybrid Simulation System", color=[100, 200, 255])
            dpg.add_text("Control Panel: DearPyGui | Map: Folium", color=[150, 150, 150])
            dpg.add_separator()
            
            # Two column layout
            with dpg.group(horizontal=True):
                
                # Left column: Parameters
                with dpg.child_window(label="Parameters", width=300, height=600, border=True):
                    dpg.add_text("Simulation Parameters", color=[100, 255, 100])
                    dpg.add_separator()
                    
                    dpg.add_text("Basic Settings:")
                    dpg.add_slider_int(
                        label="Duration (min)",
                        default_value=60,
                        min_value=5,
                        max_value=120,
                        tag="duration_slider",
                        callback=lambda s, v: self.update_param('duration', v * 60)
                    )
                    
                    dpg.add_slider_int(
                        label="Vehicles",
                        default_value=20,
                        min_value=5,
                        max_value=50,
                        tag="vehicles_slider",
                        callback=lambda s, v: self.update_param('num_vehicles', v)
                    )
                    
                    dpg.add_slider_int(
                        label="Charging Stations",
                        default_value=8,
                        min_value=3,
                        max_value=15,
                        tag="stations_slider",
                        callback=lambda s, v: self.update_param('num_charging_stations', v)
                    )
                    
                    dpg.add_separator()
                    dpg.add_text("Real-time Settings:")
                    
                    dpg.add_slider_float(
                        label="Update Interval (s)",
                        default_value=2.0,
                        min_value=0.5,
                        max_value=10.0,
                        format="%.1f",
                        tag="update_slider",
                        callback=lambda s, v: self.update_param('update_interval', v)
                    )
                    
                    dpg.add_slider_float(
                        label="Simulation Speed",
                        default_value=1.0,
                        min_value=0.1,
                        max_value=5.0,
                        format="%.1fx",
                        tag="speed_slider",
                        callback=lambda s, v: self.update_param('simulation_speed', v)
                    )
                    
                    dpg.add_separator()
                    dpg.add_text("Map Location:")
                    dpg.add_combo(
                        label="",
                        items=["West Lafayette, Indiana", "New York City, NY", "Chicago, IL"],
                        default_value="West Lafayette, Indiana",
                        tag="location_combo",
                        callback=lambda s, v: self.update_param('location', v),
                        width=-1
                    )
                    
                    dpg.add_separator()
                    
                    # Initialize button
                    dpg.add_button(
                        label="Initialize Map",
                        callback=self.initialize_map,
                        tag="init_button",
                        width=-1,
                        height=40
                    )
                    
                    dpg.add_button(
                        label="Open Map in Browser",
                        callback=self.open_map,
                        tag="open_button",
                        width=-1,
                        height=30,
                        enabled=False
                    )
                
                # Right column: Control & Status
                with dpg.child_window(label="Control & Status", width=350, height=600, border=True):
                    dpg.add_text("Simulation Control", color=[255, 200, 100])
                    dpg.add_separator()
                    
                    # Control buttons
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label="Start",
                            callback=self.start_simulation,
                            tag="start_button",
                            width=80,
                            height=35,
                            enabled=False
                        )
                        
                        dpg.add_button(
                            label="Pause",
                            callback=self.pause_simulation,
                            tag="pause_button",
                            width=80,
                            height=35,
                            enabled=False
                        )
                        
                        dpg.add_button(
                            label="Stop",
                            callback=self.stop_simulation,
                            tag="stop_button",
                            width=80,
                            height=35,
                            enabled=False
                        )
                    
                    dpg.add_separator()
                    dpg.add_text("Real-time Status", color=[255, 255, 100])
                    
                    # Progress
                    dpg.add_text("Progress:")
                    dpg.add_progress_bar(tag="progress_bar", default_value=0.0, overlay="0%")
                    dpg.add_text("00:00:00 / 01:00:00", tag="time_display")
                    
                    dpg.add_separator()
                    dpg.add_text("Live Metrics:")
                    
                    # Metrics
                    dpg.add_text("Active Vehicles: 0", tag="active_vehicles")
                    dpg.add_text("Completed Orders: 0", tag="completed_orders")
                    dpg.add_text("Total Revenue: $0.00", tag="total_revenue")
                    dpg.add_text("Map Updates: 0", tag="map_updates")
                    
                    dpg.add_separator()
                    dpg.add_text("System Status:")
                    dpg.add_text("Ready", tag="system_status", color=[100, 255, 100])
                    
                    dpg.add_separator()
                    dpg.add_text("Map Communication:")
                    dpg.add_text("HTML File: Not created", tag="file_status")
                    dpg.add_text("Last Update: Never", tag="last_update")

    def update_param(self, param_name: str, value):
        """Update simulation parameter"""
        self.sim_params[param_name] = value
        print(f"Parameter updated: {param_name} = {value}")

    def initialize_map(self):
        """Initialize Folium map"""
        if not MAP_AVAILABLE:
            dpg.set_value("system_status", "Map modules not available")
            return
        
        try:
            dpg.configure_item("init_button", enabled=False)
            dpg.set_value("system_status", "Initializing map...")
            
            location = self.sim_params['location']
            print(f"Initializing map for {location}...")
            
            # Create map manager
            self.map_manager = MapManager(location)
            
            # Create initial Folium map
            self.create_folium_map()
            
            # Update status
            dpg.set_value("system_status", f"Map ready: {location}")
            dpg.set_value("file_status", f"HTML File: {self.map_filename}")
            dpg.configure_item("init_button", enabled=True)
            dpg.configure_item("open_button", enabled=True)
            dpg.configure_item("start_button", enabled=True)
            
            print("Map initialized successfully!")
            
        except Exception as e:
            print(f"Map initialization failed: {e}")
            dpg.set_value("system_status", f"Error: {str(e)}")
            dpg.configure_item("init_button", enabled=True)

    def create_folium_map(self):
        """Create/update Folium map"""
        if not self.map_manager:
            return
        
        try:
            # Get map center
            nodes = self.map_manager.get_all_nodes()
            sample_nodes = nodes[:50]  # Sample for performance
            
            lats = []
            lons = []
            for node in sample_nodes:
                lon, lat = self.map_manager.graph.nodes[node]['x'], self.map_manager.graph.nodes[node]['y']
                lats.append(lat)
                lons.append(lon)
            
            center_lat = sum(lats) / len(lats)
            center_lon = sum(lons) / len(lons)
            
            # Create Folium map
            self.folium_map = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=13,
                tiles='OpenStreetMap'
            )
            
            # Add title
            title_html = f'''
            <h3 align="center" style="font-size:20px"><b>EV Simulation - {self.sim_params['location']}</b></h3>
            <p align="center">Real-time: {time.strftime("%H:%M:%S")}</p>
            '''
            self.folium_map.get_root().html.add_child(folium.Element(title_html))
            
            # Generate simulation data
            self.generate_simulation_data()
            
            # Add vehicles
            for vehicle in self.simulation_data['vehicles']:
                folium.Marker(
                    location=[vehicle['lat'], vehicle['lon']],
                    popup=f"Vehicle {vehicle['id']}<br>Status: {vehicle['status']}<br>Battery: {vehicle['battery']:.1f}%",
                    tooltip=f"Vehicle {vehicle['id']}",
                    icon=folium.Icon(color='blue', icon='car', prefix='fa')
                ).add_to(self.folium_map)
            
            # Add charging stations
            for station in self.simulation_data['charging_stations']:
                folium.Marker(
                    location=[station['lat'], station['lon']],
                    popup=f"Station {station['id']}<br>Available: {station['available']}/{station['total']}<br>Power: {station['power']}kW",
                    tooltip=f"Charging Station {station['id']}",
                    icon=folium.Icon(color='red', icon='plug', prefix='fa')
                ).add_to(self.folium_map)
            
            # Save map
            self.folium_map.save(self.map_filename)
            
            # Update status
            current_time = time.strftime("%H:%M:%S")
            dpg.set_value("last_update", f"Last Update: {current_time}")
            
            print("Folium map updated")
            
        except Exception as e:
            print(f"Failed to create Folium map: {e}")

    def generate_simulation_data(self):
        """Generate simulated vehicle and station data"""
        if not self.map_manager:
            return
        
        # Generate vehicles
        vehicle_nodes = self.map_manager.get_random_nodes(self.sim_params['num_vehicles'])
        self.simulation_data['vehicles'] = []
        
        for i, node in enumerate(vehicle_nodes):
            lon = self.map_manager.graph.nodes[node]['x']
            lat = self.map_manager.graph.nodes[node]['y']
            
            self.simulation_data['vehicles'].append({
                'id': i + 1,
                'node': node,
                'lat': lat,
                'lon': lon,
                'status': 'available',
                'battery': 75.0 + (i % 5) * 5  # Vary battery levels
            })
        
        # Generate charging stations
        station_nodes = self.map_manager.select_charging_station_nodes(self.sim_params['num_charging_stations'])
        self.simulation_data['charging_stations'] = []
        
        for i, node in enumerate(station_nodes):
            lon = self.map_manager.graph.nodes[node]['x']
            lat = self.map_manager.graph.nodes[node]['y']
            
            self.simulation_data['charging_stations'].append({
                'id': i + 1,
                'node': node,
                'lat': lat,
                'lon': lon,
                'power': 50,
                'available': 2 + (i % 3),
                'total': 4
            })

    def start_simulation(self):
        """Start simulation"""
        self.is_running = True
        self.is_paused = False
        
        # Update button states
        dpg.configure_item("start_button", enabled=False)
        dpg.configure_item("pause_button", enabled=True)
        dpg.configure_item("stop_button", enabled=True)
        
        # Start simulation thread
        self.simulation_thread = threading.Thread(target=self.simulation_loop, daemon=True)
        self.simulation_thread.start()
        
        # Start map update thread
        self.map_update_thread = threading.Thread(target=self.map_update_loop, daemon=True)
        self.map_update_thread.start()
        
        dpg.set_value("system_status", "Simulation running...")
        print("Simulation started!")

    def pause_simulation(self):
        """Pause/resume simulation"""
        self.is_paused = not self.is_paused
        if self.is_paused:
            dpg.set_item_label("pause_button", "Resume")
            dpg.set_value("system_status", "Simulation paused")
        else:
            dpg.set_item_label("pause_button", "Pause")
            dpg.set_value("system_status", "Simulation running...")

    def stop_simulation(self):
        """Stop simulation"""
        self.is_running = False
        self.is_paused = False
        
        # Update button states
        dpg.configure_item("start_button", enabled=True)
        dpg.configure_item("pause_button", enabled=False)
        dpg.configure_item("stop_button", enabled=False)
        dpg.set_item_label("pause_button", "Pause")
        
        dpg.set_value("system_status", "Simulation stopped")
        print("Simulation stopped")

    def simulation_loop(self):
        """Main simulation loop"""
        start_time = time.time()
        
        while self.is_running:
            if not self.is_paused:
                # Update simulation time
                elapsed = (time.time() - start_time) * self.sim_params['simulation_speed']
                self.simulation_data['current_time'] = elapsed
                
                # Update metrics
                self.update_simulation_metrics()
                
                # Check completion
                if elapsed >= self.sim_params['duration']:
                    self.stop_simulation()
                    break
            
            time.sleep(0.1)

    def map_update_loop(self):
        """Map update loop"""
        update_count = 0
        
        while self.is_running:
            if not self.is_paused:
                try:
                    # Update map
                    self.create_folium_map()
                    update_count += 1
                    dpg.set_value("map_updates", f"Map Updates: {update_count}")
                    
                except Exception as e:
                    print(f"Map update failed: {e}")
            
            # Wait for next update
            time.sleep(self.sim_params['update_interval'])

    def update_simulation_metrics(self):
        """Update simulation metrics in UI"""
        # Update progress
        progress = self.simulation_data['current_time'] / self.sim_params['duration']
        dpg.set_value("progress_bar", progress)
        dpg.configure_item("progress_bar", overlay=f"{progress*100:.1f}%")
        
        # Update time display
        current = int(self.simulation_data['current_time'])
        total = self.sim_params['duration']
        time_str = f"{current//3600:02d}:{(current%3600)//60:02d}:{current%60:02d} / {total//3600:02d}:{(total%3600)//60:02d}:{total%60:02d}"
        dpg.set_value("time_display", time_str)
        
        # Simulate changing metrics
        active_vehicles = len([v for v in self.simulation_data['vehicles'] if v['status'] == 'available'])
        completed_orders = int(self.simulation_data['current_time'] / 60)  # 1 order per minute
        total_revenue = completed_orders * 15.50  # $15.50 per order
        
        dpg.set_value("active_vehicles", f"Active Vehicles: {active_vehicles}")
        dpg.set_value("completed_orders", f"Completed Orders: {completed_orders}")
        dpg.set_value("total_revenue", f"Total Revenue: ${total_revenue:.2f}")

    def open_map(self):
        """Open map in browser"""
        if os.path.exists(self.map_filename):
            webbrowser.open(self.map_filename)
            print(f"Opened {self.map_filename} in browser")
        else:
            print("Map file not found")

    def run(self):
        """Run the application"""
        self.create_control_panel()
        
        dpg.create_viewport(title="Hybrid EV Simulation System", width=700, height=700)
        dpg.setup_dearpygui()
        dpg.set_primary_window("main_window", True)
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()


def main():
    """Main function"""
    print("Starting Hybrid Simulation UI...")
    print("Features:")
    print("- DearPyGui: Real-time control panel")
    print("- Folium: High-quality interactive map")
    print("- Auto-refresh: Map updates every few seconds")
    
    app = HybridSimulationUI()
    app.run()


if __name__ == "__main__":
    main() 