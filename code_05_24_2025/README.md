# 电车司机仿真系统

一个基于真实地图数据的电动车辆运营仿真系统，模拟电动车辆在城市中接送乘客、充电和调度的完整过程。

## 功能特性

- **真实地图支持**：基于OpenStreetMap数据，支持全球任意城市
- **完整业务流程**：订单生成、车辆调度、路径规划、充电管理
- **实时可视化**：动态展示车辆位置、订单状态、充电站使用情况
- **详细统计分析**：收入统计、车辆利用率、充电效率等关键指标
- **灵活配置**：支持自定义车辆数量、充电站位置、订单生成率等参数

## 系统架构

```
ev-simulation/
├── config/              # 配置模块
│   └── simulation_config.py
├── core/                # 核心业务模块
│   ├── map_manager.py   # 地图管理
│   ├── vehicle_manager.py # 车辆管理
│   ├── order_system.py  # 订单系统
│   ├── charging_manager.py # 充电管理
│   └── simulation_engine.py # 仿真引擎
├── models/              # 数据模型
│   ├── vehicle.py       # 车辆模型
│   ├── order.py         # 订单模型
│   └── charging_station.py # 充电站模型
├── utils/               # 工具函数
│   ├── geometry.py      # 几何计算
│   └── path_utils.py    # 路径处理
├── visualization/       # 可视化模块
│   └── visualizer.py
├── data/                # 数据管理
│   └── data_manager.py
└── main.py              # 主程序入口
```

## 安装说明

### 1. 环境要求

- Python 3.8+
- pip 包管理器

### 2. 安装依赖

```bash
# 克隆项目
git clone <项目地址>
cd ev-simulation

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. FFmpeg安装（可选，用于生成MP4）

- **Windows**: 下载并安装 [FFmpeg](https://ffmpeg.org/download.html)
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt-get install ffmpeg`

## 快速开始

### 基本使用

```bash
# 使用默认配置运行
python main.py

# 指定地点运行
python main.py -l "Beijing, China"

# 自定义参数
python main.py -l "Shanghai, China" -v 30 -d 1800
```

### 命令行参数

```
基本参数:
  -l, --location TEXT      仿真地点（默认: West Lafayette, IN）
  -v, --vehicles INT       车辆数量（默认: 20）
  -d, --duration INT       仿真时长，单位秒（默认: 3600）
  -c, --config FILE        自定义配置文件路径

输出参数:
  -o, --output TEXT        输出文件名（不含扩展名）
  -f, --format {html,mp4}  动画格式（默认: html）

运行模式:
  --headless              无头模式（无可视化）
  --no-animation          禁用动画生成

数据保存:
  --save-data             保存仿真数据
  --report                生成仿真报告
  --excel                 导出Excel文件
```

### 示例命令

```bash
# 1. 快速测试（10辆车，5分钟）
python main.py -v 10 -d 300

# 2. 生成北京地区的仿真报告
python main.py -l "Beijing, China" -v 50 -d 3600 --save-data --report

# 3. 批量仿真（无可视化）
python main.py --headless -v 100 -d 7200 --save-data --excel

# 4. 生成MP4视频
python main.py -f mp4 -o beijing_simulation

# 5. 使用自定义配置
python main.py -c my_config.json
```

## 配置说明

### 默认配置参数

```python
# 地图参数
location = "West Lafayette, IN"  # 仿真地点

# 车辆参数
num_vehicles = 20               # 车辆数量
vehicle_speed = 50              # 车速（km/h）
battery_capacity = 100.0        # 电池容量（%）
energy_consumption = 0.2        # 能耗率（%/km）
charging_threshold = 20.0       # 充电阈值（%）

# 订单参数
order_generation_rate = 5       # 订单生成率（订单/小时）
base_price_per_km = 2.0        # 基础价格（元/km）

# 充电站参数
num_charging_stations = 5       # 充电站数量
charging_rate = 1.0            # 充电速率（%/秒）
electricity_price = 0.8        # 电价（元/kWh）
```

### 自定义配置文件

创建 `custom_config.json`:

```json
{
    "location": "Tokyo, Japan",
    "num_vehicles": 50,
    "num_charging_stations": 10,
    "order_generation_rate": 10,
    "simulation_duration": 7200
}
```

## 输出说明

### 1. 动画文件

- **HTML格式**：可在浏览器中直接打开，支持交互
- **MP4格式**：标准视频文件，可用任意播放器观看

### 2. 数据文件

仿真结果保存在 `simulation_output/run_[时间戳]/` 目录下：

- `final_statistics.json` - 最终统计数据
- `vehicle_details.csv` - 车辆详细数据
- `station_details.csv` - 充电站详细数据
- `simulation_report.md` - 仿真报告
- `simulation_results.xlsx` - Excel汇总文件

### 3. 统计图表

- `vehicle_statistics.png` - 车辆统计分布图
- `charging_station_revenue.png` - 充电站收入对比图

## 系统特性

### 1. 智能调度算法

- 就近分配原则：优先分配距离最近的空闲车辆
- 电量考虑：低电量车辆不参与订单分配
- 充电时机：空闲时自动前往最近充电站

### 2. 真实路径规划

- 基于实际道路网络的最短路径算法
- 考虑道路长度的精确距离计算
- 平滑的路径跟踪和车辆移动

### 3. 动态定价机制

- 基础价格：按公里计费
- 高峰时段：早晚高峰自动提价
- 供需平衡：可扩展的动态定价策略

### 4. 充电管理

- 分布式充电站：自动选择最优位置
- 排队机制：充电位满时等待
- 智能充电：低电量自动寻找充电站

## 扩展开发

### 添加新的调度策略

在 `core/order_system.py` 中修改 `find_best_vehicle_for_order` 方法：

```python
def find_best_vehicle_for_order(self, order_id: str, available_vehicles: List[Vehicle]) -> Optional[Vehicle]:
    # 实现你的调度算法
    pass
```

### 自定义充电策略

在 `core/charging_manager.py` 中修改 `should_vehicle_charge` 方法：

```python
def should_vehicle_charge(self, vehicle: Vehicle) -> bool:
    # 实现你的充电决策逻辑
    pass
```

### 添加新的统计指标

在 `core/simulation_engine.py` 的 `get_final_statistics` 方法中添加：

```python
stats['custom_metric'] = calculate_custom_metric()
```

## 注意事项

1. **地图数据**：首次运行会从OpenStreetMap下载地图数据，需要网络连接
2. **缓存机制**：地图数据会缓存在 `graphml_files` 目录，避免重复下载
3. **性能考虑**：大规模仿真（>100辆车）建议使用无头模式
4. **内存使用**：长时间仿真会占用较多内存，建议定期保存数据

## 常见问题

### Q: 地图加载失败？
A: 检查网络连接，确保能访问OpenStreetMap。尝试更换地点名称，使用更具体的地名。

### Q: 动画生成很慢？
A: 使用 `--headless` 模式运行，或减少车辆数量和仿真时长。

### Q: MP4生成失败？
A: 确保已安装FFmpeg，并添加到系统PATH。

### Q: 如何提高仿真速度？
A: 
- 使用无头模式：`--headless`
- 减少时间精度：修改 `time_step` 参数
- 优化算法：简化路径规划或调度逻辑

## 许可证

MIT License

## 贡献指南

欢迎提交Issue和Pull Request！

## 联系方式

如有问题或建议，请通过Issue联系。