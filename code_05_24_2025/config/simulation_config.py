"""
仿真配置参数模块
包含所有仿真相关的配置参数
"""

# ============= 基础仿真参数 =============
SIMULATION_CONFIG = {
    # 地图参数
    'location': "Manhattan, New York, NY, USA",
    'cache_map': True,                # 是否缓存地图数据
    
    # 时间参数
    'simulation_duration': 1800,      # 仿真总时长（秒）
    'time_step': 0.1,                # 时间步长（秒）
    
    # 车辆参数
    'num_vehicles': 20,               # 车辆数量
    'vehicle_speed': 200,             # 车速（km/h） - 大幅提高！
    'vehicle_speed_mps': 200 / 3.6,  # 车速（m/s）
    'battery_capacity': 100.0,        # 电池容量（%）
    'energy_consumption': 0.8,        # 能耗率（%/km） - 增加消耗，快速看到充电
    'charging_threshold': 30.0,       # 充电阈值（%） - 提高阈值，更容易触发充电
    
    # 订单参数
    'order_generation_rate': 1000,    # 订单生成率（订单/小时） - 超大胆提高！
    'base_price_per_km': 2.0,        # 基础价格（元/km）
    'surge_multiplier': 1.5,          # 高峰时段价格倍数
    'max_waiting_time': 600,          # 最大等待时间（秒）
    
    # 充电站参数
    'num_charging_stations': 5,       # 充电站数量
    'charging_slots_per_station': 3,  # 每个充电站的充电位数量
    'charging_power': 50,             # 充电功率（kW）
    'charging_rate': 2.0,             # 充电速率（%/秒） - 提高充电速度
    'electricity_price': 0.8,         # 电价（元/kWh）
    
    # 可视化参数
    'enable_animation': True,         # 是否启用动画
    'animation_fps': 30,              # 动画帧率
    'show_preview': False,            # 是否显示预览
    'save_animation': True,           # 是否保存动画
    'animation_format': 'html',       # 动画格式 ('html' 或 'mp4')
    
    # 数据管理参数
    'save_data': False,               # 是否保存仿真数据
    'data_save_interval': 10,         # 数据保存间隔（秒）
    'output_dir': 'simulation_output' # 输出目录
}

# ============= 车辆状态定义 =============
VEHICLE_STATUS = {
    'IDLE': 'idle',                        # 空闲
    'TO_PICKUP': 'to_pickup',              # 前往接客
    'WITH_PASSENGER': 'with_passenger',     # 载客中
    'TO_CHARGING': 'to_charging',          # 前往充电
    'CHARGING': 'charging'                 # 充电中
}

# ============= 订单状态定义 =============
ORDER_STATUS = {
    'PENDING': 'pending',              # 等待分配
    'ASSIGNED': 'assigned',            # 已分配
    'PICKED_UP': 'picked_up',          # 已接客
    'COMPLETED': 'completed',          # 已完成
    'CANCELLED': 'cancelled'           # 已取消
}

# ============= 颜色配置 =============
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

# ============= 日志配置 =============
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S'
}