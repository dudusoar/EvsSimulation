"""
YAML Configuration Manager
支持YAML格式的配置文件管理，实现前后端统一配置
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, ValidationError, Field
from datetime import datetime
import os


class SimulationConfigModel(BaseModel):
    """仿真配置的Pydantic模型，用于验证YAML配置"""
    
    class SimulationSection(BaseModel):
        name: str = Field(default="EV Simulation", description="仿真名称")
        location: str = Field(default="West Lafayette, Indiana, USA", description="仿真地点")
        duration: float = Field(default=1800.0, ge=60.0, le=86400.0, description="仿真时长(秒)")
        time_step: float = Field(default=0.1, ge=0.01, le=1.0, description="时间步长(秒)")
    
    class VehiclesSection(BaseModel):
        count: int = Field(default=20, ge=1, le=1000, description="车辆数量")
        speed: float = Field(default=400.0, ge=30.0, le=500.0, description="车辆速度(km/h)")
        battery: Dict[str, float] = Field(default={
            "capacity": 100.0,
            "charging_threshold": 40.0,
            "consumption_rate": 1.2
        }, description="电池相关参数")
    
    class OrdersSection(BaseModel):
        generation_rate: int = Field(default=1000, ge=10, le=10000, description="订单生成率(订单/小时)")
        pricing: Dict[str, float] = Field(default={
            "base_price_per_km": 2.0,
            "surge_multiplier": 1.5
        }, description="定价策略")
        max_waiting_time: float = Field(default=600.0, ge=60.0, le=3600.0, description="最大等待时间(秒)")
    
    class ChargingStationsSection(BaseModel):
        count: int = Field(default=5, ge=1, le=100, description="充电站数量")
        slots_per_station: int = Field(default=3, ge=1, le=20, description="每个充电站的充电桩数量")
        charging_rate: float = Field(default=5.0, ge=0.1, le=20.0, description="充电速率(%/秒)")
        electricity_price: float = Field(default=0.8, ge=0.1, le=5.0, description="电价(USD/kWh)")
    
    class VisualizationSection(BaseModel):
        mode: str = Field(default="live", description="运行模式: live=实时可视化, headless=无界面")
        enable_animation: bool = Field(default=True, description="是否启用动画")
        animation_fps: int = Field(default=60, ge=1, le=120, description="动画帧率")
        save_animation: bool = Field(default=True, description="是否保存动画")
        animation_format: str = Field(default="html", description="动画格式")
    
    class DataSection(BaseModel):
        save_data: bool = Field(default=False, description="是否保存数据")
        save_interval: float = Field(default=10.0, ge=1.0, le=3600.0, description="数据保存间隔(秒)")
        output_dir: str = Field(default="simulation_output", description="输出目录")
    
    # 配置文件的主要部分
    simulation: SimulationSection = Field(default_factory=SimulationSection)
    vehicles: VehiclesSection = Field(default_factory=VehiclesSection)
    orders: OrdersSection = Field(default_factory=OrdersSection)
    charging_stations: ChargingStationsSection = Field(default_factory=ChargingStationsSection)
    visualization: VisualizationSection = Field(default_factory=VisualizationSection)
    data: DataSection = Field(default_factory=DataSection)
    
    # 元数据
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        extra = "allow"  # 允许额外字段，便于扩展


class YAMLConfigManager:
    """YAML配置管理器"""
    
    def __init__(self, config_dir: str = "yaml_config"):
        """初始化配置管理器
        
        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        # 配置文件路径
        self.templates_dir = self.config_dir / "templates"
        self.templates_dir.mkdir(exist_ok=True)
        
        # 默认配置文件路径
        self.default_config_path = self.config_dir / "default.yaml"
        
        # 创建默认配置文件
        self._ensure_default_config()
        
    def _ensure_default_config(self):
        """确保默认配置文件存在"""
        if not self.default_config_path.exists():
            default_config = SimulationConfigModel()
            self.save_config(default_config, "default.yaml")
    
    def load_config(self, config_file: str = "default.yaml") -> SimulationConfigModel:
        """加载YAML配置文件
        
        Args:
            config_file: 配置文件名
            
        Returns:
            验证后的配置模型
            
        Raises:
            FileNotFoundError: 配置文件不存在
            ValidationError: 配置验证失败
            yaml.YAMLError: YAML解析错误
        """
        config_path = self.config_dir / config_file
        
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                yaml_data = yaml.safe_load(file)
            
            # 添加元数据
            if yaml_data is None:
                yaml_data = {}
            
            yaml_data['metadata'] = {
                'config_file': config_file,
                'loaded_at': datetime.now().isoformat(),
                'file_path': str(config_path)
            }
            
            # 验证配置
            config = SimulationConfigModel(**yaml_data)
            return config
            
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"YAML解析错误: {e}")
        except ValidationError as e:
            raise ValidationError(f"配置验证失败: {e}")
    
    def save_config(self, config: SimulationConfigModel, config_file: str = "default.yaml") -> bool:
        """保存配置到YAML文件
        
        Args:
            config: 配置模型
            config_file: 配置文件名
            
        Returns:
            是否保存成功
        """
        try:
            config_path = self.config_dir / config_file
            
            # 转换为字典并移除元数据字段
            config_dict = config.dict()
            if 'metadata' in config_dict:
                del config_dict['metadata']
            
            # 添加注释头
            yaml_content = self._generate_yaml_with_comments(config_dict)
            
            with open(config_path, 'w', encoding='utf-8') as file:
                file.write(yaml_content)
            
            return True
            
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def _generate_yaml_with_comments(self, config_dict: Dict) -> str:
        """生成带注释的YAML内容"""
        header = f"""# EV仿真系统配置文件
# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# 配置格式版本: 2.0

"""
        
        # 转换为YAML
        yaml_content = yaml.dump(
            config_dict,
            default_flow_style=False,
            allow_unicode=True,
            indent=2,
            sort_keys=False
        )
        
        return header + yaml_content
    
    def list_configs(self) -> List[str]:
        """列出所有可用的配置文件"""
        yaml_files = list(self.config_dir.glob("*.yaml"))
        return [f.name for f in yaml_files]
    
    def create_template(self, template_name: str, base_config: Optional[SimulationConfigModel] = None) -> bool:
        """创建配置模板
        
        Args:
            template_name: 模板名称
            base_config: 基础配置，如果为None则使用默认配置
            
        Returns:
            是否创建成功
        """
        try:
            if base_config is None:
                base_config = SimulationConfigModel()
            
            template_path = self.templates_dir / f"{template_name}.yaml"
            
            # 保存模板
            config_dict = base_config.dict()
            if 'metadata' in config_dict:
                del config_dict['metadata']
            
            yaml_content = self._generate_yaml_with_comments(config_dict)
            
            with open(template_path, 'w', encoding='utf-8') as file:
                file.write(yaml_content)
            
            return True
            
        except Exception as e:
            print(f"创建模板失败: {e}")
            return False
    
    def load_template(self, template_name: str) -> SimulationConfigModel:
        """加载配置模板"""
        template_path = self.templates_dir / f"{template_name}.yaml"
        
        if not template_path.exists():
            raise FileNotFoundError(f"模板不存在: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as file:
            yaml_data = yaml.safe_load(file)
        
        return SimulationConfigModel(**yaml_data)
    
    def convert_legacy_config(self, legacy_config: Dict) -> SimulationConfigModel:
        """将传统的字典配置转换为新的YAML配置格式
        
        Args:
            legacy_config: 传统的配置字典
            
        Returns:
            转换后的配置模型
        """
        try:
            # 映射传统配置到新格式
            converted_config = {
                "simulation": {
                    "name": legacy_config.get('name', 'EV Simulation'),
                    "location": legacy_config.get('location', 'West Lafayette, Indiana, USA'),
                    "duration": legacy_config.get('simulation_duration', 1800),
                    "time_step": legacy_config.get('time_step', 0.1)
                },
                "vehicles": {
                    "count": legacy_config.get('num_vehicles', 20),
                    "speed": legacy_config.get('vehicle_speed', 400),
                    "battery": {
                        "capacity": legacy_config.get('battery_capacity', 100.0),
                        "charging_threshold": legacy_config.get('charging_threshold', 40.0),
                        "consumption_rate": legacy_config.get('energy_consumption', 1.2)
                    }
                },
                "orders": {
                    "generation_rate": legacy_config.get('order_generation_rate', 1000),
                    "pricing": {
                        "base_price_per_km": legacy_config.get('base_price_per_km', 2.0),
                        "surge_multiplier": legacy_config.get('surge_multiplier', 1.5)
                    },
                    "max_waiting_time": legacy_config.get('max_waiting_time', 600)
                },
                "charging_stations": {
                    "count": legacy_config.get('num_charging_stations', 5),
                    "slots_per_station": legacy_config.get('charging_slots_per_station', 3),
                    "charging_rate": legacy_config.get('charging_rate', 5.0),
                    "electricity_price": legacy_config.get('electricity_price', 0.8)
                },
                "visualization": {
                    "enable_animation": legacy_config.get('enable_animation', True),
                    "animation_fps": legacy_config.get('animation_fps', 60),
                    "save_animation": legacy_config.get('save_animation', True),
                    "animation_format": legacy_config.get('animation_format', 'html')
                },
                "data": {
                    "save_data": legacy_config.get('save_data', False),
                    "save_interval": legacy_config.get('data_save_interval', 10),
                    "output_dir": legacy_config.get('output_dir', 'simulation_output')
                }
            }
            
            return SimulationConfigModel(**converted_config)
            
        except Exception as e:
            print(f"转换传统配置失败: {e}")
            raise
    
    def to_legacy_format(self, config: SimulationConfigModel) -> Dict:
        """将YAML配置转换为传统格式，保持向后兼容
        
        Args:
            config: YAML配置模型
            
        Returns:
            传统格式的配置字典
        """
        legacy_config = {
            # 基础仿真参数
            'location': config.simulation.location,
            'cache_map': True,
            'simulation_duration': config.simulation.duration,
            'time_step': config.simulation.time_step,
            
            # 车辆参数
            'num_vehicles': config.vehicles.count,
            'vehicle_speed': config.vehicles.speed,
            'vehicle_speed_mps': config.vehicles.speed / 3.6,
            'battery_capacity': config.vehicles.battery.get('capacity', 100.0),
            'energy_consumption': config.vehicles.battery.get('consumption_rate', 1.2),
            'charging_threshold': config.vehicles.battery.get('charging_threshold', 40.0),
            
            # 订单参数
            'order_generation_rate': config.orders.generation_rate,
            'base_price_per_km': config.orders.pricing.get('base_price_per_km', 2.0),
            'surge_multiplier': config.orders.pricing.get('surge_multiplier', 1.5),
            'max_waiting_time': config.orders.max_waiting_time,
            
            # 充电站参数
            'num_charging_stations': config.charging_stations.count,
            'charging_slots_per_station': config.charging_stations.slots_per_station,
            'charging_power': 50,  # 固定值
            'charging_rate': config.charging_stations.charging_rate,
            'electricity_price': config.charging_stations.electricity_price,
            
            # 可视化参数
            'enable_animation': config.visualization.enable_animation,
            'animation_fps': config.visualization.animation_fps,
            'show_preview': False,  # 固定值
            'save_animation': config.visualization.save_animation,
            'animation_format': config.visualization.animation_format,
            
            # 数据管理参数
            'save_data': config.data.save_data,
            'data_save_interval': config.data.save_interval,
            'output_dir': config.data.output_dir
        }
        
        return legacy_config


# 全局配置管理器实例
config_manager = YAMLConfigManager() 