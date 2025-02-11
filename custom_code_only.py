import traci
import random
import networkx as nx
import matplotlib.pyplot as plt

# Parameters
sumo_cmd = ["sumo-gui", "-c", "osm_adjusted.sumocfg"]
max_steps = 2000
custom_vehicles = [
    {"id": "veh_10001", "start": "7620.24", "end": "1254.76"},
    {"id": "veh_10003", "start": "2408.92", "end": "6681.96"},
    {"id": "veh_10002", "start": "1254.76", "end": "7620.24"},
    {"id": "veh_10004", "start": "8332.86", "end": "1730.73"},
    {"id": "veh_10005", "start": "1730.73", "end": "(8332.86"},
]
graph_update_interval = 10  # Steps between graph updates
reroute_interval = 10  # Steps between reroutes

# Data Tracking
custom_vehicle_data = {}

def create_graph():
    """
    Create a graph from the SUMO network using edges and their connections.
    """
    G = nx.DiGraph()
    for edge_id in traci.edge.getIDList():
        # Get all lanes associated with the edge
        lane_ids = traci.edge.getLanes(edge_id)  # Fetch lane objects from the edge
        for lane in lane_ids:
            connections = traci.lane.getLinks(lane.getID())  # Get outgoing connections for each lane
            for conn in connections:
                target_lane = conn[0]
                target_edge = traci.lane.getEdgeID(target_lane)
                length = lane.getLength()
                speed = lane.getMaxSpeed()
                weight = length / speed if speed > 0 else float("inf")
                G.add_edge(edge_id, target_edge, weight=weight, length=length)
    return G

def reroute_vehicle(veh_id, G):
    """
    Dynamically reroute a vehicle using the shortest path in the graph.
    """
    try:
        current_edge = traci.vehicle.getRoadID(veh_id)
        destination = next(veh["end"] for veh in custom_vehicles if veh["id"] == veh_id)
        if current_edge and destination:
            shortest_path = nx.shortest_path(G, source=current_edge, target=destination, weight="weight")
            traci.vehicle.setRoute(veh_id, shortest_path)
            print(f"Vehicle {veh_id} dynamically rerouted.")
    except nx.NetworkXNoPath:
        print(f"No path found for vehicle {veh_id} from {current_edge} to {destination}.")
    except Exception as e:
        print(f"Error rerouting vehicle {veh_id}: {e}")

def add_custom_vehicles():
    """
    Add custom vehicles to the simulation with predefined start and end edges.
    """
    for veh in custom_vehicles:
        try:
            traci.vehicle.add(veh["id"], routeID="", typeID="passenger")
            traci.vehicle.setColor(veh["id"], (255, 0, 0))  # Set color to red
            traci.vehicle.changeTarget(veh["id"], veh["end"])
            custom_vehicle_data[veh["id"]] = {"distance": 0, "time": 0, "speed": 0}
            print(f"Added custom vehicle: {veh['id']} from {veh['start']} to {veh['end']}.")
        except Exception as e:
            print(f"Error adding custom vehicle {veh['id']}: {e}")

def track_vehicle_data(step):
    """
    Track custom vehicle data for analysis.
    """
    for veh_id in custom_vehicle_data.keys():
        if veh_id in traci.vehicle.getIDList():
            custom_vehicle_data[veh_id]["distance"] = traci.vehicle.getDistance(veh_id)
            custom_vehicle_data[veh_id]["time"] = step
            custom_vehicle_data[veh_id]["speed"] = traci.vehicle.getSpeed(veh_id)

def plot_results():
    """
    Plot the performance of custom vehicles.
    """
    for veh_id, data in custom_vehicle_data.items():
        print(f"Vehicle {veh_id} -> Distance: {data['distance'] / 1000:.2f} km, "
              f"Time: {data['time']} s, Avg Speed: {data['speed']:.2f} m/s")

# Simulation Loop
def run_simulation():
    traci.start(sumo_cmd)
    graph = create_graph()
    step = 0

    add_custom_vehicles()

    while step < max_steps:
        traci.simulationStep()
        track_vehicle_data(step)

        # Update graph and reroute vehicles periodically
        if step % graph_update_interval == 0:
            graph = create_graph()

        if step % reroute_interval == 0:
            for veh in custom_vehicles:
                if veh["id"] in traci.vehicle.getIDList():
                    reroute_vehicle(veh["id"], graph)

        step += 1

    traci.close()
    print("Simulation complete. Results:")
    plot_results()

# Run the simulation
run_simulation()
