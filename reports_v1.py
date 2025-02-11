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
    plt.show()

# Start the simulation
traci.start(sumo_cmd)
step = 0
reduction_mechanism_activated = False

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
print("Displaying traffic trends...")

# Display trends
plot_trends(vehicle_count_history, speed_history, max_steps)
