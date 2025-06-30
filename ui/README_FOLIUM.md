# Folium 地图仿真动画 - 快速启动指南

## 🚀 快速运行

### 1. 环境准备
```bash
# 确保在项目根目录
cd EvsSimulation

# 激活虚拟环境
# Windows: evs_simulation_env\Scripts\activate
# macOS/Linux: source evs_simulation_env/bin/activate

# 安装依赖（如果还没装）
uv pip install -r requirements.txt
```

### 2. 运行演示
```bash
# 切换到UI目录
cd ui

# 运行Folium动画演示
python folium_simulation.py
```

### 3. 查看结果
- 程序会自动生成 `simulation_animation.html`
- 自动在浏览器中打开动画地图
- 可以看到5辆车在West Lafayette地图上移动

## 🎮 动画控制

### 界面元素
- **播放/暂停按钮**: 控制动画播放
- **速度滑块**: 调节播放速度（0.1x - 10x）
- **时间轴**: 拖拽跳转到指定时间点
- **循环按钮**: 开启/关闭循环播放

### 车辆颜色说明
- 🔵 蓝色: 可用状态
- 🟢 绿色: 载客状态  
- 🟠 橙色: 前往接客
- 🟣 紫色: 前往充电
- 🔷 深蓝: 其他状态

### 充电站
- 🔴 红色插头图标: 充电站位置
- 点击可查看详细信息

## 📋 技术说明

### 当前演示特性
- ✅ 5辆车辆动画轨迹
- ✅ 充电站静态标记
- ✅ 车辆状态颜色编码
- ✅ 电池电量显示
- ✅ 时间轴控制
- ✅ 地图交互功能

### 核心技术
- **地图**: Folium + OpenStreetMap
- **动画**: TimestampedGeoJson
- **控制**: Leaflet TimeDimension
- **数据**: GeoJSON格式

## 🔧 下一步开发

### 集成真实数据
当前是演示数据，下一步可以：
1. 连接真实的SimulationEngine
2. 使用真实车辆轨迹
3. 显示真实订单数据
4. 实时充电站状态

### 代码修改位置
主要修改 `folium_simulation.py` 中的：
- `create_demo_animation()` → `create_real_simulation()`
- 连接到现有的core模块

## 📁 文件说明

- `folium_simulation.py` - 主程序
- `simulation_animation.html` - 生成的动画地图
- `simulation_data.json` - 仿真数据（如果生成）

## ⚠️ 重要提醒

- 原有 `main.py` 仿真系统完全没有修改
- 两套可视化方案可以并行使用
- Folium方案是独立的新增功能

---

**最后更新**: 2025-01-01  
**运行环境**: Python 3.11 + Folium + OSMnx 