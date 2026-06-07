import os
import matplotlib.pyplot as plt
import networkx as nx
from typing import List
from graph import Graph

def draw_graph(graph: Graph, path: List[str] = None, output_filename: str = "route_map.png", highlight_metric: str = "time"):
    """
    Plots the graph topology using NetworkX and Matplotlib.
    If a path is provided, it highlights the path nodes and edges in orange/red.
    Saves the output image to the outputs/ directory.
    """
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)

    plt.figure(figsize=(10, 8))
    
    # Initialize NetworkX DiGraph (directed graph)
    G = nx.DiGraph()
    
    # Add nodes with position attributes
    pos = {}
    node_labels = {}
    for node_id, node in graph.nodes.items():
        G.add_node(node_id)
        pos[node_id] = (node.x, node.y)
        node_labels[node_id] = f"{node.name}\n({node.id})"

    # Add edges and retrieve weights
    edge_labels = {}
    for node_id, edges in graph.adjacency_list.items():
        for edge in edges:
            G.add_edge(edge.source, edge.target)
            
            # Label edges based on distance or duration
            if highlight_metric == 'distance':
                edge_labels[(edge.source, edge.target)] = f"{edge.distance:.1f}km"
            else:
                edge_labels[(edge.source, edge.target)] = f"{edge.get_weight('time'):.1f}m"

    # Draw default graph layout
    nx.draw_networkx_nodes(
        G, pos, 
        node_size=1200, 
        node_color="#2A2F35",  # Sleek dark gray
        edgecolors="#3C8DFF",  # Tech blue border
        linewidths=1.5
    )
    
    # Draw default edges
    nx.draw_networkx_edges(
        G, pos, 
        edgelist=G.edges(), 
        edge_color="#A5B1C2", 
        width=1.0, 
        arrows=True, 
        arrowsize=15, 
        connectionstyle="arc3,rad=0.08"  # Curve edges slightly to show bidirectionality
    )
    
    # Draw node text labels
    nx.draw_networkx_labels(
        G, pos, 
        labels=node_labels, 
        font_size=9, 
        font_weight="bold", 
        font_color="#2C3E50",
        verticalalignment="center"
    )

    # Draw edge labels (distances or durations)
    nx.draw_networkx_edge_labels(
        G, pos, 
        edge_labels=edge_labels, 
        font_size=7, 
        font_color="#7F8C8D",
        label_pos=0.4  # Move labels slightly towards source to avoid overlapping
    )

    # Highlight the path if provided
    if path and len(path) > 1:
        path_edges = [(path[i], path[i+1]) for i in range(len(path) - 1)]
        
        # Highlight path nodes
        nx.draw_networkx_nodes(
            G, pos, 
            nodelist=path, 
            node_size=1300, 
            node_color="#FF7675",  # Vibrant coral red
            edgecolors="#D63031",
            linewidths=2.0
        )
        
        # Highlight path edges
        nx.draw_networkx_edges(
            G, pos, 
            edgelist=path_edges, 
            edge_color="#E17055",  # Rich orange-red
            width=3.0, 
            arrows=True, 
            arrowsize=18,
            connectionstyle="arc3,rad=0.08"
        )

    plt.title(f"Intelligent Route Map ({highlight_metric.upper()} Optimization)\nMetroville Transit Graph", fontsize=12, fontweight="bold", pad=15)
    plt.axis("off")
    plt.tight_layout()
    
    # Save the file
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    print(f"🗺️  Graph visualization successfully saved to: outputs/{output_filename}")
