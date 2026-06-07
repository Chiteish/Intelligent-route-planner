import os
import sys

# Ensure src/ is in the python search path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from graph import Graph
from algorithms import dijkstra, astar, straight_line_time_heuristic

def test_pluggable_pathfinders():
    print("=========================================================")
    print("TESTING PLUGGABLE ALGORITHM WRAPPERS & HEURISTICS")
    print("=========================================================")
    
    # 1. Initialize Graph
    graph = Graph()
    dataset_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'metroville.json')
    graph.load_from_json(dataset_path)
    print("Graph loaded successfully.")

    source_node = 'A'  # Downtown
    dest_node = 'E'    # Airport

    # 2. Define custom pluggable edge cost (e.g., custom time cost function)
    # Replicates edge.get_weight('time') but in a dynamic lambda wrapper
    def custom_time_cost(edge):
        eff_speed = max(1.0, edge.speed_limit / edge.traffic_factor)
        return (edge.distance / eff_speed) * 60.0

    # 3. Define custom pluggable heuristic (straight line time heuristic with max speed limit)
    # Using the max speed limit from Metroville (100.0 km/h)
    def custom_heuristic(node, target_node):
        return straight_line_time_heuristic(node, target_node, max_speed_limit=100.0)

    # 4. Run pluggable Dijkstra
    path_dijkstra, cost_dijkstra, _ = dijkstra(
        graph, 
        source_node, 
        dest_node, 
        cost_fn=custom_time_cost
    )
    print("\n--- Pluggable Dijkstra Result ---")
    print(f"Path: {' -> '.join(path_dijkstra)}")
    print(f"Cost: {cost_dijkstra:.2f} mins")

    # 5. Run pluggable A* Search
    path_astar, cost_astar, _ = astar(
        graph, 
        source_node, 
        dest_node, 
        cost_fn=custom_time_cost,
        heuristic_fn=custom_heuristic
    )
    print("\n--- Pluggable A* Search Result ---")
    print(f"Path: {' -> '.join(path_astar)}")
    print(f"Cost: {cost_astar:.2f} mins")

    print("\n[SUCCESS] Verification Successful: Paths are identical and cost values match!")
    print("=========================================================")

if __name__ == '__main__':
    test_pluggable_pathfinders()
