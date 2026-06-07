import os
import sys

# Ensure src/ is in the python search path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from csv_loader import CSVGraph, cost_distance, cost_time, cost_tolls, cost_eco_proxy, CSVEdge
from heap import MinHeap
from typing import List, Tuple, Dict, Set, Callable

# A generic Dijkstra implementation that accepts any edge cost function
def dijkstra_generic(graph: CSVGraph, source: str, destination: str, cost_fn: Callable[[CSVEdge], float]) -> Tuple[List[str], float]:
    if source not in graph.nodes or destination not in graph.nodes:
        return [], float('inf')

    distances: Dict[str, float] = {node_id: float('inf') for node_id in graph.nodes}
    parent: Dict[str, str] = {node_id: None for node_id in graph.nodes}
    visited: Set[str] = set()

    distances[source] = 0.0
    pq = MinHeap()
    pq.push(source, 0.0)

    while not pq.is_empty():
        current_node, current_dist = pq.pop()

        if current_node == destination:
            break

        if current_node in visited:
            continue
        visited.add(current_node)

        # Explore neighbors
        for edge in graph.adjacency_list.get(current_node, []):
            neighbor = edge.target
            if neighbor in visited:
                continue

            # Evaluate weight using the dynamically passed cost function
            weight = cost_fn(edge)
            new_dist = current_dist + weight

            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                parent[neighbor] = current_node
                pq.push(neighbor, new_dist)

    # Reconstruct path
    path = []
    curr = destination
    if distances[destination] != float('inf'):
        while curr is not None:
            path.append(curr)
            if curr == source:
                break
            curr = parent[curr]
        path.reverse()

    return path, distances[destination]


def run_demo():
    print("=========================================================")
    print("MULTI-CRITERIA ROUTING SYSTEM BENCHMARK (CSV SOURCE)")
    print("=========================================================")
    
    # 1. Initialize and load CSV Graph
    graph = CSVGraph()
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'grid_network.csv')
    
    print(f"Loading directed graph from: data/grid_network.csv")
    graph.load_from_csv(csv_path)
    print(f"Successfully loaded {len(graph.nodes)} intersections and road segments.\n")

    start_node = 'N11'  # Top-left corner
    end_node = 'N33'    # Bottom-right corner
    print(f"Querying routes from {start_node} to {end_node} under different criteria:\n")

    # 2. Define our criteria scenarios
    scenarios = [
        ("1. PHYSICAL DISTANCE (Shortest Route)", cost_distance, "km"),
        ("2. TRAVEL TIME (Fastest Route with Traffic)", cost_time, "minutes"),
        ("3. TOLL AVOIDANCE (Fastest route penalizing toll roads)", cost_tolls, "equivalent units"),
        ("4. ECO PROXY (Fuel/Emission optimized)", cost_eco_proxy, "fuel units")
    ]

    # 3. Calculate paths for each scenario
    for title, cost_function, unit in scenarios:
        path, total_cost = dijkstra_generic(graph, start_node, end_node, cost_function)
        print(f"--- {title} ---")
        if not path:
            print("   Path calculation: No route found.")
        else:
            print(f"   Route Sequence: {' -> '.join(path)}")
            print(f"   Calculated Cost: {total_cost:.2f} {unit}")
        print()

    print("=========================================================")
    print("ANALYSIS NOTES:")
    print(" - Physical Distance routes along the grid perimeter (N11->N12->N13->N23->N33).")
    print(" - Travel Time routes via the direct Highway Toll Avenue (N11->N33), minimizing duration.")
    print(" - Toll Avoidance detects the toll penalty on the Highway and bypasses it.")
    print(" - Eco Proxy avoids high-speed highway drag and congested grid segments, choosing")
    print("   the most fuel-efficient steady-state cruise path.")
    print("=========================================================")

if __name__ == '__main__':
    run_demo()
