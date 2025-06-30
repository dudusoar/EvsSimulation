# 系统模块详解 | System Modules Documentation

## 概述

本文档详细描述电动车仿真系统中各个核心模块的功能、接口和实现细节。

## 核心模块架构

### 1. 仿真引擎 (SimulationEngine)

**文件位置**: `core/simulation_engine.py`

#### 职责范围
- 协调所有子系统运行
- 管理仿真时间和步进
- 处理系统事件和状态变化
- 收集和汇总统计数据

#### 关键方法

```python
class SimulationEngine:
    def __init__(self, config: Dict)
    def run_simulation(self, duration: float) -> Dict
    def run_step(self)
    def get_current_statistics(self) -> Dict
    def get_final_statistics(self) -> Dict
```

#### 仿真循环流程

```python
def run_step(self):
    # 1. 生成新订单
    new_orders = self.order_system.generate_orders(self.current_time, self.time_step)
    
    # 2. 分配订单给车辆
    self._assign_orders()
    
    # 3. 更新所有车辆状态
    self.vehicle_manager.update_all_vehicles(self.time_step)
    
    # 4. 处理车辆到达事件
    self._handle_vehicle_arrivals()
    
    # 5. 更新充电进度
    charging_updates = self.charging_manager.update_charging_progress(self.time_step)
    
    # 6. 检查充电需求
    self._check_charging_needs()
    
    # 7. 取消超时订单
    self.order_system.check_and_cancel_timeout_orders(self.current_time)
    
    # 8. 更新时间
    self.current_time += self.time_step
```

#### 事件处理机制

**订单分配事件**:
```python
def _assign_orders(self):
    pending_orders = self.order_system.get_pending_orders()
    available_vehicles = self.vehicle_manager.get_available_vehicles()
    
    for order in pending_orders:
        best_vehicle = self.order_system.find_best_vehicle_for_order(
            order.order_id, available_vehicles
        )
        if best_vehicle:
            self.order_system.assign_order_to_vehicle(
                order.order_id, best_vehicle, self.current_time
            )
```

**车辆到达事件**:
```python
def _handle_vehicle_arrivals(self):
    for vehicle in self.vehicle_manager.get_all_vehicles():
        if vehicle.has_reached_destination():
            if vehicle.status == VEHICLE_STATUS['TO_PICKUP']:
                self._handle_pickup_arrival(vehicle)
            elif vehicle.status == VEHICLE_STATUS['WITH_PASSENGER']:
                self._handle_dropoff_arrival(vehicle)
            elif vehicle.status == VEHICLE_STATUS['TO_CHARGING']:
                self._handle_charging_arrival(vehicle)
```

---

### 2. 地图管理器 (MapManager)

**文件位置**: `core/map_manager.py`

#### 职责范围
- OpenStreetMap数据加载与缓存
- 路径规划和最短路径算法
- 地图节点管理和位置计算
- 充电站位置选择

#### 关键方法

```python
class MapManager:
    def __init__(self, location: str, cache_dir: str = 'datasets/maps')
    def get_shortest_path_nodes(self, origin: int, destination: int) -> List[int]
    def get_shortest_path_points(self, origin: int, destination: int) -> List[Tuple[float, float]]
    def calculate_route_distance(self, origin: int, destination: int) -> float
    def find_nearest_node(self, position: Tuple[float, float]) -> int
    def select_charging_station_nodes(self, n: int) -> List[int]
```

#### 地图加载机制

```python
def _load_graph(self) -> nx.MultiDiGraph:
    # 1. 检查缓存
    graph_filename = self.location.lower().replace(',', '').replace(' ', '_') + '.graphml'
    graph_path = os.path.join(self.cache_dir, graph_filename)
    
    if os.path.exists(graph_path):
        return ox.load_graphml(graph_path)
    
    # 2. 从OSM下载
    graph = ox.graph_from_place(
        query=self.location,
        network_type='drive',
        simplify=True
    )
    ox.save_graphml(graph, graph_path)  # 保存缓存
    return graph
```

#### 路径规划算法

```python
def get_shortest_path_points(self, origin: int, destination: int) -> List[Tuple[float, float]]:
    # 1. 获取路径节点
    route_nodes = nx.shortest_path(
        self.projected_graph,
        origin, destination,
        weight='length'
    )
    
    # 2. 转换为详细坐标点
    path_lines = []
    for u, v in zip(route_nodes[:-1], route_nodes[1:]):
        edge_data = self.projected_graph.get_edge_data(u, v)
        edge = min(edge_data.values(), key=lambda x: x.get('length', float('inf')))
        
        if 'geometry' in edge:
            xs, ys = edge['geometry'].xy
            path_lines.append(list(zip(xs, ys)))
        else:
            p1 = self.get_node_position(u)
            p2 = self.get_node_position(v)
            path_lines.append([p1, p2])
    
    return decompose_path(path_lines)
```

---

### 3. 车辆管理器 (VehicleManager)

**文件位置**: `core/vehicle_manager.py`

#### 职责范围
- 车辆初始化和状态管理
- 车辆移动控制和路径跟踪
- 车辆调度和任务分配
- 电池状态监控

#### 关键方法

```python
class VehicleManager:
    def __init__(self, map_manager: MapManager, config: Dict)
    def update_all_vehicles(self, dt: float)
    def get_available_vehicles(self) -> List[Vehicle]
    def dispatch_vehicle_to_order(self, vehicle: Vehicle, pickup_node: int, dropoff_node: int)
    def dispatch_vehicle_to_charging(self, vehicle: Vehicle, station_node: int)
```

#### 车辆移动控制

```python
def _update_vehicle_movement(self, vehicle: Vehicle, dt: float):
    if not vehicle.path_points:
        return
    
    target_point = vehicle.get_next_path_point()
    if not target_point:
        return
    
    # 检查是否接近目标点
    if is_point_near_target(vehicle.position, target_point, self.approach_threshold):
        vehicle.advance_path_index()
        
        if vehicle.has_reached_destination():
            self._handle_arrival(vehicle)
            return
        
        target_point = vehicle.get_next_path_point()
    
    # 计算移动方向和速度
    direction = calculate_direction_to_target(vehicle.position, target_point)
    velocity = (direction[0] * self.vehicle_speed, direction[1] * self.vehicle_speed)
    
    # 更新位置
    new_position = (
        vehicle.position[0] + velocity[0] * dt,
        vehicle.position[1] + velocity[1] * dt
    )
    vehicle.update_position(new_position)
    vehicle.update_velocity(velocity)
```

#### 车辆分类查询

```python
def get_available_vehicles(self) -> List[Vehicle]:
    """获取可用车辆（空闲且电量充足）"""
    return [v for v in self.vehicles.values() 
            if v.is_idle and not v.needs_charging]

def get_vehicles_by_status(self, status: str) -> List[Vehicle]:
    """按状态获取车辆"""
    return [v for v in self.vehicles.values() if v.status == status]

def get_low_battery_vehicles(self, threshold: float = 20.0) -> List[Vehicle]:
    """获取低电量车辆"""
    return [v for v in self.vehicles.values() 
            if v.battery_percentage <= threshold]
```

---

### 4. 订单系统 (OrderSystem)

**文件位置**: `core/order_system.py`

#### 职责范围
- 随机订单生成
- 车辆匹配算法
- 动态定价机制
- 订单生命周期管理

#### 关键方法

```python
class OrderSystem:
    def __init__(self, map_manager: MapManager, config: Dict)
    def generate_orders(self, current_time: float, dt: float) -> List[Order]
    def find_best_vehicle_for_order(self, order_id: str, available_vehicles: List[Vehicle]) -> Optional[Vehicle]
    def assign_order_to_vehicle(self, order_id: str, vehicle: Vehicle, current_time: float) -> bool
    def complete_order(self, order_id: str, vehicle: Vehicle, current_time: float) -> float
```

#### 订单生成机制

```python
def generate_orders(self, current_time: float, dt: float) -> List[Order]:
    # 计算时间段内应生成的订单数
    expected_orders = self._calculate_expected_orders(current_time, dt)
    actual_orders = np.random.poisson(expected_orders)
    
    new_orders = []
    for _ in range(actual_orders):
        order = self._create_random_order(current_time)
        if order:
            self.orders[order.order_id] = order
            self.pending_orders.append(order.order_id)
            new_orders.append(order)
            self.total_orders_created += 1
    
    return new_orders
```

#### 车辆匹配算法

```python
def find_best_vehicle_for_order(self, order_id: str, available_vehicles: List[Vehicle]) -> Optional[Vehicle]:
    if not available_vehicles:
        return None
    
    order = self.orders[order_id]
    best_vehicle = None
    min_score = float('inf')
    
    for vehicle in available_vehicles:
        # 计算到接客点的距离
        distance = self.map_manager.calculate_route_distance(
            vehicle.current_node, order.pickup_node
        )
        
        # 计算评分（考虑距离和电量）
        battery_penalty = 0 if vehicle.battery_percentage > 50 else 1000
        score = distance + battery_penalty
        
        if score < min_score:
            min_score = score
            best_vehicle = vehicle
    
    return best_vehicle
```

#### 动态定价机制

```python
def _calculate_surge_multiplier(self, current_time: float) -> float:
    hour = (current_time / 3600) % 24
    
    # 高峰时段加价
    if 7 <= hour <= 9 or 17 <= hour <= 19:
        return self.surge_multiplier
    
    return 1.0
```

---

### 5. 充电管理器 (ChargingManager)

**文件位置**: `core/charging_manager.py`

#### 职责范围
- 充电站初始化和布局
- 充电需求判断和调度
- 充电进度管理
- 充电成本计算

#### 关键方法

```python
class ChargingManager:
    def __init__(self, map_manager: MapManager, config: Dict)
    def should_vehicle_charge(self, vehicle: Vehicle) -> bool
    def find_optimal_charging_station(self, vehicle: Vehicle) -> Optional[ChargingStation]
    def request_charging(self, vehicle: Vehicle, station: ChargingStation) -> bool
    def update_charging_progress(self, dt: float) -> Dict[str, float]
```

#### 充电需求判断

```python
def should_vehicle_charge(self, vehicle: Vehicle) -> bool:
    # 1. 电量检查
    if vehicle.battery_percentage > self.charging_threshold:
        return False
    
    # 2. 状态检查
    if not vehicle.is_idle:
        return False
    
    # 3. 位置检查（避免刚刚充过电）
    if hasattr(vehicle, 'last_charging_time'):
        if self.current_time - vehicle.last_charging_time < 300:  # 5分钟冷却
            return False
    
    return True
```

#### 充电站选择算法

```python
def find_optimal_charging_station(self, vehicle: Vehicle) -> Optional[ChargingStation]:
    best_station = None
    min_cost = float('inf')
    
    for station in self.charging_stations.values():
        if not station.has_available_slot():
            continue
        
        # 计算到达成本（距离 + 等待时间）
        distance = self.map_manager.calculate_route_distance(
            vehicle.current_node, station.node_id
        )
        
        queue_penalty = (station.total_slots - station.available_slots) * 100
        total_cost = distance + queue_penalty
        
        if total_cost < min_cost:
            min_cost = total_cost
            best_station = station
    
    return best_station
```

#### 充电进度更新

```python
def update_charging_progress(self, dt: float) -> Dict[str, float]:
    charging_updates = {}
    
    for station in self.charging_stations.values():
        for vehicle_id in list(station.charging_vehicles.keys()):
            # 计算充电量
            charge_amount = station.charging_rate * dt
            charging_updates[vehicle_id] = charge_amount
            
            # 更新充电统计
            station.total_energy_delivered += charge_amount
    
    return charging_updates
```

---

## 工具模块

### 1. 几何计算 (geometry.py)

**文件位置**: `utils/geometry.py`

#### 核心功能
- 距离计算
- 方向向量计算
- 点到目标的接近判断

```python
def calculate_distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    """计算两点间欧几里得距离"""
    return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def calculate_direction_to_target(current_pos: Tuple[float, float], 
                                target_pos: Tuple[float, float]) -> Tuple[float, float]:
    """计算从当前位置到目标位置的单位方向向量"""
    dx = target_pos[0] - current_pos[0]
    dy = target_pos[1] - current_pos[1]
    distance = np.sqrt(dx**2 + dy**2)
    
    if distance == 0:
        return (0.0, 0.0)
    
    return (dx / distance, dy / distance)

def is_point_near_target(current_pos: Tuple[float, float], 
                        target_pos: Tuple[float, float], 
                        threshold: float) -> bool:
    """判断点是否接近目标"""
    return calculate_distance(current_pos, target_pos) <= threshold
```

### 2. 路径处理 (path_utils.py)

**文件位置**: `utils/path_utils.py`

#### 核心功能
- 路径分解和平滑
- 路径点插值
- 路径优化

```python
def decompose_path(path_lines: List[List[Tuple[float, float]]]) -> List[Tuple[float, float]]:
    """将路径线段分解为连续的点序列"""
    if not path_lines:
        return []
    
    result_points = []
    for line in path_lines:
        if not line:
            continue
        
        for point in line:
            if not result_points or point != result_points[-1]:
                result_points.append(point)
    
    return result_points
```

---

## 可视化模块

### 1. 🆕 实时可视化 (visualizer.py) - **已完成重大重构**

**文件位置**: `visualization/visualizer.py`

#### ✅ **重大改进：从Frame存储到实时可视化**

**🎯 完成的任务**：
- ✅ **移除传统frame存储机制** - 不再保存每一帧到内存或磁盘
- ✅ **实现matplotlib实时可视化** - 使用 `plt.ion()` 和实时画布更新
- ✅ **优化内存使用** - 避免大量frame数据占用存储空间
- ✅ **提升用户体验** - 立即查看仿真过程，无需等待动画生成

#### 功能特性
- **实时matplotlib显示** - 使用交互模式的matplotlib进行实时绘制
- **动态数据更新** - 车辆、订单、充电站状态实时更新
- **统计信息展示** - 实时显示仿真统计和性能指标
- **用户交互控制** - 支持窗口关闭和Ctrl+C中断
- **内存高效** - 不存储历史frame，只维护当前状态

#### 核心实现方法

```python
def run_live_simulation(self, duration: float = None):
    """
    运行实时可视化仿真 - 新的核心方法
    
    特点:
    - 使用 plt.ion() 启用交互模式
    - 实时更新画布而非存储帧
    - 内存效率高，无frame存储开销
    """
    print(f"🚀 Starting Live Simulation Visualization (Duration: {duration}s)")
    
    # 启用matplotlib交互模式
    plt.ion()
    plt.show()
    
    # 仿真循环
    while self.engine.current_time < duration:
        # 运行仿真步骤
        self.engine.run_step()
        
        # 实时更新显示
        self._update_live_display()
        
        # 刷新画布
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        
        # 检查窗口状态
        if not plt.get_fignums():
            break
```

#### 实时更新机制

```python
def _update_live_display(self):
    """实时更新显示元素"""
    self._update_vehicles()    # 更新车辆位置和状态
    self._update_orders()      # 更新订单显示
    self._update_info_text()   # 更新统计信息

def _update_vehicles(self):
    """实时更新车辆显示"""
    for vehicle in self.engine.get_vehicles():
        artists = self.vehicle_artists[vehicle.vehicle_id]
        
        # 更新位置
        artists['marker'].set_data([vehicle.position[0]], [vehicle.position[1]])
        
        # 更新状态颜色
        color = COLORS['vehicle'].get(vehicle.status, 'gray')
        if vehicle.battery_percentage < 20:
            color = COLORS['low_battery']
        artists['marker'].set_color(color)
        
        # 更新电池文本
        battery_text = f"{vehicle.battery_percentage:.0f}%"
        artists['text'].set_text(battery_text)
```

#### 🗑️ **已移除的传统功能**
- ❌ `create_animation()` - 传统帧序列动画生成
- ❌ `save_animation()` - 动画文件保存
- ❌ `init_animation()` - matplotlib.animation初始化
- ❌ `update_frame()` - 帧更新回调
- ❌ `matplotlib.animation.FuncAnimation` - 动画类依赖
- ❌ `tqdm` - 进度条依赖（仿真中直接显示进度）

#### 性能优势对比

| 特性 | 传统Frame存储 | 🆕 实时可视化 |
|------|--------------|-------------|
| 内存使用 | 高（存储所有帧） | 低（只维护当前状态） |
| 启动时间 | 慢（需预生成） | 快（立即开始） |
| 交互性 | 无（预生成） | 强（实时响应） |
| 存储空间 | 大（GB级） | 小（MB级） |
| 用户体验 | 延迟（需等待） | 即时（实时查看） |

### 2. 实时Web可视化 (realtime_visualizer.py)

**文件位置**: `realtime_visualizer/realtime_visualizer.py`

#### 功能特性
- **WebSocket实时通信** - 支持快进/暂停/重置
- **交互式Web界面** - 现代化控制面板
- **速度控制** - 0.1x到10x速度调节
- **RESTful API接口** - 完整的HTTP API
- **详情查看** - 点击车辆/订单查看详情

#### Web控制功能

```python
class RealtimeVisualizer:
    async def start(self):
        # 启动Flask API服务器（端口8080）
        self.api_server.start_server()
        
        # 启动WebSocket服务器（端口8765）
        await self.websocket_server.start()
        
        # 支持的控制命令：
        # - start/pause/resume/reset
        # - set_speed (0.1x - 10x)
        # - get_vehicle_details/get_order_details
```

### 3. 📊 统一数据管理 - **已完成改进**

#### ✅ **数据保存系统统一**

**之前的问题**：
- 可视化模式和无头模式使用不同的保存路径
- 文件命名不一致，缺少描述性信息

**🎯 完成的改进**：
- ✅ **统一保存路径** - 所有模式保存到 `outputs/simulation_results/`
- ✅ **智能文件命名** - 格式：`YYYYMMDD_Location_Xv_Ym`
- ✅ **一致的选项** - `--save-data`, `--report`, `--excel` 适用于所有模式
- ✅ **智能依赖** - `--report` 和 `--excel` 自动启用 `--save-data`

```python
def create_output_filename(self, location: str, num_vehicles: int, duration: float) -> str:
    """
    生成描述性文件名
    格式: YYYYMMDD_Location_Xv_Ym
    例如: 20250630_Manhattan_NY_15v_30m
    """
    date_str = datetime.now().strftime("%Y%m%d")
    
    # 清理位置名称
    clean_location = self._clean_location_name(location)
    
    # 智能时间单位
    if duration < 60:
        duration_str = f"{int(duration)}s"
    elif duration < 3600:
        duration_str = f"{int(duration//60)}m"
    else:
        duration_str = f"{int(duration//3600)}h"
    
    return f"{date_str}_{clean_location}_{num_vehicles}v_{duration_str}"
```

#### 数据管理器增强

```python
class DataManager:
    def save_simulation_results(self, final_stats: Dict, filename: str):
        """统一的数据保存方法"""
        output_dir = Path(f"outputs/simulation_results/{filename}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存JSON格式的详细数据
        self._save_json_data(final_stats, output_dir)
        
        # 保存CSV格式的表格数据
        self._save_csv_data(final_stats, output_dir)
        
        # 生成可视化图表
        self.create_visualization_charts(final_stats, output_dir)
```

### 4. 可视化模式对比

| 模式 | 命令 | 特点 | 适用场景 |
|------|------|------|----------|
| **🆕 实时matplotlib** | `python main.py` | 实时显示，无frame存储 | 快速查看，开发调试 |
| **Web交互式** | `python main.py --realtime` | 完整控制，速度调节 | 演示展示，详细分析 |
| **无头模式** | `python main.py --headless` | 最快速度，无可视化 | 批量仿真，性能测试 |

---

## 数据管理模块

### DataManager (data_manager.py)

**文件位置**: `data/data_manager.py`

#### 功能特性
- 仿真数据持久化
- 多格式数据导出
- 报告生成
- 数据分析

```python
class DataManager:
    def save_simulation_results(self, final_stats: Dict)
    def generate_report(self, final_stats: Dict)
    def export_to_excel(self, final_stats: Dict)
    def create_visualization_charts(self, final_stats: Dict)
```

---

## 模块间通信

### 依赖关系图

```
SimulationEngine
    ├── MapManager
    ├── VehicleManager → MapManager
    ├── OrderSystem → MapManager
    ├── ChargingManager → MapManager
    └── DataManager

RealtimeVisualizer
    ├── SimulationEngine
    ├── FlaskApiServer
    └── WebSocketServer
```

### 数据流图

```
配置参数 → 各管理器初始化
订单生成 → 车辆分配 → 路径规划 → 状态更新
充电检查 → 充电站分配 → 充电执行
统计收集 → 数据持久化 → 报告生成
实时数据 → WebSocket推送 → 前端展示
```

这种模块化设计确保了系统的可扩展性、可维护性和可测试性，每个模块都有明确的职责边界和标准化的接口。 