#!/usr/bin/env python3
"""
DearPyGui仿真界面框架
集成OSMnx地图显示和仿真控制功能
"""

import dearpygui.dearpygui as dpg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import threading
import time
from typing import Dict, Any, Callable
import io
from PIL import Image

try:
    from core.simulation_engine import SimulationEngine
    from core.map_manager import MapManager
    from visualization.visualizer import Visualizer
except ImportError:
    print("Warning: Core modules not available. Running in demo mode.")


class SimulationUI:
    """基于DearPyGui的仿真用户界面"""
    
    def __init__(self):
        """初始化UI"""
        self.simulation_engine = None
        self.map_manager = None
        self.visualizer = None
        
        # 仿真控制状态
        self.is_running = False
        self.is_paused = False
        self.simulation_thread = None
        
        # UI配置
        self.config = {
            'window_width': 1600,
            'window_height': 1000,
            'map_width': 800,
            'map_height': 600,
            'panel_width': 300
        }
        
        # 地图图像相关
        self.map_texture = None
        self.map_figure = None
        self.map_ax = None
        
        # 初始化参数
        self.sim_params = {
            'duration': 3600,
            'num_vehicles': 20,
            'num_charging_stations': 8,
            'vehicle_speed': 15.0,
            'charging_power': 50.0,
            'battery_capacity': 75.0
        }
        
        # 指标数据
        self.metrics = {
            'simulation_time': 0.0,
            'active_vehicles': 0,
            'pending_orders': 0,
            'active_orders': 0,
            'completed_orders': 0,
            'total_revenue': 0.0,
            'avg_battery': 0.0,
            'vehicle_utilization': 0.0
        }

    def create_context(self):
        """创建DearPyGui上下文"""
        dpg.create_context()
        dpg.create_viewport(
            title="Electric Vehicle Simulation System",
            width=self.config['window_width'],
            height=self.config['window_height'],
            resizable=True
        )
        dpg.setup_dearpygui()

    def setup_ui(self):
        """设置UI布局"""
        # 主窗口
        with dpg.window(label="EV Simulation", tag="main_window"):
            
            # 水平布局
            with dpg.group(horizontal=True):
                
                # 左侧：参数控制面板
                self.create_parameter_panel()
                
                # 中间：地图显示区域
                self.create_map_area()
                
                # 右侧：指标面板
                self.create_metrics_panel()
            
            # 底部：仿真控制面板
            self.create_control_panel()

    def create_parameter_panel(self):
        """创建参数控制面板"""
        with dpg.child_window(
            label="Simulation Parameters",
            width=self.config['panel_width'],
            height=700,
            border=True
        ):
            dpg.add_text("🔧 Simulation Configuration", color=[100, 200, 255])
            dpg.add_separator()
            
            # 基础参数
            dpg.add_text("Basic Parameters:")
            
            dpg.add_slider_int(
                label="Simulation Duration (s)",
                default_value=self.sim_params['duration'],
                min_value=300,
                max_value=7200,
                tag="duration_slider",
                callback=lambda s, v: self.update_param('duration', v)
            )
            
            dpg.add_slider_int(
                label="Number of Vehicles",
                default_value=self.sim_params['num_vehicles'],
                min_value=5,
                max_value=50,
                tag="vehicles_slider",
                callback=lambda s, v: self.update_param('num_vehicles', v)
            )
            
            dpg.add_slider_int(
                label="Charging Stations",
                default_value=self.sim_params['num_charging_stations'],
                min_value=3,
                max_value=20,
                tag="stations_slider",
                callback=lambda s, v: self.update_param('num_charging_stations', v)
            )
            
            dpg.add_separator()
            dpg.add_text("Vehicle Configuration:")
            
            dpg.add_slider_float(
                label="Vehicle Speed (m/s)",
                default_value=self.sim_params['vehicle_speed'],
                min_value=5.0,
                max_value=30.0,
                format="%.1f",
                tag="speed_slider",
                callback=lambda s, v: self.update_param('vehicle_speed', v)
            )
            
            dpg.add_slider_float(
                label="Battery Capacity (kWh)",
                default_value=self.sim_params['battery_capacity'],
                min_value=40.0,
                max_value=100.0,
                format="%.1f",
                tag="battery_slider",
                callback=lambda s, v: self.update_param('battery_capacity', v)
            )
            
            dpg.add_slider_float(
                label="Charging Power (kW)",
                default_value=self.sim_params['charging_power'],
                min_value=25.0,
                max_value=150.0,
                format="%.1f",
                tag="charging_slider",
                callback=lambda s, v: self.update_param('charging_power', v)
            )
            
            dpg.add_separator()
            
            # 地图配置
            dpg.add_text("Map Configuration:")
            dpg.add_combo(
                label="Location",
                items=["West Lafayette, Indiana", "New York City, NY", "San Francisco, CA"],
                default_value="West Lafayette, Indiana",
                tag="location_combo"
            )
            
            dpg.add_separator()
            
            # 初始化按钮
            dpg.add_button(
                label="🚀 Initialize Simulation",
                callback=self.initialize_simulation,
                tag="init_button",
                width=-1,
                height=50
            )

    def create_map_area(self):
        """创建地图显示区域"""
        with dpg.child_window(
            label="Map View",
            width=self.config['map_width'],
            height=700,
            border=True
        ):
            dpg.add_text("🗺️ Real-time Map View", color=[100, 255, 100])
            dpg.add_separator()
            
            # 地图控制工具栏
            with dpg.group(horizontal=True):
                dpg.add_button(label="🔍 Zoom In", callback=self.zoom_in)
                dpg.add_button(label="🔍 Zoom Out", callback=self.zoom_out)
                dpg.add_button(label="🏠 Reset View", callback=self.reset_view)
                dpg.add_button(label="📱 Update Map", callback=self.update_map_display)
            
            dpg.add_separator()
            
            # 地图图像显示区域
            dpg.add_image(
                "map_texture",
                width=self.config['map_width'] - 20,
                height=self.config['map_height'] - 100,
                tag="map_image"
            )
            
            # 地图状态信息
            dpg.add_text("Map Status: Ready", tag="map_status")

    def create_metrics_panel(self):
        """创建指标显示面板"""
        with dpg.child_window(
            label="Real-time Metrics",
            width=self.config['panel_width'],
            height=700,
            border=True
        ):
            dpg.add_text("📊 Key Performance Indicators", color=[255, 200, 100])
            dpg.add_separator()
            
            # 实时指标显示
            dpg.add_text("Simulation Progress:")
            dpg.add_progress_bar(tag="sim_progress", default_value=0.0, overlay="0%")
            dpg.add_text("00:00:00 / 01:00:00", tag="time_display")
            
            dpg.add_separator()
            dpg.add_text("Fleet Status:")
            
            # 车队指标
            dpg.add_text("Active Vehicles: 0", tag="active_vehicles")
            dpg.add_text("Average Battery: 0%", tag="avg_battery")
            dpg.add_text("Vehicle Utilization: 0%", tag="vehicle_util")
            
            dpg.add_separator()
            dpg.add_text("Order Management:")
            
            # 订单指标
            dpg.add_text("Pending Orders: 0", tag="pending_orders")
            dpg.add_text("Active Orders: 0", tag="active_orders")
            dpg.add_text("Completed Orders: 0", tag="completed_orders")
            
            dpg.add_separator()
            dpg.add_text("Financial Performance:")
            
            # 财务指标
            dpg.add_text("Total Revenue: $0.00", tag="total_revenue")
            dpg.add_text("Revenue/Hour: $0.00", tag="revenue_hour")
            
            dpg.add_separator()
            
            # 实时图表区域
            dpg.add_text("Performance Charts:")
            dpg.add_plot(
                label="Real-time Metrics",
                height=200,
                width=-1,
                tag="metrics_plot"
            )
            
            # 添加图表轴
            dpg.add_plot_axis(dpg.mvXAxis, label="Time", tag="x_axis", parent="metrics_plot")
            dpg.add_plot_axis(dpg.mvYAxis, label="Value", tag="y_axis", parent="metrics_plot")

    def create_control_panel(self):
        """创建仿真控制面板"""
        dpg.add_separator()
        
        with dpg.group(horizontal=True):
            dpg.add_text("🎮 Simulation Control:", color=[255, 255, 100])
            
            # 仿真控制按钮
            dpg.add_button(
                label="▶️ Start",
                callback=self.start_simulation,
                tag="start_button",
                width=100,
                height=40
            )
            
            dpg.add_button(
                label="⏸️ Pause",
                callback=self.pause_simulation,
                tag="pause_button",
                width=100,
                height=40,
                enabled=False
            )
            
            dpg.add_button(
                label="⏹️ Stop",
                callback=self.stop_simulation,
                tag="stop_button",
                width=100,
                height=40,
                enabled=False
            )
            
            dpg.add_button(
                label="🔄 Reset",
                callback=self.reset_simulation,
                tag="reset_button",
                width=100,
                height=40
            )
            
            # 速度控制
            dpg.add_text("Speed:")
            dpg.add_slider_float(
                label="",
                default_value=1.0,
                min_value=0.1,
                max_value=10.0,
                format="%.1fx",
                width=150,
                tag="speed_control",
                callback=self.adjust_speed
            )

    def update_param(self, param_name: str, value: Any):
        """更新仿真参数"""
        self.sim_params[param_name] = value
        print(f"Parameter updated: {param_name} = {value}")

    def initialize_simulation(self):
        """初始化仿真系统"""
        try:
            # 禁用初始化按钮
            dpg.configure_item("init_button", enabled=False)
            
            # 更新状态
            dpg.set_value("map_status", "Initializing simulation...")
            
            # 获取地图位置
            location = dpg.get_value("location_combo")
            
            # 创建仿真组件
            print(f"🔧 Initializing simulation for {location}...")
            self.map_manager = MapManager(location)
            self.simulation_engine = SimulationEngine(self.sim_params)
            
            # 初始化地图显示
            self.setup_map_display()
            
            # 更新UI状态
            dpg.set_value("map_status", f"Ready - {location}")
            dpg.configure_item("start_button", enabled=True)
            dpg.configure_item("init_button", enabled=True)
            
            print("✅ Simulation initialized successfully!")
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            dpg.set_value("map_status", f"Error: {str(e)}")
            dpg.configure_item("init_button", enabled=True)

    def setup_map_display(self):
        """设置地图显示"""
        if not self.map_manager:
            return
        
        # 创建matplotlib图形
        self.map_figure, self.map_ax = self.map_manager.setup_plot(show_preview=False)
        self.map_figure.set_size_inches(8, 6)
        
        # 转换为纹理
        self.update_map_texture()

    def update_map_texture(self):
        """更新地图纹理"""
        if not self.map_figure:
            return
        
        # 渲染matplotlib图形到内存
        canvas = FigureCanvasAgg(self.map_figure)
        canvas.draw()
        
        # 获取图像数据
        buf = canvas.buffer_rgba()
        w, h = canvas.get_width_height()
        
        # 转换为numpy数组
        img_array = np.frombuffer(buf, dtype=np.uint8).reshape((h, w, 4))
        
        # 转换为RGB (DearPyGui需要RGB格式)
        img_rgb = img_array[:, :, :3]
        
        # 归一化到0-1范围
        img_normalized = img_rgb.astype(np.float32) / 255.0
        
        # 创建或更新纹理
        if self.map_texture is None:
            with dpg.texture_registry():
                self.map_texture = dpg.add_raw_texture(
                    width=w,
                    height=h,
                    default_value=img_normalized.flatten(),
                    format=dpg.mvFormat_Float_rgb,
                    tag="map_texture"
                )
        else:
            dpg.set_value("map_texture", img_normalized.flatten())

    def start_simulation(self):
        """开始仿真"""
        if not self.simulation_engine:
            print("❌ Please initialize simulation first!")
            return
        
        self.is_running = True
        self.is_paused = False
        
        # 更新按钮状态
        dpg.configure_item("start_button", enabled=False)
        dpg.configure_item("pause_button", enabled=True)
        dpg.configure_item("stop_button", enabled=True)
        
        # 启动仿真线程
        self.simulation_thread = threading.Thread(target=self.simulation_loop)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
        
        print("🚀 Simulation started!")

    def pause_simulation(self):
        """暂停/恢复仿真"""
        if self.is_running:
            self.is_paused = not self.is_paused
            if self.is_paused:
                dpg.set_item_label("pause_button", "▶️ Resume")
                print("⏸️ Simulation paused")
            else:
                dpg.set_item_label("pause_button", "⏸️ Pause")
                print("▶️ Simulation resumed")

    def stop_simulation(self):
        """停止仿真"""
        self.is_running = False
        self.is_paused = False
        
        # 更新按钮状态
        dpg.configure_item("start_button", enabled=True)
        dpg.configure_item("pause_button", enabled=False)
        dpg.configure_item("stop_button", enabled=False)
        dpg.set_item_label("pause_button", "⏸️ Pause")
        
        print("⏹️ Simulation stopped")

    def reset_simulation(self):
        """重置仿真"""
        self.stop_simulation()
        
        # 重置指标
        for key in self.metrics:
            self.metrics[key] = 0.0
        
        self.update_metrics_display()
        print("🔄 Simulation reset")

    def adjust_speed(self, sender, value):
        """调整仿真速度"""
        print(f"🏃 Simulation speed: {value:.1f}x")

    def simulation_loop(self):
        """仿真主循环"""
        start_time = time.time()
        
        while self.is_running:
            if not self.is_paused:
                try:
                    # 运行仿真步骤
                    self.simulation_engine.run_step()
                    
                    # 更新指标
                    self.update_metrics()
                    
                    # 更新地图显示
                    self.update_map_display()
                    
                    # 检查仿真是否完成
                    if self.simulation_engine.current_time >= self.sim_params['duration']:
                        self.stop_simulation()
                        break
                        
                except Exception as e:
                    print(f"❌ Simulation error: {e}")
                    self.stop_simulation()
                    break
            
            # 控制更新频率
            time.sleep(0.1)

    def update_metrics(self):
        """更新指标数据"""
        if not self.simulation_engine:
            return
        
        # 获取当前统计数据
        stats = self.simulation_engine.get_current_statistics()
        
        # 更新metrics字典
        self.metrics.update({
            'simulation_time': stats.get('simulation_time', 0.0),
            'active_vehicles': stats.get('vehicles', {}).get('total_vehicles', 0),
            'pending_orders': stats.get('orders', {}).get('pending_orders', 0),
            'active_orders': stats.get('orders', {}).get('active_orders', 0),
            'completed_orders': stats.get('orders', {}).get('total_orders_completed', 0),
            'total_revenue': stats.get('orders', {}).get('total_revenue', 0.0),
            'avg_battery': stats.get('vehicles', {}).get('avg_battery_percentage', 0.0),
            'vehicle_utilization': stats.get('vehicles', {}).get('utilization_rate', 0.0) * 100
        })
        
        # 更新UI显示
        self.update_metrics_display()

    def update_metrics_display(self):
        """更新指标显示"""
        # 进度条
        progress = self.metrics['simulation_time'] / self.sim_params['duration']
        dpg.set_value("sim_progress", progress)
        dpg.configure_item("sim_progress", overlay=f"{progress*100:.1f}%")
        
        # 时间显示
        current_time = int(self.metrics['simulation_time'])
        total_time = self.sim_params['duration']
        time_str = f"{current_time//3600:02d}:{(current_time%3600)//60:02d}:{current_time%60:02d} / {total_time//3600:02d}:{(total_time%3600)//60:02d}:{total_time%60:02d}"
        dpg.set_value("time_display", time_str)
        
        # 指标文本
        dpg.set_value("active_vehicles", f"Active Vehicles: {self.metrics['active_vehicles']}")
        dpg.set_value("avg_battery", f"Average Battery: {self.metrics['avg_battery']:.1f}%")
        dpg.set_value("vehicle_util", f"Vehicle Utilization: {self.metrics['vehicle_utilization']:.1f}%")
        
        dpg.set_value("pending_orders", f"Pending Orders: {self.metrics['pending_orders']}")
        dpg.set_value("active_orders", f"Active Orders: {self.metrics['active_orders']}")
        dpg.set_value("completed_orders", f"Completed Orders: {self.metrics['completed_orders']}")
        
        dpg.set_value("total_revenue", f"Total Revenue: ${self.metrics['total_revenue']:.2f}")
        
        # 计算每小时收入
        if self.metrics['simulation_time'] > 0:
            revenue_per_hour = self.metrics['total_revenue'] / (self.metrics['simulation_time'] / 3600)
            dpg.set_value("revenue_hour", f"Revenue/Hour: ${revenue_per_hour:.2f}")

    def update_map_display(self):
        """更新地图显示"""
        if not self.map_ax or not self.simulation_engine:
            return
        
        # 清除旧的动态元素
        self.map_ax.clear()
        
        # 重新绘制地图
        self.map_manager.setup_plot(show_preview=False)
        
        # 添加车辆、订单等动态元素
        # (这里可以调用现有的visualizer方法)
        
        # 更新纹理
        self.update_map_texture()

    def zoom_in(self):
        """地图放大"""
        print("🔍 Zoom in")

    def zoom_out(self):
        """地图缩小"""
        print("🔍 Zoom out")

    def reset_view(self):
        """重置地图视图"""
        print("🏠 Reset view")

    def run(self):
        """运行UI"""
        self.create_context()
        self.setup_ui()
        
        # 设置主窗口为全屏
        dpg.set_primary_window("main_window", True)
        
        # 显示视窗
        dpg.show_viewport()
        
        # 启动DearPyGui
        dpg.start_dearpygui()
        
        # 清理
        dpg.destroy_context()


def main():
    """主函数"""
    print("🚀 Starting EV Simulation UI...")
    
    app = SimulationUI()
    app.run()


if __name__ == "__main__":
    main() 