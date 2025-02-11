import matplotlib.pyplot as plt
import numpy as np

# Data for travel times
routes = ["Route 1", "Route 2", "Route 3", "Route 4", "Route 5"]
actual_times = [15, 22.51, 20, 25, 17.5]  # Actual SUMO times
scaled_times = [t * 2 for t in actual_times]  # Applying scale factor

# Create Bar Chart: Actual vs. Scaled Travel Times
fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(routes))
width = 0.3

ax.bar(x - width/2, actual_times, width, label="Actual Time (SUMO)", color="blue")
ax.bar(x + width/2, scaled_times, width, label="Scaled Time (Real-World)", color="orange")

# Labels and formatting
ax.set_xlabel("Routes")
ax.set_ylabel("Time (Minutes)")
ax.set_title("Comparison of Actual vs. Scaled Travel Times")
ax.set_xticks(x)
ax.set_xticklabels(routes)
ax.legend()
ax.grid(axis="y", linestyle="--", alpha=0.7)

# Save figure
plt.savefig("actual_vs_scaled_time.png")
plt.show()

# Generate Line Graph for Baseline Travel Times
baseline_times = [30, 45, 40, 50, 35]  # Given BTT (Baseline Travel Time)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(routes, baseline_times, marker="o", linestyle="-", color="red", label="Baseline Travel Time")

# Labels and formatting
ax.set_xlabel("Routes")
ax.set_ylabel("Travel Time (Minutes)")
ax.set_title("Baseline Travel Times for Each Route")
ax.legend()
ax.grid(axis="y", linestyle="--", alpha=0.7)

# Save figure
plt.savefig("baseline_travel_time_chart.png")
plt.show()
