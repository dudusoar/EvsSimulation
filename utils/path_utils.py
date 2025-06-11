"""
Path Processing Utility Module
Provides path decomposition, merging and other path-related utility functions
"""

from typing import List, Tuple
import numpy as np


def decompose_path(lines: List[List[Tuple[float, float]]]) -> List[Tuple[float, float]]:
    """
    Decompose OpenStreetMap geometric paths (polylines) into continuous coordinate point lists
    
    Args:
        lines: List of polylines, each line is a list of coordinate points
    
    Returns:
        Continuous coordinate point list
    """
    if not lines:
        return []
    
    path = []
    for line in lines:
        for point in line:
            path.append(point)
    
    # Remove duplicate points
    clean_path = []
    if path:
        for i in range(len(path)):
            if i == 0 or path[i] != path[i-1]:
                clean_path.append(path[i])
    
    return clean_path


def simplify_path(path_points: List[Tuple[float, float]], tolerance: float = 5.0) -> List[Tuple[float, float]]:
    """
    Simplify path by removing unnecessary intermediate points
    Uses Douglas-Peucker algorithm
    
    Args:
        path_points: Original path point list
        tolerance: Tolerance (meters)
    
    Returns:
        Simplified path point list
    """
    if len(path_points) <= 2:
        return path_points
    
    # Douglas-Peucker algorithm implementation
    def perpendicular_distance(point: Tuple[float, float], 
                             line_start: Tuple[float, float], 
                             line_end: Tuple[float, float]) -> float:
        """Calculate perpendicular distance from point to line segment"""
        x0, y0 = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        # If line segment degenerates to a point
        if x1 == x2 and y1 == y2:
            return np.sqrt((x0 - x1)**2 + (y0 - y1)**2)
        
        # Calculate perpendicular distance
        numerator = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
        denominator = np.sqrt((y2 - y1)**2 + (x2 - x1)**2)
        
        return numerator / denominator if denominator > 0 else 0
    
    def douglas_peucker(points: List[Tuple[float, float]], epsilon: float) -> List[Tuple[float, float]]:
        """Douglas-Peucker recursive implementation"""
        if len(points) <= 2:
            return points
        
        # Find the point with maximum distance
        max_distance = 0
        max_index = 0
        
        for i in range(1, len(points) - 1):
            distance = perpendicular_distance(points[i], points[0], points[-1])
            if distance > max_distance:
                max_distance = distance
                max_index = i
        
        # If maximum distance is greater than threshold, recursively process
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
    Resample path to make spacing between path points approximately equal
    
    Args:
        path_points: Original path point list
        target_spacing: Target spacing (meters)
    
    Returns:
        Resampled path point list
    """
    if len(path_points) < 2:
        return path_points
    
    resampled = [path_points[0]]
    accumulated_distance = 0.0
    
    for i in range(1, len(path_points)):
        prev_point = path_points[i - 1]
        curr_point = path_points[i]
        
        # Calculate length of current segment
        segment_length = np.sqrt((curr_point[0] - prev_point[0])**2 + 
                               (curr_point[1] - prev_point[1])**2)
        
        if accumulated_distance + segment_length >= target_spacing:
            # Need to add points on this segment
            remaining_distance = target_spacing - accumulated_distance
            
            while remaining_distance <= segment_length:
                # Calculate interpolation ratio
                ratio = remaining_distance / segment_length
                
                # Interpolate new point
                new_x = prev_point[0] + ratio * (curr_point[0] - prev_point[0])
                new_y = prev_point[1] + ratio * (curr_point[1] - prev_point[1])
                resampled.append((new_x, new_y))
                
                # Update distance
                remaining_distance += target_spacing
            
            # Update accumulated distance
            accumulated_distance = segment_length - (remaining_distance - target_spacing)
        else:
            accumulated_distance += segment_length
    
    # Add the last point
    if resampled[-1] != path_points[-1]:
        resampled.append(path_points[-1])
    
    return resampled


def merge_close_points(path_points: List[Tuple[float, float]], 
                      min_distance: float = 1.0) -> List[Tuple[float, float]]:
    """
    Merge path points that are too close to each other
    
    Args:
        path_points: Original path point list
        min_distance: Minimum distance threshold (meters)
    
    Returns:
        Merged path point list
    """
    if len(path_points) <= 1:
        return path_points
    
    merged = [path_points[0]]
    
    for i in range(1, len(path_points)):
        curr_point = path_points[i]
        last_merged = merged[-1]
        
        # Calculate distance
        distance = np.sqrt((curr_point[0] - last_merged[0])**2 + 
                         (curr_point[1] - last_merged[1])**2)
        
        # Only add if distance is large enough
        if distance >= min_distance:
            merged.append(curr_point)
    
    return merged


def extract_path_segment(path_points: List[Tuple[float, float]], 
                        start_index: int, 
                        end_index: int) -> List[Tuple[float, float]]:
    """
    Extract a segment of the path
    
    Args:
        path_points: Complete path point list
        start_index: Start index
        end_index: End index (inclusive)
    
    Returns:
        Path segment
    """
    start_index = max(0, start_index)
    end_index = min(len(path_points) - 1, end_index)
    
    if start_index > end_index:
        return []
    
    return path_points[start_index:end_index + 1]