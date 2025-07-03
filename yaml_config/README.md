# YAML配置文件 | YAML Configurations

这个目录包含所有的YAML配置文件，用于控制仿真参数。

## 📁 文件说明

### 🎯 实际使用的配置
- `default.yaml` - 默认配置，运行 `python main.py` 时使用

### 📋 参考示例（可复制修改）
- `headless_batch.yaml` - 批处理模式示例（50车，60秒，无界面）
- `west_lafayette_demo.yaml` - 演示模式示例（20车，30分钟，可视化）

## 🚀 如何使用

### 运行现有配置
```bash
# 使用默认配置
python main.py

# 使用指定配置
python main.py -c headless_batch.yaml
python main.py -c west_lafayette_demo.yaml
```

### 创建自定义配置
```bash
# 1. 复制示例配置
copy yaml_config\headless_batch.yaml yaml_config\my_test.yaml

# 2. 编辑参数
notepad yaml_config\my_test.yaml

# 3. 运行自定义配置
python main.py -c my_test.yaml
```

### 查看所有可用配置
```bash
python main.py --list
```

## ⚙️ 配置参数说明

每个YAML文件都包含这些主要部分：

```yaml
simulation:
  name: "配置名称"
  location: "West Lafayette, Indiana, USA"  # 仿真地点
  duration: 60.0                           # 仿真时长(秒)

visualization:
  mode: live                               # live=可视化, headless=无界面

vehicles:
  count: 20                                # 车辆数量
  speed: 400.0                             # 车辆速度(km/h)

orders:
  generation_rate: 1000                    # 订单生成率(订单/小时)

data:
  save_data: false                         # 是否保存数据
  save_interval: 10.0                      # 进度报告间隔(秒)
```

## 💡 快速配置技巧

| 需求 | 设置 |
|------|------|
| 快速测试 | `duration: 60`, `mode: headless` |
| 详细演示 | `duration: 1800`, `mode: live` |
| 高强度测试 | `vehicles.count: 100`, `orders.generation_rate: 5000` |
| 批量分析 | `save_data: true`, `mode: headless` |

## 🎯 记住

- **所有参数都在YAML中** - 不需要修改Python代码
- **配置即记录** - 每个YAML文件就是一次仿真的完整记录
- **简单复制** - 复制现有配置，改几个参数就是新配置 