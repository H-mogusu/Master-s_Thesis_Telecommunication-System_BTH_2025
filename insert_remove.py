import traci
import random

# Parameters
vehicle_limit = 4000
max_steps = 2400  # Extend simulation duration
removal_rate = 0.03  # Reduced to 3% to avoid overly aggressive removal
insertion_rate = 0.02  # Hypothetical percentage for vehicle insertion (check route settings)

def remove_random_vehicles(rate):
    """
    Remove a percentage of vehicles randomly from the simulation.
    """
    vehicle_ids = traci.vehicle.getIDList()
    num_to_remove = int(len(vehicle_ids) * rate)
    vehicles_to_remove = random.sample(vehicle_ids, min(num_to_remove, len(vehicle_ids)))
    for veh_id in vehicles_to_remove:
        traci.vehicle.remove(veh_id)
    print(f"Removed {num_to_remove} vehicles.")

# SUMO Simulation Command
sumo_cmd = ["sumo-gui", "-c", "osm_adjusted.sumocfg"]

traci.start(sumo_cmd)
step = 0
reduction_mechanism_activated = False
vehicles_inserted = 0  # Counter for tracking inserted vehicles
vehicles_removed = 0  # Counter for tracking removed vehicles

while step < max_steps:
    traci.simulationStep()
    
    # Track vehicle counts
    current_vehicles = traci.vehicle.getIDCount()
    vehicles_inserted += traci.simulation.getDepartedNumber()
    vehicles_removed += traci.simulation.getArrivedNumber()

    print(f"Step {step}: {current_vehicles} vehicles currently in the simulation.")
    
    if current_vehicles >= vehicle_limit and not reduction_mechanism_activated:
        print(f"Vehicle limit reached: {vehicle_limit}. Initiating reduction mechanisms.")
        reduction_mechanism_activated = True
    
    if reduction_mechanism_activated:
        # Remove vehicles at a higher rate than insertion
        remove_random_vehicles(removal_rate)
    
    step += 1

traci.close()

# Final report
print(f"Simulation ended. Vehicles inserted: {vehicles_inserted}, vehicles removed: {vehicles_removed}.")
