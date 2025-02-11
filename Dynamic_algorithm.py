import os
import sys
import traci
import sumolib
import networkx as nx
import numpy as np
import pandas as pd
import ast  # Used to convert string tuples into actual numerical tuples

# Load SUMO Network
sumoBinary = sumolib.checkBinary('sumo-gui')  # Use 'sumo' for GUI mode, 'sumo' for CLI mode
sumoConfig = "osm_adjusted.sumocfg"  # Replace with your SUMO configuration file

# Start SUMO Simulation
traci.start([sumoBinary, "-c", sumoConfig, "--tripinfo-output", "tripinfo.xml"])

# Load Road Network as Graph
net = sumolib.net.readNet("osm.net.xml")
G = nx.DiGraph()

# Populate Graph from SUMO network
for edge in net.getEdges():
    G.add_edge(edge.getFromNode().getID(), edge.getToNode().getID(), weight=edge.getLength())

# Load Vehicle Start & Destination Data from Excel
df = pd.read_excel("REPORT/passenger_car_report.xlsx")

# Create a dictionary {Vehicle_ID: (Start_Coordinate, End_Coordinate)}
vehicle_routes = {}
for _, row in df.iterrows():
    start_coord = ast.literal_eval(row["start Cordinates"])  # Convert string to tuple
    end_coord = ast.literal_eval(row["end Cordinates"])  # Convert string to tuple
    vehicle_routes[row["Vehicle ID"]] = (start_coord, end_coord)

# Function to Find Nearest SUMO Network Node
def get_nearest_node(coord):
    min_distance = float("inf")
    nearest_node = None
    for node in net.getNodes():
        x, y = node.getCoord()
        distance = np.sqrt((coord[0] - x) ** 2 + (coord[1] - y) ** 2)
        if distance < min_distance:
            min_distance = distance
            nearest_node = node.getID()
    return nearest_node

# Define Heuristic Function for A*
def heuristic(node, goal):
    x1, y1 = net.getNode(node).getCoord()
    x2, y2 = net.getNode(goal).getCoord()
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)  # Euclidean distance heuristic

# Function to Compute Routes (Switching Logic)
def compute_route(vehicle_id, start_node, end_node):
    edge_traffic = {edge: traci.edge.getLastStepVehicleNumber(edge) for edge in G.edges}

    # Check congestion level for current edges
    congestion_threshold = 5  # Adjust this value based on scenario
    congested_edges = [edge for edge, count in edge_traffic.items() if count > congestion_threshold]

    # Decide algorithm dynamically
    if any(edge in congested_edges for edge in nx.shortest_path(G, start_node, end_node, weight="weight")):
        print(f"Vehicle {vehicle_id} switching to A* due to congestion.")
        path = nx.astar_path(G, start_node, end_node, weight="weight", heuristic=lambda u, v: heuristic(u, v))
    else:
        print(f"Vehicle {vehicle_id} using Dijkstra (No Congestion).")
        path = nx.shortest_path(G, start_node, end_node, weight="weight", method="dijkstra")

    return path

# Main Simulation Loop
step = 0
while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()

    for veh_id in traci.vehicle.getIDList():
        if veh_id in vehicle_routes:
            start_coord, end_coord = vehicle_routes[veh_id]

            # Convert coordinates to nearest SUMO node
            start_edge = get_nearest_node(start_coord)
            end_edge = get_nearest_node(end_coord)

            new_route = compute_route(veh_id, start_edge, end_edge)
            traci.vehicle.setRoute(veh_id, new_route)

    step += 1

traci.close()
