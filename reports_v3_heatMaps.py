import os
import traci
import random
import matplotlib.pyplot as plt

# Parameters
sumo_cmd = ["sumo-gui", "-c", "osm_adjusted.sumocfg"]
vehicle_limit = 4000  # Maximum allowed vehicles in the simulation
max_steps = 1800  # Total simulation steps
high_removal_rate = 0.03  # Initial removal rate (3%)
low_removal_rate = 0.005  # Reduced removal rate (0.5%)
removal_interval = 5  # Perform removal every 5 steps
free_flow_range = (1500, 1600)  # Range of vehicles for minimal traffic

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

# Ensure REPORTS folder exists
os.makedirs("REPORTS", exist_ok=True)

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

def collect_vehicle_details(step):
    """
    Collects details for up to 10 vehicles during the simulation.
    """
    for veh_id in traci.vehicle.getIDList()[:10]:  # Limit to 10 vehicles
        if veh_id not in vehicle_details:
            position = traci.vehicle.getPosition(veh_id)
            vehicle_details[veh_id] = {
                "start": position,
                "distance": 0,
                "speed": [],
            }
        vehicle_details[veh_id]["distance"] = traci.vehicle.getDistance(veh_id)
        vehicle_details[veh_id]["speed"].append(traci.vehicle.getSpeed(veh_id))

def generate_heatmap(data, title, filename):
    """
    Generates and saves a heatmap.
    Args:
        data (list): List of vehicle positions as (x, y) coordinates.
        title (str): Title of the heatmap.
        filename (str): Output file path.
    """
    if not data:
        print(f"No data to generate {title} heatmap.")
        return

    x, y = zip(*data)
    plt.figure(figsize=(10, 8))
    plt.scatter(x, y, c='red', alpha=0.6, s=10)  # Scatter plot for clearer visibility
    plt.title(title)
    plt.xlabel("X-coordinate")
    plt.ylabel("Y-coordinate")
    plt.grid(True)
    plt.savefig(filename)
    plt.close()

def plot_trends(vehicle_count_history, speed_history, steps):
    """
    Plots traffic trends based on collected data.
    """
    plt.figure(figsize=(14, 7))

    # Plot vehicle count over time
    plt.subplot(2, 1, 1)
    plt.plot(range(steps), vehicle_count_history, label="Vehicle Count")
    plt.axhline(vehicle_limit, color="red", linestyle="--", label="Vehicle Limit")
    plt.xlabel("Time Step")
    plt.ylabel("Number of Vehicles")
    plt.title("Vehicle Count Over Time")
    plt.legend()

    # Plot average speed over time
    plt.subplot(2, 1, 2)
    plt.plot(range(steps), speed_history, label="Average Speed", color="orange")
    plt.xlabel("Time Step")
    plt.ylabel("Speed (m/s)")
    plt.title("Average Speed Over Time")
    plt.legend()

    plt.tight_layout()
    plt.savefig("REPORTS/traffic_trends.png")
    plt.close()

# Main Simulation Loop
traci.start(sumo_cmd)
step = 0
reduction_mechanism_activated = False
captured_peak = False

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

    # Stage-based speed tracking
    if step < max_steps // 3:
        stage_speed_data["start"].append(avg_speed)
        collect_vehicle_positions(step, "start")
    elif max_steps // 3 <= step < 2 * max_steps // 3:
        stage_speed_data["peak"].append(avg_speed)
        collect_vehicle_positions(step, "peak")
        captured_peak = True
    else:
        stage_speed_data["offpeak"].append(avg_speed)
        collect_vehicle_positions(step, "offpeak")

    # Vehicle removal logic
    if current_vehicles >= vehicle_limit and not reduction_mechanism_activated:
        reduction_mechanism_activated = True

    if reduction_mechanism_activated and step % removal_interval == 0:
        if current_vehicles > free_flow_range[1]:
            remove_random_vehicles(high_removal_rate)
        elif free_flow_range[0] <= current_vehicles <= free_flow_range[1]:
            remove_random_vehicles(low_removal_rate)

    # Collect vehicle details
    collect_vehicle_details(step)
    step += 1

traci.close()

# Save reports and plots
with open("REPORTS/simulation_summary.txt", "w") as f:
    f.write(f"Total Steps: {max_steps}\n")
    f.write(f"Maximum Vehicles in Network: {max(vehicle_count_history)}\n")
    f.write(f"Vehicles Inserted: {vehicles_inserted}\n")
    f.write(f"Vehicles Removed: {vehicles_removed}\n")
    f.write(f"Average Speed (Start): {sum(stage_speed_data['start']) / len(stage_speed_data['start']):.2f} m/s\n")
    f.write(f"Average Speed (Peak): {sum(stage_speed_data['peak']) / len(stage_speed_data['peak']):.2f} m/s\n")
    f.write(f"Average Speed (Off-Peak): {sum(stage_speed_data['offpeak']) / len(stage_speed_data['offpeak']):.2f} m/s\n")

with open("REPORTS/vehicle_details.txt", "w") as f:
    for veh_id, data in vehicle_details.items():
        start = data["start"]
        f.write(f"Vehicle {veh_id}: Start={start}, Distance={data['distance']:.2f} m, Avg Speed={sum(data['speed']) / len(data['speed']):.2f} m/s\n")

generate_heatmap(heatmap_data_start, "Traffic at Start", "REPORTS/heatmap_start.png")
generate_heatmap(heatmap_data_peak, "Traffic at Peak", "REPORTS/heatmap_peak.png")
generate_heatmap(heatmap_data_offpeak, "Traffic at Off-Peak", "REPORTS/heatmap_offpeak.png")
plot_trends(vehicle_count_history, speed_history, max_steps)
