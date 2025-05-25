"""
地图管理模块
负责加载OSM地图数据、路径规划、节点管理等地图相关功能
继承并优化原有的osm_request.py和graph_search.py功能
"""

import os
import random
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional, Dict
import numpy as np
from utils.path_utils import decompose_path


class MapManager:
    """地图管理器类"""
    
    def __init__(self, location: str, cache_dir: str = 'datasets/maps'):
        """
        初始化地图管理器
        
        参数:
            location: 地理位置查询字符串
            cache_dir: 缓存目录
        """
        self.location = location
        self.cache_dir = cache_dir
        
        # 创建缓存目录
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        
        # 加载地图
        self.graph = self._load_graph()
        self.projected_graph = ox.project_graph(self.graph)
        
        # 缓存节点位置
        self._node_positions = {}
        self._cache_node_positions()
        
        # 图形对象（用于可视化）
        self.fig = None
        self.ax = None
    
    # ============= 地图加载方法 =============
    def _load_graph(self) -> nx.MultiDiGraph:
        """加载地图图形"""
        # 构造缓存文件名
        graph_filename = self.location.lower().replace(',', '').replace(' ', '_') + '.graphml'
        graph_path = os.path.join(self.cache_dir, graph_filename)
        
        # 尝试从缓存加载
        if os.path.exists(graph_path):
            print(f"从缓存加载地图: {graph_path}")
            return ox.load_graphml(graph_path)
        
        # 从OSM下载
        print(f"从OpenStreetMap下载地图: {self.location}")
        try:
            graph = ox.graph_from_place(
                query=self.location,
                network_type='drive',
                simplify=True
            )
            # 保存到缓存
            ox.save_graphml(graph, graph_path)
            return graph
        except Exception as e:
            raise Exception(f"无法获取地图 {self.location}: {str(e)}")
    
    def _cache_node_positions(self):
        """缓存所有节点的位置"""
        for node in self.projected_graph.nodes():
            self._node_positions[node] = (
                self.projected_graph.nodes[node]['x'],
                self.projected_graph.nodes[node]['y']
            )
    
    # ============= 节点管理方法 =============
    def get_all_nodes(self) -> List[int]:
        """获取所有节点ID"""
        return list(self.projected_graph.nodes())
    
    def get_random_nodes(self, n: int) -> List[int]:
        """获取n个随机节点"""
        all_nodes = self.get_all_nodes()
        return random.sample(all_nodes, min(n, len(all_nodes)))
    
    def get_node_position(self, node_id: int) -> Tuple[float, float]:
        """获取节点位置"""
        return self._node_positions.get(node_id, (0.0, 0.0))
    
    def find_nearest_node(self, position: Tuple[float, float]) -> int:
        """找到离给定位置最近的节点"""
        x, y = position
        # 使用原始图（经纬度）进行查找
        return ox.nearest_nodes(self.graph, x, y)
    
    # ============= 路径规划方法 =============
    def get_shortest_path_nodes(self, origin: int, destination: int) -> List[int]:
        """获取最短路径的节点列表"""
        try:
            return nx.shortest_path(
                self.projected_graph,
                origin,
                destination,
                weight='length'
            )
        except nx.NetworkXNoPath:
            return []
    
    def get_shortest_path_points(self, origin: int, destination: int) -> List[Tuple[float, float]]:
        """获取最短路径的详细坐标点"""
        # 获取路径节点
        route_nodes = self.get_shortest_path_nodes(origin, destination)
        if not route_nodes:
            return []
        
        # 将节点路径转换为详细坐标点
        path_lines = []
        edge_nodes = list(zip(route_nodes[:-1], route_nodes[1:]))
        
        for u, v in edge_nodes:
            # 获取两节点间的边数据
            edge_data = self.projected_graph.get_edge_data(u, v)
            if edge_data:
                # 选择最短的边
                edge = min(edge_data.values(), key=lambda x: x.get('length', float('inf')))
                
                # 检查是否有详细几何信息
                if 'geometry' in edge:
                    xs, ys = edge['geometry'].xy
                    path_lines.append(list(zip(xs, ys)))
                else:
                    # 直线连接
                    p1 = self.get_node_position(u)
                    p2 = self.get_node_position(v)
                    path_lines.append([p1, p2])
        
        # 分解为连续路径点
        return decompose_path(path_lines)
    
    def calculate_route_distance(self, origin: int, destination: int) -> float:
        """计算路径距离（米）"""
        try:
            return nx.shortest_path_length(
                self.projected_graph,
                origin,
                destination,
                weight='length'
            )
        except nx.NetworkXNoPath:
            return float('inf')
    
    # ============= 充电站相关方法 =============
    def select_charging_station_nodes(self, n: int) -> List[int]:
        """
        选择n个节点作为充电站位置
        尽量选择分布均匀的节点
        """
        all_nodes = self.get_all_nodes()
        
        if n >= len(all_nodes):
            return all_nodes
        
        # 使用K-means思想选择分散的节点
        selected_nodes = []
        remaining_nodes = all_nodes.copy()
        
        # 选择第一个节点（随机）
        first_node = random.choice(remaining_nodes)
        selected_nodes.append(first_node)
        remaining_nodes.remove(first_node)
        
        # 选择剩余节点（最大化最小距离）
        while len(selected_nodes) < n and remaining_nodes:
            max_min_distance = -1
            best_node = None
            
            for node in remaining_nodes[:100]:  # 限制搜索范围以提高效率
                # 计算到已选节点的最小距离
                min_distance = float('inf')
                node_pos = self.get_node_position(node)
                
                for selected in selected_nodes:
                    selected_pos = self.get_node_position(selected)
                    distance = np.sqrt(
                        (node_pos[0] - selected_pos[0])**2 + 
                        (node_pos[1] - selected_pos[1])**2
                    )
                    min_distance = min(min_distance, distance)
                
                # 选择最小距离最大的节点
                if min_distance > max_min_distance:
                    max_min_distance = min_distance
                    best_node = node
            
            if best_node:
                selected_nodes.append(best_node)
                remaining_nodes.remove(best_node)
        
        return selected_nodes
    
    def find_nearest_nodes(self, position: Tuple[float, float], n: int = 5) -> List[Tuple[int, float]]:
        """
        找到离给定位置最近的n个节点
        返回: [(节点ID, 距离), ...]
        """
        distances = []
        for node_id, node_pos in self._node_positions.items():
            distance = np.sqrt(
                (position[0] - node_pos[0])**2 + 
                (position[1] - node_pos[1])**2
            )
            distances.append((node_id, distance))
        
        # 排序并返回最近的n个
        distances.sort(key=lambda x: x[1])
        return distances[:n]
    
    # ============= 可视化方法 =============
    def setup_plot(self, show_preview: bool = False) -> Tuple[plt.Figure, plt.Axes]:
        """设置地图绘图"""
        self.fig, self.ax = ox.plot_graph(
            self.projected_graph,
            node_size=0,
            edge_linewidth=0.5,
            show=show_preview,
            close=False,
            bgcolor='white',
            edge_color='gray'
        )
        self.ax.set_title(self.location)
        return self.fig, self.ax
    
    def plot_route(self, route_nodes: List[int], color: str = 'red', linewidth: float = 2):
        """在地图上绘制路径"""
        if not self.ax or len(route_nodes) < 2:
            return
        
        # 获取路径坐标
        x_coords = [self._node_positions[node][0] for node in route_nodes]
        y_coords = [self._node_positions[node][1] for node in route_nodes]
        
        # 绘制路径
        self.ax.plot(x_coords, y_coords, color=color, linewidth=linewidth, alpha=0.7)
    
    # ============= 信息获取方法 =============
    def get_map_info(self) -> Dict:
        """获取地图信息"""
        return {
            'location': self.location,
            'num_nodes': self.projected_graph.number_of_nodes(),
            'num_edges': self.projected_graph.number_of_edges(),
            'graph_area': ox.project_graph(self.graph).graph.get('area', 0)
        }