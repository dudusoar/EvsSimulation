# Folium 地图仿真动画技术指南

## 概述

本文档记录了在电动车仿真系统中实现Folium地图动画的技术方案和实现细节。

## 技术背景

### 问题描述
用户希望在Folium交互式地图上运行仿真动画，替代或补充现有的matplotlib可视化方案。

### 解决方案
创建独立的Folium动画系统，保持原有OSMnx+NetworkX计算核心不变，使用Folium的TimestampedGeoJson功能实现车辆轨迹动画。

## 技术架构

### 核心组件
- **计算后端**: OSMnx + NetworkX（保持不变）
- **可视化前端**: Folium + TimestampedGeoJson 
- **动画控制**: Leaflet TimeDimension插件
- **数据格式**: GeoJSON FeatureCollection

### 文件结构
```
ui/
├── folium_simulation.py          # 新增Folium仿真演示
├── demo_ui.py                   # 原有DearPyGui演示（保留）
└── hybrid_demo.py               # 混合架构演示（保留）
```

## 实现细节

### 1. 车辆动画实现

使用TimestampedGeoJson创建时间序列地理数据：

```python
# 为每个车辆创建时间序列轨迹
for vehicle_id in all_vehicle_ids:
    vehicle_path = []
    for frame in animation_data:
        # 创建带时间戳的GeoJSON特征
        feature = {
            'type': 'Feature',
            'geometry': {'type': 'Point', 'coordinates': [lon, lat]},
            'properties': {
                'time': timestamp.isoformat(),
                'style': {'color': vehicle_color, 'radius': 8},
                'popup': f"Vehicle {vehicle_id}<br>Status: {status}<br>Battery: {battery}%"
            }
        }
        vehicle_path.append(feature)
```

### 2. 时间控制器配置

```python
# 配置时间维度控制器
timeDimensionControl = L.Control.TimeDimensionCustom({
    "position": "bottomleft",
    "minSpeed": 0.1,
    "maxSpeed": 10,
    "autoPlay": true,
    "loopButton": true,
    "timeSliderDragUpdate": true,
    "speedSlider": true,
    "playerOptions": {
        "transitionTime": 200,
        "loop": true,
        "startOver": true
    }
})
```

### 3. 充电站显示

```python
# 静态充电站标记
folium.Marker(
    location=[lat, lon],
    popup=f"Charging Station {station_id}<br>Power: {power}kW",
    icon=folium.Icon(color='red', icon='plug', prefix='fa')
).add_to(map)
```

## 核心优势

### 1. 高质量可视化
- 原生Web地图，无图像质量损失
- 专业级地图交互体验
- 支持缩放、平移、图层控制

### 2. 强大的动画功能
- 时间轴控制回放
- 速度调节（0.1x - 10x）
- 循环播放支持
- 拖拽时间点跳转

### 3. 系统兼容性
- 保持原有计算核心不变
- 与现有matplotlib方案并存
- 独立运行，互不干扰

## 当前状态

### ✅ 已完成
- [x] 基础Folium动画框架
- [x] 车辆轨迹动画演示
- [x] 充电站静态标记
- [x] 时间控制器集成
- [x] 多车辆并行动画
- [x] 车辆状态颜色编码
- [x] 弹窗信息显示

### 🔄 演示程序运行方式

```bash
# 切换到UI目录
cd ui

# 运行Folium动画演示
python folium_simulation.py

# 自动生成 simulation_animation.html 并在浏览器中打开
```

### 📋 技术特性

1. **车辆动画**
   - 5辆演示车辆，不同颜色
   - 圆形轨迹路径模拟
   - 状态变化动画（可用/载客/充电等）
   - 电池电量显示

2. **地图功能**
   - West Lafayette地区地图
   - 3个充电站标记
   - 缩放平移交互
   - 弹窗详细信息

3. **动画控制**
   - 自动播放
   - 循环模式
   - 速度控制滑块
   - 时间拖拽跳转

## 下一步开发计划

### 🎯 集成真实仿真数据
- 连接现有SimulationEngine
- 从真实车辆路径生成轨迹
- 实时订单状态显示
- 充电站状态更新

### 🔧 功能增强
- 订单pickup/delivery位置标记
- 车辆路径轨迹线显示
- 实时统计面板
- 图层开关控制

### 🎨 界面优化
- 自定义车辆图标
- 状态图例说明
- 性能指标显示
- 响应式布局

## 技术依赖

### 新增依赖
```txt
folium>=0.20.0
seaborn>=0.12.0  # 已添加到requirements.txt
```

### 核心插件
- Leaflet TimeDimension
- FontAwesome图标库
- Bootstrap样式框架

## 文件清单

### 新增文件
- `ui/folium_simulation.py` - Folium动画演示主程序
- `doc/FOLIUM_ANIMATION_GUIDE.md` - 本技术指南

### 修改文件  
- `requirements.txt` - 添加seaborn依赖

### 未修改文件
- `main.py` - 原有仿真主程序（完全保持原样）
- `core/` - 所有仿真引擎文件
- `models/` - 所有数据模型文件
- `visualization/` - 原有可视化文件

## 重要说明

⚠️ **系统安全性**: 原有仿真系统完全未被修改，新的Folium方案作为独立模块存在，确保现有功能不受影响。

💡 **开发建议**: 建议先在演示程序基础上逐步集成真实仿真数据，确保动画性能和用户体验。

---

**文档创建**: 2025-01-01  
**最后更新**: 2025-01-01  
**技术栈**: OSMnx + NetworkX + Folium + TimestampedGeoJson 