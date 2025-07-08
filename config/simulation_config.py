"""
Simulation Configuration Parameters Module
现在支持YAML配置驱动，同时保持向后兼容性
"""

from .yaml_config_manager import config_manager, SimulationConfigModel
from typing import Dict, Any
import os

# ============= YAML配置系统 =============
def get_config(config_file: str = "default.yaml") -> Dict[str, Any]:
    """获取配置，优先使用YAML配置，fallback到传统配置
    
    Args:
        config_file: YAML配置文件名
        
    Returns:
        配置字典，格式兼容传统系统
    """
    try:
        # 尝试加载YAML配置
        yaml_config = config_manager.load_config(config_file)
        return config_manager.to_legacy_format(yaml_config)
    except Exception as e:
        print(f"YAML配置加载失败，使用默认配置: {e}")
        return DEFAULT_CONFIG

def load_yaml_config(config_file: str = "default.yaml") -> SimulationConfigModel:
    """直接加载YAML配置模型"""
    return config_manager.load_config(config_file)

def save_yaml_config(config: SimulationConfigModel, config_file: str = "default.yaml") -> bool:
    """保存YAML配置"""
    return config_manager.save_config(config, config_file)

def convert_dict_to_yaml(config_dict: Dict) -> SimulationConfigModel:
    """将字典配置转换为YAML配置"""
    return config_manager.convert_legacy_config(config_dict)

# ============= 默认配置 (向后兼容) =============
DEFAULT_CONFIG = {
    # Map parameters
    'location': "West Lafayette, Indiana, USA",
    'cache_map': True,                # Whether to cache map data
    
    # Time parameters
    'simulation_duration': 100,     # Total simulation duration (seconds)
    'time_step': 1.0, #0.1                # Time step (seconds)
    
    # Vehicle parameters
    'num_vehicles': 20,               # Number of vehicles
    'vehicle_speed': 400,             # Vehicle speed (km/h) - SUPER FAST for demo! 🚀
    'vehicle_speed_mps': 400 / 3.6,  # Vehicle speed (m/s)
    'battery_capacity': 100.0,        # Battery capacity (%)
    'energy_consumption': 1.2,        # Energy consumption rate (%/km) - Higher consumption for more action
    'charging_threshold': 40.0,       # Charging threshold (%) - Higher threshold for more charging activity
    
    # Order parameters
    'order_generation_rate': 1000,    # Order generation rate (orders/hour) - Very bold increase!
    'base_price_per_km': 2.0,        # Base price (USD/km)
    'surge_multiplier': 1.5,          # Peak hour price multiplier
    'max_waiting_time': 600,          # Maximum waiting time (seconds)
    
    # Charging station parameters
    'num_charging_stations': 5,       # Number of charging stations
    'charging_slots_per_station': 3,  # Number of charging slots per station
    'charging_power': 50,             # Charging power (kW)
    'charging_rate': 5.0,             # Charging rate (%/second) - SUPER FAST charging! ⚡
    'electricity_price': 0.8,         # Electricity price (USD/kWh)
    
    # Visualization parameters
    'enable_animation': True,         # Whether to enable animation
    'animation_fps': 60,              # Animation frame rate - Higher FPS for smoother animation
    'show_preview': False,            # Whether to show preview
    'save_animation': True,           # Whether to save animation
    'animation_format': 'html',       # Animation format ('html' or 'mp4')
    
    # Data management parameters
    'save_data': False,               # Whether to save simulation data
    'data_save_interval': 10,         # Data save interval (seconds)
    'output_dir': 'simulation_output' # Output directory
}

# 向后兼容：保持SIMULATION_CONFIG变量
SIMULATION_CONFIG = get_config()

# ============= Vehicle Status Definitions =============
VEHICLE_STATUS = {
    'IDLE': 'idle',                        # Idle
    'TO_PICKUP': 'to_pickup',              # Going to pickup
    'WITH_PASSENGER': 'with_passenger',     # With passenger
    'TO_CHARGING': 'to_charging',          # Going to charging
    'CHARGING': 'charging'                 # Charging
}

# ============= Order Status Definitions =============
ORDER_STATUS = {
    'PENDING': 'pending',              # Waiting for assignment
    'ASSIGNED': 'assigned',            # Assigned
    'PICKED_UP': 'picked_up',          # Picked up
    'COMPLETED': 'completed',          # Completed
    'CANCELLED': 'cancelled'           # Cancelled
}

# ============= Color Configuration =============
COLORS = {
    'vehicle': {
        'idle': 'blue',
        'to_pickup': 'yellow',
        'with_passenger': 'green',
        'to_charging': 'orange',
        'charging': 'red'
    },
    'order': {
        'pickup': 'cyan',
        'dropoff': 'magenta'
    },
    'charging_station': 'red',
    'low_battery': 'darkred'
}

# ============= Logging Configuration =============
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S'
}