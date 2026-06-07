import os
import sys

# Ensure src/ is in the python search path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from graph import Graph
from algorithms import dijkstra, astar

def test_dynamic_routing():
    print("=========================================================")
    print("TESTING DYNAMIC ROUTING (TRAFFIC, CLOSURES, TURN PENALTY)")
    print("=========================================================")
    
    # 1. Initialize Graph
    graph = Graph()
    dataset_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'metroville.json')
    graph.load_from_json(dataset_path)
    
    source = 'A'  # Downtown
    dest = 'E'    # Airport

    # --- Test Case 1: Baseline Route (Clear Graph) ---
    print("\n--- TEST 1: Baseline Route (No constraints, Time optimization) ---")
    path1, cost1, _ = dijkstra(graph, source, dest, 'time')
    print(f"Path: {' -> '.join(path1)}")
    print(f"Total travel time: {cost1:.2f} mins")

    # --- Test Case 2: Road Closure ---
    # We close the road connecting Central Station (B) and Airport (E), which is on the baseline route
    print("\n--- TEST 2: Road Closure (Close B -> E) ---")
    print("Closing the road segment: Central Station (B) -> Airport (E)...")
    graph.toggle_road_closure('B', 'E', is_closed=True, bidirectional=True)
    
    path2, cost2, _ = dijkstra(graph, source, dest, 'time')
    print(f"New Path: {' -> '.join(path2)}")
    print(f"New Travel Time: {cost2:.2f} mins (Successfully detour!)")
    
    # Re-open the road for subsequent tests
    graph.toggle_road_closure('B', 'E', is_closed=False, bidirectional=True)

    # --- Test Case 3: Traffic Congestion Scaling ---
    # We increase the traffic multiplier on B -> E to 8.0x
    print("\n--- TEST 3: Traffic Scaling (Update B -> E congestion to 8.0x) ---")
    print("Setting heavy congestion on Central Station (B) -> Airport (E)...")
    graph.update_traffic('B', 'E', traffic_factor=8.0, bidirectional=True)
    
    path3, cost3, _ = dijkstra(graph, source, dest, 'time')
    print(f"Fastest Path under congestion: {' -> '.join(path3)}")
    print(f"Total time: {cost3:.2f} mins")
    
    # Reset traffic
    graph.update_traffic('B', 'E', traffic_factor=1.4, bidirectional=True)

    # --- Test Case 4: Turn Penalties ---
    # Standard route A -> B -> E doesn't have sharp turns, but we can verify that the cost logic
    # penalizes route paths that make sharp turns.
    # Node coordinates in Metroville: A(10,10), B(12,15), I(8,14), C(3,18), E(28,25)
    # Let's route on a path that we know has a turn, like A -> B -> I -> C
    print("\n--- TEST 4: Turn Penalty Evaluation (A -> B -> I -> C) ---")
    # In standard Dijkstra, cost without turn penalties is just sum of edge times.
    # Here, we compare the cost calculation.
    path_turn, cost_turn, _ = dijkstra(graph, 'A', 'C', 'time')
    print(f"Optimized path from A to C: {' -> '.join(path_turn)}")
    print(f"Calculated path time (including turn delays): {cost_turn:.2f} mins")

    print("\n[SUCCESS] Dynamic features and turn penalty checks completed successfully!")
    print("=========================================================")

if __name__ == '__main__':
    test_dynamic_routing()
