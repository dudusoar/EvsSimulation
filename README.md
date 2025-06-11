# Electric Vehicle Simulation System | 电动车仿真系统

<div align="center">

**Language / 语言选择:**
[🇺🇸 English](#english-documentation) | [🇨🇳 中文](#中文文档)

---

A comprehensive electric vehicle fleet simulation system based on real-world map data, simulating the complete process of electric vehicles picking up passengers, charging, and dispatching in urban environments.

基于真实地图数据的电动车辆运营仿真系统，模拟电动车辆在城市中接送乘客、充电和调度的完整过程。

</div>

---

## English Documentation

### Overview

This is a comprehensive electric vehicle fleet simulation system that models the complete lifecycle of electric vehicles operating in urban environments. The system includes passenger pickup and dropoff, charging station management, route planning, and vehicle dispatching based on real-world OpenStreetMap data.

### Key Features

- **Real-world Map Support**: Built on OpenStreetMap data, supports any city worldwide
- **Complete Business Process**: Order generation, vehicle dispatching, route planning, charging management
- **Real-time Visualization**: Dynamic display of vehicle positions, order status, charging station utilization
- **Detailed Analytics**: Revenue statistics, vehicle utilization rates, charging efficiency metrics
- **Flexible Configuration**: Customizable vehicle count, charging station locations, order generation rates

### System Architecture

```
ev-simulation/
├── config/              # Configuration module
│   └── simulation_config.py
├── core/                # Core business modules
│   ├── map_manager.py   # Map management
│   ├── vehicle_manager.py # Vehicle management
│   ├── order_system.py  # Order system
│   ├── charging_manager.py # Charging management
│   └── simulation_engine.py # Simulation engine
├── models/              # Data models
│   ├── vehicle.py       # Vehicle model
│   ├── order.py         # Order model
│   └── charging_station.py # Charging station model
├── utils/               # Utility functions
│   ├── geometry.py      # Geometric calculations
│   └── path_utils.py    # Path processing
├── visualization/       # Visualization module
│   └── visualizer.py
├── data/                # Data management
│   └── data_manager.py
└── main.py              # Main program entry
```

### Installation

#### 1. Requirements

- Python 3.8+
- pip package manager

#### 2. Install Dependencies

```bash
# Clone the project
git clone <project-url>
cd ev-simulation

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

#### 3. FFmpeg Installation (Optional, for MP4 generation)

- **Windows**: Download and install [FFmpeg](https://ffmpeg.org/download.html)
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt-get install ffmpeg`

### Quick Start

#### Basic Usage

```bash
# Run with default configuration
python main.py

# Specify location
python main.py -l "Beijing, China"

# Custom parameters
python main.py -l "Shanghai, China" -v 30 -d 1800
```

#### Command Line Arguments

```
Basic Parameters:
  -l, --location TEXT      Simulation location (default: West Lafayette, IN)
  -v, --vehicles INT       Number of vehicles (default: 20)
  -d, --duration INT       Simulation duration in seconds (default: 3600)
  -c, --config FILE        Custom configuration file path

Output Parameters:
  -o, --output TEXT        Output filename (without extension)
  -f, --format {html,mp4}  Animation format (default: html)

Run Modes:
  --headless              Headless mode (no visualization)
  --no-animation          Disable animation generation

Data Saving:
  --save-data             Save simulation data
  --report                Generate simulation report
  --excel                 Export Excel file
```

#### Example Commands

```bash
# 1. Quick test (10 vehicles, 5 minutes)
python main.py -v 10 -d 300

# 2. Generate Beijing simulation report
python main.py -l "Beijing, China" -v 50 -d 3600 --save-data --report

# 3. Batch simulation (no visualization)
python main.py --headless -v 100 -d 7200 --save-data --excel

# 4. Generate MP4 video
python main.py -f mp4 -o beijing_simulation

# 5. Use custom configuration
python main.py -c my_config.json
```

### Configuration

#### Default Configuration Parameters

```python
# Map parameters
location = "West Lafayette, IN"  # Simulation location

# Vehicle parameters
num_vehicles = 20               # Number of vehicles
vehicle_speed = 50              # Vehicle speed (km/h)
battery_capacity = 100.0        # Battery capacity (%)
energy_consumption = 0.2        # Energy consumption rate (%/km)
charging_threshold = 20.0       # Charging threshold (%)

# Order parameters
order_generation_rate = 5       # Order generation rate (orders/hour)
base_price_per_km = 2.0        # Base price (currency/km)

# Charging station parameters
num_charging_stations = 5       # Number of charging stations
charging_rate = 1.0            # Charging rate (%/second)
electricity_price = 0.8        # Electricity price (currency/kWh)
```

#### Custom Configuration File

Create `custom_config.json`:

```json
{
    "location": "Tokyo, Japan",
    "num_vehicles": 50,
    "num_charging_stations": 10,
    "order_generation_rate": 10,
    "simulation_duration": 7200
}
```

### Output Description

#### 1. Animation Files

- **HTML Format**: Can be opened directly in browser, supports interaction
- **MP4 Format**: Standard video file, playable with any video player

#### 2. Data Files

Simulation results are saved in `simulation_output/run_[timestamp]/` directory:

- `final_statistics.json` - Final statistics data
- `vehicle_details.csv` - Detailed vehicle data
- `station_details.csv` - Detailed charging station data
- `simulation_report.md` - Simulation report
- `simulation_results.xlsx` - Excel summary file

#### 3. Statistical Charts

- `vehicle_statistics.png` - Vehicle statistics distribution chart
- `charging_station_revenue.png` - Charging station revenue comparison chart

### System Features

#### 1. Intelligent Dispatching Algorithm

- Proximity-based allocation: Prioritize nearest available vehicles
- Battery consideration: Low-battery vehicles excluded from order allocation
- Charging timing: Automatic charging when idle

#### 2. Real-world Route Planning

- Shortest path algorithm based on actual road networks
- Precise distance calculation considering road lengths
- Smooth path tracking and vehicle movement

#### 3. Dynamic Pricing Mechanism

- Base pricing: Per-kilometer billing
- Peak hours: Automatic price increase during rush hours
- Supply-demand balance: Extensible dynamic pricing strategy

#### 4. Charging Management

- Distributed charging stations: Automatic optimal location selection
- Queue mechanism: Wait when charging spots are full
- Smart charging: Automatic charging station search for low battery

### Extension Development

#### Adding New Dispatching Strategies

Modify the `find_best_vehicle_for_order` method in `core/order_system.py`:

```python
def find_best_vehicle_for_order(self, order_id: str, available_vehicles: List[Vehicle]) -> Optional[Vehicle]:
    # Implement your dispatching algorithm
    pass
```

#### Custom Charging Strategies

Modify the `should_vehicle_charge` method in `core/charging_manager.py`:

```python
def should_vehicle_charge(self, vehicle: Vehicle) -> bool:
    # Implement your charging decision logic
    pass
```

#### Adding New Statistical Metrics

Add to the `get_final_statistics` method in `core/simulation_engine.py`:

```python
stats['custom_metric'] = calculate_custom_metric()
```

### Notes

1. **Map Data**: First run will download map data from OpenStreetMap, requires internet connection
2. **Caching**: Map data is cached in `graphml_files` directory to avoid repeated downloads
3. **Performance**: Large-scale simulations (>100 vehicles) recommended to use headless mode
4. **Memory Usage**: Long simulations consume significant memory, recommend periodic data saving

### Troubleshooting

#### Q: Map loading failed?
A: Check internet connection, ensure OpenStreetMap access. Try different location names, use more specific place names.

#### Q: Animation generation is slow?
A: Use `--headless` mode, or reduce vehicle count and simulation duration.

#### Q: MP4 generation failed?
A: Ensure FFmpeg is installed and added to system PATH.

#### Q: How to improve simulation speed?
A: 
- Use headless mode: `--headless`
- Reduce time precision: modify `time_step` parameter
- Optimize algorithms: simplify route planning or dispatching logic

### License

MIT License

### Contributing

Issues and Pull Requests are welcome!

---

## 中文文档

### 概述

这是一个基于真实地图数据的电动车辆运营仿真系统，模拟电动车辆在城市中接送乘客、充电和调度的完整过程。系统包括乘客接送、充电站管理、路径规划和车辆调度等功能，基于真实的OpenStreetMap数据。

### 功能特性

- **真实地图支持**：基于OpenStreetMap数据，支持全球任意城市
- **完整业务流程**：订单生成、车辆调度、路径规划、充电管理
- **实时可视化**：动态展示车辆位置、订单状态、充电站使用情况
- **详细统计分析**：收入统计、车辆利用率、充电效率等关键指标
- **灵活配置**：支持自定义车辆数量、充电站位置、订单生成率等参数

### 系统架构

```
ev-simulation/
├── config/              # 配置模块
│   └── simulation_config.py
├── core/                # 核心业务模块
│   ├── map_manager.py   # 地图管理
│   ├── vehicle_manager.py # 车辆管理
│   ├── order_system.py  # 订单系统
│   ├── charging_manager.py # 充电管理
│   └── simulation_engine.py # 仿真引擎
├── models/              # 数据模型
│   ├── vehicle.py       # 车辆模型
│   ├── order.py         # 订单模型
│   └── charging_station.py # 充电站模型
├── utils/               # 工具函数
│   ├── geometry.py      # 几何计算
│   └── path_utils.py    # 路径处理
├── visualization/       # 可视化模块
│   └── visualizer.py
├── data/                # 数据管理
│   └── data_manager.py
└── main.py              # 主程序入口
```

### 安装说明

#### 1. 环境要求

- Python 3.8+
- pip 包管理器

#### 2. 安装依赖

```bash
# 克隆项目
git clone <项目地址>
cd ev-simulation

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

#### 3. FFmpeg安装（可选，用于生成MP4）

- **Windows**: 下载并安装 [FFmpeg](https://ffmpeg.org/download.html)
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt-get install ffmpeg`

### 快速开始

#### 基本使用

```bash
# 使用默认配置运行
python main.py

# 指定地点运行
python main.py -l "Beijing, China"

# 自定义参数
python main.py -l "Shanghai, China" -v 30 -d 1800
```

#### 命令行参数

```
基本参数:
  -l, --location TEXT      仿真地点（默认: West Lafayette, IN）
  -v, --vehicles INT       车辆数量（默认: 20）
  -d, --duration INT       仿真时长，单位秒（默认: 3600）
  -c, --config FILE        自定义配置文件路径

输出参数:
  -o, --output TEXT        输出文件名（不含扩展名）
  -f, --format {html,mp4}  动画格式（默认: html）

运行模式:
  --headless              无头模式（无可视化）
  --no-animation          禁用动画生成

数据保存:
  --save-data             保存仿真数据
  --report                生成仿真报告
  --excel                 导出Excel文件
```

#### 示例命令

```bash
# 1. 快速测试（10辆车，5分钟）
python main.py -v 10 -d 300

# 2. 生成北京地区的仿真报告
python main.py -l "Beijing, China" -v 50 -d 3600 --save-data --report

# 3. 批量仿真（无可视化）
python main.py --headless -v 100 -d 7200 --save-data --excel

# 4. 生成MP4视频
python main.py -f mp4 -o beijing_simulation

# 5. 使用自定义配置
python main.py -c my_config.json
```

### 配置说明

#### 默认配置参数

```python
# 地图参数
location = "West Lafayette, IN"  # 仿真地点

# 车辆参数
num_vehicles = 20               # 车辆数量
vehicle_speed = 50              # 车速（km/h）
battery_capacity = 100.0        # 电池容量（%）
energy_consumption = 0.2        # 能耗率（%/km）
charging_threshold = 20.0       # 充电阈值（%）

# 订单参数
order_generation_rate = 5       # 订单生成率（订单/小时）
base_price_per_km = 2.0        # 基础价格（元/km）

# 充电站参数
num_charging_stations = 5       # 充电站数量
charging_rate = 1.0            # 充电速率（%/秒）
electricity_price = 0.8        # 电价（元/kWh）
```

#### 自定义配置文件

创建 `custom_config.json`:

```json
{
    "location": "Tokyo, Japan",
    "num_vehicles": 50,
    "num_charging_stations": 10,
    "order_generation_rate": 10,
    "simulation_duration": 7200
}
```

### 输出说明

#### 1. 动画文件

- **HTML格式**：可在浏览器中直接打开，支持交互
- **MP4格式**：标准视频文件，可用任意播放器观看

#### 2. 数据文件

仿真结果保存在 `simulation_output/run_[时间戳]/` 目录下：

- `final_statistics.json` - 最终统计数据
- `vehicle_details.csv` - 车辆详细数据
- `station_details.csv` - 充电站详细数据
- `simulation_report.md` - 仿真报告
- `simulation_results.xlsx` - Excel汇总文件

#### 3. 统计图表

- `vehicle_statistics.png` - 车辆统计分布图
- `charging_station_revenue.png` - 充电站收入对比图

### 系统特性

#### 1. 智能调度算法

- 就近分配原则：优先分配距离最近的空闲车辆
- 电量考虑：低电量车辆不参与订单分配
- 充电时机：空闲时自动前往最近充电站

#### 2. 真实路径规划

- 基于实际道路网络的最短路径算法
- 考虑道路长度的精确距离计算
- 平滑的路径跟踪和车辆移动

#### 3. 动态定价机制

- 基础价格：按公里计费
- 高峰时段：早晚高峰自动提价
- 供需平衡：可扩展的动态定价策略

#### 4. 充电管理

- 分布式充电站：自动选择最优位置
- 排队机制：充电位满时等待
- 智能充电：低电量自动寻找充电站

### 扩展开发

#### 添加新的调度策略

在 `core/order_system.py` 中修改 `find_best_vehicle_for_order` 方法：

```python
def find_best_vehicle_for_order(self, order_id: str, available_vehicles: List[Vehicle]) -> Optional[Vehicle]:
    # 实现你的调度算法
    pass
```

#### 自定义充电策略

在 `core/charging_manager.py` 中修改 `should_vehicle_charge` 方法：

```python
def should_vehicle_charge(self, vehicle: Vehicle) -> bool:
    # 实现你的充电决策逻辑
    pass
```

#### 添加新的统计指标

在 `core/simulation_engine.py` 的 `get_final_statistics` 方法中添加：

```python
stats['custom_metric'] = calculate_custom_metric()
```

### 注意事项

1. **地图数据**：首次运行会从OpenStreetMap下载地图数据，需要网络连接
2. **缓存机制**：地图数据会缓存在 `graphml_files` 目录，避免重复下载
3. **性能考虑**：大规模仿真（>100辆车）建议使用无头模式
4. **内存使用**：长时间仿真会占用较多内存，建议定期保存数据

### 常见问题

#### Q: 地图加载失败？
A: 检查网络连接，确保能访问OpenStreetMap。尝试更换地点名称，使用更具体的地名。

#### Q: 动画生成很慢？
A: 使用 `--headless` 模式运行，或减少车辆数量和仿真时长。

#### Q: MP4生成失败？
A: 确保已安装FFmpeg，并添加到系统PATH。

#### Q: 如何提高仿真速度？
A: 
- 使用无头模式：`--headless`
- 减少时间精度：修改 `time_step` 参数
- 优化算法：简化路径规划或调度逻辑

### 许可证

MIT License

### 贡献指南

欢迎提交Issue和Pull Request！

### 联系方式

如有问题或建议，请通过Issue联系。

---

<div align="center">

**Navigation / 导航:**
[🔝 Back to Top / 返回顶部](#electric-vehicle-simulation-system--电动车仿真系统) | 
[🇺🇸 English](#english-documentation) | 
[🇨🇳 中文](#中文文档)

</div>