# Electric Vehicle Fleet Simulation System | 电动车队仿真系统

<div align="center">

**Language / 语言选择:**
[🇺🇸 English](#english-documentation) | [🇨🇳 中文](#中文文档)

---

A comprehensive electric vehicle fleet simulation system featuring dual simulation engines, real-world map integration, and modern web interface for urban mobility analysis.

基于真实地图数据的电动车队仿真系统，提供双仿真引擎、现代化Web界面，专用于城市出行分析。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com/)
[![OSMnx](https://img.shields.io/badge/OSMnx-2.0+-orange.svg)](https://osmnx.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## English Documentation

### 🌟 Overview

This is a state-of-the-art electric vehicle fleet simulation system designed for comprehensive urban mobility analysis. The system provides **dual simulation architectures** to meet different research and demonstration needs:

1. **🐍 Python Simulation Engine**: YAML-configured standalone simulation with matplotlib visualization
2. **🌐 Web Application System**: Modern browser-based interface with real-time interaction

Both systems share the same sophisticated simulation core while offering different user experiences and deployment scenarios.

### ✨ Key Features

#### 🏗️ **Dual Simulation Architecture**
- **Standalone Python Engine**: Command-line driven with YAML configuration
- **Web Application Interface**: Browser-based with real-time controls
- **Shared Core Logic**: Both systems use identical simulation algorithms

#### 🗺️ **Real-World Map Integration**
- **OpenStreetMap Data**: Supports any city worldwide with automatic map downloading
- **Realistic Road Networks**: Accurate distance calculations and route planning
- **Smart Caching**: Efficient map data storage to avoid repeated downloads

#### 🚗 **Comprehensive Vehicle Management**
- **Fleet Operations**: Vehicle dispatching, passenger pickup/dropoff
- **Battery Management**: Realistic battery consumption and charging behavior
- **Intelligent Routing**: Shortest path algorithms on real road networks

#### ⚡ **Advanced Charging Infrastructure**
- **Distributed Charging Stations**: Strategic placement throughout the city
- **Queue Management**: Realistic waiting times when stations are occupied
- **Smart Charging**: Automatic low-battery vehicle redirection

#### 📊 **Rich Analytics & Visualization**
- **Real-time Monitoring**: Live vehicle tracking and system statistics
- **Performance Metrics**: Revenue, utilization rates, efficiency analysis
- **Multiple Output Formats**: Interactive charts, data exports, simulation reports

### 🏗️ System Architecture

```
EvsSimulation/
├── 🐍 Python Simulation Engine
│   ├── main.py                  # YAML-driven entry point
│   ├── core/                    # Simulation engine modules
│   │   ├── simulation_engine.py # Core simulation logic
│   │   ├── vehicle_manager.py   # Vehicle fleet management
│   │   ├── order_system.py      # Order generation & dispatching
│   │   ├── charging_manager.py  # Charging infrastructure
│   │   └── map_manager.py       # Map data & route planning
│   ├── models/                  # Data models
│   │   ├── vehicle.py           # Vehicle state & behavior
│   │   ├── order.py             # Order lifecycle
│   │   └── charging_station.py  # Charging station management
│   ├── config/                  # Configuration system
│   │   ├── yaml_config_manager.py # YAML configuration handler
│   │   └── simulation_config.py   # Legacy config support
│   ├── visualization/           # Matplotlib visualization
│   │   └── visualizer.py        # Real-time visualization
│   └── yaml_config/             # YAML configuration files
│       ├── default.yaml         # Default configuration
│       ├── west_lafayette_demo.yaml # Demo configuration
│       └── headless_batch.yaml  # Batch processing config
│
├── 🌐 Web Application System
│   ├── backend/                 # FastAPI backend
│   │   ├── main.py              # Web server entry point
│   │   ├── api/                 # REST API endpoints
│   │   │   ├── simulation.py    # Simulation control API
│   │   │   ├── data.py          # Data query API
│   │   │   └── config.py        # Configuration API
│   │   ├── websocket/           # Real-time communication
│   │   │   └── simulation_ws.py # WebSocket handlers
│   │   └── services/            # Business logic
│   │       └── simulation_service.py # Simulation management
│   └── frontend/                # Web interface
│       ├── templates/           # HTML pages
│       │   ├── index.html       # Main dashboard
│       │   ├── vehicles.html    # Vehicle tracking
│       │   ├── orders.html      # Order monitoring
│       │   ├── charging-stations.html # Charging infrastructure
│       │   └── config.html      # Configuration panel
│       └── static/              # Frontend assets
│           ├── js/              # JavaScript modules
│           └── css/             # Stylesheets
│
└── 📁 Shared Resources
    ├── data/                    # Data management
    ├── utils/                   # Utility functions
    ├── datasets/                # Map cache & simulation data
    └── doc/                     # Comprehensive documentation
```

### 🚀 Quick Start

#### 📋 Prerequisites

- **Python 3.8+** with pip package manager
- **Internet connection** for initial map data download
- **Modern web browser** for web interface (Chrome/Firefox/Safari)

#### ⚙️ Installation

```bash
# Clone the repository
git clone <repository-url>
cd EvsSimulation

# Create virtual environment (strongly recommended)
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 🎯 Usage Examples

##### 1. Python Simulation (YAML-Driven)

```bash
# Quick demo with default settings
python main.py

# Use specific configuration
python main.py -c yaml_config/west_lafayette_demo.yaml

# Headless batch processing
python main.py -c yaml_config/headless_batch.yaml

# List available configurations
python main.py --list
```

##### 2. Web Application

```bash
# Activate virtual environment
.venv\Scripts\activate

# Start web server (run from project root)
uvicorn webapp.backend.main:app --host 127.0.0.1 --port 8080 --reload

# Access web interface
# Main Dashboard: http://127.0.0.1:8080
# API Documentation: http://127.0.0.1:8080/docs
```

### 📖 Configuration System

#### YAML Configuration (Python Engine)

The Python simulation engine uses YAML files for complete configuration:

```yaml
# Example: yaml_config/custom_simulation.yaml
simulation:
  name: "Custom EV Fleet Simulation"
  location: "Manhattan, New York, NY, USA"
  duration: 3600  # seconds
  time_step: 0.1

vehicles:
  count: 25
  battery_capacity: 75.0  # kWh
  max_speed: 60  # km/h
  charging_threshold: 20  # %

orders:
  generation_rate: 40  # orders per hour
  base_price_per_km: 2.5  # $/km

charging:
  stations_count: 8
  slots_per_station: 4
  charging_power: 50  # kW

visualization:
  mode: "live"  # or "headless"
  fps: 30

data:
  save_data: true
  save_interval: 60  # seconds
```

### 🎮 Web Interface Guide

#### 🏠 Main Dashboard (`/`)
- **🎛️ Control Panel**: Create, start, pause, stop simulations
- **🗺️ Interactive Map**: Real-time vehicle tracking with Leaflet integration
- **📊 Live Statistics**: Revenue, utilization rates, performance metrics
- **📈 Dynamic Charts**: Real-time data visualization

#### 🚗 Vehicle Tracking (`/vehicles`)
- **📋 Fleet Overview**: Comprehensive vehicle status table
- **🔋 Battery Monitoring**: Real-time battery level tracking
- **📍 Location Tracking**: GPS coordinates and current status
- **🔍 Filter & Search**: Advanced filtering capabilities

#### 📦 Order Management (`/orders`)
- **📝 Order Queue**: Pending and active order monitoring
- **⏱️ Timing Analysis**: Wait times and completion statistics
- **🎯 Assignment Tracking**: Vehicle-order assignment visualization
- **📊 Performance Metrics**: Order completion rates and revenue

#### ⚡ Charging Infrastructure (`/charging-stations`)
- **🔌 Station Status**: Real-time charging station availability
- **📈 Utilization Rates**: Usage statistics and efficiency metrics
- **⏳ Queue Management**: Waiting vehicle tracking
- **💰 Revenue Analysis**: Charging station profitability

#### ⚙️ Configuration Panel (`/config`)
- **🎛️ Simulation Parameters**: Vehicle count, duration, location
- **🔧 System Settings**: Battery capacity, charging rates, pricing
- **📊 Data Export Options**: Configure data saving and reporting
- **🎨 Visualization Settings**: Display preferences and update rates

### 📚 Documentation

The project includes comprehensive documentation in the `doc/` directory:

- **📖 README.md**: This overview document
- **🏗️ PROJECT_ARCHITECTURE.md**: Detailed system architecture
- **🔧 TECHNICAL_IMPLEMENTATION.md**: Implementation details
- **📡 API_REFERENCE.md**: Web API documentation
- **📊 DATA_MODELS.md**: Data structure reference
- **⚙️ WEBAPP_EXPANSION_DESIGN.md**: Web system design
- **🔍 SYSTEM_MODULES.md**: Module documentation
- **❓ WEBAPP_TROUBLESHOOTING.md**: Common issues & solutions

### 🚨 Troubleshooting

#### Common Issues

**Q: Map loading failed?**
```
✅ Solution: Check internet connection and try a different city name
📝 Example: Use "Manhattan, New York, NY, USA" instead of "NYC"
```

**Q: Web interface won't start?**
```
✅ Solution: Ensure you're running uvicorn from the project root directory
📝 Command: uvicorn webapp.backend.main:app --host 127.0.0.1 --port 8080 --reload
```

**Q: Python simulation crashes?**
```
✅ Solution: Verify virtual environment activation and dependency installation
📝 Check: .venv\Scripts\activate && pip install -r requirements.txt
```

### 📈 Performance Recommendations

- **🖥️ For Demos**: Use web interface with 10-30 vehicles
- **📊 For Analysis**: Use Python engine with headless mode
- **🔍 For Development**: Use live visualization with small fleet sizes
- **⚡ For Batch Processing**: Use headless configuration templates

### 🤝 Contributing

We welcome contributions! Please see our contribution guidelines:

1. **🍴 Fork** the repository
2. **🌟 Create** a feature branch
3. **✅ Add** tests for new functionality  
4. **📝 Update** documentation
5. **🔄 Submit** a pull request

### 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 中文文档

### 🌟 概述

这是一个先进的电动车队仿真系统，专为全面的城市出行分析而设计。系统提供**双仿真架构**以满足不同的研究和演示需求：

1. **🐍 Python仿真引擎**：YAML配置驱动的独立仿真，支持matplotlib可视化
2. **🌐 Web应用系统**：现代化浏览器界面，支持实时交互

两套系统共享相同的复杂仿真内核，同时提供不同的用户体验和部署场景。

### ✨ 核心特性

#### 🏗️ **双仿真架构**
- **独立Python引擎**：命令行驱动，YAML配置
- **Web应用界面**：浏览器访问，实时控制
- **共享核心逻辑**：两套系统使用相同的仿真算法

#### 🗺️ **真实地图集成**
- **OpenStreetMap数据**：支持全球任意城市，自动地图下载
- **真实路网**：精确距离计算和路径规划
- **智能缓存**：高效地图数据存储，避免重复下载

#### 🚗 **全面车队管理**
- **车队运营**：车辆调度、乘客接送
- **电池管理**：真实电池消耗和充电行为
- **智能路径**：基于真实路网的最短路径算法

#### ⚡ **先进充电基础设施**
- **分布式充电站**：城市内战略性布局
- **队列管理**：充电站占用时的真实等待时间
- **智能充电**：低电量车辆自动重定向

### 🚀 快速开始

#### 📋 环境要求

- **Python 3.8+** 和 pip 包管理器
- **网络连接** 用于初始地图数据下载
- **现代浏览器** 用于Web界面 (Chrome/Firefox/Safari)

#### ⚙️ 安装说明

```bash
# 克隆仓库
git clone <仓库地址>
cd EvsSimulation

# 创建虚拟环境（强烈推荐）
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 🎯 使用示例

##### 1. Python仿真（YAML驱动）

```bash
# 使用默认设置的快速演示
python main.py

# 使用特定配置
python main.py -c yaml_config/west_lafayette_demo.yaml

# 无界面批处理
python main.py -c yaml_config/headless_batch.yaml

# 列出可用配置
python main.py --list
```

##### 2. Web应用

```bash
# 激活虚拟环境
.venv\Scripts\activate

# 启动Web服务器（在项目根目录运行）
uvicorn webapp.backend.main:app --host 127.0.0.1 --port 8080 --reload

# 访问Web界面
# 主控制台: http://127.0.0.1:8080
# API文档: http://127.0.0.1:8080/docs
```

### 📖 配置系统

#### YAML配置（Python引擎）

Python仿真引擎使用YAML文件进行完整配置：

```yaml
# 示例: yaml_config/custom_simulation.yaml
simulation:
  name: "自定义电动车队仿真"
  location: "北京市, 中国"
  duration: 3600  # 秒
  time_step: 0.1

vehicles:
  count: 25
  battery_capacity: 75.0  # kWh
  max_speed: 60  # km/h
  charging_threshold: 20  # %

orders:
  generation_rate: 40  # 订单/小时
  base_price_per_km: 2.5  # 元/km

charging:
  stations_count: 8
  slots_per_station: 4
  charging_power: 50  # kW

visualization:
  mode: "live"  # 或 "headless"
  fps: 30

data:
  save_data: true
  save_interval: 60  # 秒
```

### 🎮 Web界面指南

#### 🏠 主控制台 (`/`)
- **🎛️ 控制面板**：创建、启动、暂停、停止仿真
- **🗺️ 交互地图**：基于Leaflet的实时车辆跟踪
- **📊 实时统计**：收入、利用率、性能指标
- **📈 动态图表**：实时数据可视化

#### 🚗 车辆跟踪 (`/vehicles`)
- **📋 车队概览**：全面的车辆状态表格
- **🔋 电池监控**：实时电池电量跟踪
- **📍 位置跟踪**：GPS坐标和当前状态
- **🔍 筛选搜索**：高级筛选功能

#### 📦 订单管理 (`/orders`)
- **📝 订单队列**：待处理和活跃订单监控
- **⏱️ 时间分析**：等待时间和完成统计
- **🎯 分配跟踪**：车辆-订单分配可视化
- **📊 性能指标**：订单完成率和收入

#### ⚡ 充电基础设施 (`/charging-stations`)
- **🔌 充电站状态**：实时充电站可用性
- **📈 利用率**：使用统计和效率指标
- **⏳ 队列管理**：等待车辆跟踪
- **💰 收入分析**：充电站盈利能力

#### ⚙️ 配置面板 (`/config`)
- **🎛️ 仿真参数**：车辆数量、持续时间、位置
- **🔧 系统设置**：电池容量、充电速率、定价
- **📊 数据导出选项**：配置数据保存和报告
- **🎨 可视化设置**：显示偏好和更新速率

### 📚 文档说明

项目在 `doc/` 目录中包含全面的文档：

- **📖 README.md**：概览文档
- **🏗️ PROJECT_ARCHITECTURE.md**：详细系统架构
- **🔧 TECHNICAL_IMPLEMENTATION.md**：实现细节
- **📡 API_REFERENCE.md**：Web API文档
- **📊 DATA_MODELS.md**：数据结构参考
- **⚙️ WEBAPP_EXPANSION_DESIGN.md**：Web系统设计
- **🔍 SYSTEM_MODULES.md**：模块文档
- **❓ WEBAPP_TROUBLESHOOTING.md**：常见问题解决

### 🚨 故障排除

#### 常见问题

**Q: 地图加载失败？**
```
✅ 解决方案：检查网络连接，尝试不同的城市名称
📝 示例：使用"北京市, 中国"而不是"北京"
```

**Q: Web界面无法启动？**
```
✅ 解决方案：确保从项目根目录运行uvicorn命令
📝 命令：uvicorn webapp.backend.main:app --host 127.0.0.1 --port 8080 --reload
```

**Q: Python仿真崩溃？**
```
✅ 解决方案：验证虚拟环境激活和依赖安装
📝 检查：.venv\Scripts\activate && pip install -r requirements.txt
```

### 📈 性能建议

- **🖥️ 演示用途**：使用Web界面，10-30辆车
- **📊 分析用途**：使用Python引擎，无界面模式
- **🔍 开发用途**：使用实时可视化，小车队规模
- **⚡ 批处理**：使用无界面配置模板

### 🤝 贡献指南

欢迎贡献！请查看我们的贡献指南：

1. **🍴 Fork** 仓库
2. **🌟 创建** 功能分支
3. **✅ 添加** 新功能测试
4. **📝 更新** 文档
5. **🔄 提交** Pull Request

### 📜 许可证

本项目基于MIT许可证 - 详情请查看 [LICENSE](LICENSE) 文件。

---

<div align="center">

**Navigation / 导航:**
[🔝 Back to Top / 返回顶部](#electric-vehicle-fleet-simulation-system--电动车队仿真系统) | 
[🇺🇸 English](#english-documentation) | 
[🇨🇳 中文](#中文文档)

**Quick Links / 快速链接:**
[📖 Documentation / 文档](doc/) | 
[🚀 Quick Start / 快速开始](#quick-start) | 
[⚙️ Configuration / 配置](#configuration-system) | 
[🎮 Web Interface / Web界面](#web-interface-guide)

</div> 