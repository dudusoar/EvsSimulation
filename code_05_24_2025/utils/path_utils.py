"""
路径处理工具模块
提供路径分解、合并等路径相关的工具函数
"""

from typing import List, Tuple
import numpy as np


def decompose_path(lines: List[List[Tuple[float, float]]]) -> List[Tuple[float, float]]:
    """
    将OpenStreetMap的几何路径（多段线）分解为连续的坐标点列表
    
    参数:
        lines: 多段线列表，每段线是坐标点列表
    
    返回:
        连续的坐标点列表
    """
    if not lines:
        return []
    
    path = []
    for line in lines:
        for point in line:
            path.append(point)
    
    # 去除重复点
    clean_path = []
    if path:
        for i in range(len(path)):
            if i == 0 or path[i] != path[i-1]:
                clean_path.append(path[i])
    
    return clean_path


def simplify_path(path_points: List[Tuple[float, float]], tolerance: float = 5.0) -> List[Tuple[float, float]]:
    """
    简化路径，移除不必要的中间点
    使用Douglas-Peucker算法
    
    参数:
        path_points: 原始路径点列表
        tolerance: 容差（米）
    
    返回:
        简化后的路径点列表
    """
    if len(path_points) <= 2:
        return path_points
    
    # Douglas-Peucker算法实现
    def perpendicular_distance(point: Tuple[float, float], 
                             line_start: Tuple[float, float], 
                             line_end: Tuple[float, float]) -> float:
        """计算点到线段的垂直距离"""
        x0, y0 = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        # 如果线段退化为点
        if x1 == x2 and y1 == y2:
            return np.sqrt((x0 - x1)**2 + (y0 - y1)**2)
        
        # 计算垂直距离
        numerator = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
        denominator = np.sqrt((y2 - y1)**2 + (x2 - x1)**2)
        
        return numerator / denominator if denominator > 0 else 0
    
    def douglas_peucker(points: List[Tuple[float, float]], epsilon: float) -> List[Tuple[float, float]]:
        """Douglas-Peucker递归实现"""
        if len(points) <= 2:
            return points
        
        # 找到距离最大的点
        max_distance = 0
        max_index = 0
        
        for i in range(1, len(points) - 1):
            distance = perpendicular_distance(points[i], points[0], points[-1])
            if distance > max_distance:
                max_distance = distance
                max_index = i
        
        # 如果最大距离大于阈值，递归处理
        if max_distance > epsilon:
            left_part = douglas_peucker(points[:max_index + 1], epsilon)
            right_part = douglas_peucker(points[max_index:], epsilon)
            return left_part[:-1] + right_part
        else:
            return [points[0], points[-1]]
    
    return douglas_peucker(path_points, tolerance)


def resample_path(path_points: List[Tuple[float, float]], 
                  target_spacing: float = 50.0) -> List[Tuple[float, float]]:
    """
    重新采样路径，使路径点之间的间距大致相等
    
    参数:
        path_points: 原始路径点列表
        target_spacing: 目标间距（米）
    
    返回:
        重新采样后的路径点列表
    """
    if len(path_points) < 2:
        return path_points
    
    resampled = [path_points[0]]
    accumulated_distance = 0.0
    
    for i in range(1, len(path_points)):
        prev_point = path_points[i - 1]
        curr_point = path_points[i]
        
        # 计算当前段的长度
        segment_length = np.sqrt((curr_point[0] - prev_point[0])**2 + 
                               (curr_point[1] - prev_point[1])**2)
        
        if accumulated_distance + segment_length >= target_spacing:
            # 需要在这一段上添加点
            remaining_distance = target_spacing - accumulated_distance
            
            while remaining_distance <= segment_length:
                # 计算插值比例
                ratio = remaining_distance / segment_length
                
                # 插值新点
                new_x = prev_point[0] + ratio * (curr_point[0] - prev_point[0])
                new_y = prev_point[1] + ratio * (curr_point[1] - prev_point[1])
                resampled.append((new_x, new_y))
                
                # 更新距离
                remaining_distance += target_spacing
            
            # 更新累积距离
            accumulated_distance = segment_length - (remaining_distance - target_spacing)
        else:
            accumulated_distance += segment_length
    
    # 添加最后一个点
    if resampled[-1] != path_points[-1]:
        resampled.append(path_points[-1])
    
    return resampled


def merge_close_points(path_points: List[Tuple[float, float]], 
                      min_distance: float = 1.0) -> List[Tuple[float, float]]:
    """
    合并过于接近的路径点
    
    参数:
        path_points: 原始路径点列表
        min_distance: 最小距离阈值（米）
    
    返回:
        合并后的路径点列表
    """
    if len(path_points) <= 1:
        return path_points
    
    merged = [path_points[0]]
    
    for i in range(1, len(path_points)):
        curr_point = path_points[i]
        last_merged = merged[-1]
        
        # 计算距离
        distance = np.sqrt((curr_point[0] - last_merged[0])**2 + 
                         (curr_point[1] - last_merged[1])**2)
        
        # 只有距离足够大时才添加
        if distance >= min_distance:
            merged.append(curr_point)
    
    return merged


def extract_path_segment(path_points: List[Tuple[float, float]], 
                        start_index: int, 
                        end_index: int) -> List[Tuple[float, float]]:
    """
    提取路径的一个片段
    
    参数:
        path_points: 完整路径点列表
        start_index: 起始索引
        end_index: 结束索引（包含）
    
    返回:
        路径片段
    """
    start_index = max(0, start_index)
    end_index = min(len(path_points) - 1, end_index)
    
    if start_index > end_index:
        return []
    
    return path_points[start_index:end_index + 1]