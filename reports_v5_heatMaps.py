import os
import traci
import sumolib
import networkx as nx
import matplotlib.pyplot as plt
import random
import pandas as pd

# Parameters
sumo_cmd = ["sumo-gui", "-c", "osm_adjusted.sumocfg"]
vehicle_limit = 3000
max_steps = 600
high_removal_rate = 0.03
low_removal_rate = 0.005
removal_interval = 5
free_flow_range = (1600, 1800)

# Data storage
vehicle_count_history = []
speed_history = []
vehicles_inserted = 0
vehicles_removed = 0
stage_speed_data = {"start": [], "peak": [], "offpeak": []}
heatmap_data_start = []
heatmap_data_peak = []
heatmap_data_offpeak = []
vehicle_details = {}

os.makedirs("REPORTS", exist_ok=True)

# Load SUMO network
net = sumolib.net.readNet("osm.net.xml")

# Create graph
graph = nx.DiGraph()
for edge in net.getEdges():
    from_node = edge.getFromNode().getID()
    to_node = edge.getToNode().getID()
    weight = edge.getLength()
    graph.add_edge(from_node, to_node, id=edge.getID(), weight=weight)

def monitor_congestion(threshold=10):
    congested_edges = []
    for edge in traci.edge.getIDList():
        vehicle_count = traci.edge.getLastStepVehicleNumber(edge)
        if vehicle_count > threshold:
            congested_edges.append(edge)
    return congested_edges

def calculate_new_route(source, target, congested_edges):
    for edge in congested_edges:
        try:
            from_node = net.getEdge(edge).getFromNode().getID()
            to_node = net.getEdge(edge).getToNode().getID()
            if graph.has_edge(from_node, to_node):
                graph[from_node][to_node]['weight'] = float('inf')
        except Exception:
            continue
    try:
        shortest_path = nx.shortest_path(graph, source=source, target=target, weight="weight")
        return shortest_path
    except nx.NetworkXNoPath:
        print(f"No path found from {source} to {target}.")
        return []

def add_duplicate_vehicle(base_vehicle_id, new_vehicle_id):
    try:
        current_route = traci.vehicle.getRoute(base_vehicle_id)
        traci.vehicle.add(new_vehicle_id, routeID="", typeID="passenger")
        traci.vehicle.setRoute(new_vehicle_id, current_route)
        print(f"Duplicate vehicle '{new_vehicle_id}' created.")
    except traci.TraCIException as e:
        print(f"Error creating duplicate vehicle: {e}")

def reroute_vehicle(vehicle_id, congested_edges):
    try:
        current_edge = traci.vehicle.getRoadID(vehicle_id)
        if not current_edge:
            return
        target_edge = traci.vehicle.getRoute(vehicle_id)[-1]
        source_node = net.getEdge(current_edge).getFromNode().getID()
        target_node = net.getEdge(target_edge).getToNode().getID()
        new_route = calculate_new_route(source_node, target_node, congested_edges)
        if new_route:
            edge_ids = [graph.edges[u, v]['id'] for u, v in zip(new_route[:-1], new_route[1:])]
            traci.vehicle.setRoute(vehicle_id, edge_ids)
            print(f"Vehicle '{vehicle_id}' rerouted dynamically.")
    except Exception as e:
        print(f"Error rerouting vehicle '{vehicle_id}': {e}")

def highlight_vehicle(vehicle_id, color=(255, 0, 0, 255)):
    try:
        traci.vehicle.setColor(vehicle_id, color)
    except traci.TraCIException:
        pass

# Main Simulation Loop
traci.start(sumo_cmd)
step = 0
reduction_mechanism_activated = False
duplicated = False

while step < max_steps:
    traci.simulationStep()
    current_vehicles = traci.vehicle.getIDCount()
    vehicle_count_history.append(current_vehicles)

    avg_speed = (
        sum(traci.vehicle.getSpeed(veh_id) for veh_id in traci.vehicle.getIDList())
        / current_vehicles if current_vehicles > 0 else 0
    )
    speed_history.append(avg_speed)
    vehicles_inserted += traci.simulation.getDepartedNumber()
    vehicles_removed += traci.simulation.getArrivedNumber()

    if "veh99" in traci.vehicle.getIDList():
        highlight_vehicle("veh99", (0, 0, 255, 255))  # Blue for original
        if not duplicated:
            add_duplicate_vehicle("veh99", "veh99_dynamic")  # Create duplicate
            duplicated = True

    if "veh99_dynamic" in traci.vehicle.getIDList():
        highlight_vehicle("veh99_dynamic", (255, 0, 0, 255))  # Red for dynamic
        if step % 10 == 0:
            congested_edges = monitor_congestion(threshold=10)
            reroute_vehicle("veh99_dynamic", congested_edges)

    if step < max_steps // 3:
        stage_speed_data["start"].append(avg_speed)
    elif max_steps // 3 <= step < 2 * max_steps // 3:
        stage_speed_data["peak"].append(avg_speed)
    else:
        stage_speed_data["offpeak"].append(avg_speed)

    if current_vehicles >= vehicle_limit and not reduction_mechanism_activated:
        reduction_mechanism_activated = True

    if reduction_mechanism_activated and step % removal_interval == 0:
        if current_vehicles > free_flow_range[1]:
            remove_random_vehicles(high_removal_rate)
        elif free_flow_range[0] <= current_vehicles <= free_flow_range[1]:
            remove_random_vehicles(low_removal_rate)

    step += 1

traci.close()
print("Simulation complete.")
