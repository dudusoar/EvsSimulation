# DearPyGui仿真界面安装指南

## 依赖安装

### 1. 安装DearPyGui
```bash
pip install dearpygui
```

### 2. 安装其他依赖
```bash
pip install matplotlib numpy pillow
```

### 3. 验证安装
```bash
python -c "import dearpygui.dearpygui as dpg; print('DearPyGui版本:', dpg.get_dearpygui_version())"
```

## 运行演示

### 1. 基础演示
```bash
cd ui
python demo_ui.py
```

### 2. 完整界面（需要完整仿真系统）
```bash
cd ui  
python dearpygui_interface.py
```

## 界面功能说明

### 参数控制面板
- **仿真时长**: 300-7200秒可调
- **车辆数量**: 5-50辆
- **充电站数量**: 3-20个
- **车辆速度**: 5-30 m/s
- **电池容量**: 40-100 kWh
- **地图位置**: 支持多个城市选择

### 地图显示区域
- 实时显示车辆、充电站位置
- 缩放控制功能
- 地图状态监控

### 指标监控面板
- **仿真进度**: 进度条和时间显示
- **车队状态**: 车辆数量、电池状态、利用率
- **订单管理**: 待处理、进行中、已完成订单
- **财务指标**: 总收入、时收入统计

### 仿真控制面板
- **开始/暂停/停止**: 完整的仿真控制
- **重置功能**: 恢复初始状态
- **速度控制**: 0.1x-10x倍速调节

## 技术特性

### GPU加速渲染
- 支持百万级数据点实时显示
- 60fps流畅动画效果
- 硬件加速图形处理

### 响应式设计
- 自适应窗口大小
- 灵活的布局系统
- 现代化UI风格

### 多线程架构
- 主线程处理UI交互
- 后台线程运行仿真
- 实时数据更新机制

## 系统要求

### 最低配置
- Python 3.7+
- 2GB RAM
- 支持OpenGL 3.0的显卡

### 推荐配置
- Python 3.9+
- 4GB+ RAM
- 独立显卡
- 1920x1080分辨率

## 常见问题

### Q: DearPyGui安装失败
A: 确保Python版本>=3.7，尝试使用pip升级：
```bash
pip install --upgrade pip
pip install dearpygui
```

### Q: 界面显示异常
A: 检查显卡驱动和OpenGL支持：
```bash
python -c "import dearpygui.dearpygui as dpg; dpg.create_context(); print('OpenGL支持正常')"
```

### Q: 中文字符显示问题
A: 确保系统支持UTF-8编码，或在代码中设置字体：
```python
dpg.add_font("path/to/chinese_font.ttf", 16)
```

### Q: 性能优化建议
A: 
- 减少实时更新频率
- 使用纹理缓存
- 限制同时显示的数据点数量

## 开发指南

### 集成现有系统
1. 导入现有的仿真模块
2. 实现数据接口转换
3. 配置地图显示参数
4. 测试完整功能

### 自定义主题
```python
with dpg.theme() as custom_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (30, 30, 30))
        dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 6)
```

### 扩展功能
- 添加新的图表类型
- 集成更多地图控制
- 实现数据导出功能
- 增加配置保存/加载

## 支持与反馈

如有问题或建议，请联系开发团队或提交Issue。 