"""
可视化模块
负责仿真过程的实时可视化和动画生成
继承并优化原有animate.py的功能
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle
import numpy as np
from typing import List, Dict, Tuple, Optional
from tqdm import tqdm
from datetime import datetime
import os

from core.simulation_engine import SimulationEngine
from models.vehicle import Vehicle
from models.order import Order
from models.charging_station import ChargingStation
from config.simulation_config import COLORS, VEHICLE_STATUS, ORDER_STATUS


class Visualizer:
    """可视化器类"""
    
    def __init__(self, simulation_engine: SimulationEngine, config: Dict):
        """
        初始化可视化器
        
        参数:
            simulation_engine: 仿真引擎
            config: 配置参数
        """
        self.engine = simulation_engine
        self.config = config
        
        # 获取地图图形
        self.fig, self.ax = self.engine.map_manager.setup_plot(
            show_preview=config.get('show_preview', False)
        )
        
        # 动画参数
        self.fps = config.get('animation_fps', 30)
        self.interval = 1000 / self.fps  # 毫秒
        
        # 图形元素存储
        self.vehicle_artists = {}  # vehicle_id -> {'marker': artist, 'text': artist}
        self.order_markers = {}    # order_id -> {'pickup': artist, 'dropoff': artist}
        self.station_markers = []  # 充电站标记
        
        # 信息文本
        self.info_text = None
        self.stats_text = None
        
        # 初始化图形元素
        self._initialize_graphics()
    
    # ============= 初始化方法 =============
    def _initialize_graphics(self):
        """Initialize graphics elements"""
        # 创建车辆图形
        for vehicle in self.engine.get_vehicles():
            # 车辆标记 - 调小尺寸
            marker, = self.ax.plot(
                [], [], 
                marker='o', 
                markersize=5,  # 从8改为5
                color=COLORS['vehicle']['idle'],
                markeredgecolor='black',
                markeredgewidth=0.5,
                animated=True
            )
            
            # 电量文本
            text = self.ax.text(
                0, 0, '', 
                fontsize=7,  # 从8改为7
                ha='center', 
                va='bottom',
                animated=True
            )
            
            self.vehicle_artists[vehicle.vehicle_id] = {
                'marker': marker,
                'text': text
            }
        
        # 创建充电站图形 - 调小尺寸
        for station in self.engine.get_charging_stations():
            marker, = self.ax.plot(
                station.position[0], 
                station.position[1],
                marker='s',
                markersize=7,  # 从12改为7
                color=COLORS['charging_station'],
                markeredgecolor='black',
                markeredgewidth=1,
                animated=True
            )
            self.station_markers.append(marker)
        
        # 创建信息文本
        self.info_text = self.ax.text(
            0.02, 0.98, '', 
            transform=self.ax.transAxes,
            fontsize=9,  # 从10改为9
            va='top',
            ha='left',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
            animated=True
        )
        
        self.stats_text = self.ax.text(
            0.98, 0.98, '', 
            transform=self.ax.transAxes,
            fontsize=8,  # 从9改为8
            va='top',
            ha='right',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
            animated=True
        )
    
    # ============= 动画更新方法 =============
    def init_animation(self):
        """初始化动画"""
        # 清空所有动态元素
        for vehicle_id, artists in self.vehicle_artists.items():
            artists['marker'].set_data([], [])
            artists['text'].set_text('')
        
        for order_id, markers in self.order_markers.items():
            if 'pickup' in markers:
                markers['pickup'].set_data([], [])
            if 'dropoff' in markers:
                markers['dropoff'].set_data([], [])
        
        self.info_text.set_text('')
        self.stats_text.set_text('')
        
        # 返回所有需要更新的artist
        artists = []
        for v_artists in self.vehicle_artists.values():
            artists.extend([v_artists['marker'], v_artists['text']])
        artists.extend(self.station_markers)
        artists.extend([self.info_text, self.stats_text])
        
        return artists
    
    def update_frame(self, frame_num: int):
        """Update one frame"""
        # 运行仿真步骤
        self.engine.run_step()
        
        # 更新车辆
        self._update_vehicles()
        
        # 更新订单
        self._update_orders()
        
        # 更新信息文本
        self._update_info_text()
        
        # 收集所有artist
        artists = []
        for v_artists in self.vehicle_artists.values():
            artists.extend([v_artists['marker'], v_artists['text']])
        for markers in self.order_markers.values():
            if 'pickup' in markers:
                artists.append(markers['pickup'])
            if 'dropoff' in markers:
                artists.append(markers['dropoff'])
            if 'pickup_text' in markers:
                artists.append(markers['pickup_text'])
            if 'dropoff_text' in markers:
                artists.append(markers['dropoff_text'])
        artists.extend([self.info_text, self.stats_text])
        
        return artists
    
    def _update_vehicles(self):
        """Update vehicle display"""
        vehicles = self.engine.get_vehicles()
        
        for vehicle in vehicles:
            if vehicle.vehicle_id not in self.vehicle_artists:
                continue
            
            artists = self.vehicle_artists[vehicle.vehicle_id]
            
            # 更新位置
            artists['marker'].set_data([vehicle.position[0]], [vehicle.position[1]])
            
            # 更新颜色
            color = COLORS['vehicle'].get(vehicle.status, 'gray')
            if vehicle.battery_percentage < 20:
                color = COLORS['low_battery']
            artists['marker'].set_color(color)
            
            # 更新电量文本 - 改为英文
            battery_text = f"{vehicle.battery_percentage:.0f}%"
            if vehicle.status == VEHICLE_STATUS['WITH_PASSENGER']:
                battery_text += " P"  # Passenger
            elif vehicle.status == VEHICLE_STATUS['CHARGING']:
                battery_text += " C"  # Charging
            
            artists['text'].set_text(battery_text)
            artists['text'].set_position((vehicle.position[0], vehicle.position[1] + 50))
    
    def _update_orders(self):
        """Update order display"""
        orders_info = self.engine.get_orders()
        
        # 获取所有活跃订单（待分配和进行中）
        active_orders = orders_info['pending'] + orders_info['active']
        
        # 移除已完成订单的标记
        completed_order_ids = set(self.order_markers.keys()) - set(o.order_id for o in active_orders)
        for order_id in completed_order_ids:
            if order_id in self.order_markers:
                markers = self.order_markers[order_id]
                if 'pickup' in markers:
                    markers['pickup'].remove()
                if 'dropoff' in markers:
                    markers['dropoff'].remove()
                if 'pickup_text' in markers:
                    markers['pickup_text'].remove()
                if 'dropoff_text' in markers:
                    markers['dropoff_text'].remove()
                del self.order_markers[order_id]
        
        # 更新活跃订单
        for order in active_orders:
            if order.order_id not in self.order_markers:
                # 创建新标记
                self.order_markers[order.order_id] = {}
                
                # 上车点标记（三角形）- 调小尺寸
                pickup_marker, = self.ax.plot(
                    order.pickup_position[0],
                    order.pickup_position[1],
                    marker='^',
                    markersize=6,  # 从10改为6
                    color=COLORS['order']['pickup'],
                    markeredgecolor='black',
                    markeredgewidth=0.5,
                    animated=True
                )
                self.order_markers[order.order_id]['pickup'] = pickup_marker
                
                # 上车点编号文本
                pickup_text = self.ax.text(
                    order.pickup_position[0], 
                    order.pickup_position[1] + 30,
                    f"#{order.order_id[-3:]}",  # 显示订单编号后3位
                    fontsize=6,
                    ha='center',
                    va='bottom',
                    color='darkblue',
                    weight='bold',
                    animated=True
                )
                self.order_markers[order.order_id]['pickup_text'] = pickup_text
                
                # 下车点标记（倒三角形）- 始终显示
                dropoff_marker, = self.ax.plot(
                    order.dropoff_position[0],
                    order.dropoff_position[1],
                    marker='v',
                    markersize=6,  # 从10改为6
                    color=COLORS['order']['dropoff'],
                    markeredgecolor='black',
                    markeredgewidth=0.5,
                    animated=True
                )
                self.order_markers[order.order_id]['dropoff'] = dropoff_marker
                
                # 下车点编号文本
                dropoff_text = self.ax.text(
                    order.dropoff_position[0], 
                    order.dropoff_position[1] - 30,
                    f"#{order.order_id[-3:]}",  # 显示订单编号后3位
                    fontsize=6,
                    ha='center',
                    va='top',
                    color='darkmagenta',
                    weight='bold',
                    animated=True
                )
                self.order_markers[order.order_id]['dropoff_text'] = dropoff_text
    
    def _update_info_text(self):
        """Update information text"""
        # 获取统计信息
        stats = self.engine.get_current_statistics()
        
        # 主要信息
        info_lines = [
            f"Simulation time: {stats['simulation_time']:.1f} seconds",
            f"Vehicles: {stats['vehicles']['total_vehicles']} vehicles",
            f"Orders: {stats['orders']['pending_orders']} pending, "
            f"{stats['orders']['active_orders']} active",
            f"Average battery: {stats['vehicles']['avg_battery_percentage']:.1f}%"
        ]
        self.info_text.set_text('\n'.join(info_lines))
        
        # 统计信息
        stats_lines = [
            f"Completed orders: {stats['orders']['total_orders_completed']}",
            f"Total revenue: ¥{stats['orders']['total_revenue']:.2f}",
            f"Vehicle utilization: {stats['vehicles']['utilization_rate']*100:.1f}%",
            f"Charging station utilization: {stats['charging']['avg_utilization_rate']*100:.1f}%"
        ]
        self.stats_text.set_text('\n'.join(stats_lines))
    
    # ============= 动画生成方法 =============
    def create_animation(self, duration: float) -> animation.FuncAnimation:
        """
        创建动画
        
        参数:
            duration: 仿真时长（秒）
        
        返回:
            动画对象
        """
        n_frames = int(duration / self.engine.time_step)
        
        # 创建动画
        ani = animation.FuncAnimation(
            self.fig,
            self.update_frame,
            init_func=self.init_animation,
            frames=tqdm(range(n_frames), desc="Generating animation"),
            interval=self.interval,
            blit=True,
            repeat=False
        )
        
        return ani
    
    def save_animation(self, filename: str = None, format: str = 'html'):
        """
        保存动画
        
        参数:
            filename: 文件名（不含扩展名）
            format: 格式 ('html' 或 'mp4')
        """
        # 确保输出目录存在
        output_dir = 'outputs/visualizations'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ev_simulation_{timestamp}"
        
        duration = self.config.get('simulation_duration', 3600)
        ani = self.create_animation(duration)
        
        if format == 'html':
            writer = animation.HTMLWriter(fps=self.fps)
            output_file = os.path.join(output_dir, f"{filename}.html")
        elif format == 'mp4':
            writer = animation.FFMpegWriter(fps=self.fps)
            output_file = os.path.join(output_dir, f"{filename}.mp4")
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        print(f"Saving animation to: {output_file}")
        ani.save(output_file, writer=writer)
        print("Animation saved successfully!")
        
        return output_file