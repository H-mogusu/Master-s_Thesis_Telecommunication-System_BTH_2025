<<<<<<< HEAD
import xml.etree.ElementTree as ET
from collections import defaultdict

# Constants
VEHICLES_PER_HOUR_PER_LANE = 180  # Base capacity of a single lane in vehicles/hour
CONGESTION_FACTOR = 0.6  # General adjustment for real-world conditions

# Traffic weights by road type
TRAFFIC_WEIGHTS = {
    "motorway": 1.2,     # Motorways handle more traffic
    "primary": 1.0,      # Main roads with standard capacity
    "secondary": 0.8,    # Smaller roads with reduced traffic
    "residential": 0.5,  # Local streets with minimal traffic
    "default": 0.3       # Unknown or other road types
}

def get_traffic_weight(road_type):
    """Returns traffic weight based on road type."""
    return TRAFFIC_WEIGHTS.get(road_type, TRAFFIC_WEIGHTS["default"])

def analyze_network(file_path):
    """
    Analyze a SUMO .net.xml file to estimate traffic capacity and count edges by road type.
    
    Args:
        file_path (str): Path to the .net.xml file.
    
    Returns:
        dict: Summary of total capacity, edge counts, and edge capacities.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    total_capacity = 0
    active_edges = 0
    edge_capacities = {}
    edge_counts = defaultdict(int)
    bbox = {"min_x": None, "min_y": None, "max_x": None, "max_y": None}

    for edge in root.findall("edge"):
        # Skip internal or non-vehicle edges
        if "function" in edge.attrib and edge.attrib["function"] in ["internal", "pedestrian"]:
            continue

        edge_id = edge.attrib["id"]
        road_type = edge.attrib.get("type", "unknown")  # Default to 'unknown' if no type is specified
        traffic_weight = get_traffic_weight(road_type)

        edge_capacity = 0
        is_active = False

        # Process each lane
        for lane in edge.findall("lane"):
            lane_length = float(lane.attrib["length"])
            lane_speed = float(lane.attrib["speed"])
            lane_shape = lane.attrib.get("shape", None)  # Get lane shape if available
            num_lanes = 1  # Each <lane> represents a single lane

            # Update bounding box from lane shapes
            if lane_shape:
                points = [tuple(map(float, coord.split(","))) for coord in lane_shape.split()]
                for x, y in points:
                    bbox["min_x"] = x if bbox["min_x"] is None or x < bbox["min_x"] else bbox["min_x"]
                    bbox["max_x"] = x if bbox["max_x"] is None or x > bbox["max_x"] else bbox["max_x"]
                    bbox["min_y"] = y if bbox["min_y"] is None or y < bbox["min_y"] else bbox["min_y"]
                    bbox["max_y"] = y if bbox["max_y"] is None or y > bbox["max_y"] else bbox["max_y"]

            # Calculate lane capacity
            lane_capacity = VEHICLES_PER_HOUR_PER_LANE * traffic_weight * CONGESTION_FACTOR
            edge_capacity += lane_capacity
            is_active = True

        if is_active:
            active_edges += 1
            edge_capacities[edge_id] = {"capacity": edge_capacity, "type": road_type}
            total_capacity += edge_capacity

        # Count edges by road type
        edge_counts[road_type] += 1

    return {
        "total_capacity": total_capacity,
        "active_edges": active_edges,
        "edge_capacities": edge_capacities,
        "edge_counts": dict(edge_counts),
        "bounding_box": bbox
    }

# Main Execution
if __name__ == "__main__":
    # Path to your .net.xml file
    net_file = "osm.net.xml"  # Update with your file path

    # Analyze the network
    result = analyze_network(net_file)

    # Summary Output
    print(f"Total Network Capacity (Peak Hour): {result['total_capacity']:.0f} vehicles/hour")
    print(f"Number of Active Edges: {result['active_edges']}")
    print(f"Average Capacity per Active Edge: {result['total_capacity'] / result['active_edges']:.2f} vehicles/hour\n")

    # Display Edge Counts by Road Type
    print("Edge Counts by Road Type:")
    for road_type, count in result["edge_counts"].items():
        print(f"  {road_type}: {count} edges")

    # Sort edges by capacity
    sorted_edges = sorted(result["edge_capacities"].items(), key=lambda x: x[1]["capacity"], reverse=True)

    # Display Top 5 Edges by Capacity
    print("\nTop 5 Edges by Capacity:")
    for edge_id, data in sorted_edges[:5]:
        print(f"  Edge {edge_id}: {data['capacity']:.0f} vehicles/hour (Type: {data['type']})")

    # Display Bottom 5 Edges by Capacity
    print("\nBottom 5 Edges by Capacity:")
    for edge_id, data in sorted_edges[-5:]:
        print(f"  Edge {edge_id}: {data['capacity']:.0f} vehicles/hour (Type: {data['type']})")

    # Display Geographic Bounding Box
    bbox = result["bounding_box"]
    print("\nGeographic Bounding Box:")
    print(f"  Min Longitude (x): {bbox['min_x']}")
    print(f"  Max Longitude (x): {bbox['max_x']}")
    print(f"  Min Latitude (y): {bbox['min_y']}")
    print(f"  Max Latitude (y): {bbox['max_y']}")

    # Optional: Save results to a file
    with open("edge_analysis.csv", "w") as file:
        file.write("Edge ID,Capacity (vehicles/hour),Type\n")
        for edge_id, data in result["edge_capacities"].items():
            file.write(f"{edge_id},{data['capacity']:.0f},{data['type']}\n")
=======
import xml.etree.ElementTree as ET
from collections import defaultdict

# Constants
VEHICLES_PER_HOUR_PER_LANE = 180  # Base capacity of a single lane in vehicles/hour
CONGESTION_FACTOR = 0.6  # General adjustment for real-world conditions

# Traffic weights by road type
TRAFFIC_WEIGHTS = {
    "motorway": 1.2,     # Motorways handle more traffic
    "primary": 1.0,      # Main roads with standard capacity
    "secondary": 0.8,    # Smaller roads with reduced traffic
    "residential": 0.5,  # Local streets with minimal traffic
    "default": 0.3       # Unknown or other road types
}

def get_traffic_weight(road_type):
    """Returns traffic weight based on road type."""
    return TRAFFIC_WEIGHTS.get(road_type, TRAFFIC_WEIGHTS["default"])

def analyze_network(file_path):
    """
    Analyze a SUMO .net.xml file to estimate traffic capacity and count edges by road type.
    
    Args:
        file_path (str): Path to the .net.xml file.
    
    Returns:
        dict: Summary of total capacity, edge counts, and edge capacities.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    total_capacity = 0
    active_edges = 0
    edge_capacities = {}
    edge_counts = defaultdict(int)
    bbox = {"min_x": None, "min_y": None, "max_x": None, "max_y": None}

    for edge in root.findall("edge"):
        # Skip internal or non-vehicle edges
        if "function" in edge.attrib and edge.attrib["function"] in ["internal", "pedestrian"]:
            continue

        edge_id = edge.attrib["id"]
        road_type = edge.attrib.get("type", "unknown")  # Default to 'unknown' if no type is specified
        traffic_weight = get_traffic_weight(road_type)

        edge_capacity = 0
        is_active = False

        # Process each lane
        for lane in edge.findall("lane"):
            lane_length = float(lane.attrib["length"])
            lane_speed = float(lane.attrib["speed"])
            lane_shape = lane.attrib.get("shape", None)  # Get lane shape if available
            num_lanes = 1  # Each <lane> represents a single lane

            # Update bounding box from lane shapes
            if lane_shape:
                points = [tuple(map(float, coord.split(","))) for coord in lane_shape.split()]
                for x, y in points:
                    bbox["min_x"] = x if bbox["min_x"] is None or x < bbox["min_x"] else bbox["min_x"]
                    bbox["max_x"] = x if bbox["max_x"] is None or x > bbox["max_x"] else bbox["max_x"]
                    bbox["min_y"] = y if bbox["min_y"] is None or y < bbox["min_y"] else bbox["min_y"]
                    bbox["max_y"] = y if bbox["max_y"] is None or y > bbox["max_y"] else bbox["max_y"]

            # Calculate lane capacity
            lane_capacity = VEHICLES_PER_HOUR_PER_LANE * traffic_weight * CONGESTION_FACTOR
            edge_capacity += lane_capacity
            is_active = True

        if is_active:
            active_edges += 1
            edge_capacities[edge_id] = {"capacity": edge_capacity, "type": road_type}
            total_capacity += edge_capacity

        # Count edges by road type
        edge_counts[road_type] += 1

    return {
        "total_capacity": total_capacity,
        "active_edges": active_edges,
        "edge_capacities": edge_capacities,
        "edge_counts": dict(edge_counts),
        "bounding_box": bbox
    }

# Main Execution
if __name__ == "__main__":
    # Path to your .net.xml file
    net_file = "osm.net.xml"  # Update with your file path

    # Analyze the network
    result = analyze_network(net_file)

    # Summary Output
    print(f"Total Network Capacity (Peak Hour): {result['total_capacity']:.0f} vehicles/hour")
    print(f"Number of Active Edges: {result['active_edges']}")
    print(f"Average Capacity per Active Edge: {result['total_capacity'] / result['active_edges']:.2f} vehicles/hour\n")

    # Display Edge Counts by Road Type
    print("Edge Counts by Road Type:")
    for road_type, count in result["edge_counts"].items():
        print(f"  {road_type}: {count} edges")

    # Sort edges by capacity
    sorted_edges = sorted(result["edge_capacities"].items(), key=lambda x: x[1]["capacity"], reverse=True)

    # Display Top 5 Edges by Capacity
    print("\nTop 5 Edges by Capacity:")
    for edge_id, data in sorted_edges[:5]:
        print(f"  Edge {edge_id}: {data['capacity']:.0f} vehicles/hour (Type: {data['type']})")

    # Display Bottom 5 Edges by Capacity
    print("\nBottom 5 Edges by Capacity:")
    for edge_id, data in sorted_edges[-5:]:
        print(f"  Edge {edge_id}: {data['capacity']:.0f} vehicles/hour (Type: {data['type']})")

    # Display Geographic Bounding Box
    bbox = result["bounding_box"]
    print("\nGeographic Bounding Box:")
    print(f"  Min Longitude (x): {bbox['min_x']}")
    print(f"  Max Longitude (x): {bbox['max_x']}")
    print(f"  Min Latitude (y): {bbox['min_y']}")
    print(f"  Max Latitude (y): {bbox['max_y']}")

    # Optional: Save results to a file
    with open("edge_analysis.csv", "w") as file:
        file.write("Edge ID,Capacity (vehicles/hour),Type\n")
        for edge_id, data in result["edge_capacities"].items():
            file.write(f"{edge_id},{data['capacity']:.0f},{data['type']}\n")
>>>>>>> ce6e8c5d58803f5752e3c7e69c69579183fcd88f
