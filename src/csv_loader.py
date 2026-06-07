import os
import csv
from typing import Dict, List, Callable

class CSVNode:
    """Represents a node loaded from a CSV structure."""
    def __init__(self, node_id: str):
        self.id = node_id
        # In simple CSV grids, coordinates can default to 0.0 or be inferred
        self.x = 0.0
        self.y = 0.0

    def __repr__(self):
        return f"CSVNode({self.id})"


class CSVEdge:
    """Represents a directed road with attributes loaded from a CSV row."""
    def __init__(self, source: str, target: str, distance: float, speed_limit: float, traffic_factor: float, is_toll: bool):
        self.source = source
        self.target = target
        self.distance = distance          # in km
        self.speed_limit = speed_limit      # in km/h
        self.traffic_factor = traffic_factor  # 1.0 = clear, >1.0 = congested
        self.is_toll = is_toll              # Boolean flag representing toll roads

    def __repr__(self):
        return f"CSVEdge({self.source} -> {self.target}, dist={self.distance}km, speed={self.speed_limit}km/h, toll={self.is_toll})"


class CSVGraph:
    """Represents a directed graph loaded dynamically from CSV files."""
    def __init__(self):
        self.nodes: Dict[str, CSVNode] = {}
        self.adjacency_list: Dict[str, List[CSVEdge]] = {}

    def get_or_create_node(self, node_id: str) -> CSVNode:
        """Retrieves an existing node or initializes a new one."""
        if node_id not in self.nodes:
            self.nodes[node_id] = CSVNode(node_id)
            self.adjacency_list[node_id] = []
        return self.nodes[node_id]

    def add_directed_edge(self, source: str, target: str, distance: float, speed_limit: float, traffic_factor: float, is_toll: bool):
        """Adds a single directed edge (road segment) to the graph."""
        self.get_or_create_node(source)
        self.get_or_create_node(target)
        
        edge = CSVEdge(source, target, distance, speed_limit, traffic_factor, is_toll)
        self.adjacency_list[source].append(edge)

    def load_from_csv(self, csv_path: str):
        """Parses rows from a CSV file and constructs the directed adjacency list."""
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found at: {csv_path}")

        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                source = row['source'].strip()
                target = row['target'].strip()
                distance = float(row['distance_km'])
                speed_limit = float(row['speed_limit_kmh'])
                traffic_factor = float(row['traffic_factor'])
                is_toll = int(row['is_toll']) == 1
                one_way = int(row['one_way']) == 1

                # 1. Add the forward edge (source -> target)
                self.add_directed_edge(source, target, distance, speed_limit, traffic_factor, is_toll)

                # 2. Add the backward edge (target -> source) ONLY if it's NOT a one-way road
                if not one_way:
                    self.add_directed_edge(target, source, distance, speed_limit, traffic_factor, is_toll)


# =====================================================================
# ⚖️ REUSABLE EDGE COST FUNCTIONS
# =====================================================================

def cost_distance(edge: CSVEdge) -> float:
    """Cost = Physical distance in kilometers (km)."""
    return edge.distance


def cost_time(edge: CSVEdge) -> float:
    """Cost = Estimated travel time in minutes (mins)."""
    effective_speed = max(1.0, edge.speed_limit / edge.traffic_factor)
    time_hours = edge.distance / effective_speed
    return time_hours * 60.0


def cost_tolls(edge: CSVEdge, toll_fee_minutes_penalty: float = 15.0) -> float:
    """
    Cost = Time in minutes + Toll Penalty.
    If the road has a toll, it adds a penalty (default: 15 minutes of delay).
    This allows algorithms to route around tollways unless the detour is too long.
    """
    base_time = cost_time(edge)
    toll_penalty = toll_fee_minutes_penalty if edge.is_toll else 0.0
    return base_time + toll_penalty


def cost_eco_proxy(edge: CSVEdge) -> float:
    """
    Cost = Fuel consumption proxy (Eco-scoring).
    Models vehicle fuel burn based on speed efficiency and traffic:
    - Low speeds (< 35 km/h) represent stop-and-go load, increasing fuel rate (+50%).
    - Moderate speeds (35 - 75 km/h) represent efficient cruising (baseline 1.0).
    - High speeds (> 75 km/h) represent high aerodynamic drag (+30% load).
    - Traffic delays increase fuel burn proportionally.
    """
    # 1. Base travel time (more travel time = more fuel burned idling)
    time_mins = cost_time(edge)
    
    # 2. Speed-load multiplier
    speed = edge.speed_limit
    if speed < 35.0:
        speed_load_multiplier = 1.5   # Inefficient low-speed urban driving
    elif speed > 75.0:
        speed_load_multiplier = 1.3   # Inefficient high-speed highway drag
    else:
        speed_load_multiplier = 1.0   # Sweet spot cruise efficiency (e.g. 50 km/h)

    # 3. Congestion fuel penalty
    traffic_penalty = edge.traffic_factor
    
    # Final eco proxy score (proportional to fuel consumed)
    return time_mins * speed_load_multiplier * traffic_penalty
