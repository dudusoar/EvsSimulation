#!/usr/bin/env python3
"""
Folium EV Simulation Runner
Real simulation animation on interactive map
"""

import folium
from folium.plugins import TimestampedGeoJson
import json
import time
import threading
import webbrowser
import sys
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import math

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.map_manager import MapManager
    from core.simulation_engine import SimulationEngine
    MAP_AVAILABLE = True
    print("Simulation modules loaded successfully")
except ImportError as e:
    print(f"Warning: Simulation modules not available: {e}")
    MAP_AVAILABLE = False


class FoliumSimulationRunner:
    """Run EV simulation on Folium map"""
    
    def __init__(self, location="West Lafayette, Indiana"):
        self.location = location
        self.map_manager = None
        self.simulation_engine = None
        
        # Simulation parameters
        self.sim_config = {
            'location': location,
            'num_vehicles': 15,
            'num_charging_stations': 6,
            'duration': 300,  # 5 minutes for demo
            'time_step': 1.0,  # 1 second per step
            'animation_speed': 0.5  # seconds between frames
        }
        
        # Animation data
        self.animation_data = []
        self.current_frame = 0
        self.is_running = False
        
        # File paths
        self.map_file = "simulation_animation.html"
        self.data_file = "simulation_data.json"

    def initialize_simulation(self):
        """Initialize the simulation system"""
        if not MAP_AVAILABLE:
            print("Simulation modules not available")
            return False
        
        try:
            print(f"Initializing simulation for {self.location}...")
            
            # Create map manager
            self.map_manager = MapManager(self.location)
            
            # Create simulation engine
            self.simulation_engine = SimulationEngine(self.sim_config)
            
            print("Simulation initialized successfully!")
            return True
            
        except Exception as e:
            print(f"Failed to initialize simulation: {e}")
            return False

    def generate_simulation_frames(self):
        """Generate all simulation frames"""
        if not self.simulation_engine:
            return
        
        print("Generating simulation frames...")
        frames = []
        
        # Run simulation and capture each frame
        total_steps = int(self.sim_config['duration'] / self.sim_config['time_step'])
        
        for step in range(total_steps):
            # Run one simulation step
            self.simulation_engine.run_step()
            
            # Capture current state
            frame_data = self.capture_simulation_frame(step)
            frames.append(frame_data)
            
            # Progress indicator
            if step % 20 == 0:
                progress = (step / total_steps) * 100
                print(f"Progress: {progress:.1f}%")
        
        self.animation_data = frames
        print(f"Generated {len(frames)} simulation frames")

    def capture_simulation_frame(self, step: int) -> Dict:
        """Capture current simulation state as a frame"""
        frame_time = step * self.sim_config['time_step']
        
        # Get vehicles
        vehicles = []
        for vehicle in self.simulation_engine.get_vehicles():
            if vehicle.current_node:
                lat, lon = self.get_node_coordinates(vehicle.current_node)
                
                # Determine vehicle status and color
                status = "available"
                color = "blue"
                
                if hasattr(vehicle, 'current_task') and vehicle.current_task:
                    if vehicle.current_task.get('type') == 'pickup':
                        status = "to_pickup"
                        color = "orange"
                    elif vehicle.current_task.get('type') == 'delivery':
                        status = "with_passenger"
                        color = "green"
                    elif vehicle.current_task.get('type') == 'charging':
                        status = "to_charging"
                        color = "purple"
                
                vehicles.append({
                    'id': vehicle.vehicle_id,
                    'lat': lat,
                    'lon': lon,
                    'status': status,
                    'color': color,
                    'battery': vehicle.battery_percentage,
                    'speed': getattr(vehicle, 'current_speed', 0)
                })
        
        # Get orders
        orders = []
        order_data = self.simulation_engine.get_orders()
        
        # Pending orders
        for order in order_data.get('pending', []):
            pickup_lat, pickup_lon = self.get_node_coordinates(order.pickup_node)
            delivery_lat, delivery_lon = self.get_node_coordinates(order.delivery_node)
            
            orders.append({
                'id': order.order_id,
                'type': 'pending',
                'pickup_lat': pickup_lat,
                'pickup_lon': pickup_lon,
                'delivery_lat': delivery_lat,
                'delivery_lon': delivery_lon,
                'color': 'red'
            })
        
        # Active orders
        for order in order_data.get('active', []):
            pickup_lat, pickup_lon = self.get_node_coordinates(order.pickup_node)
            delivery_lat, delivery_lon = self.get_node_coordinates(order.delivery_node)
            
            orders.append({
                'id': order.order_id,
                'type': 'active',
                'pickup_lat': pickup_lat,
                'pickup_lon': pickup_lon,
                'delivery_lat': delivery_lat,
                'delivery_lon': delivery_lon,
                'color': 'yellow'
            })
        
        # Get charging stations
        stations = []
        for station in self.simulation_engine.get_charging_stations():
            lat, lon = self.get_node_coordinates(station.node_id)
            
            stations.append({
                'id': station.station_id,
                'lat': lat,
                'lon': lon,
                'power': station.charging_power,
                'occupied': len(station.charging_vehicles),
                'capacity': station.capacity,
                'color': 'red' if len(station.charging_vehicles) >= station.capacity else 'darkred'
            })
        
        # Get statistics
        stats = self.simulation_engine.get_current_statistics()
        
        return {
            'time': frame_time,
            'step': step,
            'vehicles': vehicles,
            'orders': orders,
            'stations': stations,
            'stats': {
                'simulation_time': frame_time,
                'active_vehicles': len(vehicles),
                'pending_orders': len([o for o in orders if o['type'] == 'pending']),
                'active_orders': len([o for o in orders if o['type'] == 'active']),
                'total_revenue': stats.get('orders', {}).get('total_revenue', 0),
                'avg_battery': stats.get('vehicles', {}).get('avg_battery_percentage', 0)
            }
        }

    def get_node_coordinates(self, node_id: int) -> Tuple[float, float]:
        """Get lat/lon coordinates for a node"""
        if not self.map_manager:
            return 40.4259, -86.9081  # Default West Lafayette
        
        try:
            lon = self.map_manager.graph.nodes[node_id]['x']
            lat = self.map_manager.graph.nodes[node_id]['y']
            return lat, lon
        except:
            return 40.4259, -86.9081

    def create_animated_map(self):
        """Create Folium map with animation"""
        if not self.animation_data:
            print("No animation data available")
            return
        
        print("Creating animated map...")
        
        # Calculate map center
        all_lats = []
        all_lons = []
        
        for frame in self.animation_data[:10]:  # Sample first 10 frames
            for vehicle in frame['vehicles']:
                all_lats.append(vehicle['lat'])
                all_lons.append(vehicle['lon'])
        
        center_lat = sum(all_lats) / len(all_lats) if all_lats else 40.4259
        center_lon = sum(all_lons) / len(all_lons) if all_lons else -86.9081
        
        # Create base map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=13,
            tiles='OpenStreetMap'
        )
        
        # Add title and controls
        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 400px; height: 80px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:16px; padding: 10px">
        <h3>🚗 EV Simulation Animation</h3>
        <p>📍 Location: ''' + self.location + '''</p>
        <p>⏱️ <span id="sim-time">Time: 00:00</span> | 🔋 <span id="avg-battery">Battery: 0%</span></p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Add charging stations (static)
        if self.animation_data:
            first_frame = self.animation_data[0]
            for station in first_frame['stations']:
                folium.Marker(
                    location=[station['lat'], station['lon']],
                    popup=f"Charging Station {station['id']}<br>Power: {station['power']}kW<br>Capacity: {station['capacity']}",
                    tooltip=f"Station {station['id']}",
                    icon=folium.Icon(color='red', icon='plug', prefix='fa')
                ).add_to(m)
        
        # Create timestamped data for vehicles
        self.add_vehicle_animation(m)
        
        # Add animation controls
        self.add_animation_controls(m)
        
        # Save map
        m.save(self.map_file)
        print(f"Animated map saved as: {self.map_file}")

    def add_vehicle_animation(self, map_obj):
        """Add vehicle animation using timestamped data"""
        # Prepare timestamped features for each vehicle
        vehicle_features = []
        
        # Get all unique vehicle IDs
        all_vehicle_ids = set()
        for frame in self.animation_data:
            for vehicle in frame['vehicles']:
                all_vehicle_ids.add(vehicle['id'])
        
        # Create animation data for each vehicle
        for vehicle_id in all_vehicle_ids:
            vehicle_path = []
            
            for frame in self.animation_data:
                # Find this vehicle in current frame
                vehicle_data = None
                for v in frame['vehicles']:
                    if v['id'] == vehicle_id:
                        vehicle_data = v
                        break
                
                if vehicle_data:
                    # Create timestamp
                    timestamp = datetime.now() + timedelta(seconds=frame['time'])
                    
                    # Create feature for this time point
                    feature = {
                        'type': 'Feature',
                        'geometry': {
                            'type': 'Point',
                            'coordinates': [vehicle_data['lon'], vehicle_data['lat']]
                        },
                        'properties': {
                            'time': timestamp.isoformat(),
                            'style': {
                                'color': vehicle_data['color'],
                                'fillColor': vehicle_data['color'],
                                'fillOpacity': 0.8,
                                'radius': 8
                            },
                            'popup': f"Vehicle {vehicle_id}<br>Status: {vehicle_data['status']}<br>Battery: {vehicle_data['battery']:.1f}%"
                        }
                    }
                    vehicle_path.append(feature)
            
            # Add this vehicle's path to the map
            if vehicle_path:
                TimestampedGeoJson(
                    {
                        'type': 'FeatureCollection',
                        'features': vehicle_path
                    },
                    period='PT1S',  # 1 second intervals
                    add_last_point=True,
                    auto_play=False,
                    loop=False,
                    max_speed=10,
                    loop_button=True,
                    date_options='YYYY-MM-DD HH:mm:ss',
                    time_slider_drag_update=True
                ).add_to(map_obj)

    def add_animation_controls(self, map_obj):
        """Add custom animation controls"""
        # Add JavaScript for real-time updates
        animation_js = '''
        <script>
        let simulationData = ''' + json.dumps(self.animation_data) + ''';
        let currentFrame = 0;
        let isPlaying = false;
        let animationInterval;
        
        function updateDisplay(frameIndex) {
            if (frameIndex < simulationData.length) {
                let frame = simulationData[frameIndex];
                
                // Update time display
                let minutes = Math.floor(frame.time / 60);
                let seconds = Math.floor(frame.time % 60);
                document.getElementById('sim-time').innerHTML = 
                    'Time: ' + minutes.toString().padStart(2, '0') + ':' + seconds.toString().padStart(2, '0');
                
                // Update battery display
                document.getElementById('avg-battery').innerHTML = 
                    'Battery: ' + frame.stats.avg_battery.toFixed(1) + '%';
            }
        }
        
        function playAnimation() {
            if (isPlaying) return;
            isPlaying = true;
            
            animationInterval = setInterval(() => {
                updateDisplay(currentFrame);
                currentFrame++;
                
                if (currentFrame >= simulationData.length) {
                    pauseAnimation();
                    currentFrame = 0;
                }
            }, ''' + str(int(self.sim_config['animation_speed'] * 1000)) + ''');
        }
        
        function pauseAnimation() {
            isPlaying = false;
            if (animationInterval) {
                clearInterval(animationInterval);
            }
        }
        
        // Auto-start animation after 2 seconds
        setTimeout(() => {
            console.log('Starting EV simulation animation...');
            updateDisplay(0);
        }, 2000);
        </script>
        '''
        
        map_obj.get_root().html.add_child(folium.Element(animation_js))

    def export_simulation_data(self):
        """Export simulation data as JSON"""
        data = {
            'config': self.sim_config,
            'frames': self.animation_data,
            'summary': {
                'total_frames': len(self.animation_data),
                'duration': self.sim_config['duration'],
                'location': self.location
            }
        }
        
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Simulation data exported to: {self.data_file}")

    def create_demo_animation(self):
        """Create demo animation with simulated data"""
        print("Creating demo animation...")
        
        # Create base map for West Lafayette
        center_lat, center_lon = 40.4259, -86.9081
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=14,
            tiles='OpenStreetMap'
        )
        
        # Add title
        title_html = '''
        <div style="position: fixed; top: 10px; left: 50px; width: 400px; height: 80px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:16px; padding: 10px">
        <h3>🚗 EV Simulation Demo</h3>
        <p>📍 Location: West Lafayette, Indiana</p>
        <p>⏱️ Watch the vehicles move in real-time!</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Add charging stations
        stations = [
            [40.4289, -86.9081, "Purdue Memorial Union"],
            [40.4259, -86.9181, "Walmart Supercenter"],
            [40.4309, -86.9031, "Village Shopping Center"],
        ]
        
        for i, (lat, lon, name) in enumerate(stations):
            folium.Marker(
                location=[lat, lon],
                popup=f"Charging Station {i+1}<br>{name}<br>Power: 50kW",
                tooltip=f"Station {i+1}",
                icon=folium.Icon(color='red', icon='plug', prefix='fa')
            ).add_to(m)
        
        # Create vehicle animation paths
        vehicle_paths = []
        
        for vehicle_id in range(5):
            path = []
            # Create a circular path for each vehicle
            for t in range(100):  # 100 time points
                angle = (t * 0.1 + vehicle_id * 1.2) % (2 * 3.14159)
                radius = 0.01 + vehicle_id * 0.002
                
                lat = center_lat + radius * math.cos(angle)
                lon = center_lon + radius * math.sin(angle)
                
                # Create timestamp
                timestamp = datetime.now() + timedelta(seconds=t*2)
                
                # Determine color based on vehicle state
                colors = ['blue', 'green', 'orange', 'purple', 'darkblue']
                status = ['available', 'with_passenger', 'to_pickup', 'charging', 'available'][t % 5]
                
                feature = {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [lon, lat]
                    },
                    'properties': {
                        'time': timestamp.isoformat(),
                        'style': {
                            'color': colors[vehicle_id],
                            'fillColor': colors[vehicle_id],
                            'fillOpacity': 0.8,
                            'radius': 8
                        },
                        'popup': f"Vehicle {vehicle_id+1}<br>Status: {status}<br>Battery: {85 + t%15}%"
                    }
                }
                path.append(feature)
            
            vehicle_paths.append(path)
        
        # Add vehicle animations
        for vehicle_id, path in enumerate(vehicle_paths):
            TimestampedGeoJson(
                {
                    'type': 'FeatureCollection',
                    'features': path
                },
                period='PT2S',  # 2 second intervals
                add_last_point=True,
                auto_play=True,
                loop=True,
                max_speed=10,
                loop_button=True,
                date_options='YYYY-MM-DD HH:mm:ss',
                time_slider_drag_update=True
            ).add_to(m)
        
        # Save map
        m.save(self.map_file)
        print(f"Demo map saved as: {self.map_file}")

    def run_simulation(self):
        """Run the complete simulation process"""
        print("🚗 Starting EV Simulation on Folium Map")
        print("=" * 50)
        
        # Create simplified demo
        self.create_demo_animation()
        
        print("\n✅ Demo Complete!")
        print(f"📁 Map file: {self.map_file}")
        
        # Open in browser
        print(f"\n🌐 Opening {self.map_file} in browser...")
        webbrowser.open(self.map_file)


def main():
    """Main function"""
    print("EV Simulation on Folium Map")
    
    # Create simulation runner
    runner = FoliumSimulationRunner("West Lafayette, Indiana")
    
    # Run simulation
    runner.run_simulation()


if __name__ == "__main__":
    main() 