import matplotlib.pyplot as plt
import numpy as np

# Data from Scenario 1: Dynamic Rerouting without Passenger Pickup
routes = ["Route 1", "Route 2", "Route 3", "Route 4", "Route 5"]
btt = [30, 45, 40, 50, 35]  # Baseline Travel Time (BTT)
rtt = [26, 42, 43, 48, 27]  # Rerouted Travel Time (RTT)
time_saved = [4, 3, -3, 2, 8]  # Time Saved

# Plot Comparison of BTT vs. RTT (Bar Chart)
fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(routes))
width = 0.3

ax.bar(x - width/2, btt, width, label="Baseline Travel Time (BTT)", color="red")
ax.bar(x + width/2, rtt, width, label="Rerouted Travel Time (RTT)", color="green")

ax.set_xlabel("Routes")
ax.set_ylabel("Time (Minutes)")
ax.set_title("Comparison of Baseline and Rerouted Travel Times")
ax.set_xticks(x)
ax.set_xticklabels(routes)
ax.legend()
ax.grid(axis="y", linestyle="--", alpha=0.7)

# Save figure
plt.savefig("rtt_vs_btt.png")
plt.show()

# Plot Histogram of Time Savings
fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(time_saved, bins=np.arange(min(time_saved)-1, max(time_saved)+2, 1), color="blue", alpha=0.7, edgecolor="black")

ax.set_xlabel("Time Saved (Minutes)")
ax.set_ylabel("Frequency")
ax.set_title("Histogram of Time Savings Across Routes")
ax.grid(axis="y", linestyle="--", alpha=0.7)

# Save figure
plt.savefig("time_savings_distribution.png")
plt.show()
