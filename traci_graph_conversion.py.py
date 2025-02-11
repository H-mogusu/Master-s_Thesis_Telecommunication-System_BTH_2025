import sumolib
import networkx as nx
import traci
import scipy as sp

# Load the SUMO network file
net = sumolib.net.readNet("osm.net.xml")

# Create a directed graph
graph = nx.DiGraph()

# Add edges to the graph
for edge in net.getEdges():
    # Extract edge details
    edge_id = edge.getID()
    from_node = edge.getFromNode().getID()
    to_node = edge.getToNode().getID()
    weight = edge.getLength()  # Use edge length as the weight

    # Add the edge to the graph
    graph.add_edge(from_node, to_node, id=edge_id, weight=weight)

# Print some graph details
print(f"Graph has {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges.")

# Example: Access nodes and edges
print("Sample nodes:", list(graph.nodes)[:5])
print("Sample edges with weights:", list(graph.edges(data=True))[:5])

source = "9263388830"
target = "135521212"
shortest_path = nx.shortest_path(graph, source=source, target=target, weight="weight")
#print(f"Shortest path from {source} to {target}: {shortest_path}")

import matplotlib.pyplot as plt
nx.draw(graph, with_labels=True, node_size=10, font_size=8)
plt.show()
