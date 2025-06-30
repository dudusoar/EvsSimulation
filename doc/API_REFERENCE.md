# API接口参考 | API Reference Documentation

## 概述

本文档详细描述了电动车仿真系统的所有API接口，包括命令行接口、实时可视化API和内部编程接口。

## 命令行接口 (CLI)

### 主程序调用

**基本语法**:
```bash
python main.py [OPTIONS]
```

### 基础参数

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `-l, --location` | string | "West Lafayette, IN" | 仿真地点 |
| `-v, --vehicles` | int | 20 | 车辆数量 |
| `-d, --duration` | int | 3600 | 仿真时长（秒） |
| `-c, --config` | string | None | 自定义配置文件路径 |

### 输出参数

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `--save-data` | flag | False | 保存仿真数据（JSON + CSV）|
| `--report` | flag | False | 生成详细仿真报告 |
| `--excel` | flag | False | 导出Excel文件 |

### 运行模式

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `--headless` | flag | False | 无头模式（无可视化，最快速度） |
| `--realtime` | flag | False | 启动实时Web可视化服务器 |

### 🆕 **重大改进：已移除的传统动画参数**

以下参数已被移除，因为系统已从frame存储转换为实时可视化：
- ~~`-o, --output`~~ - 动画输出文件名（已移除）
- ~~`-f, --format`~~ - 动画格式html/mp4（已移除）
- ~~`--no-animation`~~ - 禁用动画生成（已移除）

### 数据保存参数

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `--save-data` | flag | False | 保存仿真数据 |
| `--report` | flag | False | 生成仿真报告 |
| `--excel` | flag | False | 导出Excel文件 |

### 使用示例

```bash
# 1. 🆕 实时matplotlib可视化（默认模式）
python main.py -v 10 -d 300

# 2. 带数据保存的实时可视化
python main.py -l "Beijing, China" -v 50 -d 3600 --save-data

# 3. 完整报告生成
python main.py -v 20 -d 1800 --save-data --report --excel

# 4. 批量仿真（无可视化，最快速度）
python main.py --headless -v 100 -d 7200 --save-data

# 5. 🆕 实时Web交互式可视化（支持快进控制）
python main.py --realtime -l "Manhattan, New York" -v 30

# 6. 使用自定义配置
python main.py -c custom_config.json --save-data --report
```

---

## 实时可视化 API

### HTTP RESTful API

**基础URL**: `http://localhost:8080/api/`

#### 1. 仿真控制接口

**启动仿真**
```http
POST /api/simulation/start
Content-Type: application/json

{
    "location": "Manhattan, New York",
    "num_vehicles": 20,
    "duration": 1800
}
```

**响应**:
```json
{
    "success": true,
    "simulation_id": "sim_12345",
    "message": "Simulation started successfully"
}
```

**暂停仿真**
```http
POST /api/simulation/pause
```

**恢复仿真**
```http
POST /api/simulation/resume
```

**停止仿真**
```http
POST /api/simulation/stop
```

#### 2. 状态查询接口

**获取仿真状态**
```http
GET /api/simulation/status
```

**响应**:
```json
{
    "status": "running",
    "current_time": 1234.5,
    "total_duration": 3600,
    "progress": 34.3
}
```

**获取实时统计**
```http
GET /api/simulation/statistics
```

**响应**:
```json
{
    "simulation_time": 1234.5,
    "vehicles": {
        "total": 20,
        "idle": 12,
        "busy": 6,
        "charging": 2
    },
    "orders": {
        "total_created": 45,
        "completed": 38,
        "pending": 3,
        "cancelled": 4
    },
    "revenue": {
        "total": 2456.78,
        "average_per_order": 64.65
    }
}
```

#### 3. 数据访问接口

**获取车辆列表**
```http
GET /api/vehicles
```

**响应**:
```json
{
    "vehicles": [
        {
            "vehicle_id": "V001",
            "position": [40.7128, -74.0060],
            "status": "idle",
            "battery_percentage": 85.2,
            "current_order": null
        },
        // ... 更多车辆
    ]
}
```

**获取特定车辆信息**
```http
GET /api/vehicles/{vehicle_id}
```

**获取订单列表**
```http
GET /api/orders?status=pending&limit=10
```

**获取充电站信息**
```http
GET /api/charging-stations
```

**响应**:
```json
{
    "stations": [
        {
            "station_id": "STATION_1",
            "position": [40.7589, -73.9851],
            "total_slots": 3,
            "available_slots": 1,
            "utilization_rate": 66.7
        },
        // ... 更多充电站
    ]
}
```

#### 4. 配置接口

**获取当前配置**
```http
GET /api/config
```

**更新配置参数**
```http
PUT /api/config
Content-Type: application/json

{
    "order_generation_rate": 10,
    "charging_threshold": 25.0
}
```

### WebSocket 实时数据流

**连接URL**: `ws://localhost:8765`

#### 消息格式

**客户端订阅消息**:
```json
{
    "type": "subscribe",
    "topics": ["vehicles", "orders", "statistics"]
}
```

**服务器推送消息**:
```json
{
    "type": "vehicle_update",
    "timestamp": 1234567890.123,
    "data": {
        "vehicle_id": "V001",
        "position": [40.7128, -74.0060],
        "status": "to_pickup",
        "battery_percentage": 82.1
    }
}
```

**订单更新消息**:
```json
{
    "type": "order_update",
    "timestamp": 1234567890.123,
    "data": {
        "order_id": "ORDER_abc123",
        "status": "assigned",
        "pickup_position": [40.7589, -73.9851],
        "dropoff_position": [40.7505, -73.9934],
        "assigned_vehicle_id": "V003"
    }
}
```

**统计更新消息**:
```json
{
    "type": "statistics_update",
    "timestamp": 1234567890.123,
    "data": {
        "total_revenue": 2456.78,
        "completed_orders": 38,
        "active_vehicles": 18
    }
}
```

---

## 内部编程接口

### SimulationEngine 接口

```python
class SimulationEngine:
    def __init__(self, config: Dict)
    def run_simulation(self, duration: float) -> Dict
    def run_step(self) -> None
    def get_current_statistics(self) -> Dict
    def get_final_statistics(self) -> Dict
    def get_vehicles(self) -> List[Vehicle]
    def get_orders(self) -> Dict
    def get_charging_stations(self) -> List[ChargingStation]
```

### MapManager 接口

```python
class MapManager:
    def __init__(self, location: str, cache_dir: str = 'datasets/maps')
    def get_all_nodes(self) -> List[int]
    def get_random_nodes(self, n: int) -> List[int]
    def get_node_position(self, node_id: int) -> Tuple[float, float]
    def find_nearest_node(self, position: Tuple[float, float]) -> int
    def get_shortest_path_nodes(self, origin: int, destination: int) -> List[int]
    def get_shortest_path_points(self, origin: int, destination: int) -> List[Tuple[float, float]]
    def calculate_route_distance(self, origin: int, destination: int) -> float
    def select_charging_station_nodes(self, n: int) -> List[int]
```

### VehicleManager 接口

```python
class VehicleManager:
    def __init__(self, map_manager: MapManager, config: Dict)
    def update_all_vehicles(self, dt: float) -> None
    def get_all_vehicles(self) -> List[Vehicle]
    def get_available_vehicles(self) -> List[Vehicle]
    def get_vehicles_by_status(self, status: str) -> List[Vehicle]
    def dispatch_vehicle_to_order(self, vehicle: Vehicle, pickup_node: int, dropoff_node: int) -> None
    def dispatch_vehicle_to_charging(self, vehicle: Vehicle, station_node: int) -> None
    def charge_vehicle(self, vehicle_id: str, charge_amount: float) -> None
    def get_fleet_statistics(self) -> Dict
```

### OrderSystem 接口

```python
class OrderSystem:
    def __init__(self, map_manager: MapManager, config: Dict)
    def generate_orders(self, current_time: float, dt: float) -> List[Order]
    def get_pending_orders(self) -> List[Order]
    def get_active_orders(self) -> List[Order]
    def find_best_vehicle_for_order(self, order_id: str, available_vehicles: List[Vehicle]) -> Optional[Vehicle]
    def assign_order_to_vehicle(self, order_id: str, vehicle: Vehicle, current_time: float) -> bool
    def pickup_passenger(self, order_id: str, vehicle: Vehicle, current_time: float) -> bool
    def complete_order(self, order_id: str, vehicle: Vehicle, current_time: float) -> float
    def cancel_order(self, order_id: str, current_time: float) -> None
    def get_statistics(self) -> Dict
```

### ChargingManager 接口

```python
class ChargingManager:
    def __init__(self, map_manager: MapManager, config: Dict)
    def should_vehicle_charge(self, vehicle: Vehicle) -> bool
    def find_optimal_charging_station(self, vehicle: Vehicle) -> Optional[ChargingStation]
    def request_charging(self, vehicle: Vehicle, station: ChargingStation) -> bool
    def stop_charging(self, vehicle: Vehicle) -> Tuple[float, float]
    def update_charging_progress(self, dt: float) -> Dict[str, float]
    def get_station_list(self) -> List[ChargingStation]
    def get_statistics(self) -> Dict
```

---

## 数据模型接口

### Vehicle 接口

```python
class Vehicle:
    # 属性访问
    @property
    def battery_percentage(self) -> float
    @property
    def is_idle(self) -> bool
    @property
    def needs_charging(self) -> bool
    @property
    def has_passenger(self) -> bool
    
    # 状态管理
    def update_status(self, new_status: str) -> None
    def assign_task(self, task: Dict) -> None
    def clear_task(self) -> None
    
    # 位置管理
    def update_position(self, new_position: Tuple[float, float]) -> None
    def set_route(self, route_nodes: List[int], path_points: List[Tuple[float, float]]) -> None
    def has_reached_destination(self) -> bool
    
    # 电池管理
    def consume_battery(self, distance_km: float) -> None
    def charge_battery(self, amount: float) -> None
    def calculate_range(self) -> float
    
    # 统计
    def get_statistics(self) -> Dict
```

### Order 接口

```python
class Order:
    # 状态管理
    def assign_to_vehicle(self, vehicle_id: str, current_time: float) -> None
    def pickup_passenger(self, current_time: float) -> None
    def complete_order(self, current_time: float) -> None
    def cancel_order(self, current_time: float) -> None
    
    # 价格计算
    def calculate_price(self, base_rate: float = 2.0) -> float
    
    # 时间计算
    def get_waiting_time(self, current_time: float) -> float
    def get_total_time(self) -> float
    
    # 状态查询
    def is_pending(self) -> bool
    def is_completed(self) -> bool
    
    # 信息获取
    def get_info(self) -> Dict
```

### ChargingStation 接口

```python
class ChargingStation:
    # 容量管理
    def has_available_slot(self) -> bool
    def start_charging(self, vehicle_id: str) -> bool
    def stop_charging(self, vehicle_id: str) -> bool
    def is_vehicle_charging(self, vehicle_id: str) -> bool
    
    # 计费
    def calculate_charging_cost(self, energy_amount: float) -> float
    
    # 统计
    def get_utilization_rate(self) -> float
    def get_statistics(self) -> Dict
```

---

## 配置接口

### SIMULATION_CONFIG 结构

```python
SIMULATION_CONFIG = {
    # 地图参数
    'location': str,                    # 仿真地点
    'cache_map': bool,                  # 是否缓存地图
    
    # 时间参数
    'simulation_duration': int,         # 仿真时长（秒）
    'time_step': float,                # 时间步长（秒）
    
    # 车辆参数
    'num_vehicles': int,               # 车辆数量
    'vehicle_speed': float,            # 车速（km/h）
    'battery_capacity': float,         # 电池容量（%）
    'energy_consumption': float,       # 能耗率（%/km）
    'charging_threshold': float,       # 充电阈值（%）
    
    # 订单参数
    'order_generation_rate': int,      # 订单生成率（单/小时）
    'base_price_per_km': float,       # 基础价格（元/km）
    'surge_multiplier': float,         # 高峰倍数
    'max_waiting_time': int,           # 最大等待时间（秒）
    
    # 充电站参数
    'num_charging_stations': int,      # 充电站数量
    'charging_slots_per_station': int, # 每站充电位数
    'charging_rate': float,            # 充电速率（%/秒）
    'electricity_price': float,        # 电价（元/kWh）
    
    # 可视化参数
    'enable_animation': bool,          # 启用动画
    'animation_fps': int,              # 动画帧率
    'save_animation': bool,            # 保存动画
    
    # 数据管理参数
    'save_data': bool,                 # 保存数据
    'output_dir': str                  # 输出目录
}
```

---

## 错误处理

### HTTP API 错误响应

```json
{
    "success": false,
    "error": {
        "code": "INVALID_PARAMETER",
        "message": "Invalid vehicle count: must be between 1 and 1000",
        "details": {
            "parameter": "num_vehicles",
            "value": 1500,
            "valid_range": [1, 1000]
        }
    }
}
```

### 常见错误码

| 错误码 | 描述 |
|--------|------|
| `INVALID_PARAMETER` | 参数值无效 |
| `SIMULATION_NOT_RUNNING` | 仿真未运行 |
| `RESOURCE_NOT_FOUND` | 资源不存在 |
| `NETWORK_ERROR` | 网络连接错误 |
| `MAP_LOAD_FAILED` | 地图加载失败 |
| `INSUFFICIENT_RESOURCES` | 资源不足 |

### Python 异常

```python
# 地图相关异常
class MapLoadError(Exception):
    """地图加载失败"""
    pass

# 车辆相关异常
class VehicleNotFoundError(Exception):
    """车辆不存在"""
    pass

# 订单相关异常
class OrderNotFoundError(Exception):
    """订单不存在"""
    pass

# 充电相关异常
class ChargingStationFullError(Exception):
    """充电站已满"""
    pass
```

---

## 版本兼容性

### API 版本控制

- **当前版本**: v1.0
- **向后兼容**: 支持到 v0.9
- **版本标识**: 通过HTTP头 `API-Version` 指定

### 弃用通知

已弃用的接口将在响应中包含 `Deprecated` 头部：

```http
HTTP/1.1 200 OK
Deprecated: true
Sunset: 2024-12-31
Link: </api/v2/vehicles>; rel="successor-version"
```

这套API接口设计提供了完整的系统控制和数据访问能力，支持传统批处理仿真和实时交互仿真两种模式。 