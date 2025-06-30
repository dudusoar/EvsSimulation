#!/usr/bin/env python3
"""
DearPyGui仿真界面演示
展示基本界面布局和控件功能
"""

import dearpygui.dearpygui as dpg
import math
import random
import time
import threading

class DemoSimulationUI:
    """演示版仿真界面"""
    
    def __init__(self):
        self.is_running = False
        self.is_paused = False
        self.simulation_time = 0.0
        self.demo_thread = None
        
        # 演示数据
        self.metrics = {
            'vehicles': 20,
            'orders': 15,
            'revenue': 1250.75,
            'battery': 85.5
        }

    def setup_ui(self):
        """设置UI界面"""
        
        # 创建主窗口
        with dpg.window(label="电动车仿真系统演示", tag="main_window"):
            
            # 水平布局：三面板设计
            with dpg.group(horizontal=True):
                
                # 左侧：参数控制面板
                with dpg.child_window(label="参数控制", width=300, height=600, border=True):
                    dpg.add_text("🔧 仿真参数配置", color=[100, 200, 255])
                    dpg.add_separator()
                    
                    dpg.add_text("基础参数：")
                    dpg.add_slider_int(label="仿真时长(秒)", default_value=3600, 
                                     min_value=300, max_value=7200, tag="duration")
                    dpg.add_slider_int(label="车辆数量", default_value=20, 
                                     min_value=5, max_value=50, tag="vehicles")
                    dpg.add_slider_int(label="充电站数量", default_value=8, 
                                     min_value=3, max_value=20, tag="stations")
                    
                    dpg.add_separator()
                    dpg.add_text("车辆配置：")
                    dpg.add_slider_float(label="行驶速度(m/s)", default_value=15.0, 
                                       min_value=5.0, max_value=30.0, format="%.1f")
                    dpg.add_slider_float(label="电池容量(kWh)", default_value=75.0, 
                                       min_value=40.0, max_value=100.0, format="%.1f")
                    
                    dpg.add_separator()
                    dpg.add_text("地图选择：")
                    dpg.add_combo(label="位置", 
                                items=["West Lafayette, IN", "New York City, NY", "San Francisco, CA"],
                                default_value="West Lafayette, IN")
                    
                    dpg.add_separator()
                    dpg.add_button(label="🚀 初始化仿真", callback=self.initialize_demo, 
                                 width=-1, height=50)
                
                # 中央：地图显示区域
                with dpg.child_window(label="地图视图", width=700, height=600, border=True):
                    dpg.add_text("🗺️ 实时地图显示", color=[100, 255, 100])
                    dpg.add_separator()
                    
                    # 地图工具栏
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="🔍+", callback=lambda: print("放大"))
                        dpg.add_button(label="🔍-", callback=lambda: print("缩小"))
                        dpg.add_button(label="🏠", callback=lambda: print("重置视图"))
                        dpg.add_button(label="🔄", callback=lambda: print("刷新地图"))
                    
                    dpg.add_separator()
                    
                    # 地图显示区域（使用绘图演示）
                    with dpg.plot(label="地图", height=400, width=-1, tag="map_plot"):
                        dpg.add_plot_axis(dpg.mvXAxis, label="经度", tag="x_axis")
                        dpg.add_plot_axis(dpg.mvYAxis, label="纬度", tag="y_axis")
                        
                        # 添加一些演示数据点
                        self.create_demo_map_data()
                    
                    dpg.add_text("地图状态：已就绪", tag="map_status")
                
                # 右侧：指标监控面板
                with dpg.child_window(label="实时指标", width=300, height=600, border=True):
                    dpg.add_text("📊 关键性能指标", color=[255, 200, 100])
                    dpg.add_separator()
                    
                    dpg.add_text("仿真进度：")
                    dpg.add_progress_bar(tag="progress", default_value=0.0, overlay="0%")
                    dpg.add_text("00:00:00 / 01:00:00", tag="time_display")
                    
                    dpg.add_separator()
                    dpg.add_text("车队状态：")
                    dpg.add_text("活跃车辆：20", tag="active_vehicles")
                    dpg.add_text("平均电量：85.5%", tag="avg_battery")
                    dpg.add_text("车辆利用率：72.3%", tag="utilization")
                    
                    dpg.add_separator()
                    dpg.add_text("订单管理：")
                    dpg.add_text("待处理：5", tag="pending_orders")
                    dpg.add_text("进行中：8", tag="active_orders") 
                    dpg.add_text("已完成：42", tag="completed_orders")
                    
                    dpg.add_separator()
                    dpg.add_text("财务表现：")
                    dpg.add_text("总收入：$1,250.75", tag="total_revenue")
                    dpg.add_text("时收入：$312.19", tag="hourly_revenue")
                    
                    dpg.add_separator()
                    
                    # 性能图表
                    with dpg.plot(label="性能趋势", height=150, width=-1, tag="metrics_plot"):
                        dpg.add_plot_axis(dpg.mvXAxis, label="时间", tag="mx_axis")
                        dpg.add_plot_axis(dpg.mvYAxis, label="数值", tag="my_axis")
            
            dpg.add_separator()
            
            # 底部：仿真控制面板
            with dpg.group(horizontal=True):
                dpg.add_text("🎮 仿真控制：", color=[255, 255, 100])
                
                dpg.add_button(label="▶️ 开始", callback=self.start_demo, 
                             tag="start_btn", width=80, height=35)
                dpg.add_button(label="⏸️ 暂停", callback=self.pause_demo, 
                             tag="pause_btn", width=80, height=35, enabled=False)
                dpg.add_button(label="⏹️ 停止", callback=self.stop_demo, 
                             tag="stop_btn", width=80, height=35, enabled=False)
                dpg.add_button(label="🔄 重置", callback=self.reset_demo, 
                             tag="reset_btn", width=80, height=35)
                
                dpg.add_text("速度：")
                dpg.add_slider_float(label="", default_value=1.0, min_value=0.1, max_value=5.0,
                                   format="%.1fx", width=120, callback=self.adjust_speed)

    def create_demo_map_data(self):
        """创建演示地图数据"""
        # 模拟车辆位置
        vehicle_x = [random.uniform(-86.95, -86.90) for _ in range(10)]
        vehicle_y = [random.uniform(40.40, 40.45) for _ in range(10)]
        
        # 模拟充电站位置
        station_x = [random.uniform(-86.95, -86.90) for _ in range(5)]
        station_y = [random.uniform(40.40, 40.45) for _ in range(5)]
        
        # 添加到图表
        dpg.add_scatter_series(vehicle_x, vehicle_y, label="车辆", parent="y_axis", tag="vehicles_series")
        dpg.add_scatter_series(station_x, station_y, label="充电站", parent="y_axis", tag="stations_series")

    def initialize_demo(self):
        """初始化演示"""
        print("🔧 正在初始化仿真演示...")
        dpg.set_value("map_status", "正在初始化...")
        
        # 模拟初始化过程
        import time
        time.sleep(1)
        
        dpg.set_value("map_status", "已就绪 - West Lafayette, IN")
        print("✅ 演示初始化完成！")

    def start_demo(self):
        """开始演示"""
        print("🚀 开始仿真演示")
        self.is_running = True
        self.is_paused = False
        
        # 更新按钮状态
        dpg.configure_item("start_btn", enabled=False)
        dpg.configure_item("pause_btn", enabled=True)
        dpg.configure_item("stop_btn", enabled=True)
        
        # 启动演示线程
        self.demo_thread = threading.Thread(target=self.demo_loop, daemon=True)
        self.demo_thread.start()

    def pause_demo(self):
        """暂停/恢复演示"""
        self.is_paused = not self.is_paused
        if self.is_paused:
            dpg.set_item_label("pause_btn", "▶️ 恢复")
            print("⏸️ 仿真暂停")
        else:
            dpg.set_item_label("pause_btn", "⏸️ 暂停")
            print("▶️ 仿真恢复")

    def stop_demo(self):
        """停止演示"""
        print("⏹️ 停止仿真演示")
        self.is_running = False
        self.is_paused = False
        
        # 重置按钮状态
        dpg.configure_item("start_btn", enabled=True)
        dpg.configure_item("pause_btn", enabled=False)
        dpg.configure_item("stop_btn", enabled=False)
        dpg.set_item_label("pause_btn", "⏸️ 暂停")

    def reset_demo(self):
        """重置演示"""
        self.stop_demo()
        self.simulation_time = 0.0
        self.update_metrics_display()
        print("🔄 演示已重置")

    def adjust_speed(self, sender, value):
        """调整仿真速度"""
        print(f"🏃 仿真速度：{value:.1f}x")

    def demo_loop(self):
        """演示主循环"""
        while self.is_running:
            if not self.is_paused:
                # 更新仿真时间
                self.simulation_time += 1.0
                
                # 更新演示数据
                self.update_demo_data()
                
                # 更新UI显示
                self.update_metrics_display()
                
                # 检查是否完成
                max_time = dpg.get_value("duration")
                if self.simulation_time >= max_time:
                    self.stop_demo()
                    break
            
            time.sleep(0.1)

    def update_demo_data(self):
        """更新演示数据"""
        # 模拟数据变化
        self.metrics['vehicles'] = random.randint(18, 22)
        self.metrics['orders'] = random.randint(10, 20)
        self.metrics['revenue'] += random.uniform(0.5, 2.0)
        self.metrics['battery'] = max(20, min(100, self.metrics['battery'] + random.uniform(-1, 1)))

    def update_metrics_display(self):
        """更新指标显示"""
        # 更新进度
        max_time = dpg.get_value("duration")
        progress = self.simulation_time / max_time
        dpg.set_value("progress", progress)
        dpg.configure_item("progress", overlay=f"{progress*100:.1f}%")
        
        # 更新时间显示
        current = int(self.simulation_time)
        total = int(max_time)
        time_str = f"{current//3600:02d}:{(current%3600)//60:02d}:{current%60:02d} / {total//3600:02d}:{(total%3600)//60:02d}:{total%60:02d}"
        dpg.set_value("time_display", time_str)
        
        # 更新指标
        dpg.set_value("active_vehicles", f"活跃车辆：{self.metrics['vehicles']}")
        dpg.set_value("avg_battery", f"平均电量：{self.metrics['battery']:.1f}%")
        dpg.set_value("total_revenue", f"总收入：${self.metrics['revenue']:.2f}")

    def run(self):
        """运行演示"""
        dpg.create_context()
        
        # 设置主题
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (22, 22, 22))
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (30, 30, 30))
                dpg.add_theme_color(dpg.mvThemeCol_Button, (51, 122, 183))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (71, 142, 203))
        
        dpg.bind_theme(global_theme)
        
        self.setup_ui()
        
        dpg.create_viewport(title="DearPyGui 电动车仿真演示", width=1400, height=800)
        dpg.setup_dearpygui()
        dpg.set_primary_window("main_window", True)
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()


def main():
    """主函数"""
    print("🚀 启动DearPyGui仿真界面演示...")
    demo = DemoSimulationUI()
    demo.run()


if __name__ == "__main__":
    main() 