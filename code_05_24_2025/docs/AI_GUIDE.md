# AI助手核心指南

🤖 **专为AI助手和用户设计的精简项目指南**

## 🚀 项目概况

**电车司机仿真系统** - Python 3.11+ 高性能仿真项目

- **主程序**: `main.py` (187行)  
- **当前版本**: v2.0.0 (超高性能版)
- **核心功能**: 20辆电车 + 1000订单/小时 + 实时可视化

## ⚡ 快速演示 (推荐新手)

```bash
# 90秒看完整流程 - 立即有效果!
python main.py -v 20 -d 90 --save-data

# 30秒快速测试
python main.py -v 10 -d 30

# 英文可视化版 (推荐)
python main.py -v 8 -d 120 --save-data
```

## 🏗️ 核心模块架构

```
main.py (主控制器)
├── SimulationEngine (协调中心)
│   ├── MapManager        - 地图和路径 (datasets/maps/)
│   ├── VehicleManager    - 车辆管理 (20车 200km/h)
│   ├── OrderSystem       - 订单系统 (1000/小时)
│   ├── ChargingManager   - 充电管理 (5站 快速充电)
│   ├── Visualizer        - 英文可视化 (实时30fps)
│   └── DataManager       - 数据保存 (outputs/)
```

## 📁 关键路径 (v2.0.0)

### 输入数据
- **地图**: `datasets/maps/west_lafayette_in.graphml` ✅
- **配置**: `config/simulation_config.py` (高性能参数)

### 输出数据  
- **仿真结果**: `outputs/simulation_results/run_YYYYMMDD_HHMMSS/`
- **动画**: `outputs/visualizations/ev_simulation_*.html`
- **分析**: `outputs/analysis/`

## ⚙️ 高性能配置 (v2.0.0)

### 核心参数
```python
'vehicle_speed': 200,          # km/h - 最大速度
'order_generation_rate': 1000, # 订单/小时 (每3.6秒1个)
'num_vehicles': 20,            # 车辆数量
'simulation_duration': 3600,   # 仿真时长(秒)
'charging_threshold': 30.0,    # 充电阈值(%)
'initial_orders': 10,          # 预生成订单数 🆕
```

### 预期性能
- **90秒内**: 100%车辆利用率 + ¥50+收入
- **订单完成率**: 30%+
- **车队平均行驶**: 4-5公里

## 💻 模块功能详解

### 1. MapManager (`core/map_manager.py`)
**功能**: 地图加载、路径规划、节点管理
```python
# 主要方法
get_shortest_path_nodes(origin, destination)  # 路径规划
select_charging_station_nodes(n)             # 充电站选择
find_nearest_node(position)                  # 最近节点
```

### 2. VehicleManager 
**功能**: 20辆高速电车管理 (200km/h)
- 状态: idle/to_pickup/with_passenger/charging
- 电量管理: 100%容量, 0.8%/km消耗, 30%阈值充电
- 智能调度: 基于距离和电量分配订单

### 3. OrderSystem
**功能**: 超高频订单生成和分配
- **预生成**: 启动即有10个初始订单 🆕
- **高频生成**: 1000订单/小时 (每3.6秒1个)
- **智能分配**: 最近距离 + 电量考虑
- **生命周期**: 生成→分配→接客→完成

### 4. ChargingManager
**功能**: 5个充电站快速充电管理
- 每站3个充电位
- 充电速率: 2.0%/秒 (快速充电)
- 智能排队和调度

### 5. Visualizer (`visualization/visualizer.py`)
**功能**: 英文实时可视化 (解决字体问题)
- **英文界面**: 完全兼容
- **小标识**: 与地图协调
- **订单显示**: 起点+终点+编号同时显示
- **实时统计**: 收入、利用率等动态更新

### 6. DataManager (`data/data_manager.py`)
**功能**: 数据保存和报告生成
```python
# 保存到 outputs/simulation_results/
- final_statistics.json    # 最终统计
- time_series.csv         # 时间序列数据
- vehicle_details.csv     # 车辆详情
- simulation_report.md    # 自动报告
```

## 🎯 数据结构速查

### 车辆状态
```python
vehicle = {
    'vehicle_id': str,
    'position': (x, y),
    'status': 'idle'|'to_pickup'|'with_passenger'|'charging',
    'battery_percentage': float,  # 0-100
    'current_task': dict
}
```

### 订单数据
```python
order = {
    'order_id': str,
    'pickup_position': (x, y),
    'dropoff_position': (x, y), 
    'status': 'pending'|'assigned'|'completed',
    'creation_time': float
}
```

## 🛠️ 开发规范

### 命名约定
```python
# 变量/函数: snake_case
vehicle_manager = VehicleManager()
def get_nearest_vehicle():

# 类名: PascalCase  
class SimulationEngine:

# 常量: UPPER_SNAKE_CASE
SIMULATION_DURATION = 3600
```

### 导入顺序
```python
# 1. 标准库
import os, sys
from typing import Dict, List

# 2. 第三方库
import numpy as np
import matplotlib.pyplot as plt

# 3. 本地模块
from config.simulation_config import SIMULATION_CONFIG
```

## 🚨 故障排查

### 常见问题
1. **车辆不移动** → 检查路径规划 `get_shortest_path_nodes()`
2. **订单不生成** → 确认 `order_generation_rate` 和初始订单
3. **可视化空白** → 检查matplotlib后端和字体设置
4. **路径错误** → 确认 `datasets/maps/west_lafayette_in.graphml` 存在
5. **性能缓慢** → 检查车辆数量和订单频率设置

### 调试命令
```python
# 检查车辆状态
print(f"车辆位置: {vehicle.position}")
print(f"电量: {vehicle.battery_percentage}%")

# 验证路径
assert os.path.exists("datasets/maps/west_lafayette_in.graphml")

# 检查配置
print(f"订单生成率: {config['order_generation_rate']}")
```

## 📚 重要文档速查

### 必读文档
- **[快速参考](specs/quick_reference.md)** - 详细配置和命令
- **[更新日志](logs/updates/changelog.md)** - v2.0.0变更记录
- **[代码规范](specs/code_conventions.md)** - 编码风格

### 数据说明
- **[输入数据组织](../datasets/README.md)** - datasets目录说明
- **[输出结果管理](../outputs/README.md)** - outputs目录说明

### 项目设计
- **[项目文档v1](project_docs/v1/项目文档_v1.md)** - 初始设计
- **[项目文档v2](project_docs/v2/项目文档_v2.md)** - 当前设计

## 🎯 AI助手工作流程

### 开始工作
1. 查看本指南获取项目概况
2. 检查更新日志了解最新变更  
3. 确认数据路径和配置参数

### 编写代码
1. 遵循命名规范和导入顺序
2. 使用标准数据结构格式
3. 保持与现有模块的一致性

### 调试问题
1. 先检查常见问题列表
2. 使用调试命令验证状态
3. 查看仿真日志获取详细信息

### 更新文档
1. 重大变更更新changelog
2. 配置变更更新quick_reference
3. 新功能更新本指南

---

**最后更新**: 2025-05-24  
**版本**: v2.0.0 高性能仿真版 🚀  
**🤖 AI助手 + 👨‍💻 用户友好设计** 