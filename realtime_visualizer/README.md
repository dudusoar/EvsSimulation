# Real-time Visualization System

## 🚀 Quick Start

### 方式一：通过主程序启动（推荐）

```bash
# 启动实时可视化系统（默认West Lafayette）
python main.py --realtime

# 指定曼哈顿 + 30辆车
python main.py --realtime -l "Manhattan, New York" -v 30

# 指定北京 + 50辆车
python main.py --realtime -l "Beijing, China" -v 50
```

### 方式二：直接启动模块

```bash
# 进入模块目录
cd realtime_visualizer

# 启动服务器
python realtime_visualizer.py
```

## 📱 使用界面

启动后会看到：
```
🚀 Starting Real-time Visualization System...
============================================================
Configuration:
- Location: Manhattan, New York
- Vehicles: 30
- Mode: Real-time Interactive Visualization

📡 Services will be available at:
   Frontend: http://localhost:8080
   WebSocket: ws://localhost:8765

Press Ctrl+C to stop the server
============================================================
```

**然后用浏览器打开：http://localhost:8080**

## 🎮 控制功能

### 仿真控制
- **▶ Start**: 开始仿真
- **⏸ Pause**: 暂停仿真  
- **▶ Resume**: 恢复仿真
- **🔄 Reset**: 重置仿真

### 速度控制
- 滑动条调节：0.1x - 10x速度
- 快捷按钮：1x, 2x, 5x, 10x

### 实时信息
- **统计面板**: 车辆数、订单状态、收入、电池状态
- **地图标记**: 
  - 🟢 可用车辆
  - 🟠 接客中车辆  
  - 🔵 服务中车辆
  - 🔴 充电中车辆
  - 🟡 待处理订单
- **详情查看**: 点击车辆/订单查看详细信息

### 快捷键
- **空格键**: 播放/暂停切换
- **Ctrl+R**: 重置仿真
- **ESC**: 关闭详情面板

## 🔧 技术架构

```
浏览器界面 ←→ WebSocket ←→ 仿真引擎
   (8080)        (8765)        (后台)
```

- **前端**: 现代化Web界面，Leaflet.js地图
- **通信**: WebSocket实时双向通信
- **后端**: Python异步服务器
- **数据**: 实时流传输，无需存储

## 🆚 对比传统方式

| 特性 | 传统方式 | 实时可视化 |
|------|----------|------------|
| 交互性 | 无 | 完全交互 |
| 控制 | 预设参数 | 实时调节 |
| 存储 | 大量frame文件 | 无需存储 |
| 速度 | 固定 | 动态调节 |
| 反馈 | 结束后 | 实时显示 |

## ⚠️ 依赖安装

如果遇到错误，请安装依赖：

```bash
pip install websockets>=11.0.0 aiohttp>=3.8.0
```

## 🐛 故障排除

### 端口被占用
```bash
# 查看端口占用
netstat -ano | findstr :8080
netstat -ano | findstr :8765

# 更换端口（修改realtime_visualizer.py中的端口号）
```

### 浏览器无法连接
1. 确认服务器已启动
2. 检查防火墙设置
3. 尝试刷新页面
4. 查看浏览器控制台错误

### WebSocket连接失败
- 等待几秒后会自动重连
- 检查终端是否有错误信息
- 确认WebSocket服务正常运行 