from typing import List
from graph import Graph

def get_traffic_label(factor: float) -> str:
    """Returns a user-friendly traffic description label based on the traffic factor."""
    if factor <= 1.0:
        return "Clear 🟢"
    elif factor <= 1.3:
        return "Light Traffic 🟡"
    elif factor <= 1.8:
        return "Moderate Traffic 🟠"
    else:
        return "Heavy Congestion 🔴"


def generate_route_summary(graph: Graph, path: List[str], routing_metric: str) -> str:
    """
    Analyzes the path nodes in the graph and generates a detailed, 
    human-readable route summary report with step-by-step directions.
    """
    if not path:
        return "❌ ROUTE SUMMARY: No path found or path is empty."

    summary = []
    summary.append("=========================================================")
    summary.append("🚗                 ROUTE SUMMARY REPORT                  ")
    summary.append("=========================================================")
    
    start_node = graph.get_node(path[0])
    end_node = graph.get_node(path[-1])
    
    summary.append(f"🟢 Origin:      {start_node.name} ({start_node.id})")
    summary.append(f"🔴 Destination: {end_node.name} ({end_node.id})")
    summary.append(f"⚖️  Optimized by: {routing_metric.capitalize()}")
    summary.append("---------------------------------------------------------")
    summary.append("🔀 Step-by-Step Directions:")

    total_distance = 0.0
    total_time = 0.0

    for i in range(len(path) - 1):
        curr_id = path[i]
        next_id = path[i+1]
        
        curr_node = graph.get_node(curr_id)
        next_node = graph.get_node(next_id)
        
        # Find the edge connecting curr_id to next_id
        target_edge = None
        for edge in graph.get_neighbors(curr_id):
            if edge.target == next_id:
                target_edge = edge
                break
        
        if target_edge:
            dist = target_edge.distance
            time_mins = target_edge.get_weight('time')
            traffic = target_edge.traffic_factor
            speed = target_edge.speed_limit
            
            total_distance += dist
            total_time += time_mins
            
            traffic_lbl = get_traffic_label(traffic)
            
            summary.append(
                f" {i+1}. From {curr_node.name} ➔ Head to {next_node.name}\n"
                f"    🛣️  Road: {dist:.1f} km | Speed Limit: {speed:.0f} km/h\n"
                f"    🚗 Traffic: {traffic_lbl} ({traffic:.1f}x delay) | 🕒 Est. Segment Time: {time_mins:.1f} mins"
            )
        else:
            summary.append(f" {i+1}. Move from {curr_node.name} ➔ {next_node.name} (Road details unavailable)")

    summary.append("---------------------------------------------------------")
    summary.append("📊 Cumulative Metrics:")
    summary.append(f"   📏 Total Physical Distance: {total_distance:.2f} km")
    
    # Format total time nicely (hours & minutes)
    if total_time >= 60.0:
        hrs = int(total_time // 60)
        mins = total_time % 60
        summary.append(f"   🕒 Total Estimated Duration: {hrs} hr {mins:.1f} mins")
    else:
        summary.append(f"   🕒 Total Estimated Duration: {total_time:.1f} mins")
        
    summary.append("=========================================================")

    return "\n".join(summary)
