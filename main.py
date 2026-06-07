import os
import sys
import time

# Reconfigure stdout/stderr to support UTF-8 (emojis) on Windows consoles
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Ensure src/ is in the python search path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from graph import Graph
from algorithms import dijkstra, astar
from summary import generate_route_summary
from visualizer import draw_graph

try:
    from colorama import init, Fore, Style
    # Initialize colorama for Windows cmd colors
    init(autoreset=True)
except ImportError:
    # Dummy classes if colorama is not installed
    class DummyColor:
        def __getattr__(self, name):
            return ""
    Fore = DummyColor()
    Style = DummyColor()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def select_node(graph: Graph, prompt: str) -> str:
    """Prompts user to select a valid node from the graph."""
    while True:
        print(f"\n📍 Available Locations:")
        for node_id, node in graph.nodes.items():
            print(f"   [{node_id}] - {node.name}")
        
        choice = input(prompt).strip().upper()
        if choice in graph.nodes:
            return choice
        print(f"{Fore.RED}❌ Invalid selection. Please choose a letter from the list.")

def display_welcome_banner():
    print(f"{Fore.CYAN}{Style.BRIGHT}=========================================================")
    print(f"{Fore.CYAN}{Style.BRIGHT}🗺️   INTELLIGENT ROUTE PLANNER - GRAPH ALGORITHM CLI    🗺️")
    print(f"{Fore.CYAN}{Style.BRIGHT}=========================================================")
    print(f" This utility parses spatial map networks, models congestion,")
    print(f" and calculates optimal navigation routes in real-time.")
    print("=========================================================\n")

def run_cli_simulation():
    # 1. Initialize and Load Graph
    graph = Graph()
    dataset_path = os.path.join(os.path.dirname(__file__), 'data', 'metroville.json')
    
    if not os.path.exists(dataset_path):
        print(f"{Fore.RED}❌ Error: Location dataset '{dataset_path}' not found.")
        return

    print(f"⚙️  Parsing location dataset '{Fore.GREEN}data/metroville.json{Style.RESET_ALL}'...")
    graph.load_from_json(dataset_path)
    print(f"✨ Successfully loaded {Fore.GREEN}{len(graph.nodes)} locations{Style.RESET_ALL} and {Fore.GREEN}{sum(len(adj) for adj in graph.adjacency_list.values())} roads{Style.RESET_ALL}!")

    # 2. Perform BFS/DFS Connectivity Check
    print("🔍 Running sanity connectivity checks...")
    bfs_visited = graph.bfs('A')
    dfs_visited = graph.dfs('A')
    
    if len(bfs_visited) == len(graph.nodes):
        print(f"   ✅ Connectivity Check: {Fore.GREEN}Graph is fully connected.{Style.RESET_ALL}")
    else:
        print(f"   ⚠️  Warning: {Fore.RED}Disconnected graph detected!{Style.RESET_ALL} Some locations are unreachable.")
    
    # Pause to show information
    time.sleep(1)

    while True:
        clear_screen()
        display_welcome_banner()
        
        # 3. Source and Target Selection
        print(f"{Fore.YELLOW}{Style.BRIGHT}--- SELECT ROUTE ENDPOINTS ---")
        source = select_node(graph, "👉 Enter Starting Location Code (e.g. A): ")
        destination = select_node(graph, "👉 Enter Destination Location Code (e.g. E): ")
        
        if source == destination:
            print(f"\n{Fore.RED}❌ Start and destination cannot be identical! Press Enter to retry.")
            input()
            continue

        # 4. Optimization Metric Selection
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}--- SELECT OPTIMIZATION METRIC ---")
        print(" [1] Travel Time (Optimize for fastest route with traffic delays)")
        print(" [2] Physical Distance (Optimize for shortest physical route)")
        metric_choice = input("👉 Enter choice (1 or 2): ").strip()
        metric = 'distance' if metric_choice == '2' else 'time'
        metric_label = 'Distance' if metric == 'distance' else 'Travel Time'

        # 5. Pathfinding execution & Performance Benchmarking
        print(f"\n📊 Executing pathfinders and benchmarking performances...")
        
        # Run Dijkstra
        t0 = time.perf_counter_ns()
        path_dijkstra, cost_dijkstra, _ = dijkstra(graph, source, destination, metric)
        t_dijkstra = (time.perf_counter_ns() - t0) / 1000.0  # in microseconds
        
        # Run A* Search
        t0 = time.perf_counter_ns()
        path_astar, cost_astar, _ = astar(graph, source, destination, metric)
        t_astar = (time.perf_counter_ns() - t0) / 1000.0  # in microseconds

        # Print Benchmark Report
        print(f"\n{Fore.MAGENTA}{Style.BRIGHT}---------------------------------------------------------")
        print(f"{Fore.MAGENTA}{Style.BRIGHT}⚡ ALGORITHM PERFORMANCE BENCHMARK")
        print(f"{Fore.MAGENTA}{Style.BRIGHT}---------------------------------------------------------")
        print(f" 🔹 Dijkstra's Executed in:  {Fore.GREEN}{t_dijkstra:.2f} μs")
        print(f" 🔹 A* Search Executed in:   {Fore.GREEN}{t_astar:.2f} μs")
        speedup = ((t_dijkstra - t_astar) / t_dijkstra) * 100 if t_dijkstra > 0 else 0
        if speedup > 0:
            print(f" 🚀 A* Search was {Fore.CYAN}{speedup:.1f}% faster{Style.RESET_ALL} due to coordinate heuristic pruning!")
        print(f"---------------------------------------------------------")

        # 6. Generate Reports
        if not path_astar or cost_astar == float('inf'):
            print(f"{Fore.RED}❌ No path could be calculated between '{source}' and '{destination}'.")
        else:
            summary_report = generate_route_summary(graph, path_astar, metric)
            print(f"\n{Fore.GREEN}{Style.BRIGHT}Route calculated successfully!")
            print(summary_report)

            # 7. Generate Matplotlib Image Visualizations
            print(f"\n🖌️  Generating static visualization render...")
            draw_graph(graph, path_astar, f"route_{source}_to_{destination}_{metric}.png", metric)

        # 8. Web visualizer pointer
        print(f"\n{Fore.CYAN}💡 Pro-Tip: Open {Fore.YELLOW}src/web/index.html{Fore.CYAN} in your browser")
        print(f"            to interactively add nodes, draw edges, and watch animations!")

        # Loop controller
        print("\n=========================================================")
        choice = input("🔄 Would you like to plan another route? (y/n): ").strip().lower()
        if choice != 'y':
            print(f"\n{Fore.GREEN}👋 Thank you for using the Intelligent Route Planner! Safe travels.")
            break

if __name__ == "__main__":
    run_cli_simulation()
