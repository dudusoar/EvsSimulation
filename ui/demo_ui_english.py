#!/usr/bin/env python3
"""
DearPyGui Simulation Interface Demo (English Version)
Demonstrates basic interface layout and controls
"""

import dearpygui.dearpygui as dpg
import math
import random
import time
import threading

class DemoSimulationUI:
    """Demo simulation interface"""
    
    def __init__(self):
        self.is_running = False
        self.is_paused = False
        self.simulation_time = 0.0
        self.demo_thread = None
        
        # Demo data
        self.metrics = {
            'vehicles': 20,
            'orders': 15,
            'revenue': 1250.75,
            'battery': 85.5
        }

    def setup_ui(self):
        """Setup UI interface"""
        
        # Create main window
        with dpg.window(label="Electric Vehicle Simulation System Demo", tag="main_window"):
            
            # Horizontal layout: three-panel design
            with dpg.group(horizontal=True):
                
                # Left panel: Parameter control
                with dpg.child_window(label="Parameters", width=300, height=600, border=True):
                    dpg.add_text("Simulation Configuration", color=[100, 200, 255])
                    dpg.add_separator()
                    
                    dpg.add_text("Basic Parameters:")
                    dpg.add_slider_int(label="Duration (seconds)", default_value=3600, 
                                     min_value=300, max_value=7200, tag="duration")
                    dpg.add_slider_int(label="Number of Vehicles", default_value=20, 
                                     min_value=5, max_value=50, tag="vehicles")
                    dpg.add_slider_int(label="Charging Stations", default_value=8, 
                                     min_value=3, max_value=20, tag="stations")
                    
                    dpg.add_separator()
                    dpg.add_text("Vehicle Configuration:")
                    dpg.add_slider_float(label="Speed (m/s)", default_value=15.0, 
                                       min_value=5.0, max_value=30.0, format="%.1f")
                    dpg.add_slider_float(label="Battery Capacity (kWh)", default_value=75.0, 
                                       min_value=40.0, max_value=100.0, format="%.1f")
                    
                    dpg.add_separator()
                    dpg.add_text("Map Selection:")
                    dpg.add_combo(label="Location", 
                                items=["West Lafayette, IN", "New York City, NY", "San Francisco, CA"],
                                default_value="West Lafayette, IN")
                    
                    dpg.add_separator()
                    dpg.add_button(label="Initialize Simulation", callback=self.initialize_demo, 
                                 width=-1, height=50)
                
                # Center panel: Map display area
                with dpg.child_window(label="Map View", width=700, height=600, border=True):
                    dpg.add_text("Real-time Map Display", color=[100, 255, 100])
                    dpg.add_separator()
                    
                    # Map toolbar
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Zoom In", callback=lambda: print("Zoom in"))
                        dpg.add_button(label="Zoom Out", callback=lambda: print("Zoom out"))
                        dpg.add_button(label="Reset View", callback=lambda: print("Reset view"))
                        dpg.add_button(label="Refresh", callback=lambda: print("Refresh map"))
                    
                    dpg.add_separator()
                    
                    # Map display area (using plot for demo)
                    with dpg.plot(label="Map", height=400, width=-1, tag="map_plot"):
                        dpg.add_plot_axis(dpg.mvXAxis, label="Longitude", tag="x_axis")
                        dpg.add_plot_axis(dpg.mvYAxis, label="Latitude", tag="y_axis")
                        
                        # Add demo data points
                        self.create_demo_map_data()
                    
                    dpg.add_text("Map Status: Ready", tag="map_status")
                
                # Right panel: Metrics monitoring
                with dpg.child_window(label="Real-time Metrics", width=300, height=600, border=True):
                    dpg.add_text("Key Performance Indicators", color=[255, 200, 100])
                    dpg.add_separator()
                    
                    dpg.add_text("Simulation Progress:")
                    dpg.add_progress_bar(tag="progress", default_value=0.0, overlay="0%")
                    dpg.add_text("00:00:00 / 01:00:00", tag="time_display")
                    
                    dpg.add_separator()
                    dpg.add_text("Fleet Status:")
                    dpg.add_text("Active Vehicles: 20", tag="active_vehicles")
                    dpg.add_text("Average Battery: 85.5%", tag="avg_battery")
                    dpg.add_text("Vehicle Utilization: 72.3%", tag="utilization")
                    
                    dpg.add_separator()
                    dpg.add_text("Order Management:")
                    dpg.add_text("Pending: 5", tag="pending_orders")
                    dpg.add_text("Active: 8", tag="active_orders") 
                    dpg.add_text("Completed: 42", tag="completed_orders")
                    
                    dpg.add_separator()
                    dpg.add_text("Financial Performance:")
                    dpg.add_text("Total Revenue: $1,250.75", tag="total_revenue")
                    dpg.add_text("Hourly Revenue: $312.19", tag="hourly_revenue")
                    
                    dpg.add_separator()
                    
                    # Performance chart
                    with dpg.plot(label="Performance Trends", height=150, width=-1, tag="metrics_plot"):
                        dpg.add_plot_axis(dpg.mvXAxis, label="Time", tag="mx_axis")
                        dpg.add_plot_axis(dpg.mvYAxis, label="Value", tag="my_axis")
            
            dpg.add_separator()
            
            # Bottom panel: Simulation control
            with dpg.group(horizontal=True):
                dpg.add_text("Simulation Control:", color=[255, 255, 100])
                
                dpg.add_button(label="Start", callback=self.start_demo, 
                             tag="start_btn", width=80, height=35)
                dpg.add_button(label="Pause", callback=self.pause_demo, 
                             tag="pause_btn", width=80, height=35, enabled=False)
                dpg.add_button(label="Stop", callback=self.stop_demo, 
                             tag="stop_btn", width=80, height=35, enabled=False)
                dpg.add_button(label="Reset", callback=self.reset_demo, 
                             tag="reset_btn", width=80, height=35)
                
                dpg.add_text("Speed:")
                dpg.add_slider_float(label="", default_value=1.0, min_value=0.1, max_value=5.0,
                                   format="%.1fx", width=120, callback=self.adjust_speed)

    def create_demo_map_data(self):
        """Create demo map data"""
        # Simulate vehicle positions
        vehicle_x = [random.uniform(-86.95, -86.90) for _ in range(10)]
        vehicle_y = [random.uniform(40.40, 40.45) for _ in range(10)]
        
        # Simulate charging station positions
        station_x = [random.uniform(-86.95, -86.90) for _ in range(5)]
        station_y = [random.uniform(40.40, 40.45) for _ in range(5)]
        
        # Add to chart
        dpg.add_scatter_series(vehicle_x, vehicle_y, label="Vehicles", parent="y_axis", tag="vehicles_series")
        dpg.add_scatter_series(station_x, station_y, label="Charging Stations", parent="y_axis", tag="stations_series")

    def initialize_demo(self):
        """Initialize demo"""
        print("Initializing simulation demo...")
        dpg.set_value("map_status", "Initializing...")
        
        # Simulate initialization process
        time.sleep(1)
        
        dpg.set_value("map_status", "Ready - West Lafayette, IN")
        print("Demo initialization complete!")

    def start_demo(self):
        """Start demo"""
        print("Starting simulation demo")
        self.is_running = True
        self.is_paused = False
        
        # Update button states
        dpg.configure_item("start_btn", enabled=False)
        dpg.configure_item("pause_btn", enabled=True)
        dpg.configure_item("stop_btn", enabled=True)
        
        # Start demo thread
        self.demo_thread = threading.Thread(target=self.demo_loop, daemon=True)
        self.demo_thread.start()

    def pause_demo(self):
        """Pause/resume demo"""
        self.is_paused = not self.is_paused
        if self.is_paused:
            dpg.set_item_label("pause_btn", "Resume")
            print("Simulation paused")
        else:
            dpg.set_item_label("pause_btn", "Pause")
            print("Simulation resumed")

    def stop_demo(self):
        """Stop demo"""
        print("Stopping simulation demo")
        self.is_running = False
        self.is_paused = False
        
        # Reset button states
        dpg.configure_item("start_btn", enabled=True)
        dpg.configure_item("pause_btn", enabled=False)
        dpg.configure_item("stop_btn", enabled=False)
        dpg.set_item_label("pause_btn", "Pause")

    def reset_demo(self):
        """Reset demo"""
        self.stop_demo()
        self.simulation_time = 0.0
        self.update_metrics_display()
        print("Demo reset")

    def adjust_speed(self, sender, value):
        """Adjust simulation speed"""
        print(f"Simulation speed: {value:.1f}x")

    def demo_loop(self):
        """Demo main loop"""
        while self.is_running:
            if not self.is_paused:
                # Update simulation time
                self.simulation_time += 1.0
                
                # Update demo data
                self.update_demo_data()
                
                # Update UI display
                self.update_metrics_display()
                
                # Check if complete
                max_time = dpg.get_value("duration")
                if self.simulation_time >= max_time:
                    self.stop_demo()
                    break
            
            time.sleep(0.1)

    def update_demo_data(self):
        """Update demo data"""
        # Simulate data changes
        self.metrics['vehicles'] = random.randint(18, 22)
        self.metrics['orders'] = random.randint(10, 20)
        self.metrics['revenue'] += random.uniform(0.5, 2.0)
        self.metrics['battery'] = max(20, min(100, self.metrics['battery'] + random.uniform(-1, 1)))

    def update_metrics_display(self):
        """Update metrics display"""
        # Update progress
        max_time = dpg.get_value("duration")
        progress = self.simulation_time / max_time
        dpg.set_value("progress", progress)
        dpg.configure_item("progress", overlay=f"{progress*100:.1f}%")
        
        # Update time display
        current = int(self.simulation_time)
        total = int(max_time)
        time_str = f"{current//3600:02d}:{(current%3600)//60:02d}:{current%60:02d} / {total//3600:02d}:{(total%3600)//60:02d}:{total%60:02d}"
        dpg.set_value("time_display", time_str)
        
        # Update metrics
        dpg.set_value("active_vehicles", f"Active Vehicles: {self.metrics['vehicles']}")
        dpg.set_value("avg_battery", f"Average Battery: {self.metrics['battery']:.1f}%")
        dpg.set_value("total_revenue", f"Total Revenue: ${self.metrics['revenue']:.2f}")

    def run(self):
        """Run demo"""
        dpg.create_context()
        
        # Set theme
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (22, 22, 22))
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (30, 30, 30))
                dpg.add_theme_color(dpg.mvThemeCol_Button, (51, 122, 183))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (71, 142, 203))
        
        dpg.bind_theme(global_theme)
        
        self.setup_ui()
        
        dpg.create_viewport(title="DearPyGui EV Simulation Demo", width=1400, height=800)
        dpg.setup_dearpygui()
        dpg.set_primary_window("main_window", True)
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()


def main():
    """Main function"""
    print("Starting DearPyGui simulation interface demo...")
    
    demo = DemoSimulationUI()
    demo.run()


if __name__ == "__main__":
    main() 