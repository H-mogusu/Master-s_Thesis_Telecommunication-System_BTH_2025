import matplotlib.pyplot as plt
import numpy as np

# Data from the thesis for different scenarios
routes = ["Route 1", "Route 2", "Route 3", "Route 4", "Route 5", "Average"]

# Travel times (Baseline, Rerouted, Rerouted with 1 Pickup, Rerouted with 2 Pickups)
baseline = [30, 45, 40, 50, 35, 40]
rerouted = [26, 42, 43, 48, 27, 37.2]
rerouted_1_pickup = [28.5, 43.1, 39.5, 50.15, 30.1, 38.27]
rerouted_2_pickups = [32.1, 45, 41, 49.8, 33.1, 40.2]

# Percentage improvement in travel time
time_saved_rerouted = [(b - r) / b * 100 for b, r in zip(baseline, rerouted)]
time_saved_rerouted_1_pickup = [(b - r) / b * 100 for b, r in zip(baseline, rerouted_1_pickup)]
time_saved_rerouted_2_pickups = [(b - r) / b * 100 for b, r in zip(baseline, rerouted_2_pickups)]

# Create a bar chart for percentage time saved
x = np.arange(len(routes))
width = 0.2

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(x - width, time_saved_rerouted, width, label="Rerouted (No Pickup)", color="blue")
ax.bar(x, time_saved_rerouted_1_pickup, width, label="Rerouted (1 Pickup)", color="orange")
ax.bar(x + width, time_saved_rerouted_2_pickups, width, label="Rerouted (2 Pickups)", color="green")

# Labels and formatting
ax.set_xlabel("Routes")
ax.set_ylabel("Time Saved (%)")
ax.set_title("Percentage Time Saved in Different Rerouting Scenarios")
ax.set_xticks(x)
ax.set_xticklabels(routes)
ax.legend()
ax.grid(axis="y", linestyle="--", alpha=0.7)

# Display the plot
plt.xticks(rotation=30)
plt.tight_layout()
plt.show()
