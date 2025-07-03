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

---

## 🌐 Web应用数据模型

### API响应格式

#### 通用响应结构
```python
@dataclass
class APIResponse:
    success: bool                      # 请求是否成功
    message: str                       # 响应消息
    data: Optional[Dict] = None        # 响应数据
    error: Optional[str] = None        # 错误信息
    timestamp: float = None            # 响应时间戳
```

#### 仿真状态响应
```python
@dataclass
class SimulationStatus:
    simulation_id: str                 # 仿真实例ID
    status: str                        # 运行状态
    current_time: float                # 当前仿真时间
    total_duration: float              # 总仿真时长
    progress: float                    # 进度百分比
    statistics: Dict                   # 实时统计数据
    
    # 统计数据结构
    statistics = {
        'vehicles': {
            'total_count': int,
            'idle_count': int,
            'to_pickup_count': int,
            'with_passenger_count': int,
            'charging_count': int,
            'average_battery': float
        },
        'orders': {
            'total_orders': int,
            'completed_orders': int,
            'active_orders': int,
            'pending_orders': int,
            'average_wait_time': float
        },
        'revenue': {
            'total_revenue': float,
            'average_order_value': float,
            'revenue_per_hour': float
        },
        'charging': {
            'total_sessions': int,
            'active_sessions': int,
            'total_energy': float,
            'average_utilization': float
        }
    }
```

#### 车辆数据响应
```python
@dataclass
class VehicleResponse:
    vehicles: List[VehicleData]        # 车辆列表
    total_count: int                   # 总车辆数
    status_counts: Dict[str, int]      # 状态分布统计
    
@dataclass
class VehicleData:
    id: str                            # 车辆ID
    status: str                        # 当前状态
    position: Dict[str, float]         # 位置 {'lat': float, 'lon': float}
    battery_percentage: float          # 电量百分比
    current_order: Optional[str]       # 当前订单ID
    route: List[Dict[str, float]]      # 路径点列表
    statistics: Dict                   # 车辆统计数据
    
    # 车辆统计数据结构
    statistics = {
        'total_distance': float,       # 总行驶距离
        'total_orders': int,           # 完成订单数
        'total_revenue': float,        # 总收入
        'total_charging_cost': float,  # 总充电成本
        'utilization_rate': float,     # 利用率
        'idle_time': float             # 空闲时间
    }
```

#### 订单数据响应
```python
@dataclass
class OrderResponse:
    orders: List[OrderData]            # 订单列表
    total_count: int                   # 总订单数
    status_counts: Dict[str, int]      # 状态分布统计
    
@dataclass
class OrderData:
    id: str                            # 订单ID
    status: str                        # 订单状态
    pickup_location: Dict[str, float]  # 接客点 {'lat': float, 'lon': float}
    dropoff_location: Dict[str, float] # 目的地 {'lat': float, 'lon': float}
    creation_time: float               # 创建时间
    waiting_time: Optional[float]      # 等待时间
    estimated_price: float             # 预估价格
    final_price: Optional[float]       # 最终价格
    assigned_vehicle: Optional[str]    # 分配的车辆ID
    pickup_eta: Optional[float]        # 预估接客时间
```

#### 充电站数据响应
```python
@dataclass
class ChargingStationResponse:
    charging_stations: List[ChargingStationData]  # 充电站列表
    system_stats: Dict                            # 系统统计
    
@dataclass
class ChargingStationData:
    id: str                            # 充电站ID
    location: Dict[str, float]         # 位置 {'lat': float, 'lon': float}
    total_slots: int                   # 总充电位数
    available_slots: int               # 可用充电位数
    charging_vehicles: List[Dict]      # 正在充电的车辆
    utilization_rate: float            # 使用率
    total_energy_dispensed: float      # 总供电量
    total_revenue: float               # 总收入
    
    # 正在充电的车辆数据结构
    charging_vehicles = [{
        'vehicle_id': str,             # 车辆ID
        'start_time': float,           # 开始充电时间
        'progress': float,             # 充电进度 (%)
        'estimated_completion': float   # 预估完成时间
    }]
    
    # 系统统计数据结构
    system_stats = {
        'total_stations': int,         # 总充电站数
        'total_slots': int,            # 总充电位数
        'occupied_slots': int,         # 占用充电位数
        'system_utilization': float,   # 系统利用率
        'queue_length': int            # 排队车辆数
    }
```

### WebSocket消息格式

#### 基础消息结构
```python
@dataclass
class WebSocketMessage:
    type: str                          # 消息类型
    timestamp: float                   # 时间戳
    data: Dict                         # 消息数据
    simulation_id: Optional[str] = None # 仿真实例ID
```

#### 仿真状态更新消息
```json
{
    "type": "simulation_update",
    "timestamp": 1699123456.789,
    "simulation_id": "sim_123456789",
    "data": {
        "current_time": 1250.5,
        "status": "running",
        "progress": 34.7,
        "statistics": {
            "total_revenue": 2847.50,
            "active_orders": 15,
            "completed_orders": 398,
            "vehicle_utilization": 78.5
        }
    }
}
```

#### 车辆位置更新消息
```json
{
    "type": "vehicle_update",
    "timestamp": 1699123456.789,
    "simulation_id": "sim_123456789",
    "data": {
        "vehicles": [
            {
                "id": "vehicle_001",
                "position": {"lat": 40.4267, "lon": -86.9137},
                "status": "with_passenger",
                "battery_percentage": 85.5,
                "route": [
                    {"lat": 40.4267, "lon": -86.9137},
                    {"lat": 40.4289, "lon": -86.9140}
                ]
            }
        ]
    }
}
```

#### 订单状态更新消息
```json
{
    "type": "order_update",
    "timestamp": 1699123456.789,
    "simulation_id": "sim_123456789",
    "data": {
        "orders": [
            {
                "id": "order_123",
                "status": "assigned",
                "assigned_vehicle": "vehicle_003",
                "pickup_eta": 2.5,
                "pickup_location": {"lat": 40.4250, "lon": -86.9120},
                "dropoff_location": {"lat": 40.4300, "lon": -86.9200}
            }
        ]
    }
}
```

#### 充电站状态更新消息
```json
{
    "type": "charging_update",
    "timestamp": 1699123456.789,
    "simulation_id": "sim_123456789",
    "data": {
        "stations": [
            {
                "id": "station_001",
                "available_slots": 2,
                "total_slots": 4,
                "charging_vehicles": [
                    {
                        "vehicle_id": "vehicle_005",
                        "progress": 65.5,
                        "estimated_completion": 180.0
                    }
                ],
                "utilization_rate": 50.0
            }
        ]
    }
}
```

#### 系统告警消息
```json
{
    "type": "alert",
    "timestamp": 1699123456.789,
    "simulation_id": "sim_123456789",
    "data": {
        "alert_id": "alert_001",
        "level": "warning",  // "info", "warning", "error", "critical"
        "category": "vehicle", // "vehicle", "order", "charging", "system"
        "message": "Vehicle vehicle_007 battery level below 15%",
        "details": {
            "vehicle_id": "vehicle_007",
            "battery_percentage": 12.3,
            "current_location": {"lat": 40.4234, "lon": -86.9145},
            "nearest_charging_station": "station_003",
            "distance_to_station": 2.1
        },
        "suggested_action": "Redirect to nearest charging station",
        "auto_resolve": false
    }
}
```

#### 客户端控制消息
```json
{
    "type": "control_command",
    "timestamp": 1699123456.789,
    "simulation_id": "sim_123456789",
    "data": {
        "command": "pause",  // "start", "pause", "resume", "stop", "restart"
        "parameters": {},
        "client_id": "client_001"
    }
}
```

### 配置数据模型

#### Web配置参数
```python
@dataclass
class WebConfig:
    # 服务器配置
    host: str = "127.0.0.1"
    port: int = 8080
    debug: bool = True
    reload: bool = True
    
    # WebSocket配置
    websocket_max_connections: int = 100
    websocket_ping_interval: int = 30
    websocket_ping_timeout: int = 10
    
    # 数据更新配置
    update_interval: float = 0.1       # 数据更新间隔 (秒)
    batch_size: int = 50               # 批量更新大小
    max_history_records: int = 1000    # 最大历史记录数
    
    # 地图配置
    default_zoom: int = 13             # 默认地图缩放级别
    map_update_interval: float = 0.2   # 地图更新间隔 (秒)
    
    # 图表配置
    chart_data_points: int = 100       # 图表数据点数量
    chart_update_interval: float = 1.0 # 图表更新间隔 (秒)
```

### 错误处理模型

#### 错误响应格式
```python
@dataclass
class ErrorResponse:
    success: bool = False
    error: ErrorDetail
    
@dataclass
class ErrorDetail:
    code: str                          # 错误代码
    message: str                       # 错误消息
    details: Optional[Dict] = None     # 错误详情
    timestamp: float                   # 错误时间戳
    request_id: Optional[str] = None   # 请求ID
```

#### 常见错误代码
```python
ERROR_CODES = {
    'SIMULATION_NOT_FOUND': 'SIM001',
    'INVALID_PARAMETER': 'VAL001',
    'RESOURCE_BUSY': 'RES001', 
    'INSUFFICIENT_BATTERY': 'VEH001',
    'CHARGING_STATION_FULL': 'CHG001',
    'ORDER_NOT_ASSIGNABLE': 'ORD001',
    'MAP_LOAD_FAILED': 'MAP001',
    'WEBSOCKET_ERROR': 'WS001',
    'DATABASE_ERROR': 'DB001',
    'INTERNAL_ERROR': 'SYS001'
}
```

### 数据验证模型

#### Pydantic验证模型
```python
from pydantic import BaseModel, Field, validator

class SimulationConfigModel(BaseModel):
    location: str = Field(..., min_length=1, max_length=200)
    num_vehicles: int = Field(..., ge=1, le=1000)
    duration: float = Field(..., gt=0, le=86400)  # 最大24小时
    vehicle_speed: float = Field(..., gt=0, le=500)
    battery_capacity: float = Field(..., gt=0, le=1000)
    
    @validator('location')
    def location_must_be_valid(cls, v):
        if not v.strip():
            raise ValueError('Location cannot be empty')
        return v.strip()
    
    @validator('num_vehicles')
    def vehicles_must_be_reasonable(cls, v):
        if v > 100:
            warnings.warn(f'Large number of vehicles ({v}) may impact performance')
        return v

class VehicleCreateModel(BaseModel):
    position: Tuple[float, float]
    battery_percentage: float = Field(default=100.0, ge=0, le=100)
    
class OrderCreateModel(BaseModel):
    pickup_location: Tuple[float, float]
    dropoff_location: Tuple[float, float]
    priority: int = Field(default=1, ge=1, le=5)
```

---

## 📊 数据关系扩展图

```
Web Application Layer
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │   REST API  │    │ WebSocket   │    │  Static     │      │
│  │             │    │ Handler     │    │ Files       │      │
│  │ /api/...    │    │ /ws/{id}    │    │ /static/... │      │
│  └─────────────┘    └─────────────┘    └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
Core Simulation Engine
┌─────────────────────────────────────────────────────────────┐
│  ┌─────────────┐     1:N     ┌─────────────┐                │
│  │   Vehicle   │ ←───────── │    Order    │                │
│  │             │            │             │                │
│  │ vehicle_id  │            │assigned_    │                │
│  │ status      │            │vehicle_id   │                │
│  │ position    │            │ status      │                │
│  └─────────────┘            └─────────────┘                │
│         │                          │                       │
│         │ M:N                      │ 1:1                   │
│         │                          │                       │
│  ┌─────────────┐            ┌─────────────┐                │
│  │ChargingSttn │            │  MapNode    │                │
│  │             │            │             │                │
│  │ station_id  │            │  node_id    │                │
│  │ node_id     │            │  position   │                │
│  │ capacity    │            │             │                │
│  └─────────────┘            └─────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

这套完整的数据模型文档为双仿真系统提供了统一的数据格式标准，确保Python引擎和Web应用之间的数据一致性和互操作性。 