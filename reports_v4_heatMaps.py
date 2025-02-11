import os
import traci
import random
import matplotlib.pyplot as plt
import pandas as pd

# Parameters
sumo_cmd = ["sumo-gui", "-c", "osm_adjusted.sumocfg"]
vehicle_limit = 3000  # Maximum allowed vehicles in the simulation
max_steps = 600  # Total simulation steps
high_removal_rate = 0.03  # Initial removal rate (3%)
low_removal_rate = 0.005  # Reduced removal rate (0.5%)
removal_interval = 5  # Perform removal every 5 steps
free_flow_range = (1600, 1800)  # Range of vehicles for minimal traffic

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

def highlight_vehicle(vehicle_id, color=(255, 0, 0, 255)):
    """
    Highlights a specific vehicle by changing its color.
    Args:
        vehicle_id (str): ID of the vehicle to highlight.
        color (tuple): RGBA color tuple (default is red).
    """
    try:
        traci.vehicle.setColor(vehicle_id, color)
        print(f"Vehicle '{vehicle_id}' highlighted with color {color}.")
    except traci.TraCIException:
        print(f"Vehicle '{vehicle_id}' not found.")

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
    Collects details for passenger cars during the simulation.
    """
    for veh_id in traci.vehicle.getIDList():
        if "passenger" in traci.vehicle.getTypeID(veh_id):
            if veh_id not in vehicle_details:
                position = traci.vehicle.getPosition(veh_id)
                vehicle_details[veh_id] = {
                    "start": position,
                    "distance": 0,
                    "speed": [],
                    "end": None,
                }
            vehicle_details[veh_id]["distance"] = traci.vehicle.getDistance(veh_id)
            vehicle_details[veh_id]["speed"].append(traci.vehicle.getSpeed(veh_id))
            vehicle_details[veh_id]["end"] = traci.vehicle.getPosition(veh_id)

def generate_heatmap(data, title, filename, ratio=1000):
    """
    Generates and saves a heatmap.
    Args:
        data (list): List of vehicle positions as (x, y) coordinates.
        title (str): Title of the heatmap.
        filename (str): Output file path.
        ratio (int): Ratio for scaling (1 dot = X cars).
    """
    if not data:
        print(f"No data to generate {title} heatmap.")
        return

    x, y = zip(*data)
    plt.figure(figsize=(10, 8))
    plt.hist2d(x, y, bins=(50, 50), cmin=ratio, cmap='YlOrRd')
    plt.colorbar(label=f'Number of vehicles (scaled by {ratio})')
    plt.title(title)
    plt.xlabel("X-coordinate")
    plt.ylabel("Y-coordinate")
    plt.grid(True)
    plt.savefig(filename)
    plt.close()

def plot_trends(vehicle_count_history, speed_history, stage_speed_data):
    """
    Plots traffic trends based on collected data and generates stage-specific graphs.
    """
    # Overall trends
    plt.figure(figsize=(14, 7))

    # Vehicle Count Over Time
    plt.subplot(2, 1, 1)
    plt.plot(range(len(vehicle_count_history)), vehicle_count_history, label="Vehicle Count")
    plt.axhline(vehicle_limit, color="red", linestyle="--", label="Vehicle Limit")
    plt.xlabel("Time Step")
    plt.ylabel("Number of Vehicles")
    plt.title("Vehicle Count Over Time")
    plt.legend()

    # Average Speed Over Time
    plt.subplot(2, 1, 2)
    plt.plot(range(len(speed_history)), speed_history, label="Average Speed", color="orange")
    plt.xlabel("Time Step")
    plt.ylabel("Speed (m/s)")
    plt.title("Average Speed Over Time")
    plt.legend()

    plt.tight_layout()
    plt.savefig("REPORTS/traffic_trends.png")
    plt.close()

    # Stage-specific average speeds
    plt.figure(figsize=(10, 5))
    stages = ["Start", "Peak", "Off-Peak"]
    avg_speeds = [
        sum(stage_speed_data["start"]) / len(stage_speed_data["start"]),
        sum(stage_speed_data["peak"]) / len(stage_speed_data["peak"]),
        sum(stage_speed_data["offpeak"]) / len(stage_speed_data["offpeak"]),
    ]
    plt.bar(stages, avg_speeds, color=["blue", "orange", "green"])
    plt.xlabel("Stages")
    plt.ylabel("Average Speed (m/s)")
    plt.title("Average Speeds Across Different Traffic Stages")
    plt.savefig("REPORTS/stage_avg_speeds.png")
    plt.close()

def generate_passenger_car_report():
    """
    Generates a detailed report for passenger cars with the specified criteria.
    """
    df = pd.DataFrame.from_dict(vehicle_details, orient='index')
    df['average_speed'] = df['speed'].apply(lambda x: sum(x) / len(x) if len(x) > 0 else 0)
    df = df.sort_values(by='distance', ascending=False)

    top_5_longest = df.head(5)
    middle_5 = df.iloc[len(df)//2 - 2:len(df)//2 + 3]
    slowest_5 = df.nsmallest(5, 'average_speed')

    with pd.ExcelWriter("REPORTS/passenger_car_report.xlsx") as writer:
        top_5_longest.to_excel(writer, sheet_name="Longest Distance", index=True)
        middle_5.to_excel(writer, sheet_name="Middle Speed", index=True)
        slowest_5.to_excel(writer, sheet_name="Slowest Cars", index=True)

    print("Passenger car report saved to REPORTS/passenger_car_report.xlsx")

# Main Simulation Loop
traci.start(sumo_cmd)
step = 0
reduction_mechanism_activated = False

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

    # Highlight veh99 in red
    if "veh99" in traci.vehicle.getIDList():
        highlight_vehicle("veh99")

    # Stage-based speed tracking
    if step < max_steps // 3:
        stage_speed_data["start"].append(avg_speed)
        collect_vehicle_positions(step, "start")
    elif max_steps // 3 <= step < 2 * max_steps // 3:
        stage_speed_data["peak"].append(avg_speed)
        collect_vehicle_positions(step, "peak")
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
generate_heatmap(heatmap_data_start, "Traffic at Start", "REPORTS/heatmap_start2.png")
generate_heatmap(heatmap_data_peak, "Traffic at Peak", "REPORTS/heatmap_peak2.png")
generate_heatmap(heatmap_data_offpeak, "Traffic at Off-Peak", "REPORTS/heatmap_offpeak2.png")
plot_trends(vehicle_count_history, speed_history, stage_speed_data)
generate_passenger_car_report()

print("Simulation complete. Reports generated in the REPORTS folder.")
