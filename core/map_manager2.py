
    def calculate_travel_time_weights(self, default_speed_kmh: float = 50.0):
    
        
        #""" Calculate travel time weights for all edges"""

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

            data['time'] = length_m / speed_mps if speed_mps > 0 else float('inf')


    def get_shortest_path_nodes(self, origin: int, destination: int) -> List[int]:
        #Get shortest path node list
        try:
            return nx.shortest_path(
                self.projected_graph,
                origin,
                destination,
                weight='time'
            )
        except nx.NetworkXNoPath:
            return []
         
    # Test: Gets a list of nodes' (x,y) coordinates for the shotrtest path to a given node using Dijkstra
    # with the esge weights being the distances between nodes
    # Input: node ID from which to start (int), node ID to end (int)
    # Output: List of node *x,y) coordinates that gives the shortest path (Tuple List)
    
    def get_shortest_path_points(self, origin: int, destination: int) -> List[Tuple[float, float]]:
        #""Get detailed coordinate points of shortest path""
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
                edge = min(edge_data.values(), key=lambda x: x.get('time', float('inf')))
                
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
        #""Calculate route distance (meters)""
        try:
            return nx.shortest_path_length(
                self.projected_graph,
                origin,
                destination,
                weight='time'
            )
        except nx.NetworkXNoPath:
            return float('inf')