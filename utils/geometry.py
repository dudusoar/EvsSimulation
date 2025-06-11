"""
Geometry Calculation Utility Module
Provides vector calculations, distance calculations and other geometry-related utility functions
"""

import numpy as np
from typing import Tuple, List
import math


# ============= Vector Calculations =============
def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points"""
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    return np.sqrt(dx**2 + dy**2)


def calculate_vector(from_point: Tuple[float, float], to_point: Tuple[float, float]) -> Tuple[float, float]:
    """Calculate vector from one point to another"""
    return (to_point[0] - from_point[0], to_point[1] - from_point[1])


def normalize_vector(vector: Tuple[float, float]) -> Tuple[float, float]:
    """Normalize vector"""
    magnitude = np.sqrt(vector[0]**2 + vector[1]**2)
    if magnitude > 0:
        return (vector[0] / magnitude, vector[1] / magnitude)
    return (0.0, 0.0)


def calculate_angle(vector1: Tuple[float, float], vector2: Tuple[float, float]) -> float:
    """Calculate angle between two vectors (radians)"""
    # Normalize vectors
    v1_norm = normalize_vector(vector1)
    v2_norm = normalize_vector(vector2)
    
    # Calculate dot product
    dot_product = v1_norm[0] * v2_norm[0] + v1_norm[1] * v2_norm[1]
    
    # Clamp to [-1, 1] range to avoid numerical errors
    dot_product = np.clip(dot_product, -1.0, 1.0)
    
    # Calculate angle
    angle = np.arccos(dot_product)
    return angle


# ============= Path Calculations =============
def calculate_path_length(path_points: List[Tuple[float, float]]) -> float:
    """Calculate total path length"""
    if len(path_points) < 2:
        return 0.0
    
    total_length = 0.0
    for i in range(len(path_points) - 1):
        total_length += calculate_distance(path_points[i], path_points[i + 1])
    
    return total_length


def find_closest_point_on_path(position: Tuple[float, float], 
                              path_points: List[Tuple[float, float]]) -> Tuple[int, float]:
    """
    Find closest point on path to given position
    Returns: (index of closest point, distance to closest point)
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
    Interpolate between two points
    ratio: 0.0 means point1, 1.0 means point2
    """
    ratio = np.clip(ratio, 0.0, 1.0)
    x = point1[0] + (point2[0] - point1[0]) * ratio
    y = point1[1] + (point2[1] - point1[1]) * ratio
    return (x, y)


# ============= Position Checking =============
def is_point_near_target(position: Tuple[float, float], 
                        target: Tuple[float, float], 
                        threshold: float = 10.0) -> bool:
    """Check if point is near target position"""
    return calculate_distance(position, target) <= threshold


def calculate_direction_to_target(current_pos: Tuple[float, float], 
                                 target_pos: Tuple[float, float]) -> Tuple[float, float]:
    """Calculate unit direction vector from current position to target position"""
    direction = calculate_vector(current_pos, target_pos)
    return normalize_vector(direction)


# ============= Coordinate Conversion =============
def meters_to_degrees(meters: float, latitude: float = 40.4237) -> Tuple[float, float]:
    """
    Convert meters to latitude/longitude offset
    latitude: Reference latitude (default near West Lafayette)
    Returns: (longitude offset, latitude offset)
    """
    # Earth radius (meters)
    earth_radius = 6371000.0
    
    # Latitude offset
    lat_offset = meters / earth_radius * (180.0 / math.pi)
    
    # Longitude offset (considering latitude effect)
    lon_offset = meters / (earth_radius * math.cos(math.radians(latitude))) * (180.0 / math.pi)
    
    return (lon_offset, lat_offset)


def degrees_to_meters(lon_diff: float, lat_diff: float, latitude: float = 40.4237) -> float:
    """
    Convert latitude/longitude difference to meters
    Returns distance between two points (meters)
    """
    earth_radius = 6371000.0
    
    # Distance corresponding to latitude difference
    lat_distance = lat_diff * (math.pi / 180.0) * earth_radius
    
    # Distance corresponding to longitude difference (considering latitude effect)
    lon_distance = lon_diff * (math.pi / 180.0) * earth_radius * math.cos(math.radians(latitude))
    
    # Total distance
    return np.sqrt(lat_distance**2 + lon_distance**2)