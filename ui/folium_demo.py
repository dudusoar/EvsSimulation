#!/usr/bin/env python3
"""
OSMnx + Folium Interactive Map Demo
Creates high-quality interactive web maps
"""

import folium
import sys
import os
import webbrowser
import time
import json
from typing import List, Tuple

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.map_manager import MapManager
    MAP_AVAILABLE = True
    print("Map modules loaded successfully")
except ImportError as e:
    print(f"Warning: Map modules not available: {e}")
    MAP_AVAILABLE = False


class FoliumMapDemo:
    """Interactive map demo using Folium"""
    
    def __init__(self):
        self.map_manager = None
        self.folium_map = None
        self.location = "West Lafayette, Indiana"
        
        # Simulation data
        self.vehicles = []
        self.charging_stations = []
        
    def create_interactive_map(self):
        """Create Folium interactive map"""
        if not MAP_AVAILABLE:
            print("Map modules not available")
            return None
        
        try:
            print(f"Creating interactive map for {self.location}...")
            
            # Load OSMnx map
            self.map_manager = MapManager(self.location)
            
            # Get map bounds
            nodes = self.map_manager.get_all_nodes()
            if not nodes:
                print("No nodes found")
                return None
            
            # Calculate center and bounds
            positions = [self.map_manager.get_node_position(node) for node in nodes[:100]]
            lats = []
            lons = []
            
            for node in nodes[:100]:
                lon, lat = self.map_manager.graph.nodes[node]['x'], self.map_manager.graph.nodes[node]['y']
                lats.append(lat)
                lons.append(lon)
            
            center_lat = sum(lats) / len(lats)
            center_lon = sum(lons) / len(lons)
            
            print(f"Map center: {center_lat:.4f}, {center_lon:.4f}")
            
            # Create Folium map
            self.folium_map = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=13,
                tiles='OpenStreetMap',
                control_scale=True
            )
            
            # Add road network overlay
            self.add_road_network()
            
            # Add simulation elements
            self.add_vehicles()
            self.add_charging_stations()
            
            # Add controls
            self.add_map_controls()
            
            return self.folium_map
            
        except Exception as e:
            print(f"Failed to create map: {e}")
            return None
    
    def add_road_network(self):
        """Add road network to map"""
        if not self.map_manager or not self.folium_map:
            return
        
        try:
            print("Adding road network...")
            
            # Get edges and draw as lines
            edges = list(self.map_manager.graph.edges(data=True))
            
            # Sample edges to avoid overwhelming the map
            sample_size = min(1000, len(edges))
            import random
            sampled_edges = random.sample(edges, sample_size)
            
            for u, v, data in sampled_edges:
                # Get node coordinates
                u_lon = self.map_manager.graph.nodes[u]['x']
                u_lat = self.map_manager.graph.nodes[u]['y']
                v_lon = self.map_manager.graph.nodes[v]['x']
                v_lat = self.map_manager.graph.nodes[v]['y']
                
                # Add line to map
                folium.PolyLine(
                    locations=[[u_lat, u_lon], [v_lat, v_lon]],
                    color='gray',
                    weight=1,
                    opacity=0.6
                ).add_to(self.folium_map)
            
            print(f"Added {len(sampled_edges)} road segments")
            
        except Exception as e:
            print(f"Failed to add road network: {e}")
    
    def add_vehicles(self):
        """Add vehicles to map"""
        if not self.map_manager or not self.folium_map:
            return
        
        try:
            print("Adding vehicles...")
            
            # Get random vehicle positions
            vehicle_nodes = self.map_manager.get_random_nodes(15)
            
            for i, node in enumerate(vehicle_nodes):
                # Get coordinates
                lon = self.map_manager.graph.nodes[node]['x']
                lat = self.map_manager.graph.nodes[node]['y']
                
                # Create vehicle marker
                folium.Marker(
                    location=[lat, lon],
                    popup=f"Vehicle {i+1}<br>Node: {node}<br>Status: Available",
                    tooltip=f"Vehicle {i+1}",
                    icon=folium.Icon(
                        color='blue',
                        icon='car',
                        prefix='fa'
                    )
                ).add_to(self.folium_map)
                
                # Store vehicle data
                self.vehicles.append({
                    'id': i+1,
                    'node': node,
                    'lat': lat,
                    'lon': lon,
                    'status': 'available'
                })
            
            print(f"Added {len(vehicle_nodes)} vehicles")
            
        except Exception as e:
            print(f"Failed to add vehicles: {e}")
    
    def add_charging_stations(self):
        """Add charging stations to map"""
        if not self.map_manager or not self.folium_map:
            return
        
        try:
            print("Adding charging stations...")
            
            # Get charging station positions
            station_nodes = self.map_manager.select_charging_station_nodes(8)
            
            for i, node in enumerate(station_nodes):
                # Get coordinates
                lon = self.map_manager.graph.nodes[node]['x']
                lat = self.map_manager.graph.nodes[node]['y']
                
                # Create charging station marker
                folium.Marker(
                    location=[lat, lon],
                    popup=f"Charging Station {i+1}<br>Node: {node}<br>Power: 50kW<br>Available: 2/4",
                    tooltip=f"Charging Station {i+1}",
                    icon=folium.Icon(
                        color='red',
                        icon='plug',
                        prefix='fa'
                    )
                ).add_to(self.folium_map)
                
                # Store station data
                self.charging_stations.append({
                    'id': i+1,
                    'node': node,
                    'lat': lat,
                    'lon': lon,
                    'power': 50,
                    'available_slots': 2,
                    'total_slots': 4
                })
            
            print(f"Added {len(station_nodes)} charging stations")
            
        except Exception as e:
            print(f"Failed to add charging stations: {e}")
    
    def add_map_controls(self):
        """Add map controls and legend"""
        if not self.folium_map:
            return
        
        try:
            # Add legend
            legend_html = '''
            <div style="position: fixed; 
                        top: 10px; right: 10px; width: 200px; height: 120px; 
                        background-color: white; border:2px solid grey; z-index:9999; 
                        font-size:14px; padding: 10px">
            <h4>EV Simulation Legend</h4>
            <p><i class="fa fa-car" style="color:blue"></i> Electric Vehicles</p>
            <p><i class="fa fa-plug" style="color:red"></i> Charging Stations</p>
            <p><span style="color:gray">━━━</span> Road Network</p>
            </div>
            '''
            self.folium_map.get_root().html.add_child(folium.Element(legend_html))
            
            # Add fullscreen control
            from folium.plugins import Fullscreen
            Fullscreen().add_to(self.folium_map)
            
            # Add measure control
            from folium.plugins import MeasureControl
            MeasureControl().add_to(self.folium_map)
            
            print("Added map controls")
            
        except Exception as e:
            print(f"Failed to add controls: {e}")
    
    def add_vehicle_route(self, start_node: int, end_node: int):
        """Add vehicle route to map"""
        if not self.map_manager or not self.folium_map:
            return
        
        try:
            # Get route
            route_nodes = self.map_manager.get_shortest_path_nodes(start_node, end_node)
            if not route_nodes:
                return
            
            # Convert to coordinates
            route_coords = []
            for node in route_nodes:
                lon = self.map_manager.graph.nodes[node]['x']
                lat = self.map_manager.graph.nodes[node]['y']
                route_coords.append([lat, lon])
            
            # Add route to map
            folium.PolyLine(
                locations=route_coords,
                color='green',
                weight=4,
                opacity=0.8,
                popup="Vehicle Route"
            ).add_to(self.folium_map)
            
            print(f"Added route with {len(route_nodes)} nodes")
            
        except Exception as e:
            print(f"Failed to add route: {e}")
    
    def save_map(self, filename: str = "interactive_map.html"):
        """Save map to HTML file"""
        if not self.folium_map:
            print("No map to save")
            return
        
        try:
            self.folium_map.save(filename)
            print(f"Map saved as: {filename}")
            return filename
        except Exception as e:
            print(f"Failed to save map: {e}")
            return None
    
    def export_data(self):
        """Export simulation data as JSON"""
        data = {
            'vehicles': self.vehicles,
            'charging_stations': self.charging_stations,
            'location': self.location
        }
        
        filename = "simulation_data.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Data exported as: {filename}")
        return filename


def main():
    """Main function"""
    print("Starting Folium Interactive Map Demo...")
    
    demo = FoliumMapDemo()
    
    # Create map
    map_obj = demo.create_interactive_map()
    
    if map_obj:
        # Add a sample route
        if demo.vehicles and len(demo.vehicles) >= 2:
            start_node = demo.vehicles[0]['node']
            end_node = demo.vehicles[1]['node']
            demo.add_vehicle_route(start_node, end_node)
        
        # Save map
        filename = demo.save_map()
        
        if filename:
            # Export data
            demo.export_data()
            
            # Open in browser
            print(f"\nMap created successfully!")
            print(f"Opening {filename} in browser...")
            webbrowser.open(filename)
            
            print("\nFeatures:")
            print("- Interactive pan and zoom")
            print("- Click markers for details") 
            print("- Fullscreen mode available")
            print("- Measure distances")
            print("- Vehicle route displayed")
        else:
            print("Failed to save map")
    else:
        print("Failed to create map")


if __name__ == "__main__":
    main() 