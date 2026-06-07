import math
from typing import List, Dict, Tuple, Set, Callable
from graph import Graph, Node, Edge
from heap import MinHeap

def get_euclidean_distance(node_a: Node, node_b: Node) -> float:
    """Calculates the straight-line Cartesian distance between two nodes."""
    return math.sqrt((node_a.x - node_b.x) ** 2 + (node_a.y - node_b.y) ** 2)


def calculate_turn_penalty(p_node: Node, u_node: Node, v_node: Node, metric: str, turn_penalty_minutes: float = 0.5) -> float:
    """
    Calculates a penalty if there is a heading change at node u_node
    when transitioning from p_node -> u_node -> v_node.
    If the absolute turn angle exceeds 30 degrees, it adds a penalty.
    """
    if not p_node or not u_node or not v_node:
        return 0.0
    
    # Vector 1: p -> u
    dx1 = u_node.x - p_node.x
    dy1 = u_node.y - p_node.y
    
    # Vector 2: u -> v
    dx2 = v_node.x - u_node.x
    dy2 = v_node.y - u_node.y
    
    len1 = math.sqrt(dx1*dx1 + dy1*dy1)
    len2 = math.sqrt(dx2*dx2 + dy2*dy2)
    
    if len1 < 1e-5 or len2 < 1e-5:
        return 0.0
        
    dot = dx1*dx2 + dy1*dy2
    cos_angle = dot / (len1 * len2)
    cos_angle = max(-1.0, min(1.0, cos_angle))
    angle_rad = math.acos(cos_angle)
    
    # Check if heading change exceeds 30 degrees (approx 0.52 radians)
    if angle_rad > 0.52:
        if metric == 'time':
            return turn_penalty_minutes  # delay penalty in minutes
        elif metric == 'distance':
            return 0.1  # distance penalty in km (100 meters)
    return 0.0


def straight_line_time_heuristic(node: Node, target_node: Node, max_speed_limit: float = 100.0) -> float:
    """
    An admissible straight-line time heuristic for A* Search.
    Calculates Euclidean distance and divides by maximum speed limit to get time in minutes.
    """
    distance = get_euclidean_distance(node, target_node)
    min_time_hours = distance / max_speed_limit
    return min_time_hours * 60.0


def get_heuristic(node: Node, target_node: Node, metric: str, max_speed_limit: float = 100.0) -> float:
    """
    Calculates the default heuristic estimate (h-value) from node to target_node.
    To ensure A* remains admissible (never overestimates the true cost):
    - For 'distance': Uses the straight-line Euclidean distance (km).
    - For 'time': Uses the straight_line_time_heuristic.
    """
    if metric == 'distance':
        return get_euclidean_distance(node, target_node)
    elif metric == 'time':
        return straight_line_time_heuristic(node, target_node, max_speed_limit)
    else:
        return 0.0


def reconstruct_path(parent: Dict[str, str], source: str, destination: str) -> List[str]:
    """
    Reconstructs the path from source to destination by backtracking 
    through parent pointers. Returns an ordered list of node IDs.
    """
    path = []
    current = destination
    
    while current is not None:
        path.append(current)
        if current == source:
            break
        current = parent.get(current)

    # If the source was never reached, there is no valid path
    if not path or path[-1] != source:
        return []

    # Reverse path to yield source -> destination order
    path.reverse()
    return path


def dijkstra(
    graph: Graph, 
    source: str, 
    destination: str, 
    metric: str = 'time', 
    cost_fn: Callable[[Edge], float] = None
) -> Tuple[List[str], float, Dict[str, float]]:
    """
    Executes Dijkstra's Algorithm from source to destination.
    Accepts a pluggable cost_fn: Callable[[Edge], float] for dynamic weights.
    Returns a tuple: (shortest_path_nodes, total_cost, distances_dictionary).
    """
    if source not in graph.nodes or destination not in graph.nodes:
        return [], float('inf'), {}

    # Initialize data structures
    distances: Dict[str, float] = {node_id: float('inf') for node_id in graph.nodes}
    parent: Dict[str, str] = {node_id: None for node_id in graph.nodes}
    visited: Set[str] = set()

    distances[source] = 0.0
    
    # Initialize custom Min-Heap
    pq = MinHeap()
    pq.push(source, 0.0)

    while not pq.is_empty():
        current_node, current_dist = pq.pop()
        
        # Early termination
        if current_node == destination:
            break

        if current_node in visited:
            continue
            
        visited.add(current_node)

        # Explore neighbors
        for edge in graph.get_neighbors(current_node):
            if edge.is_closed:
                continue
            neighbor = edge.target
            if neighbor in visited:
                continue

            # Calculate path cost using pluggable cost_fn or default edge weights
            weight = cost_fn(edge) if cost_fn else edge.get_weight(metric)
            
            # Apply turn penalty if parent node exists
            p = parent[current_node]
            turn_penalty = 0.0
            if p is not None:
                p_node = graph.get_node(p)
                u_node = graph.get_node(current_node)
                v_node = graph.get_node(neighbor)
                turn_penalty = calculate_turn_penalty(p_node, u_node, v_node, metric)

            new_dist = current_dist + weight + turn_penalty

            # Relaxation step
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                parent[neighbor] = current_node
                pq.push(neighbor, new_dist)

    path = reconstruct_path(parent, source, destination)
    total_cost = distances[destination] if distances[destination] != float('inf') else float('inf')
    
    return path, total_cost, distances


def astar(
    graph: Graph, 
    source: str, 
    destination: str, 
    metric: str = 'time', 
    cost_fn: Callable[[Edge], float] = None,
    heuristic_fn: Callable[[Node, Node], float] = None
) -> Tuple[List[str], float, Dict[str, float]]:
    """
    Executes A* Search Algorithm from source to destination using coordinate heuristics.
    Accepts pluggable cost_fn and heuristic_fn for custom weighting configurations.
    Returns a tuple: (shortest_path_nodes, total_cost, distances_g_score_dictionary).
    """
    if source not in graph.nodes or destination not in graph.nodes:
        return [], float('inf'), {}

    target_node = graph.get_node(destination)
    
    # Initialize standard g-scores (actual path costs)
    g_score: Dict[str, float] = {node_id: float('inf') for node_id in graph.nodes}
    parent: Dict[str, str] = {node_id: None for node_id in graph.nodes}
    visited: Set[str] = set()

    g_score[source] = 0.0

    # Initialize priority queue (sorts by f_score = g_score + h_score)
    pq = MinHeap()
    
    # Compute starting heuristic score
    h_start = (
        heuristic_fn(graph.get_node(source), target_node) 
        if heuristic_fn else get_heuristic(graph.get_node(source), target_node, metric)
    )
    pq.push(source, h_start)  # f_score = 0 + h(source)

    while not pq.is_empty():
        current_node, current_f = pq.pop()

        # Early termination
        if current_node == destination:
            break

        if current_node in visited:
            continue

        visited.add(current_node)

        for edge in graph.get_neighbors(current_node):
            if edge.is_closed:
                continue
            neighbor = edge.target
            if neighbor in visited:
                continue

            # Compute actual step weight using pluggable cost_fn or default weights
            weight = cost_fn(edge) if cost_fn else edge.get_weight(metric)
            
            # Apply turn penalty
            p = parent[current_node]
            turn_penalty = 0.0
            if p is not None:
                p_node = graph.get_node(p)
                u_node = graph.get_node(current_node)
                v_node = graph.get_node(neighbor)
                turn_penalty = calculate_turn_penalty(p_node, u_node, v_node, metric)

            tentative_g = g_score[current_node] + weight + turn_penalty

            if tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                parent[neighbor] = current_node
                
                # Compute heuristic using pluggable heuristic_fn or default heuristics
                h_val = (
                    heuristic_fn(graph.get_node(neighbor), target_node) 
                    if heuristic_fn else get_heuristic(graph.get_node(neighbor), target_node, metric)
                )
                f_score = tentative_g + h_val
                
                pq.push(neighbor, f_score)

    path = reconstruct_path(parent, source, destination)
    total_cost = g_score[destination] if g_score[destination] != float('inf') else float('inf')
    
    return path, total_cost, g_score
