import xml.etree.ElementTree as ET

# File path
trajectory_file = "baseline_trajectory.xml"

# Vehicle prefix for passenger cars
vehicle_prefix = "veh"
num_vehicles = 10  # Number of passenger cars to analyze

# Data storage
vehicle_data = []

def process_trajectory(file):
    """
    Process the trajectory file to extract data for passenger cars.
    """
    tree = ET.parse(file)
    root = tree.getroot()
    
    vehicle_positions = {}

    # Parse each timestep
    for timestep in root.findall("timestep"):
        time = float(timestep.attrib["time"])
        for vehicle in timestep.findall("vehicle"):
            veh_id = vehicle.attrib["id"]
            if veh_id.startswith(vehicle_prefix):
                x, y = float(vehicle.attrib["x"]), float(vehicle.attrib["y"])
                speed = float(vehicle.attrib["speed"])
                if veh_id not in vehicle_positions:
                    vehicle_positions[veh_id] = {
                        "start_coord": (x, y),
                        "end_coord": (x, y),
                        "start_time": time,
                        "end_time": time,
                        "distance_traveled": 0.0
                    }
                else:
                    # Update vehicle data
                    veh = vehicle_positions[veh_id]
                    veh["end_coord"] = (x, y)
                    veh["end_time"] = time
                    veh["distance_traveled"] += speed

    # Finalize vehicle data
    for veh_id, data in vehicle_positions.items():
        travel_time = data["end_time"] - data["start_time"]
        avg_speed = data["distance_traveled"] / travel_time if travel_time > 0 else 0
        data["travel_time"] = travel_time
        data["average_speed"] = avg_speed
        vehicle_data.append({
            "id": veh_id,
            "distance_traveled": data["distance_traveled"],
            "travel_time": travel_time,
            "average_speed": avg_speed,
            "start_coord": data["start_coord"],
            "end_coord": data["end_coord"]
        })

# Process trajectory file
process_trajectory(trajectory_file)

# Sort and filter top vehicles
vehicle_data = sorted(
    vehicle_data,
    key=lambda x: x["distance_traveled"],
    reverse=True
)[:num_vehicles]

# Print Results
print(f"\nData for TOP {num_vehicles} PASSENGER CARS:")
print(f"{'ID':<15}{'Distance (km)':<15}{'Travel Time (s)':<20}{'Avg Speed (m/s)':<20}")
for veh in vehicle_data:
    distance_km = veh['distance_traveled'] / 1000  # Convert meters to km
    print(f"{veh['id']:<15}{distance_km:<15.2f}{veh['travel_time']:<20.2f}{veh['average_speed']:<20.2f}")
    print(f"  Start: {veh['start_coord']}, End: {veh['end_coord']}")
