import matplotlib.pyplot as plt
import numpy as np

# Data for Scenario 2: Dynamic Rerouting with One Passenger Pickup
routes = ["Route 1", "Route 2", "Route 3", "Route 4", "Route 5"]
btt = [30, 45, 40, 50, 35]  # Baseline Travel Time (BTT)
rtt = [26, 42, 43, 48, 27]  # Rerouted Travel Time (RTT)
rtt_pickup = [28.5, 43.1, 39.5, 50.15, 30.1]  # Rerouted Travel Time with Pickup
time_saved = [1.5, 1.9, 0.5, -0.15, 4.9]  # Time Saved

# Plot RTT vs. RTT with Pickup (Bar Chart)
fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(routes))
width = 0.3

ax.bar(x - width/2, btt, width, label="BTT", color="red")
ax.bar(x + width/2, rtt_pickup, width, label="RTT with Pickup", color="green")

ax.set_xlabel("Routes")
ax.set_ylabel("Time (Minutes)")
ax.set_title("Comparison of Baseline Travel Time and RTT with Passenger Pickup")
ax.set_xticks(x)
ax.set_xticklabels(routes)
ax.legend()
ax.grid(axis="y", linestyle="--", alpha=0.7)

# Save figure
plt.savefig("btt_vs_rtt_pickup.png")
plt.show()

# Plot Histogram of Time Savings
fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(time_saved, bins=np.arange(min(time_saved)-1, max(time_saved)+2, 1), color="green", alpha=0.7, edgecolor="black")

ax.set_xlabel("Time Saved (Minutes)")
ax.set_ylabel("Frequency")
ax.set_title("Histogram of Time Saved vs. Lost (Dynamic Rerouting with Pickup)")
ax.grid(axis="y", linestyle="--", alpha=0.7)

# Save figure
plt.savefig("time_savings_pickup.png")
plt.show()
