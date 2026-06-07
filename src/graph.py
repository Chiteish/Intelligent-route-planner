import json
from typing import List, Dict, Set

class Node:
    """Represents a location/intersection (vertex) in the routing network."""
    def __init__(self, node_id: str, name: str, x: float, y: float):
        self.id = node_id
        self.name = name
        self.x = x  # Cartesian X coordinate (for A* heuristic)
        self.y = y  # Cartesian Y coordinate (for A* heuristic)

    def __repr__(self):
        return f"Node({self.id}, '{self.name}', x={self.x}, y={self.y})"

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "x": self.x, "y": self.y}


class Edge:
    """Represents a road (weighted directed edge) between two locations."""
    def __init__(self, source: str, target: str, distance: float, speed_limit: float, traffic_factor: float = 1.0):
        self.source = source
        self.target = target
        self.distance = distance          # in kilometers (km)
        self.speed_limit = speed_limit      # in km/h (e.g. 50.0)
        self.traffic_factor = traffic_factor  # 1.0 = clear, >1.0 = congested
        self.is_closed = False              # Boolean flag representing road closure

    def get_weight(self, metric: str = 'time') -> float:
        """
        Calculates the weight (cost) of traversing this road.
        Supported metrics:
        - 'distance': Returns the physical distance in km.
        - 'time': Returns the travel time in minutes.
                  Time (hours) = Distance / Speed
                  Time (minutes) = (Distance / (Speed / Traffic)) * 60
        """
        if metric == 'distance':
            return self.distance
        elif metric == 'time':
            # Effective speed is reduced by the traffic factor
            effective_speed = max(1.0, self.speed_limit / self.traffic_factor)
            travel_time_hours = self.distance / effective_speed
            return travel_time_hours * 60.0  # Return duration in minutes
        else:
            raise ValueError(f"Unknown routing metric: {metric}")

    def __repr__(self):
        return f"Edge({self.source} -> {self.target}, dist={self.distance}km, limit={self.speed_limit}km/h, traffic={self.traffic_factor}, closed={self.is_closed})"


class Graph:
    """Represents the spatial transit network using an Adjacency List."""
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.adjacency_list: Dict[str, List[Edge]] = {}

    def add_node(self, node_id: str, name: str, x: float, y: float) -> Node:
        """Adds a location vertex to the graph."""
        node = Node(node_id, name, x, y)
        self.nodes[node_id] = node
        if node_id not in self.adjacency_list:
            self.adjacency_list[node_id] = []
        return node

    def add_edge(self, source: str, target: str, distance: float, speed_limit: float, traffic_factor: float = 1.0, bidirectional: bool = True):
        """Adds a road edge connecting two locations."""
        if source not in self.nodes or target not in self.nodes:
            raise ValueError(f"Both nodes '{source}' and '{target}' must exist in the graph before adding an edge.")

        # Create forward edge
        edge_forward = Edge(source, target, distance, speed_limit, traffic_factor)
        self.adjacency_list[source].append(edge_forward)

        # Create backward edge if bidirectional
        if bidirectional:
            edge_backward = Edge(target, source, distance, speed_limit, traffic_factor)
            self.adjacency_list[target].append(edge_backward)

    def get_neighbors(self, node_id: str) -> List[Edge]:
        """Returns the list of outgoing edges from a given node."""
        return self.adjacency_list.get(node_id, [])

    def get_node(self, node_id: str) -> Node:
        """Retrieves a node object by ID."""
        return self.nodes.get(node_id)

    def update_traffic(self, source: str, target: str, traffic_factor: float, bidirectional: bool = True):
        """Updates the traffic congestion factor on an existing road."""
        # Find forward edge and update
        updated = False
        if source in self.adjacency_list:
            for edge in self.adjacency_list[source]:
                if edge.target == target:
                    edge.traffic_factor = traffic_factor
                    updated = True

        # Find backward edge and update if bidirectional
        if bidirectional and target in self.adjacency_list:
            for edge in self.adjacency_list[target]:
                if edge.target == source:
                    edge.traffic_factor = traffic_factor
                    updated = True
        
        if not updated:
            raise ValueError(f"No edge found between '{source}' and '{target}' to update traffic.")

    def toggle_road_closure(self, source: str, target: str, is_closed: bool, bidirectional: bool = True):
        """Closes or opens a road segment dynamically."""
        updated = False
        if source in self.adjacency_list:
            for edge in self.adjacency_list[source]:
                if edge.target == target:
                    edge.is_closed = is_closed
                    updated = True

        if bidirectional and target in self.adjacency_list:
            for edge in self.adjacency_list[target]:
                if edge.target == source:
                    edge.is_closed = is_closed
                    updated = True
        
        if not updated:
            raise ValueError(f"No edge found between '{source}' and '{target}' to toggle closure.")

    def load_from_json(self, file_path: str):
        """Loads nodes and edges from a JSON data file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Add nodes
        for node_data in data.get("nodes", []):
            self.add_node(node_data["id"], node_data["name"], node_data["x"], node_data["y"])
        
        # Add edges
        for edge_data in data.get("edges", []):
            self.add_edge(
                source=edge_data["source"],
                target=edge_data["target"],
                distance=edge_data["distance"],
                speed_limit=edge_data["speed_limit"],
                traffic_factor=edge_data.get("traffic_factor", 1.0),
                bidirectional=edge_data.get("bidirectional", True)
            )

    def bfs(self, start_id: str) -> List[str]:
        """
        Performs Breadth-First Search (BFS) starting from start_id.
        Returns a list of visited node IDs in traversal order.
        """
        if start_id not in self.nodes:
            return []
        
        visited: Set[str] = {start_id}
        queue: List[str] = [start_id]
        traversal_order: List[str] = []

        while queue:
            current = queue.pop(0)  # Dequeue FIFO
            traversal_order.append(current)

            for edge in self.get_neighbors(current):
                neighbor = edge.target
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return traversal_order

    def dfs(self, start_id: str) -> List[str]:
        """
        Performs Depth-First Search (DFS) starting from start_id.
        Returns a list of visited node IDs in traversal order.
        """
        if start_id not in self.nodes:
            return []

        visited: Set[str] = set()
        traversal_order: List[str] = []

        def dfs_recursive(current_id: str):
            visited.add(current_id)
            traversal_order.append(current_id)
            
            for edge in self.get_neighbors(current_id):
                neighbor = edge.target
                if neighbor not in visited:
                    dfs_recursive(neighbor)

        dfs_recursive(start_id)
        return traversal_order
