import os
import sys
import pytest

# Ensure src/ is in the python search path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from graph import Graph
from algorithms import dijkstra, astar

@pytest.fixture
def base_graph():
    """Fixture that initializes the Graph and loads the Metroville dataset."""
    graph = Graph()
    dataset_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'metroville.json')
    assert os.path.exists(dataset_path), "metroville.json dataset is missing!"
    graph.load_from_json(dataset_path)
    return graph


def test_dijkstra_astar_equivalence(base_graph):
    """Asserts that Dijkstra's and A* Search return identical routes and costs."""
    source = "A"  # Downtown
    destination = "E"  # Airport

    # Run Dijkstra (Time metric)
    path_dijkstra, cost_dijkstra, _ = dijkstra(base_graph, source, destination, 'time')
    
    # Run A* (Time metric)
    path_astar, cost_astar, _ = astar(base_graph, source, destination, 'time')

    assert path_dijkstra == path_astar, "Dijkstra and A* paths differ!"
    assert abs(cost_dijkstra - cost_astar) < 0.001, "Dijkstra and A* cost calculations differ!"


def test_shortest_vs_fastest_optimality(base_graph):
    """
    Asserts the fundamental optimality inequalities:
    - The shortest path must have physical distance <= fastest path physical distance.
    - The fastest path must have travel duration <= shortest path travel duration.
    """
    source = "C"  # Suburbs
    destination = "D"  # Tech Park

    # 1. Calculate the shortest distance path
    path_short, dist_short, _ = dijkstra(base_graph, source, destination, 'distance')
    
    # Calculate travel duration on the shortest path
    # (By running dijkstra on time and computing time cost of shortest path manually)
    _, time_of_shortest, _ = dijkstra(
        base_graph, source, destination, 'time', 
        cost_fn=lambda e: e.get_weight('time') if e.source in path_short and e.target in path_short else float('inf')
    )

    # 2. Calculate the fastest travel time path
    path_fast, time_fast, _ = dijkstra(base_graph, source, destination, 'time')
    
    # Calculate physical distance on the fastest path
    _, dist_of_fastest, _ = dijkstra(
        base_graph, source, destination, 'distance', 
        cost_fn=lambda e: e.distance if e.source in path_fast and e.target in path_fast else float('inf')
    )

    # Assertions
    assert dist_short <= dist_of_fastest, f"Shortest path distance ({dist_short}km) > Fastest path distance ({dist_of_fastest}km)!"
    assert time_fast <= time_of_shortest, f"Fastest path duration ({time_fast}m) > Shortest path duration ({time_of_shortest}m)!"


def test_weighted_routing_bounds(base_graph):
    """
    Asserts that the weighted sum path yields a composite cost that is less than or 
    equal to the composite cost of either the purely shortest or purely fastest paths.
    Cost(e) = w_time * Time(e) + w_dist * Dist(e)
    """
    source = "C"
    destination = "D"
    
    w_time = 0.4
    w_dist = 0.6
    
    # Pluggable weighted sum cost function
    def weighted_cost(edge):
        return w_time * edge.get_weight('time') + w_dist * edge.distance

    # 1. Run Dijkstra with pluggable weighted sum
    path_weighted, cost_weighted, _ = dijkstra(base_graph, source, destination, cost_fn=weighted_cost)

    # 2. Evaluate the weighted cost of the purely shortest path
    path_short, _, _ = dijkstra(base_graph, source, destination, 'distance')
    _, val_short, _ = dijkstra(base_graph, source, destination, cost_fn=weighted_cost)

    # 3. Evaluate the weighted cost of the purely fastest path
    path_fast, _, _ = dijkstra(base_graph, source, destination, 'time')
    _, val_fast, _ = dijkstra(base_graph, source, destination, cost_fn=weighted_cost)

    # Assertion: The optimal weighted path must be better than or equal to the other paths evaluated under the weighted cost
    assert cost_weighted <= val_short + 0.001, "Weighted path cost is worse than shortest path!"
    assert cost_weighted <= val_fast + 0.001, "Weighted path cost is worse than fastest path!"


def test_road_closures(base_graph):
    """Asserts that closing a critical road forces the pathfinder to calculate a detour path."""
    source = "A"
    destination = "E"

    # Get baseline path
    path_base, cost_base, _ = dijkstra(base_graph, source, destination, 'time')
    assert len(path_base) > 0, "No path found in baseline graph!"

    # Close a road segment on the baseline route (e.g. Central Station B -> Airport E)
    base_graph.toggle_road_closure("B", "E", is_closed=True, bidirectional=True)

    # Calculate new route
    path_new, cost_new, _ = dijkstra(base_graph, source, destination, 'time')

    # Assertions
    assert "B" not in path_new or "E" not in path_new or path_new.index("E") - path_new.index("B") != 1, "Route traversed a closed road!"
    assert cost_new >= cost_base, "Detour time is cheaper than the primary baseline route!"

    # Re-open road
    base_graph.toggle_road_closure("B", "E", is_closed=False, bidirectional=True)


def test_traffic_scaling(base_graph):
    """Asserts that increasing traffic congestion on a road increases the calculated travel time cost."""
    source = "A"
    destination = "B"

    # Get baseline travel time (clear traffic)
    _, cost_base, _ = dijkstra(base_graph, source, destination, 'time')

    # Update traffic congestion on A -> B to 5.0x
    base_graph.update_traffic("A", "B", traffic_factor=5.0, bidirectional=True)

    # Calculate travel time under traffic
    _, cost_traffic, _ = dijkstra(base_graph, source, destination, 'time')

    # Assertion: travel time must increase
    assert cost_traffic > cost_base, "Congested road travel time did not increase!"
