# 快速参考手册

AI助手和用户的核心配置速查表。

## ⚙️ 核心配置参数 (v2.0.0)

### 仿真基础
```python
SIMULATION_CONFIG = {
    'simulation_duration': 3600,    # 秒 - 仿真时长
    'time_step': 0.1,              # 秒 - 时间步长
    'location': "West Lafayette, IN",  # 仿真地点
}
```

### 车辆参数 (高性能优化)
```python
'num_vehicles': 20,            # 车辆数量
'vehicle_speed': 200,          # km/h - 最大速度 (大幅提升!)
'battery_capacity': 100.0,     # % - 电池容量
'energy_consumption': 0.8,     # %/km - 耗电率 (快速消耗)
'charging_threshold': 30.0,    # % - 充电阈值 (提高触发)
'charging_rate': 2.0,          # %/秒 - 充电速率 (加快充电)
```

### 订单参数 (超高频生成)
```python
'order_generation_rate': 1000, # 订单/小时 (每3.6秒一个!)
'base_price_per_km': 2.0,      # 元/km - 基础价格
'initial_orders': 10,          # 预生成初始订单数量 🆕
'max_waiting_time': 600,       # 最大等待时间（秒）
```

### 充电站参数
```python
'num_charging_stations': 5,       # 充电站数量
'charging_slots_per_station': 3,  # 每站充电位数量
'charging_power': 50,             # 充电功率（kW）
'electricity_price': 0.8,         # 电价（元/kWh）
```

### 可视化参数
```python
'enable_animation': True,         # 是否启用动画
'animation_fps': 30,              # 动画帧率
'show_preview': False,            # 是否显示预览
'save_animation': True,           # 是否保存动画
'animation_format': 'html',       # 动画格式
```

### 数据管理
```python
'save_data': True,                # 是否保存数据
'output_dir': 'outputs/simulation_results'  # 输出目录
```

## 🔧 常用命令

### 快速演示 (推荐)
```bash
# 高性能demo - 立即看效果!
python main.py -v 20 -d 90 --save-data

# 超快速测试 - 30秒看完整流程
python main.py -v 10 -d 30

# 英文可视化版
python main.py -v 8 -d 120 --save-data
```

### 基础运行
```bash
# 默认配置 (20车,1000订单/小时)
python main.py

# 指定参数
python main.py -v 30 -d 300 --headless

# 保存数据和报告
python main.py --save-data --report --excel
```

### 命令行参数速查
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `-l, --location` | str | West Lafayette, IN | 仿真位置 |
| `-v, --vehicles` | int | 20 | 车辆数量 |
| `-d, --duration` | int | 3600 | 仿真时长(秒) |
| `--headless` | flag | False | 无可视化模式 |
| `--save-data` | flag | False | 保存仿真数据 |
| `--report` | flag | False | 生成报告 |
| `-f, --format` | str | html | 动画格式 |

## 🎯 核心数据结构

### 车辆状态
```python
VEHICLE_STATUS = {
    'IDLE': 'idle',                        # 空闲
    'TO_PICKUP': 'to_pickup',              # 前往接客
    'WITH_PASSENGER': 'with_passenger',     # 载客中
    'TO_CHARGING': 'to_charging',          # 前往充电
    'CHARGING': 'charging'                 # 充电中
}
```

### 订单状态
```python
ORDER_STATUS = {
    'PENDING': 'pending',              # 等待分配
    'ASSIGNED': 'assigned',            # 已分配
    'PICKED_UP': 'picked_up',          # 已接客
    'COMPLETED': 'completed',          # 已完成
    'CANCELLED': 'cancelled'           # 已取消
}
```

### 颜色配置
```python
COLORS = {
    'vehicle': {
        'idle': 'blue',
        'to_pickup': 'yellow', 
        'with_passenger': 'green',
        'to_charging': 'orange',
        'charging': 'red'
    },
    'order': {
        'pickup': 'cyan',
        'dropoff': 'magenta'
    },
    'charging_station': 'red'
}
```

## 📂 关键路径速查

### 输入数据位置
- **地图数据**: `datasets/maps/west_lafayette_in.graphml` ✅
- **配置文件**: `config/simulation_config.py`

### 输出数据位置
- **仿真结果**: `outputs/simulation_results/run_YYYYMMDD_HHMMSS/`
- **可视化**: `outputs/visualizations/ev_simulation_*.html`
- **分析结果**: `outputs/analysis/`
- **最终报告**: `outputs/exports/`

## 🚨 故障排查速查

### 常见问题
1. **车辆不移动** → 检查路径规划和目标设置
2. **订单不生成** → 确认 `order_generation_rate` 参数
3. **可视化空白** → 检查matplotlib后端
4. **文件找不到** → 检查 `datasets/maps/` 路径
5. **性能缓慢** → 降低车辆数或订单频率

### 调试技巧
```python
# 验证配置
assert 'simulation_duration' in SIMULATION_CONFIG
assert os.path.exists("datasets/maps/west_lafayette_in.graphml")

# 检查车辆状态
print(f"车辆位置: {vehicle.position}")
print(f"电量: {vehicle.battery_percentage}%")

# 验证订单生成
print(f"订单生成率: {config['order_generation_rate']}")
```

## 📊 性能指标 (v2.0.0)

### 预期表现
- **90秒内**: 100%车辆利用率 + ¥50+收入
- **订单完成率**: 30%+  
- **车队平均行驶**: 4-5公里
- **充电站利用率**: 60%+

### 关键模块
- **MapManager**: 路径缓存在 `datasets/maps/`
- **DataManager**: 输出到 `outputs/simulation_results/`
- **Visualizer**: 动画保存到 `outputs/visualizations/`

---

**最后更新**: 2025-05-24  
**版本**: v2.0.0 - 高性能仿真版本 🚀