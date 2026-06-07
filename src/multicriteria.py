import copy
from typing import List, Tuple, Dict, Set
from graph import Graph, Edge
from algorithms import dijkstra

def get_path_metrics(graph: Graph, path: List[str]) -> Tuple[float, float]:
    """Calculates the total physical distance (km) and travel time (minutes) for a given path."""
    total_dist = 0.0
    total_time = 0.0

    for i in range(len(path) - 1):
        u = path[i]
        v = path[i+1]
        
        # Find edge
        found_edge = None
        for edge in graph.get_neighbors(u):
            if edge.target == v:
                found_edge = edge
                break
        
        if found_edge:
            total_dist += found_edge.distance
            total_time += found_edge.get_weight('time')

    return total_dist, total_time


def yens_k_shortest_paths(graph: Graph, source: str, destination: str, K: int = 5, metric: str = 'time') -> List[List[str]]:
    """
    Computes the K-shortest loopless paths from source to destination 
    using Yen's Algorithm.
    Complexity: O(K * V * (V + E log V))
    """
    # Find the first shortest path
    first_path, cost, _ = dijkstra(graph, source, destination, metric)
    if not first_path:
        return []

    # A stores the K-shortest paths
    A: List[List[str]] = [first_path]
    
    # B is the candidate heap/set (using a list for easy loopless search)
    B: List[List[str]] = []

    # Temporary block lists for Yen's edge/node removal
    removed_edges: List[Tuple[str, Edge]] = []
    removed_nodes: Set[str] = set()

    for k in range(1, K):
        # The previous shortest path in A is A[k-1]
        prev_path = A[k-1]
        
        # Iterate over all nodes in the path except the target
        for i in range(len(prev_path) - 1):
            # 1. Choose the deviation node
            spur_node = prev_path[i]
            root_path = prev_path[:i + 1] # Prefix from source to spur_node

            # 2. Temporarily remove edges that share the same root_path prefix
            for path in A:
                if len(path) > i and path[:i+1] == root_path:
                    next_node = path[i+1]
                    # Find and remove edge (spur_node -> next_node) from graph
                    if spur_node in graph.adjacency_list:
                        edges = graph.adjacency_list[spur_node]
                        for edge in edges:
                            if edge.target == next_node:
                                removed_edges.append((spur_node, edge))
                                edges.remove(edge)
                                break

            # 3. Temporarily remove other nodes in the root_path (except spur_node) to avoid loops
            for node in root_path[:-1]:
                if node in graph.nodes:
                    removed_nodes.add(node)
                    # We block traversal through this node by clearing its neighbors
                    # and deleting it from its neighbors' target edges
                    # A cleaner way is to handle this inside the dijkstra algorithm
                    # But since we want to reuse the dijkstra module: we can remove the node edges
                    # We will temporarily remove all edges connecting to/from this node
                    if node in graph.adjacency_list:
                        for edge in graph.adjacency_list[node]:
                            removed_edges.append((node, edge))
                        graph.adjacency_list[node] = []

            # 4. Calculate spur path from spur_node to destination using Dijkstra
            spur_path, _, _ = dijkstra(graph, spur_node, destination, metric)

            if spur_path:
                # Combine root path and spur path to form candidate path
                candidate_path = root_path[:-1] + spur_path
                if candidate_path not in B and candidate_path not in A:
                    B.append(candidate_path)

            # 5. Restore all removed nodes and edges
            for node_id in removed_nodes:
                # We don't need to rebuild nodes, just restoring their edges is enough
                pass
            removed_nodes.clear()

            # Restore edges in reverse order
            for u, edge in reversed(removed_edges):
                if u in graph.adjacency_list:
                    # Restore if not already present
                    if edge not in graph.adjacency_list[u]:
                        graph.adjacency_list[u].append(edge)
            removed_edges.clear()

        # If there are no more candidates, we cannot find further shortest paths
        if not B:
            break

        # Sort candidates by cost
        # Since we use dijkstra to find spur path, we evaluate the cost of the entire candidate path
        # to select the minimum cost candidate path.
        B.sort(key=lambda p: get_path_metrics(graph, p)[0] if metric == 'distance' else get_path_metrics(graph, p)[1])
        
        # Pop the shortest candidate path and add it to A
        shortest_candidate = B.pop(0)
        A.append(shortest_candidate)

    return A


def filter_pareto_optimal(paths: List[List[str]], graph: Graph) -> List[Tuple[List[str], float, float]]:
    """
    Filters a set of candidate paths to identify the Pareto-optimal frontier.
    Evaluates paths based on two conflicting metrics: Distance (km) and Time (minutes).
    A path P1 dominates P2 if:
      - Dist(P1) <= Dist(P2) AND Time(P1) <= Time(P2)
      - AND at least one of these inequalities is strictly less.
    Returns a list of tuples: (path, distance, time) for all non-dominated paths.
    """
    path_metrics = []
    for path in paths:
        dist, time_mins = get_path_metrics(graph, path)
        path_metrics.append((path, dist, time_mins))

    pareto_frontier = []
    
    for i, (path_a, dist_a, time_a) in enumerate(path_metrics):
        is_dominated = False
        
        for j, (path_b, dist_b, time_b) in enumerate(path_metrics):
            if i == j:
                continue
            
            # Check if path B dominates path A
            # B dominates A if B is strictly better in one and not worse in the other
            better_or_equal_dist = dist_b <= dist_a
            better_or_equal_time = time_b <= time_a
            strictly_better_dist = dist_b < dist_a
            strictly_better_time = time_b < time_a
            
            if better_or_equal_dist and better_or_equal_time and (strictly_better_dist or strictly_better_time):
                is_dominated = True
                break
                
        if not is_dominated:
            # Check for duplicates in the frontier (different nodes list but same metrics)
            duplicate = False
            for _, f_dist, f_time in pareto_frontier:
                if abs(f_dist - dist_a) < 0.01 and abs(f_time - time_a) < 0.01:
                    duplicate = True
                    break
            if not duplicate:
                pareto_frontier.append((path_a, dist_a, time_a))

    # Sort frontier by distance
    pareto_frontier.sort(key=lambda x: x[1])
    return pareto_frontier
