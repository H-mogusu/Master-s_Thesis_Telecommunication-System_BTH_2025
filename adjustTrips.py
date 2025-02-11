<<<<<<< HEAD
import xml.etree.ElementTree as ET

# Define proportions
proportions = {
    "passenger": 70,
    "bus": 10,
    "truck": 10,
    "motorcycle": 10,
}

# Scale the trips
def adjust_trips(file, proportion):
    tree = ET.parse(file)
    root = tree.getroot()
    trips = root.findall("trip")
    scaled_trips = trips[:int(len(trips) * (proportion / 100))]
    root[:] = scaled_trips
    tree.write(file.replace(".trips.xml", "_adjusted.trips.xml"))

for vehicle, proportion in proportions.items():
    adjust_trips(f"osm.{vehicle}.trips.xml", proportion)
=======
import xml.etree.ElementTree as ET

# Define proportions
proportions = {
    "passenger": 70,
    "bus": 10,
    "truck": 10,
    "motorcycle": 10,
}

# Scale the trips
def adjust_trips(file, proportion):
    tree = ET.parse(file)
    root = tree.getroot()
    trips = root.findall("trip")
    scaled_trips = trips[:int(len(trips) * (proportion / 100))]
    root[:] = scaled_trips
    tree.write(file.replace(".trips.xml", "_adjusted.trips.xml"))

for vehicle, proportion in proportions.items():
    adjust_trips(f"osm.{vehicle}.trips.xml", proportion)
>>>>>>> ce6e8c5d58803f5752e3c7e69c69579183fcd88f
