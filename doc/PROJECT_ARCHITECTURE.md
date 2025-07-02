# EV Simulation System - Project Architecture | 项目架构文档

## 📋 Document Overview | 文档概述

**Version**: 3.0 (Updated for Dual Simulation Architecture)  
**Last Updated**: 2024-12  
**Language**: English | 中文

This document provides a comprehensive overview of the EV Simulation System architecture, covering both the Python simulation engine and the Web application system.

本文档提供电动车仿真系统架构的全面概述，涵盖Python仿真引擎和Web应用系统。

---

## 🏗️ System Architecture Overview | 系统架构概述

### Dual Simulation Architecture | 双仿真架构

The EV Simulation System employs a **dual architecture** approach to serve different use cases:

EV仿真系统采用**双架构**方法来服务不同的用例：

```
┌─────────────────────────────────────────────────────────────┐
│                 EV Simulation System                        │
│                   电动车仿真系统                              │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
        ┌───────────▼──────────┐   ┌───▼────────────────┐
        │  🐍 Python Engine    │   │  🌐 Web System     │
        │   Python仿真引擎      │   │   Web系统          │
        └──────────────────────┘   └────────────────────┘
        │                          │                    
        │ • YAML Configuration     │ • Browser Interface│
        │ • Command Line           │ • Real-time Control│
        │ • Batch Processing       │ • Interactive Demo │
        │ • Research Analysis      │ • Live Monitoring  │
        │                          │                    │
        │ • YAML配置              │ • 浏览器界面        │
        │ • 命令行操作             │ • 实时控制          │
        │ • 批处理                │ • 交互演示          │
        │ • 研究分析              │ • 实时监控          │
        └──────────┬───────────────┴────────────────────┘
                   │                                    
        ┌──────────▼──────────────────────────────────┐
        │         🔧 Shared Core Engine                │
        │            共享核心引擎                       │
        │                                             │
        │  • SimulationEngine  • VehicleManager      │
        │  • MapManager        • OrderSystem         │
        │  • ChargingManager   • Data Models         │
        └─────────────────────────────────────────────┘
```

### Key Architectural Principles | 关键架构原则

1. **Separation of Concerns | 关注点分离**
   - Core simulation logic is independent of UI/interface
   - 核心仿真逻辑独立于UI/界面

2. **Shared Foundation | 共享基础**
   - Both systems use identical simulation algorithms
   - 两个系统使用相同的仿真算法

3. **Interface Flexibility | 界面灵活性**
   - Multiple ways to interact with the same simulation engine
   - 多种方式与同一仿真引擎交互

4. **Configuration Driven | 配置驱动**
   - Behavior controlled by configuration rather than code changes
   - 行为由配置而非代码更改控制

---

## 🐍 Python Simulation Engine | Python仿真引擎

### Architecture Components | 架构组件

```
Python Simulation Engine
├── 📋 Configuration Layer | 配置层
│   ├── yaml_config_manager.py    # YAML configuration handler
│   ├── simulation_config.py      # Legacy config support
│   └── yaml_config/              # Configuration files
│       ├── default.yaml
│       ├── west_lafayette_demo.yaml
│       └── headless_batch.yaml
│
├── 🎮 Entry Point | 入口点
│   └── main.py                   # YAML-driven main entry
│
├── 🔧 Core Engine | 核心引擎
│   ├── simulation_engine.py      # Main simulation coordinator
│   ├── vehicle_manager.py        # Vehicle fleet management
│   ├── order_system.py           # Order generation & dispatch
│   ├── charging_manager.py       # Charging infrastructure
│   └── map_manager.py            # Map data & routing
│
├── 📊 Data Models | 数据模型
│   ├── vehicle.py                # Vehicle state & behavior
│   ├── order.py                  # Order lifecycle
│   └── charging_station.py       # Charging station logic
│
├── 🎨 Visualization | 可视化
│   └── visualizer.py             # Real-time matplotlib display
│
└── 📁 Support | 支持模块
    ├── data/                     # Data management
    ├── utils/                    # Utility functions
    └── datasets/                 # Map cache & outputs
```

### Configuration System | 配置系统

#### YAML Configuration Structure | YAML配置结构

```yaml
# Comprehensive YAML configuration schema
simulation:
  name: "Simulation Name"
  location: "City, Country"
  duration: 3600              # seconds
  time_step: 0.1             # simulation time step

vehicles:
  count: 25                  # number of vehicles
  battery_capacity: 75.0     # kWh
  max_speed: 60             # km/h
  charging_threshold: 20     # %
  energy_consumption: 0.3    # kWh/km

orders:
  generation_rate: 40        # orders per hour
  base_price_per_km: 2.5    # currency per km
  max_wait_time: 15         # minutes

charging:
  stations_count: 8          # number of stations
  slots_per_station: 4       # charging slots
  charging_power: 50         # kW
  electricity_price: 0.4     # currency per kWh

visualization:
  mode: "live"              # "live" or "headless"
  fps: 30                   # frames per second
  
data:
  save_data: true           # enable data export
  save_interval: 60         # seconds
```

### Execution Modes | 执行模式

#### 1. Live Visualization Mode | 实时可视化模式
- **Purpose**: Real-time monitoring with matplotlib
- **Use Cases**: Development, small-scale analysis, demonstrations
- **Command**: `python main.py -c config.yaml`

#### 2. Headless Mode | 无界面模式
- **Purpose**: High-performance batch processing
- **Use Cases**: Large-scale analysis, parameter sweeps, CI/CD
- **Command**: `python main.py -c headless_config.yaml`

---

## 🌐 Web Application System | Web应用系统

### Web Architecture | Web架构

```
Web Application System
├── 🖥️ Backend | 后端
│   ├── main.py                      # FastAPI application entry
│   ├── api/                         # REST API endpoints
│   │   ├── simulation.py            # Simulation control
│   │   ├── data.py                  # Data queries
│   │   └── config.py                # Configuration management
│   ├── websocket/                   # Real-time communication
│   │   └── simulation_ws.py         # WebSocket handlers
│   ├── services/                    # Business logic
│   │   └── simulation_service.py    # Core simulation interface
│   └── models/                      # API data models
│       └── response.py              # Response schemas
│
├── 🌐 Frontend | 前端
│   ├── templates/                   # HTML templates
│   │   ├── index.html               # Main dashboard
│   │   ├── vehicles.html            # Vehicle tracking
│   │   ├── orders.html              # Order management
│   │   ├── charging-stations.html   # Infrastructure monitoring
│   │   └── config.html              # Configuration panel
│   └── static/                      # Static assets
│       ├── js/                      # JavaScript modules
│       │   ├── app.js               # Main application logic
│       │   ├── websocket.js         # WebSocket client
│       │   ├── map.js               # Map controls
│       │   ├── charts.js            # Data visualization
│       │   ├── vehicles.js          # Vehicle tracking
│       │   ├── orders.js            # Order management
│       │   └── charging-stations.js # Station monitoring
│       └── css/
│           └── style.css            # Application styles
│
└── 🔧 Integration | 集成
    └── Calls Python Core Engine    # Uses same simulation logic
```

### Technology Stack | 技术栈

#### Backend Technologies | 后端技术
- **FastAPI**: Modern Python web framework
- **WebSocket**: Real-time bidirectional communication
- **Uvicorn**: ASGI server for production deployment
- **Pydantic**: Data validation and serialization

#### Frontend Technologies | 前端技术
- **Leaflet**: Interactive mapping library
- **Chart.js**: Data visualization and charting
- **Bootstrap**: Responsive UI framework
- **Vanilla JavaScript**: No framework dependencies

### Web Interface Pages | Web界面页面

#### 1. Main Dashboard (`/`) | 主控制台
- **Purpose**: Central control and overview
- **Features**: 
  - Simulation control panel
  - Real-time map with vehicle tracking
  - Live statistics and charts
  - System status monitoring

#### 2. Vehicle Tracking (`/vehicles`) | 车辆跟踪
- **Purpose**: Detailed vehicle fleet monitoring
- **Features**:
  - Comprehensive vehicle status table
  - Real-time battery monitoring
  - GPS location tracking
  - Advanced filtering and search

#### 3. Order Management (`/orders`) | 订单管理
- **Purpose**: Order lifecycle tracking
- **Features**:
  - Pending and active order queues
  - Wait time analysis
  - Vehicle-order assignment tracking
  - Performance metrics

#### 4. Charging Infrastructure (`/charging-stations`) | 充电基础设施
- **Purpose**: Charging station monitoring
- **Features**:
  - Real-time station availability
  - Utilization statistics
  - Queue management
  - Revenue analysis

#### 5. Configuration Panel (`/config`) | 配置面板
- **Purpose**: System parameter configuration
- **Features**:
  - Simulation parameter adjustment
  - System settings management
  - Data export configuration
  - Visualization preferences

---

## 🔗 Core Engine Integration | 核心引擎集成

### Shared Components | 共享组件

Both the Python and Web systems utilize the same core simulation engine:

Python和Web系统都使用相同的核心仿真引擎：

#### 1. SimulationEngine | 仿真引擎
```python
class SimulationEngine:
    """
    Central coordinator for all simulation activities
    所有仿真活动的中央协调器
    """
    def __init__(self, config):
        self.vehicle_manager = VehicleManager(config)
        self.order_system = OrderSystem(config)
        self.charging_manager = ChargingManager(config)
        self.map_manager = MapManager(config)
    
    def run_step(self):
        """Execute one simulation time step"""
    
    def get_current_statistics(self):
        """Get real-time system statistics"""
```

#### 2. VehicleManager | 车辆管理器
- Vehicle fleet initialization and management
- Battery state tracking and updates
- Location and movement coordination
- Status management (idle, to_pickup, with_passenger, etc.)

#### 3. OrderSystem | 订单系统
- Dynamic order generation based on time patterns
- Intelligent vehicle dispatch algorithms
- Order lifecycle management
- Revenue calculation and tracking

#### 4. ChargingManager | 充电管理器
- Charging station placement and management
- Queue handling for occupied stations
- Smart charging decision algorithms
- Energy consumption tracking

#### 5. MapManager | 地图管理器
- OpenStreetMap data integration
- Shortest path route calculation
- Distance and travel time estimation
- Map visualization preparation

---

## 📊 Data Flow Architecture | 数据流架构

### Python Engine Data Flow | Python引擎数据流

```
YAML Config → ConfigManager → SimulationEngine → Components
     ↓              ↓              ↓             ↓
Load Settings → Initialize → Run Simulation → Update State
     ↓              ↓              ↓             ↓
Validate → Create Objects → Execute Steps → Collect Data
     ↓              ↓              ↓             ↓
Apply → Setup System → Process Events → Export Results
```

### Web System Data Flow | Web系统数据流

```
Browser Request → FastAPI Router → Service Layer → Core Engine
       ↓               ↓              ↓             ↓
HTTP/WS → API Endpoint → Business Logic → Simulation Call
       ↓               ↓              ↓             ↓
Response ← JSON/WebSocket ← Data Processing ← Engine State
       ↓               ↓              ↓             ↓
UI Update ← Real-time Push ← Format Response ← Statistics
```

### Real-time Communication | 实时通信

#### WebSocket Architecture | WebSocket架构
```
Client (Browser)     ←→     WebSocket Server     ←→     Simulation Engine
     │                           │                           │
 UI Components       ←→    Connection Manager    ←→      State Updates
     │                           │                           │
 Event Handlers      ←→    Message Dispatcher    ←→      Data Collection
     │                           │                           │
 Display Updates     ←→    JSON Serialization    ←→      Statistics API
```

---

## 🔧 Configuration Management | 配置管理

### Configuration Hierarchy | 配置层次结构

```
1. Default Configuration | 默认配置
   └── Built-in system defaults
   
2. YAML Configuration Files | YAML配置文件
   ├── default.yaml (standard settings)
   ├── demo.yaml (demonstration settings)
   └── custom.yaml (user-defined settings)
   
3. Runtime Parameters | 运行时参数
   ├── Command line arguments
   └── Environment variables
   
4. Web Interface Settings | Web界面设置
   ├── Real-time parameter adjustment
   └── Session-based configuration
```

### Configuration Validation | 配置验证

```python
# Pydantic-based configuration validation
class SimulationConfig(BaseModel):
    simulation: SimulationSettings
    vehicles: VehicleSettings
    orders: OrderSettings
    charging: ChargingSettings
    visualization: VisualizationSettings
    data: DataSettings
    
    class Config:
        extra = "forbid"  # Prevent unknown fields
        validate_assignment = True  # Validate on assignment
```

---

## 🚀 Deployment Architecture | 部署架构

### Development Environment | 开发环境

```
Local Development
├── Python Virtual Environment
│   ├── Core simulation modules
│   └── Development dependencies
├── FastAPI Development Server
│   ├── uvicorn with auto-reload
│   └── Local file serving
└── Browser-based Testing
    ├── Real-time WebSocket connections
    └── Interactive debugging
```

### Production Considerations | 生产环境考虑

#### Scalability | 可扩展性
- **Horizontal Scaling**: Multiple simulation instances
- **Load Balancing**: WebSocket connection distribution
- **Caching**: Map data and computation results
- **Database Integration**: Persistent simulation data

#### Performance Optimization | 性能优化
- **Async Processing**: Non-blocking simulation execution
- **Memory Management**: Efficient data structure usage
- **Network Optimization**: Compressed WebSocket messages
- **Browser Optimization**: Efficient DOM updates

---

## 📁 Project Structure | 项目结构

### Complete Directory Layout | 完整目录布局

```
EvsSimulation/                    # 项目根目录
│
├── 🐍 Python Simulation Engine   # Python仿真引擎
│   ├── main.py                   # YAML-driven entry point
│   ├── core/                     # Core simulation modules
│   │   ├── __init__.py
│   │   ├── simulation_engine.py  # Main simulation coordinator
│   │   ├── vehicle_manager.py    # Vehicle fleet management
│   │   ├── order_system.py       # Order generation & dispatch
│   │   ├── charging_manager.py   # Charging infrastructure
│   │   └── map_manager.py        # Map data & routing
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   ├── vehicle.py            # Vehicle state & behavior
│   │   ├── order.py              # Order lifecycle
│   │   └── charging_station.py   # Charging station logic
│   ├── config/                   # Configuration system
│   │   ├── __init__.py
│   │   ├── yaml_config_manager.py # YAML configuration handler
│   │   └── simulation_config.py   # Legacy config support
│   ├── visualization/            # Visualization system
│   │   ├── __init__.py
│   │   └── visualizer.py         # Real-time matplotlib display
│   └── yaml_config/              # YAML configuration files
│       ├── default.yaml          # Default configuration
│       ├── west_lafayette_demo.yaml # Demo configuration
│       ├── headless_batch.yaml   # Batch processing config
│       └── templates/            # Configuration templates
│
├── 🌐 Web Application System     # Web应用系统
│   ├── backend/                  # FastAPI backend
│   │   ├── __init__.py
│   │   ├── main.py               # Web server entry point
│   │   ├── api/                  # REST API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── simulation.py     # Simulation control API
│   │   │   ├── data.py           # Data query API
│   │   │   └── config.py         # Configuration API
│   │   ├── websocket/            # Real-time communication
│   │   │   ├── __init__.py
│   │   │   └── simulation_ws.py  # WebSocket handlers
│   │   ├── services/             # Business logic
│   │   │   ├── __init__.py
│   │   │   └── simulation_service.py # Core simulation interface
│   │   ├── models/               # API data models
│   │   │   ├── __init__.py
│   │   │   └── response.py       # Response schemas
│   │   └── requirements.txt      # Backend dependencies
│   ├── frontend/                 # Web interface
│   │   ├── templates/            # HTML templates
│   │   │   ├── index.html        # Main dashboard
│   │   │   ├── vehicles.html     # Vehicle tracking
│   │   │   ├── orders.html       # Order management
│   │   │   ├── charging-stations.html # Infrastructure monitoring
│   │   │   └── config.html       # Configuration panel
│   │   └── static/               # Static assets
│   │       ├── js/               # JavaScript modules
│   │       │   ├── app.js        # Main application logic
│   │       │   ├── websocket.js  # WebSocket client
│   │       │   ├── map.js        # Map controls
│   │       │   ├── charts.js     # Data visualization
│   │       │   ├── vehicles.js   # Vehicle tracking
│   │       │   ├── orders.js     # Order management
│   │       │   └── charging-stations.js # Station monitoring
│   │       └── css/
│   │           └── style.css     # Application styles
│   ├── run.py                    # Alternative startup script (deprecated)
│   └── README.md                 # Web system documentation
│
├── 📁 Shared Resources           # 共享资源
│   ├── data/                     # Data management
│   │   ├── __init__.py
│   │   └── data_manager.py       # Data export and analysis
│   ├── utils/                    # Utility functions
│   │   ├── __init__.py
│   │   ├── geometry.py           # Geometric calculations
│   │   └── path_utils.py         # Path processing utilities
│   ├── datasets/                 # Data storage
│   │   ├── maps/                 # Cached map data
│   │   └── simulation_output/    # Simulation results
│   └── cache/                    # Temporary cache
│
├── 📚 Documentation              # 文档系统
│   ├── README.md                 # Documentation index
│   ├── PROJECT_ARCHITECTURE.md   # This document
│   ├── TECHNICAL_IMPLEMENTATION.md # Technical details
│   ├── API_REFERENCE.md          # Web API documentation
│   ├── DATA_MODELS.md            # Data structure reference
│   ├── WEBAPP_EXPANSION_DESIGN.md # Web system design
│   ├── SYSTEM_MODULES.md         # Module documentation
│   ├── WEBAPP_TROUBLESHOOTING.md # Common issues
│   ├── CODING_PRINCIPLES.md      # Development guidelines
│   └── ARCHITECTURE_DISCUSSION_SUMMARY.md # Design decisions
│
├── 🔧 Project Configuration      # 项目配置
│   ├── requirements.txt          # Python dependencies
│   ├── .gitignore               # Git ignore rules
│   ├── .venv/                   # Virtual environment
│   └── README.md                # Project overview
│
└── 📊 Additional Resources       # 额外资源
    ├── LICENSE                   # Project license
    └── CHANGELOG.md             # Version history (if available)
```

---

## 🔄 Integration Patterns | 集成模式

### Interface Abstraction | 接口抽象

```python
class SimulationInterface:
    """
    Abstract interface for different simulation frontends
    不同仿真前端的抽象接口
    """
    def create_simulation(self, config: dict) -> str:
        """Create new simulation instance"""
        
    def start_simulation(self, sim_id: str) -> bool:
        """Start simulation execution"""
        
    def get_state(self, sim_id: str) -> dict:
        """Get current simulation state"""
        
    def control_simulation(self, sim_id: str, action: str) -> bool:
        """Control simulation (pause/resume/stop)"""
```

### Configuration Adapter | 配置适配器

```python
class ConfigAdapter:
    """
    Converts between different configuration formats
    在不同配置格式之间转换
    """
    @staticmethod
    def yaml_to_legacy(yaml_config: YAMLConfig) -> dict:
        """Convert YAML config to legacy format"""
        
    @staticmethod
    def web_params_to_config(web_params: dict) -> dict:
        """Convert web parameters to simulation config"""
```

---

## 🎯 Design Goals | 设计目标

### Primary Objectives | 主要目标

1. **Flexibility | 灵活性**
   - Support multiple user interfaces and use cases
   - 支持多种用户界面和用例

2. **Maintainability | 可维护性**
   - Clean separation between core logic and presentation
   - 核心逻辑与表示层的清晰分离

3. **Extensibility | 可扩展性**
   - Easy to add new features and interfaces
   - 易于添加新功能和接口

4. **Performance | 性能**
   - Efficient execution for both interactive and batch modes
   - 交互和批处理模式的高效执行

5. **Usability | 可用性**
   - Intuitive interfaces for different user types
   - 为不同用户类型提供直观界面

### Success Metrics | 成功指标

- **Code Reuse**: >90% core logic shared between systems
- **Performance**: <100ms web response times
- **Scalability**: Support for 100+ simultaneous vehicles
- **Maintainability**: Modular architecture with clear interfaces
- **Documentation**: Comprehensive documentation coverage

---

## 🔮 Future Architecture Considerations | 未来架构考虑

### Planned Enhancements | 计划增强

1. **Microservices Architecture | 微服务架构**
   - Separate simulation engine into independent services
   - 将仿真引擎分离为独立服务

2. **Cloud Deployment | 云部署**
   - Container-based deployment with Kubernetes
   - 基于容器的Kubernetes部署

3. **Multi-tenancy | 多租户**
   - Support for multiple concurrent simulations
   - 支持多个并发仿真

4. **Real-time Collaboration | 实时协作**
   - Multiple users interacting with same simulation
   - 多用户与同一仿真交互

5. **Machine Learning Integration | 机器学习集成**
   - AI-powered optimization algorithms
   - AI驱动的优化算法

---

## 📋 Conclusion | 结论

The EV Simulation System's dual architecture successfully balances flexibility, maintainability, and performance. By sharing a common core engine while providing distinct interfaces for different use cases, the system serves both research and demonstration needs effectively.

电动车仿真系统的双架构成功平衡了灵活性、可维护性和性能。通过共享通用核心引擎，同时为不同用例提供不同接口，系统有效地服务于研究和演示需求。

The architecture is designed to evolve with changing requirements while maintaining backward compatibility and ensuring system stability.

该架构旨在随需求变化而发展，同时保持向后兼容性并确保系统稳定性。

---

**Last Updated**: December 2024  
**Document Version**: 3.0  
**Next Review**: As needed for major architectural changes 