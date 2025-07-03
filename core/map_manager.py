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
    
    # Test: Initializes the amo by loading and caching node positions
    # Input: Location needed to analyze (string), path to directory of map data (string)
    # Output: None

    
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
        self._node_positions_latlon = {}  # 添加经纬度坐标缓存
        self._cache_node_positions()
        
        # Graphics objects (for visualization)
        self.fig = None
        self.ax = None
    
    # ============= Map Loading Methods =============
    # Test: Generates Cache file name, tries loading from cache (if graphm1 file already exists, it's just loaded), 
    # downloads road network from OSM if not cached, saves the dowloaded graph to cache path, and handles errors
    # Input: None
    # Output: Directed multigraph

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
        """Cache all node positions (both projected and lat/lon)"""
        for node in self.projected_graph.nodes():
            # 投影坐标 (x, y) - 用于计算
            self._node_positions[node] = (
                self.projected_graph.nodes[node]['x'],
                self.projected_graph.nodes[node]['y']
            )
            
            # 经纬度坐标 (lon, lat) - 用于Web地图显示
            self._node_positions_latlon[node] = (
                self.graph.nodes[node]['x'],  # longitude
                self.graph.nodes[node]['y']   # latitude
            )
    
    # ============= Coordinate Conversion Methods =============
    def projected_to_latlon(self, projected_pos: Tuple[float, float]) -> Tuple[float, float]:
        """
        Convert projected coordinates to lat/lon coordinates
        
        Args:
            projected_pos: (x, y) in projected coordinates (meters)
            
        Returns:
            (longitude, latitude) in WGS84 degrees
        """
        try:
            # Use OSMnx to convert projected coordinates back to lat/lon
            import geopandas as gpd
            from shapely.geometry import Point
            
            # Create point in projected CRS
            point = Point(projected_pos[0], projected_pos[1])
            gdf = gpd.GeoDataFrame([1], geometry=[point], crs=self.projected_graph.graph['crs'])
            
            # Transform to WGS84 (EPSG:4326)
            gdf_latlon = gdf.to_crs('EPSG:4326')
            
            # Extract longitude and latitude
            lon = gdf_latlon.geometry.iloc[0].x
            lat = gdf_latlon.geometry.iloc[0].y
            
            return (lon, lat)
        except:
            # Fallback: find nearest node and use its lat/lon
            return self.find_nearest_node_latlon(projected_pos)
    
    def latlon_to_projected(self, latlon_pos: Tuple[float, float]) -> Tuple[float, float]:
        """
        Convert lat/lon coordinates to projected coordinates
        
        Args:
            latlon_pos: (longitude, latitude) in WGS84 degrees
            
        Returns:
            (x, y) in projected coordinates (meters)
        """
        try:
            import geopandas as gpd
            from shapely.geometry import Point
            
            lon, lat = latlon_pos
            
            # Create point in WGS84 CRS
            point = Point(lon, lat)
            gdf = gpd.GeoDataFrame([1], geometry=[point], crs='EPSG:4326')
            
            # Transform to projected CRS
            gdf_projected = gdf.to_crs(self.projected_graph.graph['crs'])
            
            # Extract x and y coordinates
            x = gdf_projected.geometry.iloc[0].x
            y = gdf_projected.geometry.iloc[0].y
            
            return (x, y)
        except:
            # Fallback: find nearest node and use its projected coordinates
            return self.find_nearest_node_projected(latlon_pos)
    
    def find_nearest_node_latlon(self, projected_pos: Tuple[float, float]) -> Tuple[float, float]:
        """Find nearest node's lat/lon coordinates to given projected position"""
        min_distance = float('inf')
        nearest_latlon = (0.0, 0.0)
        
        for node_id, node_proj_pos in self._node_positions.items():
            distance = np.sqrt(
                (projected_pos[0] - node_proj_pos[0])**2 + 
                (projected_pos[1] - node_proj_pos[1])**2
            )
            if distance < min_distance:
                min_distance = distance
                nearest_latlon = self._node_positions_latlon[node_id]
        
        return nearest_latlon
    
    def find_nearest_node_projected(self, latlon_pos: Tuple[float, float]) -> Tuple[float, float]:
        """Find nearest node's projected coordinates to given lat/lon position"""
        lon, lat = latlon_pos
        # Use OSMnx to find nearest node
        nearest_node = ox.nearest_nodes(self.graph, lon, lat)
        return self._node_positions.get(nearest_node, (0.0, 0.0))
    
    # ============= Node Management Methods =============
    # Test: Gets all nodes in the projected graph
    # Input: None
    # Output: List of all node IDs (int List) 

    def get_all_nodes(self) -> List[int]:
        """Get all node IDs"""
        return list(self.projected_graph.nodes())
    
    # Test: Gets n random nodes from the projected graph
    # Input: number of random nodes wanted (int)
    # Output: List of all random node IDs (int List) 

    def get_random_nodes(self, n: int) -> List[int]:
        """Get n random nodes"""
        all_nodes = self.get_all_nodes()
        return random.sample(all_nodes, min(n, len(all_nodes)))
    
    # Test: Gets position of node based on its ID
    # Input: node id (int)
    # Output: (x,y) coordinate of node (Tuple) 

    def get_node_position(self, node_id: int) -> Tuple[float, float]:
        """Get node position in projected coordinates (for calculations)"""
        return self._node_positions.get(node_id, (0.0, 0.0))
    
<<<<<<< HEAD
    # Test: Gets nearest node to a give position
    # Input: (x,y) position (Tuple)
    # Output: Node ID (int)

=======
    def get_node_position_latlon(self, node_id: int) -> Tuple[float, float]:
        """Get node position in lat/lon coordinates (for web maps)"""
        return self._node_positions_latlon.get(node_id, (0.0, 0.0))
    
>>>>>>> master
    def find_nearest_node(self, position: Tuple[float, float]) -> int:
        """Find nearest node to given position"""
        x, y = position
        # Use original graph (latitude/longitude) for search
        return ox.nearest_nodes(self.graph, x, y)
    
    # ============= Route Planning Methods =============

    # Test: Gets a list of node IDs for the shotrtest path to a given node using Dijkstra
    # with the esge weights being the distances between nodes
    # Input: node ID from which to start (int), node ID to end (int)
    # Output: List of node IDs that gives the shortest path (int List)

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
        
    # Test: Gets a list of nodes' (x,y) coordinates for the shotrtest path to a given node using Dijkstra
    # with the esge weights being the distances between nodes
    # Input: node ID from which to start (int), node ID to end (int)
    # Output: List of node *x,y) coordinates that gives the shortest path (Tuple List)
    
    def get_shortest_path_points(self, origin: int, destination: int) -> List[Tuple[float, float]]:
        """Get detailed coordinate points of shortest path"""
        # Get path nodes
        route_nodes = self.get_shortest_path_nodes(origin, destination)
        if not route_nodes: # no path exists
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
    
    # Test: Calculates distance of route using dijkstra with the length as the edge weights
    # Input: node ID from which to start (int), node ID to end (int)
    # Output: List of node *x,y) coordinates that gives the shortest path (Tuple List)

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
        
    
     # ============= Route Planning Methods TIME BASED =============

    def calculate_travel_time_weights(self, default_speed_kmh: float = 50.0):
    
        """ Calculate travel time weights for all edges"""

        for  u,v, key, data in self.projected_graph.edges(keys=True, data = True):

            #Convert length to meters (m) and speed to meters/second (m/s) for more detailed time calculation

            length_m = data.get('length',0) #0 if length is not found

            speed_mps= None

            if 'maxspeed' in data:
                #Default is kmh but if not, there will be a string after showing the unit (mph or mps)

                speed_str = data['maxspeed']

                #if km/h

                if speed_str.isdigit():
                    speed_kmh = float(speed_str)
                    speed_mps = speed_kmh * (1000/3600)

                else:
                    numeric_part = ''.join(filter(lambda x: x.isdigit() or x == '.', speed_str))

                    unit_part = speed_str.lower().replace(numeric_part, '').strip()

                    if numeric_part: #Continue only if number exists

                        speed_val = float(numeric_part)

                        if 'km/h' in unit_part or 'kmh' in unit_part:
                            speed_mps = speed_val * (1000 / 3600)  # km/h → m/s
                        
                        elif 'mph' in unit_part:
                            speed_mps = speed_val * (1609.34 / 3600)  # mph → m/s
                    
                        elif 'm/s' in unit_part or 'ms' in unit_part:
                            speed_mps = speed_val  # Already in m/s
                    
                        else:
                            # Default to km/h if unit is ambiguous
                            speed_mps = speed_val * (1000 / 3600)

            if speed_mps is None or speed_mps <= 0:
                speed_mps = default_speed_kmh * (1000 / 3600)

            data['travel_time'] = length_m / speed_mps if speed_mps > 0 else float('inf')


    def get_fastest_path_nodes(self,origin: int, destination: int) -> List[int]:
        """ Get fastest path nodes list (time based)"""

        try:
            return nx.shortest_path(
                self.projected_graph,
                origin,
                destination,
                weight = 'travel_time'
            )
        
        except nx.NetworkXNoPath:
            return []
        

    """ def calculate_route_time(self, origin: int, destination:int) -> float:
        Calculate route time (seconds)

        try: 
            return nx.shortest_path_length(
                self.projected_graph,
                origin,
                destination,
                weight = 'travel_time'
            )
        
        except nx.NetworkXNoPath:
            return float('inf')
    """
    # ============= Charging Station Related Methods =============

    # Test: Selects n random nodes as charging stations, nodes are chosen using K-means (Farthest point sampling) to ensure an
    # even distribution of charging stations
    # Input: number of charging stations (int)
    # Output: List of nodes IDs that represent charging stations (int List)

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
    
    # Test: Finds n nearest nodes to a certain position using the distance formula
    # Input: position (Tuple), number of nearest nodes (int)
    # Ouput: List of first n nearest nodes' positions (List of Tuples)
    
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

    # Test: sets up map plot
    # Input: Whether or not to show a preview (Bool)
    # Output: (figure, axes) (Tuple)

    def setup_plot(self, show_preview: bool = False) -> Tuple[plt.Figure, plt.Axes]:
        """Setup map plotting"""
        self.fig, self.ax = ox.plot_graph(
            self.projected_graph,
            node_size=0,
            edge_linewidth=1.0,  # Restored to reasonable thickness
            show=show_preview,
            close=False,
            bgcolor='white',
            edge_color='darkgray',  # Changed from 'gray' to 'darkgray' for better contrast
            figsize=(15, 12)  # Increased from (12, 10) to (15, 12) for larger map display
        )
        self.ax.set_title(self.location, fontsize=16, fontweight='bold', pad=20)
        
        # Adjust subplot parameters to give more space for the map
        self.fig.subplots_adjust(left=0.05, right=0.95, top=0.93, bottom=0.07)
        
        return self.fig, self.ax
    
    # Test: plots the route of a path on the map 
    # Input: route nodes (int List), color (string), linewidth (float)
    # Output: None
    
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

    # Test: Gets map information 
    # Input: None
    # Output: location, number of nodes, number of edges, area of graph (Dict)
    def get_map_info(self) -> Dict:
        """Get map information"""
        return {
            'location': self.location,
            'num_nodes': self.projected_graph.number_of_nodes(),
            'num_edges': self.projected_graph.number_of_edges(),
            'graph_area': ox.project_graph(self.graph).graph.get('area', 0)
        }