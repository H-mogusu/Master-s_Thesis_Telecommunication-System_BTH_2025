import traci
import random

# Parameters
vehicle_limit = 4000  # Maximum allowed vehicles in the simulation
max_steps = 2400  # Total simulation steps
high_removal_rate = 0.03  # Initial removal rate (3%)
low_removal_rate = 0.005  # Reduced removal rate (0.5%)
removal_interval = 5  # Perform removal every 5 steps
free_flow_range = (1200, 1600)  # Range of vehicles for minimal traffic

def remove_random_vehicles(rate):
    """
    Randomly remove a percentage of vehicles from the simulation.
    Args:
        rate (float): Percentage of vehicles to remove.
    """
    vehicle_ids = traci.vehicle.getIDList()
    num_to_remove = int(len(vehicle_ids) * rate)
    vehicles_to_remove = random.sample(vehicle_ids, min(num_to_remove, len(vehicle_ids)))
    for veh_id in vehicles_to_remove:
        traci.vehicle.remove(veh_id)
    print(f"Removed {num_to_remove} vehicles.")

# SUMO Simulation Command
sumo_cmd = ["sumo-gui", "-c", "osm_adjusted.sumocfg"]

# Start the simulation
traci.start(sumo_cmd)
step = 0
reduction_mechanism_activated = False  # Tracks whether reduction has started
vehicles_inserted = 0  # Counter for tracking inserted vehicles
vehicles_removed = 0  # Counter for tracking removed vehicles

while step < max_steps:
    traci.simulationStep()  # Progress simulation by one step
    
    # Track vehicle counts
    current_vehicles = traci.vehicle.getIDCount()  # Current vehicles in the network
    vehicles_inserted += traci.simulation.getDepartedNumber()  # Increment vehicles added
    vehicles_removed += traci.simulation.getArrivedNumber()  # Increment vehicles removed

    print(f"Step {step}: {current_vehicles} vehicles currently in the simulation.")
    
    if current_vehicles >= vehicle_limit and not reduction_mechanism_activated:
        # Activate reduction mechanisms when the limit is reached
        print(f"Vehicle limit reached: {vehicle_limit}. Initiating reduction mechanisms.")
        reduction_mechanism_activated = True

    if reduction_mechanism_activated and step % removal_interval == 0:
        # Adjust removal rate dynamically based on the current number of vehicles
        if current_vehicles > free_flow_range[1]:
            # Apply higher removal rate if vehicles are above free flow range
            print("Applying high removal rate to reduce congestion.")
            remove_random_vehicles(high_removal_rate)
        elif free_flow_range[0] <= current_vehicles <= free_flow_range[1]:
            # Apply reduced removal rate within free flow range
            print("Applying reduced removal rate to maintain free flow.")
            remove_random_vehicles(low_removal_rate)
    
    step += 1

# Close the simulation
traci.close()

# Final report
print(f"Simulation ended. Vehicles inserted: {vehicles_inserted}, vehicles removed: {vehicles_removed}.")
