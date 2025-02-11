import xml.etree.ElementTree as ET

# List of trip files to combine
trip_files = [
    "osm.bus.trips.xml",
    "osm.passenger.trips.xml",
    "osm.truck.trips.xml",
    "osm.motorcycle.trips.xml"
]

# Output combined file
output_file = "combined_trips.trips.xml"

# Create root element
root = ET.Element("routes")

# Iterate through each trip file and merge its content
for file in trip_files:
    tree = ET.parse(file)
    for trip in tree.getroot():
        root.append(trip)

# Write combined trips to the output file
tree = ET.ElementTree(root)
tree.write(output_file, encoding="UTF-8", xml_declaration=True)

print(f"Combined trips written to {output_file}")
