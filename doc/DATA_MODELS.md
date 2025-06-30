# 数据模型文档 | Data Models Documentation

## 概述

本文档详细描述了电动车仿真系统中使用的所有数据模型，包括它们的属性、方法和使用场景。

## 核心数据模型

### 1. Vehicle (车辆模型)

**文件位置**: `models/vehicle.py`

#### 基础属性
```python
@dataclass
class Vehicle:
    # 基本属性
    vehicle_id: str                    # 车辆唯一标识
    position: Tuple[float, float]      # 当前位置坐标 (x, y)
    velocity: Tuple[float, float]      # 当前速度向量 (vx, vy)
    
    # 电池相关
    battery_capacity: float = 100.0    # 电池容量 (%)
    current_battery: float = 100.0     # 当前电量 (%)
    consumption_rate: float = 0.2      # 能耗率 (%/km)
    
    # 状态相关
    status: str = 'idle'               # 当前状态
    current_task: Optional[Dict] = None # 当前任务
    
    # 路径相关
    current_node: Optional[int] = None  # 当前节点ID
    target_node: Optional[int] = None   # 目标节点ID
    route_nodes: List[int]              # 路径节点列表
    path_points: List[Tuple[float, float]] # 详细路径点
    path_index: int = 0                 # 当前路径点索引
    
    # 统计数据
    total_distance: float = 0.0         # 总行驶距离
    total_orders: int = 0               # 完成订单数
    total_revenue: float = 0.0          # 总收入
    total_charging_cost: float = 0.0    # 总充电成本
    idle_time: float = 0.0              # 空闲时间
```

#### 核心方法

**状态判断方法**:
- `battery_percentage`: 电池百分比
- `is_idle`: 是否空闲
- `is_charging`: 是否在充电
- `needs_charging`: 是否需要充电
- `has_passenger`: 是否载客

**位置管理方法**:
- `update_position(new_position)`: 更新位置并计算距离
- `update_velocity(new_velocity)`: 更新速度

**电池管理方法**:
- `consume_battery(distance_km)`: 消耗电量
- `charge_battery(amount)`: 充电
- `calculate_range()`: 计算剩余续航

**任务管理方法**:
- `assign_task(task)`: 分配任务
- `clear_task()`: 清除任务
- `update_status(new_status)`: 更新状态

**路径管理方法**:
- `set_route(route_nodes, path_points)`: 设置路径
- `get_next_path_point()`: 获取下一个路径点
- `advance_path_index()`: 前进到下一个路径点
- `has_reached_destination()`: 是否到达目的地

#### 状态枚举
```python
VEHICLE_STATUS = {
    'IDLE': 'idle',                    # 空闲
    'TO_PICKUP': 'to_pickup',          # 前往接客
    'WITH_PASSENGER': 'with_passenger', # 载客中
    'TO_CHARGING': 'to_charging',      # 前往充电
    'CHARGING': 'charging'             # 充电中
}
```

---

### 2. Order (订单模型)

**文件位置**: `models/order.py`

#### 基础属性
```python
@dataclass
class Order:
    # 基本信息
    order_id: str = None               # 订单唯一标识
    pickup_node: int = None            # 接客点节点ID
    dropoff_node: int = None           # 目的地节点ID
    pickup_position: Tuple[float, float] = None   # 接客点坐标
    dropoff_position: Tuple[float, float] = None  # 目的地坐标
    
    # 时间信息
    creation_time: float = 0.0         # 创建时间
    assignment_time: float = None      # 分配时间
    pickup_time: float = None          # 接客时间
    completion_time: float = None      # 完成时间
    
    # 状态信息
    status: str = 'pending'            # 订单状态
    assigned_vehicle_id: Optional[str] = None # 分配的车辆ID
    
    # 价格信息
    estimated_distance: float = 0.0    # 预估距离 (km)
    base_price: float = 0.0            # 基础价格
    surge_multiplier: float = 1.0      # 动态价格倍数
    final_price: float = 0.0           # 最终价格
```

#### 核心方法

**状态管理方法**:
- `assign_to_vehicle(vehicle_id, current_time)`: 分配给车辆
- `pickup_passenger(current_time)`: 接客
- `complete_order(current_time)`: 完成订单
- `cancel_order(current_time)`: 取消订单

**价格计算方法**:
- `calculate_price(base_rate)`: 计算价格

**时间计算方法**:
- `get_waiting_time(current_time)`: 获取等待时间
- `get_pickup_time()`: 获取接客耗时
- `get_trip_time()`: 获取行程时间
- `get_total_time()`: 获取总时间

**状态判断方法**:
- `is_pending()`: 是否等待分配
- `is_assigned()`: 是否已分配
- `is_completed()`: 是否已完成

#### 状态枚举
```python
ORDER_STATUS = {
    'PENDING': 'pending',              # 等待分配
    'ASSIGNED': 'assigned',            # 已分配
    'PICKED_UP': 'picked_up',          # 已接客
    'COMPLETED': 'completed',          # 已完成
    'CANCELLED': 'cancelled'           # 已取消
}
```

---

### 3. ChargingStation (充电站模型)

**文件位置**: `models/charging_station.py`

#### 基础属性
```python
@dataclass
class ChargingStation:
    # 基本信息
    station_id: str                    # 充电站ID
    node_id: int                       # 对应的地图节点ID
    position: Tuple[float, float]      # 位置坐标
    
    # 容量信息
    total_slots: int = 3               # 总充电位数量
    available_slots: int = 3           # 可用充电位数量
    
    # 充电参数
    charging_rate: float = 1.0         # 充电速率 (%/秒)
    electricity_price: float = 0.8     # 电价 (元/kWh)
    
    # 使用统计
    total_charging_sessions: int = 0   # 总充电次数
    total_energy_delivered: float = 0.0 # 总供电量
    total_revenue: float = 0.0         # 总收入
    
    # 当前充电车辆
    charging_vehicles: Dict[str, float] = field(default_factory=dict)
```

#### 核心方法

**容量管理方法**:
- `has_available_slot()`: 是否有空闲充电位
- `start_charging(vehicle_id)`: 开始充电
- `stop_charging(vehicle_id)`: 停止充电
- `is_vehicle_charging(vehicle_id)`: 车辆是否在充电

**计费方法**:
- `calculate_charging_cost(energy_amount)`: 计算充电费用

**统计方法**:
- `get_utilization_rate()`: 获取使用率
- `get_statistics()`: 获取统计信息

---

## 配置数据结构

### SIMULATION_CONFIG (仿真配置)

**文件位置**: `config/simulation_config.py`

```python
SIMULATION_CONFIG = {
    # 地图参数
    'location': "Manhattan, New York, NY, USA",
    'cache_map': True,
    
    # 时间参数
    'simulation_duration': 1800,       # 仿真时长 (秒)
    'time_step': 0.1,                 # 时间步长 (秒)
    
    # 车辆参数
    'num_vehicles': 20,               # 车辆数量
    'vehicle_speed': 200,             # 车速 (km/h)
    'battery_capacity': 100.0,        # 电池容量 (%)
    'energy_consumption': 0.8,        # 能耗率 (%/km)
    'charging_threshold': 30.0,       # 充电阈值 (%)
    
    # 订单参数
    'order_generation_rate': 1000,    # 订单生成率 (单/小时)
    'base_price_per_km': 2.0,        # 基础价格 (元/km)
    'surge_multiplier': 1.5,          # 高峰倍数
    'max_waiting_time': 600,          # 最大等待时间 (秒)
    
    # 充电站参数
    'num_charging_stations': 5,       # 充电站数量
    'charging_slots_per_station': 3,  # 每站充电位数
    'charging_rate': 2.0,             # 充电速率 (%/秒)
    'electricity_price': 0.8,         # 电价 (元/kWh)
    
    # 🆕 可视化参数 - 已重构为实时可视化
    'enable_live_visualization': True, # 启用实时可视化（默认模式）
    'visualization_fps': 30,           # 可视化刷新率
    'enable_web_interface': False,     # 启用Web交互界面
    
    # 🗑️ 已移除的传统动画参数：
    # 'enable_animation': 已移除 - 不再使用frame存储动画
    # 'animation_fps': 已移除 - 替换为visualization_fps
    # 'save_animation': 已移除 - 现在使用实时可视化
    
    # 数据管理参数
    'save_data': False,               # 保存数据
    'output_dir': 'simulation_output' # 输出目录
}
```

## 数据关系图

```
┌─────────────┐     1:N     ┌─────────────┐
│   Vehicle   │ ←───────── │    Order    │
│             │            │             │
│ vehicle_id  │            │assigned_    │
│ status      │            │vehicle_id   │
│ position    │            │ status      │
└─────────────┘            └─────────────┘
       │                          │
       │ M:N                      │ 1:1
       │                          │
┌─────────────┐            ┌─────────────┐
│ChargingSttn │            │  MapNode    │
│             │            │             │
│ station_id  │            │  node_id    │
│ node_id     │            │  position   │
│ capacity    │            │             │
└─────────────┘            └─────────────┘
```

## 数据生命周期

### 车辆数据生命周期
1. **初始化**: 分配初始位置和电量
2. **运行期**: 实时更新位置、电量、状态
3. **任务执行**: 接收任务、执行路径、状态变化
4. **统计更新**: 累计距离、收入、成本数据

### 订单数据生命周期
1. **创建**: 随机生成起止点和预估价格
2. **分配**: 匹配最优车辆
3. **执行**: 接客、运输、完成
4. **归档**: 记录完成时间和最终价格

### 充电站数据生命周期
1. **初始化**: 选择位置、设置容量
2. **运行期**: 管理充电队列、计算使用率
3. **计费**: 实时计算充电费用
4. **统计**: 累计服务数据和收入

## 数据持久化

### 保存格式
- **JSON格式**: 最终统计数据 (`final_statistics.json`)
- **CSV格式**: 详细数据表 (`vehicle_details.csv`, `station_details.csv`)
- **Excel格式**: 汇总报告 (`simulation_results.xlsx`)

### 数据字段映射
- 所有时间戳都以秒为单位
- 所有距离都以米为单位存储，显示时转换为公里
- 所有价格都以配置的货币单位存储 