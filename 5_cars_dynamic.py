<<<<<<< HEAD
import traci
import random

# Parameters
sumo_cmd = ["sumo-gui", "-c", "osm_adjusted.sumocfg"]  # SUMO command
vehicle_ids_to_reroute = ["veh162", "veh179", "veh2276", "veh639", "veh594"]  # Vehicles for rerouting
reroute_interval = 10  # How often to reroute (in steps)
simulation_steps = 2400  # Total simulation steps

# Travel data for comparison
original_data = {
    "veh162": {"distance": 13.80, "time": 762.00, "speed": 18.12},
    "veh179": {"distance": 13.27, "time": 1074.00, "speed": 12.36},
    "veh2276": {"distance": 12.85, "time": 859.00, "speed": 14.96},
    "veh639": {"distance": 12.71, "time": 1079.00, "speed": 11.78},
    "veh594": {"distance": 12.23, "time": 805.00, "speed": 15.19},
}

# Store results after rerouting
rerouting_results = {}

def reroute_vehicle(veh_id):
    """
    Reroutes a vehicle dynamically to avoid traffic.
    """
    try:
        current_edge = traci.vehicle.getRoadID(veh_id)
        destination_edge = traci.vehicle.getRoute(veh_id)[-1]

        if current_edge != "" and destination_edge != "":
            # Calculate alternate route dynamically
            rerouted_path = traci.simulation.findRoute(current_edge, destination_edge).edges
            traci.vehicle.setRoute(veh_id, rerouted_path)
            print(f"Vehicle {veh_id} rerouted dynamically.")
    except traci.exceptions.TraCIException as e:
        print(f"Error rerouting vehicle {veh_id}: {e}. Skipping.")

def record_vehicle_data(veh_id, step):
    """
    Records travel data for a specific vehicle at the given step.
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

def run_simulation():
    """
    Runs the simulation and dynamically reroutes selected vehicles.
    """
    traci.start(sumo_cmd)
    step = 0

    while step < simulation_steps:
        traci.simulationStep()

        # Reroute selected vehicles at intervals
        if step % reroute_interval == 0:
            for veh_id in vehicle_ids_to_reroute:
                if veh_id in traci.vehicle.getIDList():
                    reroute_vehicle(veh_id)

        # Record vehicle data at the end of the simulation
        if step == simulation_steps - 1:
            for veh_id in vehicle_ids_to_reroute:
                record_vehicle_data(veh_id, step)

        step += 1

    traci.close()
    print("Simulation complete. Generating report...")
    generate_report()

def generate_report():
    """
    Generates a report comparing pre- and post-rerouting data.
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

# Parameters
sumo_cmd = ["sumo-gui", "-c", "osm_adjusted.sumocfg"]  # SUMO command
vehicle_ids_to_reroute = ["veh162", "veh179", "veh2276", "veh639", "veh594"]  # Vehicles for rerouting
reroute_interval = 10  # How often to reroute (in steps)
simulation_steps = 2400  # Total simulation steps

# Travel data for comparison
original_data = {
    "veh162": {"distance": 13.80, "time": 762.00, "speed": 18.12},
    "veh179": {"distance": 13.27, "time": 1074.00, "speed": 12.36},
    "veh2276": {"distance": 12.85, "time": 859.00, "speed": 14.96},
    "veh639": {"distance": 12.71, "time": 1079.00, "speed": 11.78},
    "veh594": {"distance": 12.23, "time": 805.00, "speed": 15.19},
}

# Store results after rerouting
rerouting_results = {}

def reroute_vehicle(veh_id):
    """
    Reroutes a vehicle dynamically to avoid traffic.
    """
    try:
        current_edge = traci.vehicle.getRoadID(veh_id)
        destination_edge = traci.vehicle.getRoute(veh_id)[-1]

        if current_edge != "" and destination_edge != "":
            # Calculate alternate route dynamically
            rerouted_path = traci.simulation.findRoute(current_edge, destination_edge).edges
            traci.vehicle.setRoute(veh_id, rerouted_path)
            print(f"Vehicle {veh_id} rerouted dynamically.")
    except traci.exceptions.TraCIException as e:
        print(f"Error rerouting vehicle {veh_id}: {e}. Skipping.")

def record_vehicle_data(veh_id, step):
    """
    Records travel data for a specific vehicle at the given step.
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

def run_simulation():
    """
    Runs the simulation and dynamically reroutes selected vehicles.
    """
    traci.start(sumo_cmd)
    step = 0

    while step < simulation_steps:
        traci.simulationStep()

        # Reroute selected vehicles at intervals
        if step % reroute_interval == 0:
            for veh_id in vehicle_ids_to_reroute:
                if veh_id in traci.vehicle.getIDList():
                    reroute_vehicle(veh_id)

        # Record vehicle data at the end of the simulation
        if step == simulation_steps - 1:
            for veh_id in vehicle_ids_to_reroute:
                record_vehicle_data(veh_id, step)

        step += 1

    traci.close()
    print("Simulation complete. Generating report...")
    generate_report()

def generate_report():
    """
    Generates a report comparing pre- and post-rerouting data.
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
