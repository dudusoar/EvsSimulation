"""
Data Management Module
Responsible for saving, loading simulation data and generating reports
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import seaborn as sns


class DataManager:
    """Data Manager Class"""
    
    def __init__(self, output_dir: str = 'outputs/simulation_results', 
                 location: str = None, num_vehicles: int = None, 
                 duration: float = None):
        """
        Initialize data manager
        
        Args:
            output_dir: Output directory
            location: Simulation location
            num_vehicles: Number of vehicles
            duration: Simulation duration in seconds
        """
        self.output_dir = output_dir
        
        # Create output directory
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Create descriptive subdirectory name for this run
        date_stamp = datetime.now().strftime("%Y%m%d")
        
        # Build descriptive folder name
        folder_name_parts = [date_stamp]
        
        if location:
            # Clean location name for use in filename
            clean_location = location.replace(',', '').replace(' ', '_').replace('/', '_')
            # Take first part if too long
            if len(clean_location) > 20:
                clean_location = clean_location.split('_')[0]
            folder_name_parts.append(clean_location)
        
        if num_vehicles is not None:
            folder_name_parts.append(f"{num_vehicles}v")
        
        if duration is not None:
            if duration >= 3600:
                # Show in hours if >= 1 hour
                folder_name_parts.append(f"{duration/3600:.1f}h")
            elif duration >= 60:
                # Show in minutes if >= 1 minute
                folder_name_parts.append(f"{duration/60:.0f}m")
            else:
                # Show in seconds
                folder_name_parts.append(f"{duration:.0f}s")
        
        folder_name = "_".join(folder_name_parts)
        
        self.run_dir = os.path.join(output_dir, folder_name)
        os.makedirs(self.run_dir)
        
        # Data storage
        self.time_series_data = []
        self.event_log = []
    
    # ============= Data Recording Methods =============
    def record_state(self, state: Dict, timestamp: float):
        """
        Record simulation state
        
        Args:
            state: State data
            timestamp: Timestamp
        """
        state_record = {
            'timestamp': timestamp,
            **state
        }
        self.time_series_data.append(state_record)
    
    def log_event(self, event_type: str, event_data: Dict, timestamp: float):
        """
        Log event
        
        Args:
            event_type: Event type
            event_data: Event data
            timestamp: Timestamp
        """
        event = {
            'timestamp': timestamp,
            'type': event_type,
            'data': event_data
        }
        self.event_log.append(event)
    
    # ============= Data Saving Methods =============
    def save_simulation_results(self, final_stats: Dict):
        """
        Save simulation results
        
        Args:
            final_stats: Final statistics data
        """
        # Save final statistics
        stats_file = os.path.join(self.run_dir, 'final_statistics.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(final_stats, f, indent=2, ensure_ascii=False)
        
        # Save time series data
        if self.time_series_data:
            df = pd.DataFrame(self.time_series_data)
            df.to_csv(os.path.join(self.run_dir, 'time_series.csv'), index=False)
        
        # Save event log
        if self.event_log:
            events_file = os.path.join(self.run_dir, 'event_log.json')
            with open(events_file, 'w', encoding='utf-8') as f:
                json.dump(self.event_log, f, indent=2, ensure_ascii=False)
        
        # Save vehicle details
        if 'vehicle_details' in final_stats:
            vehicle_df = pd.DataFrame(final_stats['vehicle_details'])
            vehicle_df.to_csv(os.path.join(self.run_dir, 'vehicle_details.csv'), index=False)
        
        # Save charging station details
        if 'station_details' in final_stats:
            station_df = pd.DataFrame(final_stats['station_details'])
            station_df.to_csv(os.path.join(self.run_dir, 'station_details.csv'), index=False)
        
        print(f"Data saved to: {self.run_dir}")
    
    # ============= Report Generation Methods =============
    def generate_report(self, final_stats: Dict) -> str:
        """
        Generate simulation report
        
        Args:
            final_stats: Final statistics data
        
        Returns:
            Report file path
        """
        # Create report
        report_lines = [
            "# Electric Vehicle Simulation System Report",
            f"\nGenerated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\n## 1. Simulation Overview",
            f"- Simulation duration: {final_stats['summary']['total_simulation_time']:.1f} seconds",
            f"- Number of vehicles: {final_stats['vehicles']['total_vehicles']} vehicles",
            f"- Number of charging stations: {final_stats['charging']['total_stations']} stations",
            f"- Total orders: {final_stats['orders']['total_orders_created']} orders",
            
            "\n## 2. Operational Metrics",
            f"- Order completion rate: {final_stats['summary']['order_completion_rate']*100:.1f}%",
            f"- Vehicle utilization rate: {final_stats['summary']['vehicle_utilization_rate']*100:.1f}%",
            f"- Charging station utilization rate: {final_stats['summary']['charging_utilization_rate']*100:.1f}%",
            f"- Average waiting time: {final_stats['orders']['avg_waiting_time']:.1f} seconds",
            f"- Average trip time: {final_stats['orders']['avg_trip_time']:.1f} seconds",
            
            "\n## 3. Financial Metrics",
            f"- Total revenue: ${final_stats['summary']['total_revenue']:.2f}",
            f"- Total cost: ${final_stats['summary']['total_cost']:.2f}",
            f"- Total profit: ${final_stats['summary']['total_profit']:.2f}",
            f"- Average order price: ${final_stats['orders']['avg_price']:.2f}",
            f"- Average revenue per vehicle: ${final_stats['vehicles']['avg_revenue_per_vehicle']:.2f}",
            
            "\n## 4. Vehicle Statistics",
            f"- Average distance traveled: {final_stats['vehicles']['avg_distance_traveled']:.1f} km",
            f"- Average orders completed: {final_stats['vehicles']['avg_orders_completed']:.1f} orders",
            f"- Average battery level: {final_stats['vehicles']['avg_battery_percentage']:.1f}%",
            
            "\n## 5. Charging Station Statistics",
            f"- Total energy delivered: {final_stats['charging']['total_energy_delivered']:.1f} kWh",
            f"- Total charging revenue: ${final_stats['charging']['total_revenue']:.2f}",
            f"- Total vehicles served: {final_stats['charging']['total_vehicles_served']} vehicle sessions",
        ]
        
        # Save report
        report_file = os.path.join(self.run_dir, 'simulation_report.md')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        # Generate charts
        self._generate_charts(final_stats)
        
        print(f"Report generated: {report_file}")
        return report_file
    
    def _generate_charts(self, final_stats: Dict):
        """Generate statistical charts"""
        # Set plotting style
        plt.style.use('seaborn-v0_8-darkgrid')
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
        
        # 1. Vehicle revenue distribution chart
        if 'vehicle_details' in final_stats:
            vehicle_df = pd.DataFrame(final_stats['vehicle_details'])
            
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            
            # Revenue distribution
            axes[0, 0].hist(vehicle_df['total_revenue'], bins=15, edgecolor='black')
            axes[0, 0].set_title('Vehicle Revenue Distribution')
            axes[0, 0].set_xlabel('Revenue ($)')
            axes[0, 0].set_ylabel('Number of Vehicles')
            
            # Orders distribution
            axes[0, 1].hist(vehicle_df['total_orders'], bins=15, edgecolor='black')
            axes[0, 1].set_title('Orders Completed Distribution')
            axes[0, 1].set_xlabel('Number of Orders')
            axes[0, 1].set_ylabel('Number of Vehicles')
            
            # Distance traveled distribution
            axes[1, 0].hist(vehicle_df['total_distance'], bins=15, edgecolor='black')
            axes[1, 0].set_title('Distance Traveled Distribution')
            axes[1, 0].set_xlabel('Distance (km)')
            axes[1, 0].set_ylabel('Number of Vehicles')
            
            # Profit distribution
            axes[1, 1].hist(vehicle_df['profit'], bins=15, edgecolor='black')
            axes[1, 1].set_title('Profit Distribution')
            axes[1, 1].set_xlabel('Profit ($)')
            axes[1, 1].set_ylabel('Number of Vehicles')
            
            plt.tight_layout()
            plt.savefig(os.path.join(self.run_dir, 'vehicle_statistics.png'))
            plt.close()
        
        # 2. Charging station utilization chart
        if 'station_details' in final_stats:
            station_df = pd.DataFrame(final_stats['station_details'])
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Charging station revenue comparison
            ax.bar(station_df['station_id'], station_df['total_revenue'])
            ax.set_title('Charging Station Revenue')
            ax.set_xlabel('Station ID')
            ax.set_ylabel('Revenue ($)')
            ax.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            plt.savefig(os.path.join(self.run_dir, 'charging_station_revenue.png'))
            plt.close()
    
    # ============= Data Export Methods =============
    def export_to_excel(self, final_stats: Dict):
        """
        Export data to Excel file
        
        Args:
            final_stats: Final statistics data
        """
        excel_file = os.path.join(self.run_dir, 'simulation_results.xlsx')
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Summary sheet
            summary_df = pd.DataFrame([final_stats['summary']])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Vehicle details sheet
            if 'vehicle_details' in final_stats:
                vehicle_df = pd.DataFrame(final_stats['vehicle_details'])
                vehicle_df.to_excel(writer, sheet_name='Vehicles', index=False)
            
            # Charging station details sheet
            if 'station_details' in final_stats:
                station_df = pd.DataFrame(final_stats['station_details'])
                station_df.to_excel(writer, sheet_name='Charging Stations', index=False)
            
            # Order statistics sheet
            orders_df = pd.DataFrame([final_stats['orders']])
            orders_df.to_excel(writer, sheet_name='Orders', index=False)
        
        print(f"Excel file exported: {excel_file}")
    
    # ============= Data Loading Methods =============
    def load_simulation_results(self, run_dir: str) -> Dict:
        """
        Load previous simulation results
        
        Args:
            run_dir: Run directory
        
        Returns:
            Simulation result data
        """
        results = {}
        
        # Load final statistics
        stats_file = os.path.join(run_dir, 'final_statistics.json')
        if os.path.exists(stats_file):
            with open(stats_file, 'r', encoding='utf-8') as f:
                results['final_stats'] = json.load(f)
        
        # Load time series data
        time_series_file = os.path.join(run_dir, 'time_series.csv')
        if os.path.exists(time_series_file):
            results['time_series'] = pd.read_csv(time_series_file)
        
        # Load vehicle details
        vehicle_file = os.path.join(run_dir, 'vehicle_details.csv')
        if os.path.exists(vehicle_file):
            results['vehicle_details'] = pd.read_csv(vehicle_file)
        
        return results