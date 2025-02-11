import traci
import sumolib

# Define custom vehicles with start and end coordinates
custom_vehicles = [
    {"id": "car1", "start": "8416.427089912382,1416.1391034982096", "end": "7206.928088279537,1991.7293428579198"},
    {"id": "car2", "start": "6741.833105756359,3874.7253413654616", "end": "6103.028144513419,5356.659466991913"},
    {"id": "car3", "start": "7206.928088279537,1991.7293428579198", "end": "8416.427089912382,1416.1391034982096"},
]

# Function to find the nearest edge
def get_nearest_edge(net, coord):
    x, y = map(float, coord.split(","))
    edges = net.getNeighboringEdges(x, y)
    if not edges:
        raise ValueError(f"No nearby edge found for coordinate: {coord}")
    closest_edge = min(edges, key=lambda edge: edge[1])  # Find the closest edge by distance
    return closest_edge[0].getID()

# Function to inject custom vehicles dynamically
def inject_custom_vehicles(net, vehicles):
    for vehicle in vehicles:
        try:
            # Get the start and end edges
            start_edge = get_nearest_edge(net, vehicle["start"])
            end_edge = get_nearest_edge(net, vehicle["end"])
            
            # Add the vehicle to the simulation
            traci.vehicle.add(
                vehID=vehicle["id"],
                routeID="",  # Route will be dynamically assigned
                typeID="passenger",  # Default type for passenger vehicles
            )
            # Set the vehicle's target
            traci.vehicle.changeTarget(vehicle["id"], end_edge)
            print(f"Vehicle {vehicle['id']} added: {start_edge} -> {end_edge}")
        except ValueError as e:
            print(f"Error adding vehicle {vehicle['id']}: {e}")

# Main simulation
def main():
    sumo_config = "osm_adjusted.sumocfg"  # Replace with your SUMO config file
    net_file = "your_network.net.xml"  # Replace with your SUMO network file

    # Load the network
    net = sumolib.net.readNet(net_file)

    # Start SUMO simulation
    traci.start(["sumo-gui", "-c", sumo_config])  # Use "sumo" instead of "sumo-gui" for command-line execution

    step = 0
    max_steps = 1000  # Simulation length

    while step < max_steps:
        traci.simulationStep()

        # Inject custom vehicles at step 10
        if step == 10:
            inject_custom_vehicles(net, custom_vehicles)

        step += 1

    traci.close()
    print("Simulation finished.")

if __name__ == "__main__":
    main()
