import traci
import random
import matplotlib.pyplot as plt
import numpy as np

# Parameters
sumo_cmd = ["sumo-gui", "-c", "osm_adjusted.sumocfg"]
vehicle_limit = 4200  # Maximum allowed vehicles in the simulation
max_steps = 1800  # Total simulation steps
high_removal_rate = 0.03  # Initial removal rate (3%)
low_removal_rate = 0.005  # Reduced removal rate (0.5%)
removal_interval = 5  # Perform removal every 5 steps
free_flow_range = (2000, 2300)  # Range of vehicles for minimal traffic

# Data storage
vehicle_count_history = []
speed_history = []
vehicles_inserted = 0
vehicles_removed = 0
heatmap_data_start = []
heatmap_data_peak = []
heatmap_data_offpeak = []

# Helper Functions
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
    print(f"Removed {len(vehicles_to_remove)} vehicles.")

def collect_vehicle_positions(step, stage):
    """
    Collects vehicle positions for heatmap visualization.
    Args:
        step (int): Current simulation step.
        stage (str): The stage of simulation ('start', 'peak', 'offpeak').
    """
    positions = [(traci.vehicle.getPosition(veh_id)) for veh_id in traci.vehicle.getIDList()]
    if stage == "start":
        heatmap_data_start.extend(positions)
    elif stage == "peak":
        heatmap_data_peak.extend(positions)
    elif stage == "offpeak":
        heatmap_data_offpeak.extend(positions)

def generate_heatmap(data, title):
    """
    Generates and displays a heatmap.
    Args:
        data (list): List of vehicle positions as (x, y) coordinates.
        title (str): Title of the heatmap.
    """
    if not data:
        print(f"No data to generate {title} heatmap.")
        return
    
    x, y = zip(*data)
    heatmap, xedges, yedges = np.histogram2d(x, y, bins=(50, 50))

    plt.imshow(
        heatmap.T, 
        origin='lower', 
        cmap='hot', 
        interpolation='nearest'
    )
    plt.colorbar()
    plt.title(title)
    plt.xlabel("X-coordinate")
    plt.ylabel("Y-coordinate")
    plt.show()

# Main Simulation Loop
traci.start(sumo_cmd)
step = 0
reduction_mechanism_activated = False
captured_peak = False

while step < max_steps:
    traci.simulationStep()  # Progress simulation by one step
    
    # Collect current vehicle statistics
    current_vehicles = traci.vehicle.getIDCount()
    vehicle_count_history.append(current_vehicles)
    avg_speed = (
        sum(traci.vehicle.getSpeed(veh_id) for veh_id in traci.vehicle.getIDList())
        / current_vehicles if current_vehicles > 0 else 0
    )
    speed_history.append(avg_speed)
    vehicles_inserted += traci.simulation.getDepartedNumber()
    vehicles_removed += traci.simulation.getArrivedNumber()

    print(f"Step {step}: {current_vehicles} vehicles, Avg Speed: {avg_speed:.2f} m/s")

    # Collect data for heatmaps
    if step == 0:  # Start of simulation
        collect_vehicle_positions(step, "start")
    elif current_vehicles >= vehicle_limit and not captured_peak:  # Peak traffic
        collect_vehicle_positions(step, "peak")
        captured_peak = True
    elif step == max_steps - 1:  # Off-peak traffic
        collect_vehicle_positions(step, "offpeak")

    if current_vehicles >= vehicle_limit and not reduction_mechanism_activated:
        # Activate reduction mechanisms when the limit is reached
        print(f"Vehicle limit reached: {vehicle_limit}. Initiating reduction mechanisms.")
        reduction_mechanism_activated = True

    if reduction_mechanism_activated and step % removal_interval == 0:
        # Adjust removal rate dynamically based on the current number of vehicles
        if current_vehicles > free_flow_range[1]:
            print("Applying high removal rate to reduce congestion.")
            remove_random_vehicles(high_removal_rate)
        elif free_flow_range[0] <= current_vehicles <= free_flow_range[1]:
            print("Applying reduced removal rate to maintain free flow.")
            remove_random_vehicles(low_removal_rate)

    step += 1

traci.close()

# Generate report
print("Simulation complete. Generating report...")
report_file = "traffic_simulation_report.txt"
with open(report_file, "w") as f:
    f.write("Traffic Simulation Report\n")
    f.write("=" * 30 + "\n")
    f.write(f"Total Steps: {max_steps}\n")
    f.write(f"Maximum Vehicles in Network: {max(vehicle_count_history)}\n")
    f.write(f"Average Speed Over Simulation: {sum(speed_history) / len(speed_history):.2f} m/s\n")
    f.write(f"Vehicles Inserted: {vehicles_inserted}\n")
    f.write(f"Vehicles Removed: {vehicles_removed}\n")
    f.write("\nTraffic Flow Over Time:\n")
    for idx, count in enumerate(vehicle_count_history):
        if idx % 100 == 0:  # Print every 100 steps
            f.write(f"Step {idx}: {count} vehicles\n")

print(f"Report saved to {report_file}.")
print("Displaying heatmaps and traffic trends...")

# Display heatmaps and trends
generate_heatmap(heatmap_data_start, "Traffic at Start")
generate_heatmap(heatmap_data_peak, "Traffic at Peak")
generate_heatmap(heatmap_data_offpeak, "Traffic at Off-Peak")
plot_trends(vehicle_count_history, speed_history, max_steps)
