import os
import sys

# Reconfigure stdout/stderr to support UTF-8 (emojis) on Windows consoles
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Ensure src/ is in the python search path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from graph import Graph
from algorithms import dijkstra, astar

def main():
    # 1. Initialize and Load Graph
    graph = Graph()
    dataset_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'metroville.json')
    
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}")
        return

    graph.load_from_json(dataset_path)
    
    print("=========================================================")
    print("🌐 PROJECT COMPONENT: GRAPH REPRESENTATION & ADJACENCY LIST")
    print("=========================================================")
    for node_id in sorted(graph.adjacency_list.keys()):
        node = graph.get_node(node_id)
        edges = graph.adjacency_list[node_id]
        edge_strings = []
        for e in edges:
            edge_strings.append(f"{e.target} ({e.distance} km, {e.speed_limit} km/h, traffic: {e.traffic_factor})")
        print(f"📍 Location [{node_id}] - {node.name}:")
        print(f"   ➔ Connected to: {', '.join(edge_strings) if edge_strings else 'None'}")
    print("=========================================================\n")

    print("=========================================================")
    print("🔍 PROJECT COMPONENT: BFS & DFS GRAPH TRAVERSALS")
    print("=========================================================")
    start_node = 'A'  # Start traversal from Downtown
    bfs_order = graph.bfs(start_node)
    dfs_order = graph.dfs(start_node)
    
    print(f"Starting Node: [{start_node}] - {graph.get_node(start_node).name}")
    print(f"🔹 BFS Traversal Order:  {' ➔ '.join(bfs_order)}")
    print(f"🔸 DFS Traversal Order:  {' ➔ '.join(dfs_order)}")
    print("=========================================================\n")

    print("=================================================")
    print("⚡ PROJECT COMPONENT: SHORTEST PATHFINDING OUTPUT")
    print("=================================================")
    source = 'B'       # Central Station
    destination = 'F'  # Industrial Zone
    
    # Run pathfinders for distance and time
    path_dist, cost_dist, _ = dijkstra(graph, source, destination, 'distance')
    path_time, cost_time, _ = dijkstra(graph, source, destination, 'time')
    
    print(f"From: [{source}] {graph.get_node(source).name}")
    print(f"To:   [{destination}] {graph.get_node(destination).name}")
    print("-------------------------------------------------")
    print("🟢 OPTIMIZED FOR PHYSICAL DISTANCE (Shortest Path):")
    print(f"  🔹 Path Sequence: {' ➔ '.join(path_dist)}")
    print(f"  🔹 Total Distance: {cost_dist:.2f} km")
    
    # Calculate travel time for the distance path
    dist_path_time = 0.0
    for i in range(len(path_dist) - 1):
        u, v = path_dist[i], path_dist[i+1]
        for edge in graph.adjacency_list[u]:
            if edge.target == v:
                dist_path_time += edge.get_weight('time')
                break
    print(f"  🔹 Travel Time:     {dist_path_time:.2f} mins")
    
    print("-------------------------------------------------")
    print("🔵 OPTIMIZED FOR TRAVEL TIME (Fastest Path):")
    print(f"  🔹 Path Sequence: {' ➔ '.join(path_time)}")
    print(f"  🔹 Travel Time:     {cost_time:.2f} mins")
    
    # Calculate distance for the time path
    time_path_dist = 0.0
    for i in range(len(path_time) - 1):
        u, v = path_time[i], path_time[i+1]
        for edge in graph.adjacency_list[u]:
            if edge.target == v:
                time_path_dist += edge.get_weight('distance')
                break
    print(f"  🔹 Total Distance: {time_path_dist:.2f} km")
    print("=================================================\n")

if __name__ == '__main__':
    main()
