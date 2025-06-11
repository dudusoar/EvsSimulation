<<<<<<< HEAD
"""
Visualization Module
Responsible for real-time visualization and animation generation of simulation process
Inherits and optimizes functionality from original animate.py
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle
import numpy as np
from typing import List, Dict, Tuple, Optional
from tqdm import tqdm
from datetime import datetime
import os

from core.simulation_engine import SimulationEngine
from models.vehicle import Vehicle
from models.order import Order
from models.charging_station import ChargingStation
from config.simulation_config import COLORS, VEHICLE_STATUS, ORDER_STATUS


class Visualizer:
    """Visualizer class"""
    
    def __init__(self, simulation_engine: SimulationEngine, config: Dict):
        """
        Initialize visualizer
        
        Args:
            simulation_engine: Simulation engine
            config: Configuration parameters
        """
        self.engine = simulation_engine
        self.config = config
        
        # Get map graphics
        self.fig, self.ax = self.engine.map_manager.setup_plot(
            show_preview=config.get('show_preview', False)
        )
        
        # Animation parameters
        self.fps = config.get('animation_fps', 30)
        self.interval = 1000 / self.fps  # milliseconds
        
        # Graphics element storage
        self.vehicle_artists = {}  # vehicle_id -> {'marker': artist, 'text': artist}
        self.order_markers = {}    # order_id -> {'pickup': artist, 'dropoff': artist}
        self.station_markers = []  # Charging station markers
        
        # Information text
        self.info_text = None
        self.stats_text = None
        
        # Initialize graphics elements
        self._initialize_graphics()
    
    # ============= Initialization Methods =============
    def _initialize_graphics(self):
        """Initialize graphics elements"""
        # Create vehicle graphics
        for vehicle in self.engine.get_vehicles():
            # Vehicle marker - reduce size
            marker, = self.ax.plot(
                [], [], 
                marker='o', 
                markersize=5,  # Changed from 8 to 5
                color=COLORS['vehicle']['idle'],
                markeredgecolor='black',
                markeredgewidth=0.5,
                animated=True
            )
            
            # Battery text
            text = self.ax.text(
                0, 0, '', 
                fontsize=7,  # Changed from 8 to 7
                ha='center', 
                va='bottom',
                animated=True
            )
            
            self.vehicle_artists[vehicle.vehicle_id] = {
                'marker': marker,
                'text': text
            }
        
        # Create charging station graphics - reduce size
        for station in self.engine.get_charging_stations():
            marker, = self.ax.plot(
                station.position[0], 
                station.position[1],
                marker='s',
                markersize=7,  # Changed from 12 to 7
                color=COLORS['charging_station'],
                markeredgecolor='black',
                markeredgewidth=1,
                animated=True
            )
            self.station_markers.append(marker)
        
        # Create information text
        self.info_text = self.ax.text(
            0.02, 0.98, '', 
            transform=self.ax.transAxes,
            fontsize=9,  # Changed from 10 to 9
            va='top',
            ha='left',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
            animated=True
        )
        
        self.stats_text = self.ax.text(
            0.98, 0.98, '', 
            transform=self.ax.transAxes,
            fontsize=8,  # Changed from 9 to 8
            va='top',
            ha='right',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
            animated=True
        )
    
    # ============= Animation Update Methods =============
    def init_animation(self):
        """Initialize animation"""
        # Clear all dynamic elements
        for vehicle_id, artists in self.vehicle_artists.items():
            artists['marker'].set_data([], [])
            artists['text'].set_text('')
        
        for order_id, markers in self.order_markers.items():
            if 'pickup' in markers:
                markers['pickup'].set_data([], [])
            if 'dropoff' in markers:
                markers['dropoff'].set_data([], [])
        
        self.info_text.set_text('')
        self.stats_text.set_text('')
        
        # Return all artists that need updating
        artists = []
        for v_artists in self.vehicle_artists.values():
            artists.extend([v_artists['marker'], v_artists['text']])
        artists.extend(self.station_markers)
        artists.extend([self.info_text, self.stats_text])
        
        return artists
    
    def update_frame(self, frame_num: int):
        """Update one frame"""
        # Run simulation step
        self.engine.run_step()
        
        # Update vehicles
        self._update_vehicles()
        
        # Update orders
        self._update_orders()
        
        # Update information text
        self._update_info_text()
        
        # Collect all artists
        artists = []
        for v_artists in self.vehicle_artists.values():
            artists.extend([v_artists['marker'], v_artists['text']])
        for markers in self.order_markers.values():
            if 'pickup' in markers:
                artists.append(markers['pickup'])
            if 'dropoff' in markers:
                artists.append(markers['dropoff'])
            if 'pickup_text' in markers:
                artists.append(markers['pickup_text'])
            if 'dropoff_text' in markers:
                artists.append(markers['dropoff_text'])
        artists.extend([self.info_text, self.stats_text])
        
        return artists
    
    def _update_vehicles(self):
        """Update vehicle display"""
        vehicles = self.engine.get_vehicles()
        
        for vehicle in vehicles:
            if vehicle.vehicle_id not in self.vehicle_artists:
                continue
            
            artists = self.vehicle_artists[vehicle.vehicle_id]
            
            # Update position
            artists['marker'].set_data([vehicle.position[0]], [vehicle.position[1]])
            
            # Update color
            color = COLORS['vehicle'].get(vehicle.status, 'gray')
            if vehicle.battery_percentage < 20:
                color = COLORS['low_battery']
            artists['marker'].set_color(color)
            
            # Update battery text - changed to English
            battery_text = f"{vehicle.battery_percentage:.0f}%"
            if vehicle.status == VEHICLE_STATUS['WITH_PASSENGER']:
                battery_text += " P"  # Passenger
            elif vehicle.status == VEHICLE_STATUS['CHARGING']:
                battery_text += " C"  # Charging
            
            artists['text'].set_text(battery_text)
            artists['text'].set_position((vehicle.position[0], vehicle.position[1] + 50))
    
    def _update_orders(self):
        """Update order display"""
        orders_info = self.engine.get_orders()
        
        # Get all active orders (pending and in progress)
        active_orders = orders_info['pending'] + orders_info['active']
        
        # Remove markers for completed orders
        completed_order_ids = set(self.order_markers.keys()) - set(o.order_id for o in active_orders)
        for order_id in completed_order_ids:
            if order_id in self.order_markers:
                markers = self.order_markers[order_id]
                if 'pickup' in markers:
                    markers['pickup'].remove()
                if 'dropoff' in markers:
                    markers['dropoff'].remove()
                if 'pickup_text' in markers:
                    markers['pickup_text'].remove()
                if 'dropoff_text' in markers:
                    markers['dropoff_text'].remove()
                del self.order_markers[order_id]
        
        # Update active orders
        for order in active_orders:
            if order.order_id not in self.order_markers:
                # Create new markers
                self.order_markers[order.order_id] = {}
                
                # Pickup point marker (triangle) - reduce size
                pickup_marker, = self.ax.plot(
                    order.pickup_position[0],
                    order.pickup_position[1],
                    marker='^',
                    markersize=6,  # Changed from 10 to 6
                    color=COLORS['order']['pickup'],
                    markeredgecolor='black',
                    markeredgewidth=0.5,
                    animated=True
                )
                self.order_markers[order.order_id]['pickup'] = pickup_marker
                
                # Pickup point number text
                pickup_text = self.ax.text(
                    order.pickup_position[0], 
                    order.pickup_position[1] + 30,
                    f"#{order.order_id[-3:]}",  # Show last 3 digits of order ID
                    fontsize=6,
                    ha='center',
                    va='bottom',
                    color='darkblue',
                    weight='bold',
                    animated=True
                )
                self.order_markers[order.order_id]['pickup_text'] = pickup_text
                
                # Dropoff point marker (inverted triangle) - always show
                dropoff_marker, = self.ax.plot(
                    order.dropoff_position[0],
                    order.dropoff_position[1],
                    marker='v',
                    markersize=6,  # Changed from 10 to 6
                    color=COLORS['order']['dropoff'],
                    markeredgecolor='black',
                    markeredgewidth=0.5,
                    animated=True
                )
                self.order_markers[order.order_id]['dropoff'] = dropoff_marker
                
                # Dropoff point number text
                dropoff_text = self.ax.text(
                    order.dropoff_position[0], 
                    order.dropoff_position[1] - 30,
                    f"#{order.order_id[-3:]}",  # Show last 3 digits of order ID
                    fontsize=6,
                    ha='center',
                    va='top',
                    color='darkmagenta',
                    weight='bold',
                    animated=True
                )
                self.order_markers[order.order_id]['dropoff_text'] = dropoff_text
    
    def _update_info_text(self):
        """Update information text"""
        # Get statistics
        stats = self.engine.get_current_statistics()
        
        # Main information
        info_lines = [
            f"Simulation time: {stats['simulation_time']:.1f} seconds",
            f"Vehicles: {stats['vehicles']['total_vehicles']} vehicles",
            f"Orders: {stats['orders']['pending_orders']} pending, "
            f"{stats['orders']['active_orders']} active",
            f"Average battery: {stats['vehicles']['avg_battery_percentage']:.1f}%"
        ]
        self.info_text.set_text('\n'.join(info_lines))
        
        # Statistics
        stats_lines = [
            f"Completed orders: {stats['orders']['total_orders_completed']}",
            f"Total revenue: ${stats['orders']['total_revenue']:.2f}",
            f"Vehicle utilization: {stats['vehicles']['utilization_rate']*100:.1f}%",
            f"Charging station utilization: {stats['charging']['avg_utilization_rate']*100:.1f}%"
        ]
        self.stats_text.set_text('\n'.join(stats_lines))
    
    # ============= Animation Generation Methods =============
    def create_animation(self, duration: float) -> animation.FuncAnimation:
        """
        Create animation
        
        Args:
            duration: Simulation duration (seconds)
        
        Returns:
            Animation object
        """
        n_frames = int(duration / self.engine.time_step)
        
        # Create animation
        ani = animation.FuncAnimation(
            self.fig,
            self.update_frame,
            init_func=self.init_animation,
            frames=tqdm(range(n_frames), desc="Generating animation"),
            interval=self.interval,
            blit=True,
            repeat=False
        )
        
        return ani
    
    def save_animation(self, filename: str = None, format: str = 'html'):
        """
        Save animation
        
        Args:
            filename: Filename (without extension)
            format: Format ('html' or 'mp4')
        """
        # Ensure output directory exists
        output_dir = 'outputs/visualizations'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ev_simulation_{timestamp}"
        
        duration = self.config.get('simulation_duration', 3600)
        ani = self.create_animation(duration)
        
        if format == 'html':
            writer = animation.HTMLWriter(fps=self.fps)
            output_file = os.path.join(output_dir, f"{filename}.html")
        elif format == 'mp4':
            writer = animation.FFMpegWriter(fps=self.fps)
            output_file = os.path.join(output_dir, f"{filename}.mp4")
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        print(f"Saving animation to: {output_file}")
        ani.save(output_file, writer=writer)
        print("Animation saved successfully!")
        
=======
"""
Visualization Module
Responsible for real-time visualization and animation generation of simulation process
Inherits and optimizes functionality from original animate.py
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle
import numpy as np
from typing import List, Dict, Tuple, Optional
from tqdm import tqdm
from datetime import datetime
import os

from core.simulation_engine import SimulationEngine
from models.vehicle import Vehicle
from models.order import Order
from models.charging_station import ChargingStation
from config.simulation_config import COLORS, VEHICLE_STATUS, ORDER_STATUS


class Visualizer:
    """Visualizer class"""
    
    def __init__(self, simulation_engine: SimulationEngine, config: Dict):
        """
        Initialize visualizer
        
        Args:
            simulation_engine: Simulation engine
            config: Configuration parameters
        """
        self.engine = simulation_engine
        self.config = config
        
        # Get map graphics
        self.fig, self.ax = self.engine.map_manager.setup_plot(
            show_preview=config.get('show_preview', False)
        )
        
        # Animation parameters
        self.fps = config.get('animation_fps', 30)
        self.interval = 1000 / self.fps  # milliseconds
        
        # Graphics element storage
        self.vehicle_artists = {}  # vehicle_id -> {'marker': artist, 'text': artist}
        self.order_markers = {}    # order_id -> {'pickup': artist, 'dropoff': artist}
        self.station_markers = []  # Charging station markers
        
        # Information text
        self.info_text = None
        self.stats_text = None
        
        # Initialize graphics elements
        self._initialize_graphics()
    
    # ============= Initialization Methods =============
    def _initialize_graphics(self):
        """Initialize graphics elements"""
        # Create vehicle graphics
        for vehicle in self.engine.get_vehicles():
            # Vehicle marker - reduce size
            marker, = self.ax.plot(
                [], [], 
                marker='o', 
                markersize=5,  # Changed from 8 to 5
                color=COLORS['vehicle']['idle'],
                markeredgecolor='black',
                markeredgewidth=0.5,
                animated=True
            )
            
            # Battery text
            text = self.ax.text(
                0, 0, '', 
                fontsize=7,  # Changed from 8 to 7
                ha='center', 
                va='bottom',
                animated=True
            )
            
            self.vehicle_artists[vehicle.vehicle_id] = {
                'marker': marker,
                'text': text
            }
        
        # Create charging station graphics - reduce size
        for station in self.engine.get_charging_stations():
            marker, = self.ax.plot(
                station.position[0], 
                station.position[1],
                marker='s',
                markersize=7,  # Changed from 12 to 7
                color=COLORS['charging_station'],
                markeredgecolor='black',
                markeredgewidth=1,
                animated=True
            )
            self.station_markers.append(marker)
        
        # Create information text
        self.info_text = self.ax.text(
            0.02, 0.98, '', 
            transform=self.ax.transAxes,
            fontsize=9,  # Changed from 10 to 9
            va='top',
            ha='left',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
            animated=True
        )
        
        self.stats_text = self.ax.text(
            0.98, 0.98, '', 
            transform=self.ax.transAxes,
            fontsize=8,  # Changed from 9 to 8
            va='top',
            ha='right',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
            animated=True
        )
    
    # ============= Animation Update Methods =============
    def init_animation(self):
        """Initialize animation"""
        # Clear all dynamic elements
        for vehicle_id, artists in self.vehicle_artists.items():
            artists['marker'].set_data([], [])
            artists['text'].set_text('')
        
        for order_id, markers in self.order_markers.items():
            if 'pickup' in markers:
                markers['pickup'].set_data([], [])
            if 'dropoff' in markers:
                markers['dropoff'].set_data([], [])
        
        self.info_text.set_text('')
        self.stats_text.set_text('')
        
        # Return all artists that need updating
        artists = []
        for v_artists in self.vehicle_artists.values():
            artists.extend([v_artists['marker'], v_artists['text']])
        artists.extend(self.station_markers)
        artists.extend([self.info_text, self.stats_text])
        
        return artists
    
    def update_frame(self, frame_num: int):
        """Update one frame"""
        # Run simulation step
        self.engine.run_step()
        
        # Update vehicles
        self._update_vehicles()
        
        # Update orders
        self._update_orders()
        
        # Update information text
        self._update_info_text()
        
        # Collect all artists
        artists = []
        for v_artists in self.vehicle_artists.values():
            artists.extend([v_artists['marker'], v_artists['text']])
        for markers in self.order_markers.values():
            if 'pickup' in markers:
                artists.append(markers['pickup'])
            if 'dropoff' in markers:
                artists.append(markers['dropoff'])
            if 'pickup_text' in markers:
                artists.append(markers['pickup_text'])
            if 'dropoff_text' in markers:
                artists.append(markers['dropoff_text'])
        artists.extend([self.info_text, self.stats_text])
        
        return artists
    
    def _update_vehicles(self):
        """Update vehicle display"""
        vehicles = self.engine.get_vehicles()
        
        for vehicle in vehicles:
            if vehicle.vehicle_id not in self.vehicle_artists:
                continue
            
            artists = self.vehicle_artists[vehicle.vehicle_id]
            
            # Update position
            artists['marker'].set_data([vehicle.position[0]], [vehicle.position[1]])
            
            # Update color
            color = COLORS['vehicle'].get(vehicle.status, 'gray')
            if vehicle.battery_percentage < 20:
                color = COLORS['low_battery']
            artists['marker'].set_color(color)
            
            # Update battery text - changed to English
            battery_text = f"{vehicle.battery_percentage:.0f}%"
            if vehicle.status == VEHICLE_STATUS['WITH_PASSENGER']:
                battery_text += " P"  # Passenger
            elif vehicle.status == VEHICLE_STATUS['CHARGING']:
                battery_text += " C"  # Charging
            
            artists['text'].set_text(battery_text)
            artists['text'].set_position((vehicle.position[0], vehicle.position[1] + 50))
    
    def _update_orders(self):
        """Update order display"""
        orders_info = self.engine.get_orders()
        
        # Get all active orders (pending and in progress)
        active_orders = orders_info['pending'] + orders_info['active']
        
        # Remove markers for completed orders
        completed_order_ids = set(self.order_markers.keys()) - set(o.order_id for o in active_orders)
        for order_id in completed_order_ids:
            if order_id in self.order_markers:
                markers = self.order_markers[order_id]
                if 'pickup' in markers:
                    markers['pickup'].remove()
                if 'dropoff' in markers:
                    markers['dropoff'].remove()
                if 'pickup_text' in markers:
                    markers['pickup_text'].remove()
                if 'dropoff_text' in markers:
                    markers['dropoff_text'].remove()
                del self.order_markers[order_id]
        
        # Update active orders
        for order in active_orders:
            if order.order_id not in self.order_markers:
                # Create new markers
                self.order_markers[order.order_id] = {}
                
                # Pickup point marker (triangle) - reduce size
                pickup_marker, = self.ax.plot(
                    order.pickup_position[0],
                    order.pickup_position[1],
                    marker='^',
                    markersize=6,  # Changed from 10 to 6
                    color=COLORS['order']['pickup'],
                    markeredgecolor='black',
                    markeredgewidth=0.5,
                    animated=True
                )
                self.order_markers[order.order_id]['pickup'] = pickup_marker
                
                # Pickup point number text
                pickup_text = self.ax.text(
                    order.pickup_position[0], 
                    order.pickup_position[1] + 30,
                    f"#{order.order_id[-3:]}",  # Show last 3 digits of order ID
                    fontsize=6,
                    ha='center',
                    va='bottom',
                    color='darkblue',
                    weight='bold',
                    animated=True
                )
                self.order_markers[order.order_id]['pickup_text'] = pickup_text
                
                # Dropoff point marker (inverted triangle) - always show
                dropoff_marker, = self.ax.plot(
                    order.dropoff_position[0],
                    order.dropoff_position[1],
                    marker='v',
                    markersize=6,  # Changed from 10 to 6
                    color=COLORS['order']['dropoff'],
                    markeredgecolor='black',
                    markeredgewidth=0.5,
                    animated=True
                )
                self.order_markers[order.order_id]['dropoff'] = dropoff_marker
                
                # Dropoff point number text
                dropoff_text = self.ax.text(
                    order.dropoff_position[0], 
                    order.dropoff_position[1] - 30,
                    f"#{order.order_id[-3:]}",  # Show last 3 digits of order ID
                    fontsize=6,
                    ha='center',
                    va='top',
                    color='darkmagenta',
                    weight='bold',
                    animated=True
                )
                self.order_markers[order.order_id]['dropoff_text'] = dropoff_text
    
    def _update_info_text(self):
        """Update information text"""
        # Get statistics
        stats = self.engine.get_current_statistics()
        
        # Main information
        info_lines = [
            f"Simulation time: {stats['simulation_time']:.1f} seconds",
            f"Vehicles: {stats['vehicles']['total_vehicles']} vehicles",
            f"Orders: {stats['orders']['pending_orders']} pending, "
            f"{stats['orders']['active_orders']} active",
            f"Average battery: {stats['vehicles']['avg_battery_percentage']:.1f}%"
        ]
        self.info_text.set_text('\n'.join(info_lines))
        
        # Statistics
        stats_lines = [
            f"Completed orders: {stats['orders']['total_orders_completed']}",
            f"Total revenue: ${stats['orders']['total_revenue']:.2f}",
            f"Vehicle utilization: {stats['vehicles']['utilization_rate']*100:.1f}%",
            f"Charging station utilization: {stats['charging']['avg_utilization_rate']*100:.1f}%"
        ]
        self.stats_text.set_text('\n'.join(stats_lines))
    
    # ============= Animation Generation Methods =============
    def create_animation(self, duration: float) -> animation.FuncAnimation:
        """
        Create animation
        
        Args:
            duration: Simulation duration (seconds)
        
        Returns:
            Animation object
        """
        n_frames = int(duration / self.engine.time_step)
        
        # Create animation
        ani = animation.FuncAnimation(
            self.fig,
            self.update_frame,
            init_func=self.init_animation,
            frames=tqdm(range(n_frames), desc="Generating animation"),
            interval=self.interval,
            blit=True,
            repeat=False
        )
        
        return ani
    
    def save_animation(self, filename: str = None, format: str = 'html'):
        """
        Save animation
        
        Args:
            filename: Filename (without extension)
            format: Format ('html' or 'mp4')
        """
        # Ensure output directory exists
        output_dir = 'outputs/visualizations'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ev_simulation_{timestamp}"
        
        duration = self.config.get('simulation_duration', 3600)
        ani = self.create_animation(duration)
        
        if format == 'html':
            writer = animation.HTMLWriter(fps=self.fps)
            output_file = os.path.join(output_dir, f"{filename}.html")
        elif format == 'mp4':
            writer = animation.FFMpegWriter(fps=self.fps)
            output_file = os.path.join(output_dir, f"{filename}.mp4")
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        print(f"Saving animation to: {output_file}")
        ani.save(output_file, writer=writer)
        print("Animation saved successfully!")
        
>>>>>>> b9bd6771fbd7f2273a429016a9b2c009e69bada8
        return output_file