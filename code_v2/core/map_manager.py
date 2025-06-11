<<<<<<< HEAD
"""
Map Management Module
Responsible for loading OSM map data, route planning, node management and other map-related functions
Inherits and optimizes functionality from original osm_request.py and graph_search.py
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
    """Map Manager Class"""
    
    def __init__(self, location: str, cache_dir: str = 'datasets/maps'):
        """
        Initialize map manager
        
        Args:
            location: Geographic location query string
            cache_dir: Cache directory
        """
        self.location = location
        self.cache_dir = cache_dir
        
        # Create cache directory
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        
        # Load map
        self.graph = self._load_graph()
        self.projected_graph = ox.project_graph(self.graph)
        
        # Cache node positions
        self._node_positions = {}
        self._cache_node_positions()
        
        # Graphics objects (for visualization)
        self.fig = None
        self.ax = None
    
    # ============= Map Loading Methods =============
    def _load_graph(self) -> nx.MultiDiGraph:
        """Load map graph"""
        # Construct cache filename
        graph_filename = self.location.lower().replace(',', '').replace(' ', '_') + '.graphml'
        graph_path = os.path.join(self.cache_dir, graph_filename)
        
        # Try loading from cache
        if os.path.exists(graph_path):
            print(f"Loading map from cache: {graph_path}")
            return ox.load_graphml(graph_path)
        
        # Download from OSM
        print(f"Downloading map from OpenStreetMap: {self.location}")
        try:
            graph = ox.graph_from_place(
                query=self.location,
                network_type='drive',
                simplify=True
            )
            # Save to cache
            ox.save_graphml(graph, graph_path)
            return graph
        except Exception as e:
            raise Exception(f"Unable to get map for {self.location}: {str(e)}")
    
    def _cache_node_positions(self):
        """Cache all node positions"""
        for node in self.projected_graph.nodes():
            self._node_positions[node] = (
                self.projected_graph.nodes[node]['x'],
                self.projected_graph.nodes[node]['y']
            )
    
    # ============= Map Bounds Methods (NEW) =============
    def get_bounds(self) -> Dict:
        """Get map boundaries for frontend initialization"""
        try:
            # Get bounding box from original graph (lat/lng)
            nodes_data = [(data['y'], data['x']) for node, data in self.graph.nodes(data=True)]
            
            if nodes_data:
                lats, lngs = zip(*nodes_data)
                return {
                    'north': max(lats),
                    'south': min(lats), 
                    'east': max(lngs),
                    'west': min(lngs),
                    'center': [sum(lats)/len(lats), sum(lngs)/len(lngs)]
                }
            else:
                # Default bounds for West Lafayette, IN
                return {
                    'north': 40.45,
                    'south': 40.40,
                    'east': -86.90,
                    'west': -86.95,
                    'center': [40.4237, -86.9212]
                }
        except Exception as e:
            print(f"Error getting map bounds: {e}")
            # Return default bounds
            return {
                'north': 40.45,
                'south': 40.40,
                'east': -86.90,
                'west': -86.95,
                'center': [40.4237, -86.9212]
            }

    # ============= Node Management Methods =============
    def get_all_nodes(self) -> List[int]:
        """Get all node IDs"""
        return list(self.projected_graph.nodes())
    
    def get_random_nodes(self, n: int) -> List[int]:
        """Get n random nodes"""
        all_nodes = self.get_all_nodes()
        return random.sample(all_nodes, min(n, len(all_nodes)))
    
    def get_node_position(self, node_id: int) -> Tuple[float, float]:
        """Get node position in projected coordinates"""
        return self._node_positions.get(node_id, (0.0, 0.0))
    
    def get_node_position_latlon(self, node_id: int) -> Tuple[float, float]:
        """Get node position in lat/lon coordinates for frontend"""
        try:
            node_data = self.graph.nodes[node_id]
            return (node_data['y'], node_data['x'])  # (lat, lon)
        except KeyError:
            # If node not found, return default position
            return (40.4237, -86.9212)
    
    def find_nearest_node(self, position: Tuple[float, float]) -> int:
        """Find nearest node to given position"""
        x, y = position
        # Use original graph (latitude/longitude) for search
        return ox.nearest_nodes(self.graph, x, y)
    
    # ============= Route Planning Methods =============
    def get_shortest_path_nodes(self, origin: int, destination: int) -> List[int]:
        """Get shortest path node list"""
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
        """Get detailed coordinate points of shortest path"""
        # Get path nodes
        route_nodes = self.get_shortest_path_nodes(origin, destination)
        if not route_nodes:
            return []
        
        # Convert node path to detailed coordinate points
        path_lines = []
        edge_nodes = list(zip(route_nodes[:-1], route_nodes[1:]))
        
        for u, v in edge_nodes:
            # Get edge data between two nodes
            edge_data = self.projected_graph.get_edge_data(u, v)
            if edge_data:
                # Select shortest edge
                edge = min(edge_data.values(), key=lambda x: x.get('length', float('inf')))
                
                # Check if detailed geometry information exists
                if 'geometry' in edge:
                    xs, ys = edge['geometry'].xy
                    path_lines.append(list(zip(xs, ys)))
                else:
                    # Straight line connection
                    p1 = self.get_node_position(u)
                    p2 = self.get_node_position(v)
                    path_lines.append([p1, p2])
        
        # Decompose into continuous path points
        return decompose_path(path_lines)
    
    def calculate_route_distance(self, origin: int, destination: int) -> float:
        """Calculate route distance (meters)"""
        try:
            return nx.shortest_path_length(
                self.projected_graph,
                origin,
                destination,
                weight='length'
            )
        except nx.NetworkXNoPath:
            return float('inf')
    
    # ============= Charging Station Related Methods =============
    def select_charging_station_nodes(self, n: int) -> List[int]:
        """
        Select n nodes as charging station locations
        Try to select evenly distributed nodes
        """
        all_nodes = self.get_all_nodes()
        
        if n >= len(all_nodes):
            return all_nodes
        
        # Use K-means idea to select scattered nodes
        selected_nodes = []
        remaining_nodes = all_nodes.copy()
        
        # Select first node (random)
        first_node = random.choice(remaining_nodes)
        selected_nodes.append(first_node)
        remaining_nodes.remove(first_node)
        
        # Select remaining nodes (maximize minimum distance)
        while len(selected_nodes) < n and remaining_nodes:
            max_min_distance = -1
            best_node = None
            
            for node in remaining_nodes[:100]:  # Limit search range for efficiency
                # Calculate minimum distance to selected nodes
                min_distance = float('inf')
                node_pos = self.get_node_position(node)
                
                for selected in selected_nodes:
                    selected_pos = self.get_node_position(selected)
                    distance = np.sqrt(
                        (node_pos[0] - selected_pos[0])**2 + 
                        (node_pos[1] - selected_pos[1])**2
                    )
                    min_distance = min(min_distance, distance)
                
                # Select node with maximum minimum distance
                if min_distance > max_min_distance:
                    max_min_distance = min_distance
                    best_node = node
            
            if best_node:
                selected_nodes.append(best_node)
                remaining_nodes.remove(best_node)
        
        return selected_nodes
    
    def find_nearest_nodes(self, position: Tuple[float, float], n: int = 5) -> List[Tuple[int, float]]:
        """
        Find n nearest nodes to given position
        Returns: [(node_id, distance), ...]
        """
        distances = []
        for node_id, node_pos in self._node_positions.items():
            distance = np.sqrt(
                (position[0] - node_pos[0])**2 + 
                (position[1] - node_pos[1])**2
            )
            distances.append((node_id, distance))
        
        # Sort and return nearest n
        distances.sort(key=lambda x: x[1])
        return distances[:n]
    
    # ============= Visualization Methods =============
    def setup_plot(self, show_preview: bool = False) -> Tuple[plt.Figure, plt.Axes]:
        """Setup map plotting"""
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
        """Plot route on map"""
        if not self.ax or len(route_nodes) < 2:
            return
        
        # Get route coordinates
        x_coords = [self._node_positions[node][0] for node in route_nodes]
        y_coords = [self._node_positions[node][1] for node in route_nodes]
        
        # Plot route
        self.ax.plot(x_coords, y_coords, color=color, linewidth=linewidth, alpha=0.7)
    
    # ============= Information Getter Methods =============
    def get_map_info(self) -> Dict:
        """Get map information"""
        return {
            'location': self.location,
            'num_nodes': self.projected_graph.number_of_nodes(),
            'num_edges': self.projected_graph.number_of_edges(),
            'graph_area': self.projected_graph.graph.get('area', 0)
=======
"""
Map Management Module
Responsible for loading OSM map data, route planning, node management and other map-related functions
Inherits and optimizes functionality from original osm_request.py and graph_search.py
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
    """Map Manager Class"""
    
    def __init__(self, location: str, cache_dir: str = 'datasets/maps'):
        """
        Initialize map manager
        
        Args:
            location: Geographic location query string
            cache_dir: Cache directory
        """
        self.location = location
        self.cache_dir = cache_dir
        
        # Create cache directory
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        
        # Load map
        self.graph = self._load_graph()
        self.projected_graph = ox.project_graph(self.graph)
        
        # Cache node positions
        self._node_positions = {}
        self._cache_node_positions()
        
        # Graphics objects (for visualization)
        self.fig = None
        self.ax = None
    
    # ============= Map Loading Methods =============
    def _load_graph(self) -> nx.MultiDiGraph:
        """Load map graph"""
        # Construct cache filename
        graph_filename = self.location.lower().replace(',', '').replace(' ', '_') + '.graphml'
        graph_path = os.path.join(self.cache_dir, graph_filename)
        
        # Try loading from cache
        if os.path.exists(graph_path):
            print(f"Loading map from cache: {graph_path}")
            return ox.load_graphml(graph_path)
        
        # Download from OSM
        print(f"Downloading map from OpenStreetMap: {self.location}")
        try:
            graph = ox.graph_from_place(
                query=self.location,
                network_type='drive',
                simplify=True
            )
            # Save to cache
            ox.save_graphml(graph, graph_path)
            return graph
        except Exception as e:
            raise Exception(f"Unable to get map for {self.location}: {str(e)}")
    
    def _cache_node_positions(self):
        """Cache all node positions"""
        for node in self.projected_graph.nodes():
            self._node_positions[node] = (
                self.projected_graph.nodes[node]['x'],
                self.projected_graph.nodes[node]['y']
            )
    
    # ============= Node Management Methods =============
    def get_all_nodes(self) -> List[int]:
        """Get all node IDs"""
        return list(self.projected_graph.nodes())
    
    def get_random_nodes(self, n: int) -> List[int]:
        """Get n random nodes"""
        all_nodes = self.get_all_nodes()
        return random.sample(all_nodes, min(n, len(all_nodes)))
    
    def get_node_position(self, node_id: int) -> Tuple[float, float]:
        """Get node position"""
        return self._node_positions.get(node_id, (0.0, 0.0))
    
    def find_nearest_node(self, position: Tuple[float, float]) -> int:
        """Find nearest node to given position"""
        x, y = position
        # Use original graph (latitude/longitude) for search
        return ox.nearest_nodes(self.graph, x, y)
    
    # ============= Route Planning Methods =============
    def get_shortest_path_nodes(self, origin: int, destination: int) -> List[int]:
        """Get shortest path node list"""
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
        """Get detailed coordinate points of shortest path"""
        # Get path nodes
        route_nodes = self.get_shortest_path_nodes(origin, destination)
        if not route_nodes:
            return []
        
        # Convert node path to detailed coordinate points
        path_lines = []
        edge_nodes = list(zip(route_nodes[:-1], route_nodes[1:]))
        
        for u, v in edge_nodes:
            # Get edge data between two nodes
            edge_data = self.projected_graph.get_edge_data(u, v)
            if edge_data:
                # Select shortest edge
                edge = min(edge_data.values(), key=lambda x: x.get('length', float('inf')))
                
                # Check if detailed geometry information exists
                if 'geometry' in edge:
                    xs, ys = edge['geometry'].xy
                    path_lines.append(list(zip(xs, ys)))
                else:
                    # Straight line connection
                    p1 = self.get_node_position(u)
                    p2 = self.get_node_position(v)
                    path_lines.append([p1, p2])
        
        # Decompose into continuous path points
        return decompose_path(path_lines)
    
    def calculate_route_distance(self, origin: int, destination: int) -> float:
        """Calculate route distance (meters)"""
        try:
            return nx.shortest_path_length(
                self.projected_graph,
                origin,
                destination,
                weight='length'
            )
        except nx.NetworkXNoPath:
            return float('inf')
    
    # ============= Charging Station Related Methods =============
    def select_charging_station_nodes(self, n: int) -> List[int]:
        """
        Select n nodes as charging station locations
        Try to select evenly distributed nodes
        """
        all_nodes = self.get_all_nodes()
        
        if n >= len(all_nodes):
            return all_nodes
        
        # Use K-means idea to select scattered nodes
        selected_nodes = []
        remaining_nodes = all_nodes.copy()
        
        # Select first node (random)
        first_node = random.choice(remaining_nodes)
        selected_nodes.append(first_node)
        remaining_nodes.remove(first_node)
        
        # Select remaining nodes (maximize minimum distance)
        while len(selected_nodes) < n and remaining_nodes:
            max_min_distance = -1
            best_node = None
            
            for node in remaining_nodes[:100]:  # Limit search range for efficiency
                # Calculate minimum distance to selected nodes
                min_distance = float('inf')
                node_pos = self.get_node_position(node)
                
                for selected in selected_nodes:
                    selected_pos = self.get_node_position(selected)
                    distance = np.sqrt(
                        (node_pos[0] - selected_pos[0])**2 + 
                        (node_pos[1] - selected_pos[1])**2
                    )
                    min_distance = min(min_distance, distance)
                
                # Select node with maximum minimum distance
                if min_distance > max_min_distance:
                    max_min_distance = min_distance
                    best_node = node
            
            if best_node:
                selected_nodes.append(best_node)
                remaining_nodes.remove(best_node)
        
        return selected_nodes
    
    def find_nearest_nodes(self, position: Tuple[float, float], n: int = 5) -> List[Tuple[int, float]]:
        """
        Find n nearest nodes to given position
        Returns: [(node_id, distance), ...]
        """
        distances = []
        for node_id, node_pos in self._node_positions.items():
            distance = np.sqrt(
                (position[0] - node_pos[0])**2 + 
                (position[1] - node_pos[1])**2
            )
            distances.append((node_id, distance))
        
        # Sort and return nearest n
        distances.sort(key=lambda x: x[1])
        return distances[:n]
    
    # ============= Visualization Methods =============
    def setup_plot(self, show_preview: bool = False) -> Tuple[plt.Figure, plt.Axes]:
        """Setup map plotting"""
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
        """Plot route on map"""
        if not self.ax or len(route_nodes) < 2:
            return
        
        # Get route coordinates
        x_coords = [self._node_positions[node][0] for node in route_nodes]
        y_coords = [self._node_positions[node][1] for node in route_nodes]
        
        # Plot route
        self.ax.plot(x_coords, y_coords, color=color, linewidth=linewidth, alpha=0.7)
    
    # ============= Information Getter Methods =============
    def get_map_info(self) -> Dict:
        """Get map information"""
        return {
            'location': self.location,
            'num_nodes': self.projected_graph.number_of_nodes(),
            'num_edges': self.projected_graph.number_of_edges(),
            'graph_area': ox.project_graph(self.graph).graph.get('area', 0)
>>>>>>> b9bd6771fbd7f2273a429016a9b2c009e69bada8
        }