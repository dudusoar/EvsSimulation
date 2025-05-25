"""
几何计算工具模块
提供向量计算、距离计算等几何相关的工具函数
"""

import numpy as np
from typing import Tuple, List
import math


# ============= 向量计算 =============
def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """计算两点之间的欧氏距离"""
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    return np.sqrt(dx**2 + dy**2)


def calculate_vector(from_point: Tuple[float, float], to_point: Tuple[float, float]) -> Tuple[float, float]:
    """计算从一点到另一点的向量"""
    return (to_point[0] - from_point[0], to_point[1] - from_point[1])


def normalize_vector(vector: Tuple[float, float]) -> Tuple[float, float]:
    """归一化向量"""
    magnitude = np.sqrt(vector[0]**2 + vector[1]**2)
    if magnitude > 0:
        return (vector[0] / magnitude, vector[1] / magnitude)
    return (0.0, 0.0)


def calculate_angle(vector1: Tuple[float, float], vector2: Tuple[float, float]) -> float:
    """计算两个向量之间的夹角（弧度）"""
    # 归一化向量
    v1_norm = normalize_vector(vector1)
    v2_norm = normalize_vector(vector2)
    
    # 计算点积
    dot_product = v1_norm[0] * v2_norm[0] + v1_norm[1] * v2_norm[1]
    
    # 限制在[-1, 1]范围内避免数值误差
    dot_product = np.clip(dot_product, -1.0, 1.0)
    
    # 计算夹角
    angle = np.arccos(dot_product)
    return angle


# ============= 路径计算 =============
def calculate_path_length(path_points: List[Tuple[float, float]]) -> float:
    """计算路径总长度"""
    if len(path_points) < 2:
        return 0.0
    
    total_length = 0.0
    for i in range(len(path_points) - 1):
        total_length += calculate_distance(path_points[i], path_points[i + 1])
    
    return total_length


def find_closest_point_on_path(position: Tuple[float, float], 
                              path_points: List[Tuple[float, float]]) -> Tuple[int, float]:
    """
    找到路径上离给定位置最近的点
    返回：(最近点的索引, 到最近点的距离)
    """
    if not path_points:
        return -1, float('inf')
    
    min_distance = float('inf')
    closest_index = 0
    
    for i, point in enumerate(path_points):
        distance = calculate_distance(position, point)
        if distance < min_distance:
            min_distance = distance
            closest_index = i
    
    return closest_index, min_distance


def interpolate_position(point1: Tuple[float, float], 
                        point2: Tuple[float, float], 
                        ratio: float) -> Tuple[float, float]:
    """
    在两点之间插值
    ratio: 0.0 表示point1, 1.0 表示point2
    """
    ratio = np.clip(ratio, 0.0, 1.0)
    x = point1[0] + (point2[0] - point1[0]) * ratio
    y = point1[1] + (point2[1] - point1[1]) * ratio
    return (x, y)


# ============= 位置判断 =============
def is_point_near_target(position: Tuple[float, float], 
                        target: Tuple[float, float], 
                        threshold: float = 10.0) -> bool:
    """判断点是否接近目标位置"""
    return calculate_distance(position, target) <= threshold


def calculate_direction_to_target(current_pos: Tuple[float, float], 
                                 target_pos: Tuple[float, float]) -> Tuple[float, float]:
    """计算从当前位置到目标位置的单位方向向量"""
    direction = calculate_vector(current_pos, target_pos)
    return normalize_vector(direction)


# ============= 坐标转换 =============
def meters_to_degrees(meters: float, latitude: float = 40.4237) -> Tuple[float, float]:
    """
    将米转换为经纬度偏移
    latitude: 参考纬度（默认为West Lafayette附近）
    返回: (经度偏移, 纬度偏移)
    """
    # 地球半径（米）
    earth_radius = 6371000.0
    
    # 纬度偏移
    lat_offset = meters / earth_radius * (180.0 / math.pi)
    
    # 经度偏移（考虑纬度的影响）
    lon_offset = meters / (earth_radius * math.cos(math.radians(latitude))) * (180.0 / math.pi)
    
    return (lon_offset, lat_offset)


def degrees_to_meters(lon_diff: float, lat_diff: float, latitude: float = 40.4237) -> float:
    """
    将经纬度差转换为米
    返回两点之间的距离（米）
    """
    earth_radius = 6371000.0
    
    # 纬度差对应的距离
    lat_distance = lat_diff * (math.pi / 180.0) * earth_radius
    
    # 经度差对应的距离（考虑纬度的影响）
    lon_distance = lon_diff * (math.pi / 180.0) * earth_radius * math.cos(math.radians(latitude))
    
    # 总距离
    return np.sqrt(lat_distance**2 + lon_distance**2)