## Master-s_Thesis_Telecommunication-System_BTH_2025

#This guide covers:
Installing SUMO and setting up the environment.
Obtaining Gothenburg’s map and converting it into a SUMO network.
Generating traffic demand with different vehicle types.
Implementing Dijkstra and A* for adaptive routing.
Running SUMO to simulate traffic and analyze results.

#Prerequisites
Software Requirements
-Python (version  3.12.8) – Required for scripting and controlling SUMO. You can use any as long as its compatible with sumo you are using
-SUMO (version 1.21.0 ) – Open-source traffic simulation software. Use any, check compatibility

#Additional Libraries: Install the required Python packages:
-pip install networkx matplotlib sumolib traci osmium

#Installation Guide
-Installing SUMO
-Download SUMO from the official site: https://sumo.dlr.de/docs/Downloads.html
#Follow installation steps based on your OS:
-Windows: Install using the provided .exe installer.
-Linux/Mac: Install via terminal:
-sudo apt-get install sumo sumo-tools sumo-doc

#Setting Up SUMO Environment Variables (important to avoid issues during executions)
For SUMO to work with Python:
>Windows:
-setx SUMO_HOME "C:\path\to\sumo"
>Linux/Mac:
-export SUMO_HOME="/path/to/sumo"

#Getting Gothenburg Map from OpenStreetMap
Downloading the OSM File
-Go to OpenStreetMap
-Select Gothenburg and export the .osm file.
-we created multiple sections of maps from gothenburgand joined them up to make a completed map


#Converting OSM to SUMO Network
-Use netconvert to generate a SUMO-compatible network:
 -netconvert --sumo-net-file map1.net.xml,map2.net.xml,map3.net.xml,map4.net.xml,map5.net.xml,map6.net.xml,map7.net.xml,map8.net.xml -o gothenburg.net.xml
 -gothenburg.net.xml = (changed to osm.net.xml)

#Inspect the Merged Network

Open the merged network in netedit:
command:
 -netedit combined_network.net.xml

#Creating Random Trips/routes (Traffic Demand)
Generating Random Trips for Vehicles
run the randomTrips.py code as below to create random routes to the osm generated network:
created trips for each typeof vehicle

 >python randomTrips.py -n osm.net.xml -o osm.bus_adjusted.trips.xml -r osm.bus.rou.xml --period 2 --seed 42
 >python randomTrips.py -n osm.net.xml -o osm.motorcycle_adjusted.trips.xml -r osm.motorcycle.rou.xml --period 2 --seed 42
 >python randomTrips.py -n osm.net.xml -o osm.passenger_adjusted.trips.xml -r osm.passenger.rou.xml --period 2 --seed 42
 >python randomTrips.py -n osm.net.xml -o osm.bus_adjusted.trips.xml -r routes.rou.xml --period 2 --seed 42
 >python randomTrips.py -n osm.net.xml -o osm.truck_adjusted.trips.xml -r osm.truck.rou.xml --period 2 --seed 42
 
-n osm.net.xml → Specifies the SUMO network file.
-o trips.trips.xml → Defines the output trips file.
-r routes.rou.xml → Specifies where the generated routes will be stored.
--period 2 → Defines the interval between consecutive vehicle departures.
--seed 42 → Ensures reproducibility of random trip generation

#To create a simulation with buses, lorries, cars, and motorcycles:

>python randomTrips.py -n gothenburg.net.xml -r trips.rou.xml -b 5 -l 10 -c 50 -m 20 --period 1
Where:
-b 5 → Buses (5% of vehicles)
-l 10 → Lorries (10% of vehicles)
-c 50 → Cars (50% of vehicles)
-m 20 → Motorcycles (20% of vehicles)
--period 1 → Frequency of trip generation

#streamline the traffic lights
 - use tlsCycleAdaptation.py code to streamline the traffic light system because we merged small section of gothenburg map
 to create the bigger map.
 -run the sumo using randomTrips.py to have vehicles moving freely without any intervention of our algorithms then
    >sumo-gui -c osm_adjusted.sumocfg (adjust time according to your machine capability - due to too many nodes and junctions)
	- this generate baseline_trajectory.xml for all Vehicles in the network (speed, time, distance covered, cordinates etc)
	- this create a baseline_summary.xml for all vehicles too
	
#choose 5 cars randomly for simulation.
- using choosing_5_vehicles_for_simulation.py , this will choose randomly 5 cars to be used in next simulation of algorithms.
-this pick car at random from the baseline_trajectory and store in REPORTS a file called passenger_car_report excel file
- use remove_stuck_veh.py code to remove stuck vehicle ( <<normal like stalled Vehicles in real life>>this could be due to collision, lost route, vehicle in loop. the code runs through checking each vehicle to determine 
if its stuck , delayed in one spot for sometime then remove it.)

#Implementing Dijkstra and A* Algorithms for Routing
- you can input the cars (5 vehicles picke for simulation above)_in your code as shown in 
vehicle_ids_to_reroute = ["veh162", "veh179", "veh2276", "veh639", "veh594"] in 5_cars_dynamic.py code or 5_cars_dynamic_v1.py
(its random cars, next exection picks other cars randomly)


>Dijkstra Algorithm (Shortest Path Search)
Uses the shortest travel time to determine optimal routes.

>A* Algorithm (Heuristic-Based Routing)
Enhances Dijkstra by considering both distance and traffic congestion.


#Running the SUMO Simulation
>To execute the simulation with real-time routing updates:
-sumo-gui -c osm_adjusted.sumocfg

>For command-line execution:
-sumo -c osm_adjusted.sumocfg

# Visualizing and Analyzing the Results
SUMO-GUI Visualization: Displays vehicle movement.

#Data Extraction for Analysis

-run TimeSaved_in_percentage.py to simulate the time saved in percentages

#notes
-Despite having the entire of Gothenburg,
we have used a section of the map to simulate since free tire of openstreet map won't allow us to have more than 50,000 nodes out.
-We have used a factor of 2 to speed up traffic in simulation so will be the time at the end
-Figure obtained after multiple iterations to achieve best rest. 
-A lot will have to be done in future studies such as accomodating human factors and behaviors, environmental factors, accidents, road closure,
since the test was done on best ideal situation.
-Also, in future works, ML and natural selection could also be employed to make the further adversement better. 
-feel free to adjust codes to suit current research and  for analysis such heat maps/vehicle selection etc
-adjust the .sumocfg file to capture bigger section according to your computational capacity.
-other codes in these are to enhance and have different view such as 
	merge_trips.py
	reports_v()_heamaps.py
	traci_graph_conversion.py
	rerouting_dynamic.py
		study them and use where applicable in future studies
-NO LICENCE TO IT- free for reuse
UNZIP FILES