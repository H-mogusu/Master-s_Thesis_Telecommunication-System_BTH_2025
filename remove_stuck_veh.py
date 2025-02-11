import random
import traci

def remove_random_vehicles(removal_rate):
    """
    Randomly remove a percentage of vehicles stuck from the simulation.
    :param removal_rate: Fraction of vehicles to remove (e.g., 0.1 for 10%).
    """
    vehicle_list = traci.vehicle.getIDList()
    num_to_remove = int(len(vehicle_list) * removal_rate)
    if num_to_remove > 0:
        vehicles_to_remove = random.sample(vehicle_list, num_to_remove)
        for veh_id in vehicles_to_remove:
            print(f"Removing vehicle: {veh_id}")
            traci.vehicle.remove(veh_id)

def enforce_vehicle_limit(vehicle_limit):
    """
    Enforce the vehicle limit by halting new vehicle insertions.
    """
    current_vehicle_count = len(traci.vehicle.getIDList())
    if current_vehicle_count >= vehicle_limit:
        print(f"Vehicle limit reached: {vehicle_limit}. Halting new vehicle insertions.")
        traci.simulation.setParameter("", "insertionsAllowed", "false")

# SUMO Simulation Loop
sumo_cmd = ["sumo-gui", "-c", "osm_adjusted.sumocfg"]  # Use sumo-gui for visualization
traci.start(sumo_cmd)
step = 0

vehicle_limit = 4000  # Maximum number of vehicles allowed in the simulation
removal_rate = 0.1  # Remove 10% of vehicles at each step
reduction_mechanism_activated = False  # Trigger reduction only after the limit is hit

while step < 1200:  # Run for 1200 steps (20 minutes at 1 step per second)
    traci.simulationStep()

    # Check current vehicle count
    current_vehicle_count = len(traci.vehicle.getIDList())
    print(f"Step {step}: {current_vehicle_count} vehicles currently in the simulation.")

    if not reduction_mechanism_activated:
        # Enforce vehicle limit
        enforce_vehicle_limit(vehicle_limit)
        if current_vehicle_count >= vehicle_limit:
            print("Vehicle limit reached! Activating reduction mechanisms.")
            reduction_mechanism_activated = True
    else:
        # Random removal starts only after the limit is hit
        remove_random_vehicles(removal_rate)

    step += 1

traci.close()
