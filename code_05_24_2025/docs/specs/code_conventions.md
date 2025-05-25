# 代码规范和风格指南

确保代码库的一致性和可维护性。

## Python代码风格

### 命名规范
- **变量名**: `snake_case` (例: `vehicle_count`, `charging_station`)
- **函数名**: `snake_case` (例: `get_shortest_path()`, `update_vehicle_position()`)
- **类名**: `PascalCase` (例: `VehicleManager`, `SimulationEngine`)
- **常量**: `UPPER_SNAKE_CASE` (例: `MAX_VEHICLES`, `DEFAULT_CONFIG`)
- **文件名**: `snake_case.py` (例: `vehicle_manager.py`, `simulation_config.py`)

### 目录结构规范
```
模块名/
├── __init__.py          # 模块初始化
├── {主功能}.py          # 核心功能实现
├── {功能}_config.py     # 配置文件
├── {功能}_utils.py      # 工具函数
└── models/              # 数据模型 (如需要)
```

### 代码组织
```python
"""
模块文档字符串
描述模块功能和用途
"""

# 标准库导入
import os
import sys
from typing import Dict, List, Optional

# 第三方库导入
import numpy as np
import pandas as pd

# 本地导入
from config.simulation_config import SIMULATION_CONFIG
from utils.path_utils import calculate_distance

# 常量定义
MAX_BATTERY_LEVEL = 100
DEFAULT_SPEED = 50  # km/h

class ClassName:
    """类文档字符串"""
    
    def __init__(self, param: type):
        """初始化方法"""
        self.param = param
    
    def method_name(self, arg: type) -> return_type:
        """方法文档字符串"""
        pass

def function_name(param: type) -> return_type:
    """函数文档字符串"""
    pass
```

## 配置文件规范

### 配置文件结构
```python
# config/{功能}_config.py
{FEATURE}_CONFIG = {
    # 基础参数 - 用户常修改
    'param1': default_value,
    'param2': default_value,
    
    # 高级参数 - 需要理解影响
    'advanced_param1': default_value,
    
    # 系统参数 - 通常不修改
    'system_param1': default_value
}
```

### 参数注释规范
```python
SIMULATION_CONFIG = {
    # === 仿真基础参数 ===
    'simulation_duration': 3600,    # 秒 - 仿真总时长
    'time_step': 0.1,              # 秒 - 仿真时间步长
    'location': "West Lafayette",   # 字符串 - 仿真地点
    
    # === 车辆参数 ===
    'num_vehicles': 20,            # 整数 - 车辆总数
    'vehicle_speed': 50,           # km/h - 车辆最大速度
    'battery_capacity': 100,       # % - 电池容量
}
```

## 日志规范

### 日志消息格式
```python
# 使用标准日志格式
logger.info("=== 仿真开始 ===")
logger.info(f"初始化{vehicle_count}辆车辆")
logger.warning(f"车辆{vehicle_id}电量不足: {battery_level}%")
logger.error(f"路径规划失败: 从{start}到{end}")
```

### 日志级别使用
- **DEBUG**: 详细的调试信息
- **INFO**: 一般信息，进度更新
- **WARNING**: 警告信息，但不影响运行
- **ERROR**: 错误信息，需要注意

## 数据结构规范

### 字典结构命名
```python
# 使用一致的字段名
vehicle_data = {
    'vehicle_id': str,           # 唯一标识
    'position': {'x': float, 'y': float},
    'status': str,               # 'idle', 'busy', 'charging'
    'battery_level': float,      # 0-100
    'current_task': dict or None
}

order_data = {
    'order_id': str,
    'pickup_location': {'x': float, 'y': float},
    'dropoff_location': {'x': float, 'y': float},
    'creation_time': float,
    'status': str               # 'pending', 'assigned', 'completed'
}
```

### 返回值规范
```python
def get_vehicle_status(vehicle_id: str) -> Dict[str, Any]:
    """
    返回: {
        'success': bool,
        'data': dict or None,
        'error': str or None
    }
    """
    pass
```

## 性能优化规范

### 代码效率
- 使用numpy数组处理大量数值计算
- 避免不必要的循环嵌套
- 合理使用缓存机制
- 及时清理临时变量

### 内存管理
- 大数据结构使用生成器
- 及时删除不再使用的对象
- 使用适当的数据类型

## 错误处理规范

### 异常处理
```python
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"具体操作失败: {e}")
    return {'success': False, 'error': str(e)}
except Exception as e:
    logger.error(f"未预期错误: {e}")
    raise
```

### 输入验证
```python
def validate_config(config: dict) -> bool:
    """验证配置参数有效性"""
    required_keys = ['simulation_duration', 'num_vehicles']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"缺少必要配置: {key}")
    return True
```

## 文档字符串规范

### 函数文档
```python
def calculate_distance(point1: tuple, point2: tuple) -> float:
    """
    计算两点间的欧几里得距离
    
    Args:
        point1: (x, y) 第一个点的坐标
        point2: (x, y) 第二个点的坐标
    
    Returns:
        float: 两点间距离
    
    Example:
        >>> distance = calculate_distance((0, 0), (3, 4))
        >>> print(distance)  # 5.0
    """
    pass
```

## 测试规范

### 测试文件组织
```
tests/
├── test_{模块名}.py      # 对应模块的测试
├── conftest.py          # 测试配置
└── fixtures/            # 测试数据
```

### 测试函数命名
```python
def test_vehicle_movement_normal_case():
    """测试正常情况下的车辆移动"""
    pass

def test_vehicle_movement_edge_case():
    """测试边界情况下的车辆移动"""
    pass
```

---

**维护说明**: 当添加新代码时，请遵循以上规范以保持代码库的一致性。 