import traci
import random
import networkx as nx
import matplotlib.pyplot as plt

# Parameters
sumo_cmd = ["sumo-gui", "-c", "osm_adjusted.sumocfg"]
max_steps = 1600
vehicle_limit = 4000
high_removal_rate = 0.03
low_removal_rate = 0.005
removal_interval = 5
free_flow_range = (1200, 1600)
reroute_interval = 10

# Custom vehicles for dynamic routing
custom_vehicles = [
    {"id": "veh_10001", "start": "7620.24", "end": "1254.76"},
    {"id": "veh_10003", "start": "2408.92", "end": "6681.96"},
    {"id": "veh_10002", "start": "1254.76", "end": "7620.24"},
    {"id": "veh_10004", "start": "8332.86", "end": "1730.73"},
    {"id": "veh_10005", "start": "1730.73", "end": "(8332.86"},
]
custom_vehicle_data = {}

def create_graph():
    """
    Create a graph using edges and lanes from the SUMO network.
    """
    G = nx.DiGraph()
    for edge_id in traci.edge.getIDList():
        try:
            length = traci.lane.getLength(f"{edge_id}_0")
            speed = traci.edge.getMaxSpeed(edge_id)
            weight = length / speed if speed > 0 else float("inf")
            G.add_node(edge_id, length=length, speed=speed)
            for connection in traci.lane.getLinks(f"{edge_id}_0"):
                G.add_edge(edge_id, connection[0].split('_')[0], weight=weight, length=length)
        except Exception as e:
            print(f"Error processing edge {edge_id}: {e}")
    return G

def add_custom_vehicles():
    """
    Add custom vehicles to the simulation with predefined start and end edges.
    """
    for veh in custom_vehicles:
        try:
            traci.vehicle.add(veh["id"], routeID="", typeID="passenger")
            traci.vehicle.setColor(veh["id"], (255, 0, 0))  # Red color
            traci.vehicle.changeTarget(veh["id"], veh["end"])
            custom_vehicle_data[veh["id"]] = {"distance": 0, "time": 0, "speed": 0}
        except Exception as e:
            print(f"Error adding custom vehicle {veh['id']}: {e}")

def run_simulation():
    """
    Run the simulation with dynamic routing for custom vehicles.
    """
    try:
        traci.start(sumo_cmd)
        graph = create_graph()
        step = 0

        add_custom_vehicles()

        while step < max_steps:
            traci.simulationStep()
            current_vehicles = traci.vehicle.getIDCount()

            print(f"Step {step}: {current_vehicles} vehicles in simulation.")

            # Reroute custom vehicles
            if step % reroute_interval == 0:
                for veh in custom_vehicles:
                    try:
                        current_edge = traci.vehicle.getRoadID(veh["id"])
                        destination_edge = veh["end"]
                        shortest_path = nx.shortest_path(graph, source=current_edge, target=destination_edge, weight="weight")
                        traci.vehicle.setRoute(veh["id"], shortest_path)
                        print(f"Vehicle {veh['id']} rerouted to avoid congestion.")
                    except Exception as e:
                        print(f"Error rerouting vehicle {veh['id']}: {e}")

            step += 1

        traci.close()
        print("Simulation complete.")
    except Exception as e:
        print(f"Error during simulation: {e}")

# Run the simulation
run_simulation()
