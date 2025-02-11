import os
import traci
import sumolib
import networkx as nx
import matplotlib.pyplot as plt
import math

# Parameters
sumo_cmd = ["sumo-gui", "-c", "osm_adjusted.sumocfg"]
vehicle_limit = 3000
max_steps = 1600

# Coordinates for veh99
start_coord = (7224.802146144994, 1305.426251438435)
end_coord = (1115.8601140896092, 2450.517903637221)

# Data storage
vehicle_count_history = []
speed_history = []
veh99_data = {"distance": 0, "time": 0, "average_speed": 0}

# Load SUMO network
net = sumolib.net.readNet("osm.net.xml")

# Create graph
graph = nx.DiGraph()
for edge in net.getEdges():
    from_node = edge.getFromNode().getID()
    to_node = edge.getToNode().getID()
    weight = edge.getLength()
    graph.add_edge(from_node, to_node, id=edge.getID(), weight=weight)

def calculate_distance(coord1, coord2):
    """
    Calculate Euclidean distance between two coordinates.
    """
    return math.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)

def monitor_congestion(threshold=10):
    """
    Monitor congestion by identifying edges with vehicle counts above a threshold.
    """
    congested_edges = []
    for edge in traci.edge.getIDList():
        vehicle_count = traci.edge.getLastStepVehicleNumber(edge)
        if vehicle_count > threshold:
            congested_edges.append(edge)
    return congested_edges

def calculate_new_route(source, target, congested_edges):
    """
    Calculate a new route avoiding congested edges.
    """
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

def reroute_vehicle(vehicle_id, congested_edges):
    """
    Dynamically reroute the vehicle to avoid congestion.
    """
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
    """
    Highlight the specified vehicle in the simulation.
    """
    try:
        traci.vehicle.setColor(vehicle_id, color)
    except traci.TraCIException:
        pass

def add_vehicle(vehicle_id, start_coord, end_coord):
    """
    Add a vehicle to the simulation with a specified start and end coordinate.
    """
    try:
        start_edge = net.getNearestEdge(start_coord[0], start_coord[1]).getID()
        end_edge = net.getNearestEdge(end_coord[0], end_coord[1]).getID()
        traci.vehicle.add(vehicle_id, routeID="", typeID="passenger")
        traci.vehicle.moveToXY(vehicle_id, start_edge, lane=0, x=start_coord[0], y=start_coord[1])
        traci.vehicle.changeTarget(vehicle_id, end_edge)
        print(f"Vehicle '{vehicle_id}' added with start at {start_coord} and end at {end_coord}.")
    except Exception as e:
        print(f"Error adding vehicle '{vehicle_id}': {e}")

def update_vehicle_data(vehicle_id):
    """
    Update the distance, time, and average speed for veh99.
    """
    try:
        distance = traci.vehicle.getDistance(vehicle_id)
        speed = traci.vehicle.getSpeed(vehicle_id)
        veh99_data["distance"] = distance
        veh99_data["time"] += 1  # Increment time by 1 simulation step
        veh99_data["average_speed"] = distance / veh99_data["time"] if veh99_data["time"] > 0 else 0
    except Exception as e:
        print(f"Error updating data for vehicle '{vehicle_id}': {e}")

# Main Simulation Loop
traci.start(sumo_cmd)
step = 0
add_vehicle("veh99", start_coord, end_coord)

while step < max_steps:
    traci.simulationStep()
    current_vehicles = traci.vehicle.getIDCount()
    vehicle_count_history.append(current_vehicles)

    avg_speed = (
        sum(traci.vehicle.getSpeed(veh_id) for veh_id in traci.vehicle.getIDList())
        / current_vehicles if current_vehicles > 0 else 0
    )
    speed_history.append(avg_speed)

    # Highlight and reroute veh99 dynamically
    if "veh99" in traci.vehicle.getIDList():
        highlight_vehicle("veh99", (255, 0, 0, 255))  # Red for dynamic
        update_vehicle_data("veh99")
        if step % 10 == 0:
            congested_edges = monitor_congestion(threshold=10)
            reroute_vehicle("veh99", congested_edges)

    step += 1

traci.close()

# Final report
print("Simulation complete.")
print(f"Vehicle 'veh99' traveled {veh99_data['distance']:.2f} meters in {veh99_data['time']} steps.")
print(f"Average speed: {veh99_data['average_speed']:.2f} m/s.")
