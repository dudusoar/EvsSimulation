"""
数据管理模块
负责仿真数据的保存、加载和报告生成
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import seaborn as sns


class DataManager:
    """数据管理器类"""
    
    def __init__(self, output_dir: str = 'outputs/simulation_results'):
        """
        初始化数据管理器
        
        参数:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        
        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 创建本次运行的子目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = os.path.join(output_dir, f"run_{timestamp}")
        os.makedirs(self.run_dir)
        
        # 数据存储
        self.time_series_data = []
        self.event_log = []
    
    # ============= 数据记录方法 =============
    def record_state(self, state: Dict, timestamp: float):
        """
        记录仿真状态
        
        参数:
            state: 状态数据
            timestamp: 时间戳
        """
        state_record = {
            'timestamp': timestamp,
            **state
        }
        self.time_series_data.append(state_record)
    
    def log_event(self, event_type: str, event_data: Dict, timestamp: float):
        """
        记录事件
        
        参数:
            event_type: 事件类型
            event_data: 事件数据
            timestamp: 时间戳
        """
        event = {
            'timestamp': timestamp,
            'type': event_type,
            'data': event_data
        }
        self.event_log.append(event)
    
    # ============= 数据保存方法 =============
    def save_simulation_results(self, final_stats: Dict):
        """
        保存仿真结果
        
        参数:
            final_stats: 最终统计数据
        """
        # 保存最终统计
        stats_file = os.path.join(self.run_dir, 'final_statistics.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(final_stats, f, indent=2, ensure_ascii=False)
        
        # 保存时间序列数据
        if self.time_series_data:
            df = pd.DataFrame(self.time_series_data)
            df.to_csv(os.path.join(self.run_dir, 'time_series.csv'), index=False)
        
        # 保存事件日志
        if self.event_log:
            events_file = os.path.join(self.run_dir, 'event_log.json')
            with open(events_file, 'w', encoding='utf-8') as f:
                json.dump(self.event_log, f, indent=2, ensure_ascii=False)
        
        # 保存车辆详情
        if 'vehicle_details' in final_stats:
            vehicle_df = pd.DataFrame(final_stats['vehicle_details'])
            vehicle_df.to_csv(os.path.join(self.run_dir, 'vehicle_details.csv'), index=False)
        
        # 保存充电站详情
        if 'station_details' in final_stats:
            station_df = pd.DataFrame(final_stats['station_details'])
            station_df.to_csv(os.path.join(self.run_dir, 'station_details.csv'), index=False)
        
        print(f"数据已保存到: {self.run_dir}")
    
    # ============= 报告生成方法 =============
    def generate_report(self, final_stats: Dict) -> str:
        """
        生成仿真报告
        
        参数:
            final_stats: 最终统计数据
        
        返回:
            报告文件路径
        """
        # 创建报告
        report_lines = [
            "# 电车司机仿真系统报告",
            f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\n## 1. 仿真概览",
            f"- 仿真时长: {final_stats['summary']['total_simulation_time']:.1f} 秒",
            f"- 车辆数量: {final_stats['vehicles']['total_vehicles']} 辆",
            f"- 充电站数量: {final_stats['charging']['total_stations']} 个",
            f"- 总订单数: {final_stats['orders']['total_orders_created']} 个",
            
            "\n## 2. 运营指标",
            f"- 订单完成率: {final_stats['summary']['order_completion_rate']*100:.1f}%",
            f"- 车辆利用率: {final_stats['summary']['vehicle_utilization_rate']*100:.1f}%",
            f"- 充电站利用率: {final_stats['summary']['charging_utilization_rate']*100:.1f}%",
            f"- 平均等待时间: {final_stats['orders']['avg_waiting_time']:.1f} 秒",
            f"- 平均行程时间: {final_stats['orders']['avg_trip_time']:.1f} 秒",
            
            "\n## 3. 财务指标",
            f"- 总收入: ¥{final_stats['summary']['total_revenue']:.2f}",
            f"- 总成本: ¥{final_stats['summary']['total_cost']:.2f}",
            f"- 总利润: ¥{final_stats['summary']['total_profit']:.2f}",
            f"- 平均订单价格: ¥{final_stats['orders']['avg_price']:.2f}",
            f"- 每车平均收入: ¥{final_stats['vehicles']['avg_revenue_per_vehicle']:.2f}",
            
            "\n## 4. 车辆统计",
            f"- 平均行驶距离: {final_stats['vehicles']['avg_distance_traveled']:.1f} km",
            f"- 平均完成订单: {final_stats['vehicles']['avg_orders_completed']:.1f} 个",
            f"- 平均电池水平: {final_stats['vehicles']['avg_battery_percentage']:.1f}%",
            
            "\n## 5. 充电站统计",
            f"- 总供电量: {final_stats['charging']['total_energy_delivered']:.1f} kWh",
            f"- 充电总收入: ¥{final_stats['charging']['total_revenue']:.2f}",
            f"- 服务车辆总数: {final_stats['charging']['total_vehicles_served']} 辆次",
        ]
        
        # 保存报告
        report_file = os.path.join(self.run_dir, 'simulation_report.md')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        # 生成图表
        self._generate_charts(final_stats)
        
        print(f"报告已生成: {report_file}")
        return report_file
    
    def _generate_charts(self, final_stats: Dict):
        """生成统计图表"""
        # 设置绘图风格
        plt.style.use('seaborn-v0_8-darkgrid')
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
        
        # 1. 车辆收入分布图
        if 'vehicle_details' in final_stats:
            vehicle_df = pd.DataFrame(final_stats['vehicle_details'])
            
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            
            # 收入分布
            axes[0, 0].hist(vehicle_df['total_revenue'], bins=15, edgecolor='black')
            axes[0, 0].set_title('Vehicle Revenue Distribution')
            axes[0, 0].set_xlabel('Revenue (¥)')
            axes[0, 0].set_ylabel('Number of Vehicles')
            
            # 订单数分布
            axes[0, 1].hist(vehicle_df['total_orders'], bins=15, edgecolor='black')
            axes[0, 1].set_title('Orders Completed Distribution')
            axes[0, 1].set_xlabel('Number of Orders')
            axes[0, 1].set_ylabel('Number of Vehicles')
            
            # 行驶距离分布
            axes[1, 0].hist(vehicle_df['total_distance'], bins=15, edgecolor='black')
            axes[1, 0].set_title('Distance Traveled Distribution')
            axes[1, 0].set_xlabel('Distance (km)')
            axes[1, 0].set_ylabel('Number of Vehicles')
            
            # 利润分布
            axes[1, 1].hist(vehicle_df['profit'], bins=15, edgecolor='black')
            axes[1, 1].set_title('Profit Distribution')
            axes[1, 1].set_xlabel('Profit (¥)')
            axes[1, 1].set_ylabel('Number of Vehicles')
            
            plt.tight_layout()
            plt.savefig(os.path.join(self.run_dir, 'vehicle_statistics.png'))
            plt.close()
        
        # 2. 充电站利用率图
        if 'station_details' in final_stats:
            station_df = pd.DataFrame(final_stats['station_details'])
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # 充电站收入对比
            ax.bar(station_df['station_id'], station_df['total_revenue'])
            ax.set_title('Charging Station Revenue')
            ax.set_xlabel('Station ID')
            ax.set_ylabel('Revenue (¥)')
            ax.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            plt.savefig(os.path.join(self.run_dir, 'charging_station_revenue.png'))
            plt.close()
    
    # ============= 数据导出方法 =============
    def export_to_excel(self, final_stats: Dict):
        """
        导出数据到Excel文件
        
        参数:
            final_stats: 最终统计数据
        """
        excel_file = os.path.join(self.run_dir, 'simulation_results.xlsx')
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # 概览页
            summary_df = pd.DataFrame([final_stats['summary']])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # 车辆详情页
            if 'vehicle_details' in final_stats:
                vehicle_df = pd.DataFrame(final_stats['vehicle_details'])
                vehicle_df.to_excel(writer, sheet_name='Vehicles', index=False)
            
            # 充电站详情页
            if 'station_details' in final_stats:
                station_df = pd.DataFrame(final_stats['station_details'])
                station_df.to_excel(writer, sheet_name='Charging Stations', index=False)
            
            # 订单统计页
            orders_df = pd.DataFrame([final_stats['orders']])
            orders_df.to_excel(writer, sheet_name='Orders', index=False)
        
        print(f"Excel文件已导出: {excel_file}")
    
    # ============= 数据加载方法 =============
    def load_simulation_results(self, run_dir: str) -> Dict:
        """
        加载之前的仿真结果
        
        参数:
            run_dir: 运行目录
        
        返回:
            仿真结果数据
        """
        results = {}
        
        # 加载最终统计
        stats_file = os.path.join(run_dir, 'final_statistics.json')
        if os.path.exists(stats_file):
            with open(stats_file, 'r', encoding='utf-8') as f:
                results['final_stats'] = json.load(f)
        
        # 加载时间序列数据
        time_series_file = os.path.join(run_dir, 'time_series.csv')
        if os.path.exists(time_series_file):
            results['time_series'] = pd.read_csv(time_series_file)
        
        # 加载车辆详情
        vehicle_file = os.path.join(run_dir, 'vehicle_details.csv')
        if os.path.exists(vehicle_file):
            results['vehicle_details'] = pd.read_csv(vehicle_file)
        
        return results