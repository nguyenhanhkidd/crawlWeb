import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
import os

def build_graph(file):
    # Read the CSV file
    data_base = pd.read_csv(file)

    # Create empty graph
    g = nx.DiGraph()

    for _, elrow in data_base.iterrows():
        g.add_edge(elrow[0], elrow[1], attr_dict=elrow[2:].to_dict())

    # Define data structure (list) of edge colors for plotting
    edge_colors = [e[2]['attr_dict']['Color'] for e in g.edges(data=True)]

    return g, edge_colors

def visualize_graph(g, edge_colors):
    degrees = [val for (node, val) in g.degree()]

    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(g, seed=20, k=3)

    nx.draw_networkx_edges(g, pos, alpha=0.8, width=1.5, edge_color=edge_colors, arrowsize=8)
    nx.draw_networkx_nodes(g, pos, alpha=0.7, node_color="yellow", node_size=[v * 50 for v in degrees])
    # nx.draw_networkx_labels(g, pos, alpha=1, font_size=8, font_weight="bold")

    plt.title('Graph Representation of Website', size=14)
    plt.show()


def density(g):
    # Density of Graph
    return nx.density(g)

def width_of_graph(g):
    # Initialize variable to store maximum width
    max_width = 0

    # Perform BFS starting from each source node
    for source in g.nodes():
        queue = deque([(source, 0)])
        visited = set([source])
        level_widths = {}

        while queue:
            node, level = queue.popleft()
            width = level_widths.get(level, 0) + 1
            level_widths[level] = width
            max_width = max(max_width, width)

            for neighbor in g.neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, level + 1))

    return max_width

def depth_of_graph(g):
    # Initialize dictionary to store depths for each node
    depths = {}

    # Perform DFS starting from each source node
    for source in g.nodes():
        stack = [(source, 0)]
        visited = set([source])
        max_depth = 0

        while stack:
            node, depth = stack.pop()
            max_depth = max(max_depth, depth)

            for neighbor in g.neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append((neighbor, depth + 1))
        depths[source] = max_depth

    return depths

def leaf_nodes(g):
    leaf_nodes = []
    count = 0
    # Get depths of each node
    depths = depth_of_graph(g)
    for node, depth in depths.items():
        if depth == 0:
            leaf_nodes.append(node)
            count += 1
    return count

if __name__ == "__main__":
    file = "database---tokiocity.csv"
    g, edge_colors = build_graph(file)

    visualize_graph(g, edge_colors)

    density_value = density(g)
    width_value = width_of_graph(g)
    depths = depth_of_graph(g)
    max_depth = max(depths.values())
    leafs = leaf_nodes(g)

    # Create a DataFrame with the results
    results_df = pd.DataFrame({
        'File Name': [file],
        'Density': [density_value],
        'Width': [width_value],
        'Maximum Depth': [max_depth],
        'Leafs': [leafs]
    })

    # Append the DataFrame to the CSV file
    if not os.path.isfile('usability_metrics.csv'):
        results_df.to_csv('usability_metrics.csv', index=False)
    else:
        results_df.to_csv('usability_metrics.csv', mode='a', header=False, index=False)