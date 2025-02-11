<<<<<<< HEAD
import traci
import random
import matplotlib.pyplot as plt

# Simulation Parameters
sumo_cmd = ["sumo-gui", "-c", "osm_adjusted.sumocfg"]  # SUMO configuration file
vehicle_limit = 4000  # Maximum allowed vehicles in the simulation
max_steps = 1600  # Total simulation steps
high_removal_rate = 0.03  # Initial removal rate (3%)
low_removal_rate = 0.005  # Reduced removal rate (0.5%)
removal_interval = 5  # Perform removal every 5 steps
free_flow_range = (1400, 1600)  # Range of vehicles for minimal traffic
reroute_interval = 10  # Steps between rerouting
graph_update_interval = 10  # Steps between graph updates
vehicle_ids_to_reroute = ["veh162", "veh179", "veh2276", "veh639", "veh594"]  # Vehicles to dynamically reroute

# Data tracking
vehicle_count_history = []
speed_history = []
original_data = {
    "veh162": {"distance": 13.80, "time": 762.00, "speed": 18.12},
    "veh163": {"distance": 13.27, "time": 1074.00, "speed": 12.36},
    "veh322": {"distance": 12.85, "time": 859.00, "speed": 14.96},
    "veh594": {"distance": 12.71, "time": 1079.00, "speed": 11.78},
    "veh873": {"distance": 12.23, "time": 805.00, "speed": 15.19},
}
rerouting_results = {}

# Functions
def create_graph():
    """
    Create a graph using edges and lanes from the SUMO network.
    """
    graph = {}
    for edge_id in traci.edge.getIDList():
        lane_id = edge_id + "_0"
        if lane_id in traci.lane.getIDList():
            connections = traci.lane.getLinks(lane_id)  # Get lane links
            graph[edge_id] = {conn[0]: traci.lane.getLength(lane_id) for conn in connections if conn[0]}
    return graph

def reroute_vehicle(veh_id, graph):
    """
    Dynamically reroute a vehicle using the shortest path in the graph.
    """
    try:
        current_edge = traci.vehicle.getRoadID(veh_id)
        destination_edge = traci.vehicle.getRoute(veh_id)[-1]

        if current_edge and destination_edge and current_edge in graph:
            shortest_path = [current_edge]
            while shortest_path[-1] != destination_edge:
                neighbors = graph[shortest_path[-1]]
                if not neighbors:
                    break
                shortest_path.append(min(neighbors, key=neighbors.get))
            traci.vehicle.setRoute(veh_id, shortest_path)
            print(f"Vehicle {veh_id} dynamically rerouted.")
    except Exception as e:
        print(f"Error rerouting vehicle {veh_id}: {e}")

def remove_random_vehicles(rate):
    """
    Remove a percentage of vehicles randomly from the simulation.
    """
    vehicles_to_remove = random.sample(traci.vehicle.getIDList(), int(len(traci.vehicle.getIDList()) * rate))
    for veh_id in vehicles_to_remove:
        traci.vehicle.remove(veh_id)
    print(f"Removed {len(vehicles_to_remove)} vehicles.")

def record_vehicle_data(veh_id, step):
    """
    Record final data for selected vehicles.
    """
    if veh_id in traci.vehicle.getIDList():
        travel_time = step - traci.vehicle.getDeparture(veh_id)
        distance_traveled = traci.vehicle.getDistance(veh_id)
        avg_speed = distance_traveled / travel_time if travel_time > 0 else 0

        rerouting_results[veh_id] = {
            "distance": distance_traveled / 1000,  # Convert to km
            "time": travel_time,
            "speed": avg_speed,
        }

def plot_trends():
    """
    Plot traffic trends for vehicle count and speed.
    """
    plt.figure(figsize=(14, 7))

    # Plot vehicle count over time
    plt.subplot(2, 1, 1)
    plt.plot(range(len(vehicle_count_history)), vehicle_count_history, label="Vehicle Count")
    plt.axhline(vehicle_limit, color="red", linestyle="--", label="Vehicle Limit")
    plt.xlabel("Time Step")
    plt.ylabel("Number of Vehicles")
    plt.title("Vehicle Count Over Time")
    plt.legend()

    # Plot average speed over time
    plt.subplot(2, 1, 2)
    plt.plot(range(len(speed_history)), speed_history, label="Average Speed", color="orange")
    plt.xlabel("Time Step")
    plt.ylabel("Speed (m/s)")
    plt.title("Average Speed Over Time")
    plt.legend()

    plt.tight_layout()
    plt.show()

def run_simulation():
    """
    Run the simulation, enforcing vehicle limits and dynamic rerouting.
    """
    traci.start(sumo_cmd)
    graph = create_graph()
    step = 0
    reached_limit = False

    while step < max_steps:
        traci.simulationStep()
        current_vehicles = traci.vehicle.getIDCount()

        vehicle_count_history.append(current_vehicles)
        avg_speed = (
            sum(traci.vehicle.getSpeed(veh_id) for veh_id in traci.vehicle.getIDList())
            / current_vehicles if current_vehicles > 0 else 0
        )
        speed_history.append(avg_speed)

        # Enforce vehicle limit and adjust removal rate dynamically
        if current_vehicles >= vehicle_limit:
            if not reached_limit:
                print(f"Vehicle limit reached: {vehicle_limit}. Managing traffic.")
                reached_limit = True

            if step % removal_interval == 0:
                if current_vehicles > free_flow_range[1]:
                    print("Applying high removal rate to reduce congestion.")
                    remove_random_vehicles(high_removal_rate)
                elif free_flow_range[0] <= current_vehicles <= free_flow_range[1]:
                    print("Applying low removal rate to maintain free flow.")
                    remove_random_vehicles(low_removal_rate)

        # Update graph and reroute vehicles periodically
        if step % graph_update_interval == 0:
            for veh_id in vehicle_ids_to_reroute:
                if veh_id in traci.vehicle.getIDList():
                    reroute_vehicle(veh_id, graph)

        # Record data at the last step
        if step == max_steps - 1:
            for veh_id in vehicle_ids_to_reroute:
                record_vehicle_data(veh_id, step)

        step += 1

    traci.close()
    print("Simulation complete. Generating report...")
    generate_report()
    plot_trends()

def generate_report():
    """
    Generate a comparison report for selected vehicles.
    """
    print("\nComparison of Pre- and Post-Rerouting Data:")
    print("{:<10} {:<15} {:<15} {:<15}".format("Vehicle", "Distance (km)", "Time (s)", "Avg Speed (m/s)"))
    print("-" * 55)

    for veh_id, original in original_data.items():
        rerouted = rerouting_results.get(veh_id, {})
        print("{:<10} {:<15.2f} {:<15.2f} {:<15.2f}".format(
            veh_id,
            rerouted.get("distance", 0),
            rerouted.get("time", 0),
            rerouted.get("speed", 0),
        ))

# Run the simulation
run_simulation()
=======
import traci
import random
import matplotlib.pyplot as plt

# Simulation Parameters
sumo_cmd = ["sumo-gui", "-c", "osm_adjusted.sumocfg"]  # SUMO configuration file
vehicle_limit = 4000  # Maximum allowed vehicles in the simulation
max_steps = 1600  # Total simulation steps
high_removal_rate = 0.03  # Initial removal rate (3%)
low_removal_rate = 0.005  # Reduced removal rate (0.5%)
removal_interval = 5  # Perform removal every 5 steps
free_flow_range = (1400, 1600)  # Range of vehicles for minimal traffic
reroute_interval = 10  # Steps between rerouting
graph_update_interval = 10  # Steps between graph updates
vehicle_ids_to_reroute = ["veh162", "veh179", "veh2276", "veh639", "veh594"]  # Vehicles to dynamically reroute

# Data tracking
vehicle_count_history = []
speed_history = []
original_data = {
    "veh162": {"distance": 13.80, "time": 762.00, "speed": 18.12},
    "veh163": {"distance": 13.27, "time": 1074.00, "speed": 12.36},
    "veh322": {"distance": 12.85, "time": 859.00, "speed": 14.96},
    "veh594": {"distance": 12.71, "time": 1079.00, "speed": 11.78},
    "veh873": {"distance": 12.23, "time": 805.00, "speed": 15.19},
}
rerouting_results = {}

# Functions
def create_graph():
    """
    Create a graph using edges and lanes from the SUMO network.
    """
    graph = {}
    for edge_id in traci.edge.getIDList():
        lane_id = edge_id + "_0"
        if lane_id in traci.lane.getIDList():
            connections = traci.lane.getLinks(lane_id)  # Get lane links
            graph[edge_id] = {conn[0]: traci.lane.getLength(lane_id) for conn in connections if conn[0]}
    return graph

def reroute_vehicle(veh_id, graph):
    """
    Dynamically reroute a vehicle using the shortest path in the graph.
    """
    try:
        current_edge = traci.vehicle.getRoadID(veh_id)
        destination_edge = traci.vehicle.getRoute(veh_id)[-1]

        if current_edge and destination_edge and current_edge in graph:
            shortest_path = [current_edge]
            while shortest_path[-1] != destination_edge:
                neighbors = graph[shortest_path[-1]]
                if not neighbors:
                    break
                shortest_path.append(min(neighbors, key=neighbors.get))
            traci.vehicle.setRoute(veh_id, shortest_path)
            print(f"Vehicle {veh_id} dynamically rerouted.")
    except Exception as e:
        print(f"Error rerouting vehicle {veh_id}: {e}")

def remove_random_vehicles(rate):
    """
    Remove a percentage of vehicles randomly from the simulation.
    """
    vehicles_to_remove = random.sample(traci.vehicle.getIDList(), int(len(traci.vehicle.getIDList()) * rate))
    for veh_id in vehicles_to_remove:
        traci.vehicle.remove(veh_id)
    print(f"Removed {len(vehicles_to_remove)} vehicles.")

def record_vehicle_data(veh_id, step):
    """
    Record final data for selected vehicles.
    """
    if veh_id in traci.vehicle.getIDList():
        travel_time = step - traci.vehicle.getDeparture(veh_id)
        distance_traveled = traci.vehicle.getDistance(veh_id)
        avg_speed = distance_traveled / travel_time if travel_time > 0 else 0

        rerouting_results[veh_id] = {
            "distance": distance_traveled / 1000,  # Convert to km
            "time": travel_time,
            "speed": avg_speed,
        }

def plot_trends():
    """
    Plot traffic trends for vehicle count and speed.
    """
    plt.figure(figsize=(14, 7))

    # Plot vehicle count over time
    plt.subplot(2, 1, 1)
    plt.plot(range(len(vehicle_count_history)), vehicle_count_history, label="Vehicle Count")
    plt.axhline(vehicle_limit, color="red", linestyle="--", label="Vehicle Limit")
    plt.xlabel("Time Step")
    plt.ylabel("Number of Vehicles")
    plt.title("Vehicle Count Over Time")
    plt.legend()

    # Plot average speed over time
    plt.subplot(2, 1, 2)
    plt.plot(range(len(speed_history)), speed_history, label="Average Speed", color="orange")
    plt.xlabel("Time Step")
    plt.ylabel("Speed (m/s)")
    plt.title("Average Speed Over Time")
    plt.legend()

    plt.tight_layout()
    plt.show()

def run_simulation():
    """
    Run the simulation, enforcing vehicle limits and dynamic rerouting.
    """
    traci.start(sumo_cmd)
    graph = create_graph()
    step = 0
    reached_limit = False

    while step < max_steps:
        traci.simulationStep()
        current_vehicles = traci.vehicle.getIDCount()

        vehicle_count_history.append(current_vehicles)
        avg_speed = (
            sum(traci.vehicle.getSpeed(veh_id) for veh_id in traci.vehicle.getIDList())
            / current_vehicles if current_vehicles > 0 else 0
        )
        speed_history.append(avg_speed)

        # Enforce vehicle limit and adjust removal rate dynamically
        if current_vehicles >= vehicle_limit:
            if not reached_limit:
                print(f"Vehicle limit reached: {vehicle_limit}. Managing traffic.")
                reached_limit = True

            if step % removal_interval == 0:
                if current_vehicles > free_flow_range[1]:
                    print("Applying high removal rate to reduce congestion.")
                    remove_random_vehicles(high_removal_rate)
                elif free_flow_range[0] <= current_vehicles <= free_flow_range[1]:
                    print("Applying low removal rate to maintain free flow.")
                    remove_random_vehicles(low_removal_rate)

        # Update graph and reroute vehicles periodically
        if step % graph_update_interval == 0:
            for veh_id in vehicle_ids_to_reroute:
                if veh_id in traci.vehicle.getIDList():
                    reroute_vehicle(veh_id, graph)

        # Record data at the last step
        if step == max_steps - 1:
            for veh_id in vehicle_ids_to_reroute:
                record_vehicle_data(veh_id, step)

        step += 1

    traci.close()
    print("Simulation complete. Generating report...")
    generate_report()
    plot_trends()

def generate_report():
    """
    Generate a comparison report for selected vehicles.
    """
    print("\nComparison of Pre- and Post-Rerouting Data:")
    print("{:<10} {:<15} {:<15} {:<15}".format("Vehicle", "Distance (km)", "Time (s)", "Avg Speed (m/s)"))
    print("-" * 55)

    for veh_id, original in original_data.items():
        rerouted = rerouting_results.get(veh_id, {})
        print("{:<10} {:<15.2f} {:<15.2f} {:<15.2f}".format(
            veh_id,
            rerouted.get("distance", 0),
            rerouted.get("time", 0),
            rerouted.get("speed", 0),
        ))

# Run the simulation
run_simulation()
>>>>>>> ce6e8c5d58803f5752e3c7e69c69579183fcd88f
