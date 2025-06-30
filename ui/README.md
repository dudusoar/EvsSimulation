# DearPyGui仿真界面框架设计

## 概述

基于DearPyGui的电动车仿真系统UI框架，实现参数控制、实时地图显示和指标监控三大核心功能。

## 框架特点

### 1. 现代化UI设计
- GPU加速渲染，支持百万级数据实时显示
- 响应式布局，自适应不同分辨率
- 主题定制，提供暗色和亮色模式
- 矢量图标和现代化控件

### 2. 三面板架构

#### 左侧：参数控制面板 (300px)
- **基础参数配置**
  - 仿真时长：300-7200秒可调
  - 车辆数量：5-50辆
  - 充电站数量：3-20个
  
- **车辆配置**
  - 行驶速度：5-30 m/s
  - 电池容量：40-100 kWh
  - 充电功率：25-150 kW
  
- **地图选择**
  - West Lafayette, Indiana（默认）
  - New York City, NY
  - San Francisco, CA

#### 中央：地图显示区域 (800px)
- **实时地图渲染**
  - OSMnx地图集成显示
  - matplotlib → DearPyGui纹理转换
  - 车辆、充电站、订单位置实时更新
  
- **地图控制工具**
  - 缩放控制（放大/缩小）
  - 视图重置
  - 手动刷新

#### 右侧：指标监控面板 (300px)
- **仿真进度**
  - 进度条显示
  - 时间计数器（HH:MM:SS格式）
  
- **车队状态**
  - 活跃车辆数量
  - 平均电池电量
  - 车辆利用率
  
- **订单管理**
  - 待处理订单
  - 进行中订单
  - 已完成订单
  
- **财务指标**
  - 总收入
  - 每小时收入

#### 底部：仿真控制面板
- **主控制按钮**
  - ▶️ 开始/暂停
  - ⏹️ 停止
  - 🔄 重置
  
- **速度控制**
  - 0.1x - 10x倍速调节

## 技术实现

### 地图集成方案
```python
# OSMnx matplotlib → DearPyGui纹理转换
def update_map_texture(self):
    canvas = FigureCanvasAgg(self.map_figure)
    canvas.draw()
    buf = canvas.buffer_rgba()
    img_array = np.frombuffer(buf, dtype=np.uint8)
    # 转换为DearPyGui纹理格式
```

### 多线程架构
- **主线程**：UI渲染和用户交互
- **仿真线程**：后台运行仿真计算
- **更新线程**：定期更新UI指标显示

### 状态管理
```python
# 仿真状态控制
self.is_running = False    # 仿真运行状态
self.is_paused = False     # 暂停状态
self.simulation_thread     # 仿真线程对象
```

## 与现有系统集成

### 保持OSMnx后端不变
- 继续使用OSMnx进行图计算
- matplotlib仅作为中间渲染层
- NetworkX路径计算逻辑完全保留

### 增强可视化能力
```python
# 利用OSMnx绘图参数实现精细控制
ox.plot_graph(G, 
    node_color='red',           # 节点颜色
    node_size=50,              # 节点大小
    edge_color='blue',         # 边线颜色
    edge_linewidth=2,          # 线宽
    figsize=(10, 10)           # 图形尺寸
)
```

## 位置精度保证

### 像素级坐标映射
- OSMnx坐标 → matplotlib坐标 → DearPyGui像素
- 图标尺寸自适应缩放级别
- 交互点击坐标反向映射

### 图标尺寸管理
```python
# 根据地图缩放级别调整图标大小
icon_size = base_size * zoom_factor
# 确保最小/最大尺寸限制
icon_size = max(min_size, min(icon_size, max_size))
```

## 安装与使用

### 依赖安装
```bash
pip install dearpygui
pip install matplotlib
pip install numpy
pip install pillow
```

### 运行界面
```bash
cd ui
python dearpygui_interface.py
```

## 扩展功能规划

### 高级控件
- 热力图显示（订单密度、车辆分布）
- 路径轨迹动画
- 统计图表集成（ImPlot）

### 数据导出
- 仿真结果导出
- 截图保存
- 配置参数保存/加载

### 性能优化
- 地图瓦片缓存
- 增量更新机制
- GPU加速渲染

## 总结

这个DearPyGui框架设计完美符合您的需求：

1. ✅ **保持OSMnx核心**：所有图计算和路径规划逻辑不变
2. ✅ **精确位置显示**：像素级坐标映射，图标尺寸自适应
3. ✅ **完整UI面板**：参数控制、仿真控制、指标显示
4. ✅ **暂停/倍速支持**：多线程架构，完整的仿真控制
5. ✅ **现代化界面**：GPU加速，响应式设计

这个方案既满足了技术需求，又提供了优秀的用户体验，是当前最佳的解决方案。 