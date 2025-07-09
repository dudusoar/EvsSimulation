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

# 5. 使用自定义配置

python main.py -c custom_config.json --save-data --report
```

---

## 🌐 Web API 接口

### 基础信息

**基础URL**: `http://127.0.0.1:8080`  
**API版本**: v1  
**认证**: 暂不需要（开发版）  
**数据格式**: JSON  

### 仿真控制 API

#### 创建仿真实例

```http
POST /api/simulation/create
Content-Type: application/json

{
    "location": "West Lafayette, Indiana, USA",
    "num_vehicles": 20,
    "duration": 3600,
    "charging_stations": 5,
    "vehicle_speed": 50,
    "battery_capacity": 100.0
}
```

**响应**:
```json
{
    "success": true,
    "simulation_id": "sim_123456789",
    "status": "created",
    "message": "Simulation created successfully"
}
```

#### 启动仿真

```http
POST /api/simulation/{simulation_id}/start
```

**响应**:
```json
{
    "success": true,
    "status": "started",
    "message": "Simulation started successfully"
}
```

#### 控制仿真

```http
POST /api/simulation/{simulation_id}/control
Content-Type: application/json

{
    "action": "pause"  # 可选: "pause", "resume", "stop", "restart"
}
```

**响应**:
```json
{
    "success": true,
    "status": "paused",
    "message": "Simulation paused"
}
```

#### 获取仿真状态

```http
GET /api/simulation/{simulation_id}/status
```

**响应**:
```json
{
    "simulation_id": "sim_123456789",
    "status": "running",
    "current_time": 1250.5,
    "total_duration": 3600,
    "progress": 34.7,
    "statistics": {
        "total_orders": 425,
        "completed_orders": 398,
        "active_orders": 15,
        "total_revenue": 2847.50,
        "average_wait_time": 3.2
    }
}
```

### 数据查询 API

#### 获取车辆信息

```http
GET /api/data/vehicles?simulation_id={simulation_id}
```

**响应**:
```json
{
    "vehicles": [
        {
            "id": "vehicle_001",
            "status": "with_passenger",
            "position": {
                "lat": 40.4267,
                "lon": -86.9137
            },
            "battery_percentage": 85.5,
            "current_order": "order_789",
            "route": [
                {"lat": 40.4267, "lon": -86.9137},
                {"lat": 40.4289, "lon": -86.9140}
            ]
        }
    ],
    "total_count": 20,
    "status_counts": {
        "idle": 8,
        "to_pickup": 5,
        "with_passenger": 4,
        "charging": 3
    }
}
```

#### 获取订单信息

```http
GET /api/data/orders?simulation_id={simulation_id}&status=pending
```

**响应**:
```json
{
    "orders": [
        {
            "id": "order_123",
            "status": "pending",
            "pickup_location": {
                "lat": 40.4250,
                "lon": -86.9120
            },
            "dropoff_location": {
                "lat": 40.4300,
                "lon": -86.9200
            },
            "creation_time": 1248.3,
            "waiting_time": 2.2,
            "estimated_price": 15.50,
            "assigned_vehicle": null
        }
    ],
    "total_count": 15,
    "status_counts": {
        "pending": 15,
        "assigned": 8,
        "in_progress": 4,
        "completed": 398
    }
}
```

#### 获取充电站信息

```http
GET /api/data/charging-stations?simulation_id={simulation_id}
```

**响应**:
```json
{
    "charging_stations": [
        {
            "id": "station_001",
            "location": {
                "lat": 40.4280,
                "lon": -86.9150
            },
            "total_slots": 4,
            "available_slots": 2,
            "charging_vehicles": [
                {
                    "vehicle_id": "vehicle_005",
                    "start_time": 1200.0,
                    "progress": 65.5
                }
            ],
            "utilization_rate": 50.0,
            "total_energy_dispensed": 125.8
        }
    ],
    "system_stats": {
        "total_stations": 5,
        "total_slots": 20,
        "occupied_slots": 8,
        "system_utilization": 40.0
    }
}
```

### 配置管理 API

#### 获取当前配置

```http
GET /api/config/current?simulation_id={simulation_id}
```

**响应**:
```json
{
    "simulation_id": "sim_123456789",
    "config": {
        "location": "West Lafayette, Indiana, USA",
        "num_vehicles": 20,
        "duration": 3600,
        "vehicle_speed": 50,
        "battery_capacity": 100.0,
        "charging_threshold": 20.0,
        "order_generation_rate": 1000,
        "base_price_per_km": 2.0,
        "num_charging_stations": 5,
        "charging_rate": 5.0
    }
}
```

#### 更新配置参数

```http
PUT /api/config/update
Content-Type: application/json

{
    "simulation_id": "sim_123456789",
    "parameters": {
        "order_generation_rate": 1200,
        "base_price_per_km": 2.5
    }
}
```

### WebSocket 实时通信

#### 连接WebSocket

```javascript
const ws = new WebSocket('ws://127.0.0.1:8080/ws/{simulation_id}');

ws.onopen = function(event) {
    console.log('WebSocket连接已建立');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    handleRealtimeUpdate(data);
};
```

#### WebSocket消息格式

**仿真状态更新**:
```json
{
    "type": "simulation_update",
    "timestamp": 1699123456.789,
    "data": {
        "current_time": 1250.5,
        "statistics": {
            "total_revenue": 2847.50,
            "active_orders": 15,
            "completed_orders": 398
        }
    }
}
```

**车辆位置更新**:
```json
{
    "type": "vehicle_update",
    "timestamp": 1699123456.789,
    "data": {
        "vehicles": [
            {
                "id": "vehicle_001",
                "position": {"lat": 40.4267, "lon": -86.9137},
                "status": "with_passenger",
                "battery_percentage": 85.5
            }
        ]
    }
}
```

**订单状态更新**:
```json
{
    "type": "order_update",
    "timestamp": 1699123456.789,
    "data": {
        "orders": [
            {
                "id": "order_123",
                "status": "assigned",
                "assigned_vehicle": "vehicle_003",
                "pickup_eta": 2.5
            }
        ]
    }
}
```

#### 客户端发送消息

**请求数据更新**:
```json
{
    "type": "request_update",
    "data": {
        "components": ["vehicles", "orders", "statistics"]
    }
}
```

**控制仿真**:
```json
{
    "type": "control",
    "data": {
        "action": "pause"
    }
}
```

### 静态资源 API

#### 页面路由

| 路径 | 描述 | 模板文件 |
|------|------|----------|
| `/` | 主控制台 | `index.html` |
| `/vehicles` | 车辆跟踪页面 | `vehicles.html` |
| `/orders` | 订单管理页面 | `orders.html` |
| `/charging-stations` | 充电站监控页面 | `charging-stations.html` |
| `/config` | 配置面板 | `config.html` |

#### 静态文件

| 路径 | 类型 | 描述 |
|------|------|------|
| `/static/css/style.css` | CSS | 主样式表 |
| `/static/js/app.js` | JavaScript | 主应用逻辑 |
| `/static/js/websocket.js` | JavaScript | WebSocket客户端 |
| `/static/js/map.js` | JavaScript | 地图控制 |
| `/static/js/charts.js` | JavaScript | 图表组件 |

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
    def calculate_route_time(self, origin: int, destination: int) -> float
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