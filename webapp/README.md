# 🌐 EV仿真系统 - Web应用架构

## 📋 项目概述

这是EV仿真系统的Web应用版本，提供现代化的前后端分离架构：
- 🖥️ **后端**: FastAPI + WebSocket (Python)
- 🌐 **前端**: HTML5 + JavaScript + Leaflet地图
- 🔄 **实时通信**: WebSocket实时数据推送
- 🎛️ **交互控制**: 可操作的控制面板

## 🏗️ 架构设计

```
webapp/
├── backend/                 # 🐍 Python后端
│   ├── api/                # 📡 REST API接口
│   │   ├── __init__.py
│   │   ├── simulation.py   # 仿真控制API
│   │   └── data.py         # 数据查询API
│   ├── websocket/          # 🔄 WebSocket实时通信
│   │   ├── __init__.py
│   │   └── simulation_ws.py
│   ├── models/             # 📝 数据模型
│   │   ├── __init__.py
│   │   └── response.py
│   ├── services/           # 🛠️ 业务逻辑
│   │   ├── __init__.py
│   │   └── simulation_service.py
│   ├── main.py             # 🚀 FastAPI应用入口
│   └── requirements.txt    # 📦 后端依赖
│
├── frontend/               # 🌐 前端应用
│   ├── static/            # 📁 静态资源
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   ├── app.js      # 主应用逻辑
│   │   │   ├── map.js      # 地图控制
│   │   │   ├── websocket.js # WebSocket客户端
│   │   │   └── charts.js   # 图表组件
│   │   └── images/
│   └── templates/          # 📄 HTML模板
│       ├── index.html      # 主页面
│       └── dashboard.html  # 控制面板
│
├── README.md              # 📖 项目文档
└── docker-compose.yml     # 🐳 容器化部署(可选)
```

## ✨ 功能特性

### 🎛️ **控制面板**
- ⏯️ 启动/暂停/停止仿真
- ⚡ 调整仿真速度 (0.1x ~ 10x)
- ➕ 动态添加车辆/充电站
- 📊 实时参数调整

### 🗺️ **交互地图**
- 🚗 实时车辆位置和状态
- ⚡ 充电站使用情况
- 📍 订单接送点
- 🛣️ 路径跟踪
- 👆 点击交互 (查看详情、手动派单)

### 📈 **实时监控**
- 💰 收入/成本/利润图表
- 🔋 车辆电量监控
- 📦 订单完成率
- 🚦 系统性能指标

### 🔄 **数据同步**
- WebSocket实时数据推送
- 多用户同步观看
- 低延迟更新 (<100ms)

## 🚀 快速启动

### 推荐启动方式
```bash
# 在项目根目录运行（激活虚拟环境后）
.venv\Scripts\Activate.ps1
uvicorn webapp.backend.main:app --host 127.0.0.1 --port 8080 --reload
```

### 备用启动方式
```bash
# 1. 安装依赖
pip install -r webapp/backend/requirements.txt

# 2. 启动服务器（在项目根目录）
uvicorn webapp.backend.main:app --host 127.0.0.1 --port 8080 --reload
```

### 3. 访问应用
- **主界面**: http://127.0.0.1:8080
- **API文档**: http://127.0.0.1:8080/docs
- **WebSocket**: ws://127.0.0.1:8080/ws/simulation

## 🔧 技术栈

### 后端
- **FastAPI** - 现代Python Web框架
- **WebSocket** - 实时双向通信
- **Uvicorn** - ASGI服务器
- **Pydantic** - 数据验证

### 前端
- **Leaflet** - 开源地图库
- **Chart.js** - 数据可视化
- **Bootstrap** - UI框架
- **原生JavaScript** - 无框架依赖

## 🔗 与现有系统集成

该Web应用通过服务层调用现有的仿真引擎：

```python
# webapp/backend/services/simulation_service.py
from core.simulation_engine import SimulationEngine  # 复用现有引擎
from config.simulation_config import SIMULATION_CONFIG  # 复用现有配置
```

**✅ 完全不影响现有代码结构！**

## 📝 开发计划

### Phase 1: 基础框架 (1-2天)
- [ ] FastAPI后端基础架构
- [ ] WebSocket实时通信
- [ ] 基础前端页面

### Phase 2: 核心功能 (2-3天)  
- [ ] 地图集成和车辆显示
- [ ] 控制面板实现
- [ ] 实时数据同步

### Phase 3: 增强功能 (2-3天)
- [ ] 交互操作
- [ ] 图表和监控
- [ ] 性能优化

**预计总开发时间: 5-8天**

## 📖 使用指南

### 基本操作流程

1. **启动应用**: 运行 `python webapp/run.py`
2. **访问界面**: 浏览器打开 http://localhost:8000
3. **创建仿真**: 
   - 设置车辆数量和仿真时长
   - 点击"Create Simulation"按钮
4. **控制仿真**: 
   - 点击"Start"开始仿真
   - 使用"Pause"/"Resume"控制暂停/继续
   - 拖动速度滑块调整仿真速度
5. **观察结果**: 
   - 地图实时显示车辆移动
   - 左侧面板显示实时统计
   - 下方图表显示趋势分析

### 功能说明

#### 🎛️ 控制面板
- **Location**: 仿真城市（默认West Lafayette）
- **Vehicles**: 车辆数量（1-50）
- **Duration**: 仿真时长（60-3600秒）
- **Speed**: 仿真速度倍数（0.1x-5.0x）

#### 🗺️ 交互地图
- **绿色圆点**: 空闲车辆
- **蓝色圆点**: 前往接客车辆
- **橙色圆点**: 载客车辆
- **红色圆点**: 前往充电车辆
- **紫色圆点**: 充电中车辆
- **大绿圆**: 充电站
- **小蓝点**: 订单上车点
- **小红点**: 订单下车点

#### 📊 实时统计
- **Time**: 当前仿真时间
- **Revenue**: 总收入
- **Orders**: 完成订单数
- **Vehicle Util.**: 车辆利用率
- **Charging Util.**: 充电站利用率

## 🔧 开发者指南

### API 端点
- `POST /api/simulation/create` - 创建仿真
- `POST /api/simulation/control` - 控制仿真
- `GET /api/simulation/status` - 获取状态
- `GET /api/data/vehicles` - 获取车辆数据
- `WebSocket /ws/simulation` - 实时数据推送

### ⚠️ 重要提醒
**必须在项目根目录使用uvicorn命令启动**，不要使用run.py脚本！
```bash
# ✅ 正确方式（在项目根目录）
uvicorn webapp.backend.main:app --host 127.0.0.1 --port 8080 --reload

# ❌ 错误方式（会找不到模块）
python webapp/run.py
```

### 前端组件
- `app.js` - 主应用逻辑
- `websocket.js` - WebSocket通信
- `map.js` - 地图控制
- `charts.js` - 图表显示

### 后端服务
- `simulation_service.py` - 仿真服务层
- `api/` - REST API路由
- `websocket/` - WebSocket处理 