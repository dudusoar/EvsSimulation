"""
Visualization Module
Real-time visualization of simulation process using matplotlib
Provides live display without frame storage for efficient visualization
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import os
import time

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
        
        # Live visualization parameters
        self.fps = config.get('animation_fps', 30)
        
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
                markeredgewidth=0.5
            )
            
            # Battery text
            text = self.ax.text(
                0, 0, '', 
                fontsize=7,  # Changed from 8 to 7
                ha='center', 
                va='bottom'
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
                markeredgewidth=1
            )
            self.station_markers.append(marker)
        
        # Create information text
        self.info_text = self.ax.text(
            0.02, 0.98, '', 
            transform=self.ax.transAxes,
            fontsize=9,  # Changed from 10 to 9
            va='top',
            ha='left',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
        )
        
        self.stats_text = self.ax.text(
            0.98, 0.98, '', 
            transform=self.ax.transAxes,
            fontsize=8,  # Changed from 9 to 8
            va='top',
            ha='right',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
        )

    # ============= Live Simulation Methods =============
    def run_live_simulation(self, duration: float = None):
        """
        Run simulation in real-time with live display, no frame storage
        
        Args:
            duration: Simulation duration in seconds, uses config default if None
        """
        if duration is None:
            duration = self.config.get('simulation_duration', 3600)
        
        print(f"\n🚀 Starting Live Simulation Visualization (Duration: {duration}s)")
        print("💡 Close window or press Ctrl+C to stop simulation")
        print("=" * 50)
        
        # Enable interactive mode
        plt.ion()
        plt.show()
        
        # Initialize display
        self._clear_dynamic_elements()
        
        start_time = time.time()
        step_count = 0
        update_interval = 1.0 / self.fps  # Update interval
        
        try:
            while self.engine.current_time < duration:
                step_start = time.time()
                
                # Run one simulation step
                self.engine.run_step()
                step_count += 1
                
                # Update display
                self._update_live_display()
                
                # Refresh graphics
                self.fig.canvas.draw()
                self.fig.canvas.flush_events()
                
                # Check if window was closed
                if not plt.get_fignums():
                    print("\n🛑 Window closed, stopping simulation")
                    break
                
                # Control update frequency
                elapsed = time.time() - step_start
                if elapsed < update_interval:
                    plt.pause(update_interval - elapsed)
                else:
                    plt.pause(0.001)  # Give GUI some time to respond
                
                # Periodic progress output
                if step_count % 100 == 0:
                    progress = (self.engine.current_time / duration) * 100
                    print(f"Simulation progress: {progress:.1f}% (Time: {self.engine.current_time:.1f}s)")
        
        except KeyboardInterrupt:
            print("\n🛑 User interrupted simulation")
        
        except Exception as e:
            print(f"\n❌ Error during simulation: {e}")
        
        finally:
            # Display final statistics
            final_stats = self.engine.get_final_statistics()
            print("\n" + "=" * 60)
            print("📊 SIMULATION COMPLETED - FINAL STATISTICS")
            print("=" * 60)
            
            # Basic simulation info
            print(f"\n🕒 SIMULATION SUMMARY:")
            print(f"   Total simulation time: {self.engine.current_time:.1f} seconds")
            print(f"   Total simulation steps: {self.engine.statistics['total_steps']}")
            
            # Financial statistics
            summary = final_stats.get('summary', {})
            print(f"\n💰 FINANCIAL PERFORMANCE:")
            print(f"   Total revenue: ${summary.get('total_revenue', 0):.2f}")
            print(f"   Total cost: ${summary.get('total_cost', 0):.2f}")
            print(f"   Total profit: ${summary.get('total_profit', 0):.2f}")
            revenue = summary.get('total_revenue', 0)
            profit = summary.get('total_profit', 0)
            print(f"   Profit margin: {(profit/revenue*100) if revenue > 0 else 0:.1f}%")
            
            # Order statistics
            orders = final_stats.get('orders', {})
            print(f"\n📋 ORDER STATISTICS:")
            print(f"   Total orders completed: {orders.get('total_orders_completed', 0)}")
            print(f"   Total orders generated: {orders.get('total_orders_generated', 0)}")
            print(f"   Order completion rate: {summary.get('order_completion_rate', 0)*100:.1f}%")
            print(f"   Average order value: ${orders.get('avg_order_value', 0):.2f}")
            print(f"   Average waiting time: {orders.get('avg_waiting_time', 0):.1f} seconds")
            
            # Vehicle statistics
            vehicles = final_stats.get('vehicles', {})
            print(f"\n🚗 VEHICLE FLEET STATISTICS:")
            print(f"   Total vehicles: {vehicles.get('total_vehicles', 0)}")
            print(f"   Average battery level: {vehicles.get('avg_battery_percentage', 0):.1f}%")
            print(f"   Fleet utilization rate: {summary.get('vehicle_utilization_rate', 0)*100:.1f}%")
            print(f"   Total distance traveled: {vehicles.get('total_distance_traveled', 0):.1f} km")
            print(f"   Average distance per vehicle: {vehicles.get('avg_distance_per_vehicle', 0):.1f} km")
            
            # Charging statistics
            charging = final_stats.get('charging', {})
            print(f"\n🔋 CHARGING INFRASTRUCTURE:")
            print(f"   Total charging stations: {charging.get('total_stations', 0)}")
            print(f"   Average utilization rate: {summary.get('charging_utilization_rate', 0)*100:.1f}%")
            print(f"   Total charging sessions: {charging.get('total_charging_sessions', 0)}")
            print(f"   Total energy consumed: {charging.get('total_energy_consumed', 0):.1f} kWh")
            
            # Detailed vehicle performance (top 5 performers)
            if 'vehicle_details' in final_stats and final_stats['vehicle_details']:
                vehicle_details = final_stats['vehicle_details']
                # Sort by total revenue
                sorted_vehicles = sorted(vehicle_details, key=lambda x: x.get('total_revenue', 0), reverse=True)
                
                print(f"\n🏆 TOP PERFORMING VEHICLES:")
                for i, vehicle in enumerate(sorted_vehicles[:5]):
                    vehicle_id = vehicle.get('vehicle_id', f'Unknown_{i}')
                    print(f"   #{i+1}: Vehicle {vehicle_id[-6:] if len(vehicle_id) > 6 else vehicle_id}")
                    print(f"       Revenue: ${vehicle.get('total_revenue', 0):.2f}")
                    print(f"       Orders completed: {vehicle.get('orders_completed', 0)}")
                    print(f"       Distance traveled: {vehicle.get('total_distance', 0):.1f} km")
                    print(f"       Battery cycles: {vehicle.get('charging_cycles', 0)}")
            
            # Performance metrics
            print(f"\n📊 PERFORMANCE METRICS:")
            total_revenue = summary.get('total_revenue', 0)
            total_orders = orders.get('total_orders_completed', 0)
            sim_time_hours = self.engine.current_time / 3600
            
            if total_revenue > 0 and sim_time_hours > 0:
                print(f"   Revenue per hour: ${total_revenue / sim_time_hours:.2f}")
                print(f"   Orders per hour: {total_orders / sim_time_hours:.1f}")
            print(f"   Average vehicle efficiency: {vehicles.get('avg_efficiency', 0):.2f} km/kWh")
            
            print("=" * 60)
            print("📈 Simulation data is available in the final_stats object")
            print("💾 Use --save-data flag to export detailed reports and CSV files")
            
            # Keep window open for user to view final results
            print("\n💡 Close window to exit")
            plt.ioff()
            plt.show()
            
            # Return final_stats for unified saving in main.py
            return final_stats
    
    def _clear_dynamic_elements(self):
        """Clear dynamic display elements"""
        # Clear vehicle displays
        for vehicle_id, artists in self.vehicle_artists.items():
            artists['marker'].set_data([], [])
            artists['text'].set_text('')
        
        # Clear order markers
        for order_id, markers in self.order_markers.items():
            if 'pickup' in markers:
                markers['pickup'].remove()
            if 'dropoff' in markers:
                markers['dropoff'].remove()
            if 'pickup_text' in markers:
                markers['pickup_text'].remove()
            if 'dropoff_text' in markers:
                markers['dropoff_text'].remove()
        self.order_markers.clear()
        
        # Clear info text
        self.info_text.set_text('')
        self.stats_text.set_text('')
    
    def _update_live_display(self):
        """Update live display"""
        # Update vehicles
        self._update_vehicles()
        
        # Update orders
        self._update_orders()
        
        # Update info text
        self._update_info_text()

    # ============= Legacy Animation Methods (REMOVED) =============
    # init_animation() and update_frame() methods have been removed
    # These were used for traditional frame-based animation generation
    
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
                    markeredgewidth=0.5
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
                    weight='bold'
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
                    markeredgewidth=0.5
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
                    weight='bold'
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
            f"Vehicle utilization rate: {stats['vehicles']['utilization_rate']*100:.1f}%",
            f"Charging station utilization rate: {stats['charging']['avg_utilization_rate']*100:.1f}%"
        ]
        self.stats_text.set_text('\n'.join(stats_lines))
    
    # ============= Statistics Management (UNIFIED) =============
    # Data saving is now handled by the unified DataManager in main.py