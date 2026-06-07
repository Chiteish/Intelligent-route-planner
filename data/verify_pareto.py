import os
import sys

# Ensure src/ is in the python search path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from graph import Graph
from multicriteria import yens_k_shortest_paths, filter_pareto_optimal, get_path_metrics

def test_pareto_routing():
    print("=========================================================")
    print("TESTING PARETO-OPTIMAL ROUTING FRONTIER (YEN'S ALGORITHM)")
    print("=========================================================")
    
    # 1. Initialize Graph
    graph = Graph()
    dataset_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'metroville.json')
    graph.load_from_json(dataset_path)
    print("Graph loaded successfully.")

    source_node = 'C'  # Suburbs
    dest_node = 'D'    # Tech Park

    # 2. Run Yen's K-Shortest Paths (K = 6) based on Time
    print(f"\nComputing top 6 candidate paths from {source_node} to {dest_node} using Yen's Algorithm...")
    candidates = yens_k_shortest_paths(graph, source_node, dest_node, K=6, metric='time')

    print(f"\nCandidates Found ({len(candidates)} paths):")
    for i, path in enumerate(candidates):
        dist, time_mins = get_path_metrics(graph, path)
        print(f"  [{i+1}] Route: {' -> '.join(path)}")
        print(f"      Distance: {dist:.2f} km | Travel Time: {time_mins:.1f} mins")

    # 3. Filter candidates for the Pareto-Optimal set (Distance vs Time trade-offs)
    print("\nFiltering candidates for the Pareto-Optimal Frontier...")
    pareto_set = filter_pareto_optimal(candidates, graph)

    print(f"\nPareto-Optimal Routes (Non-dominated set):")
    for i, (path, dist, time_mins) in enumerate(pareto_set):
        print(f"  [Option {chr(65+i)}] Route: {' -> '.join(path)}")
        print(f"           Distance: {dist:.2f} km | Travel Time: {time_mins:.1f} mins")

    print("\n[SUCCESS] Multi-Criteria Pareto-Optimal test execution complete!")
    print("=========================================================")

if __name__ == '__main__':
    test_pareto_routing()
