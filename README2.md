# EV Simulation enhanced 

This README2 file will explain all the improvements made on the code. Moreover it will also serve to explain the details of certain functions and separating them based on different purposes (Modelling, Testing, Real Analysis)

## Separating the functions
### Modelling 
**core/charging_manager.py**

1. *\_init_*  
   Function to initialize a class that matches each station to a unique random id. Moreover, it specifies the charging rate and threshold.

   - Inputs:
       - map_manager (Object of MapManager class)
       - config (Dictionary): configuration parameters 

   - Outputs: None

3. *\_initialize_charging_stations_*  
   Specifies the number of charging stations and slots per station. Adds the details(station number, node id, x,y position, total slots, charging rate, price) to a dictionary using their station id as the key. 

   - Inputs: None
     
   - Outputs: None

### Real 
   
### Testing
**core/charging_manager.py**

1. *find_nearest_available_station*  
   Finds the nearest station based on the distance (calculated via Distance formaula) and whether it has an available slot.

   - Inputs:
       - position (Tuple): x,y position of EV on map

   - Outputs:
       - best_station (Object of ChargingStation class): Closest available station to EV or None

2. *find_optimal_charging_station*  
   Finds the best charging station based on distance (determined via Dijkstra), availability, and queue time.

   - Inputs:
       - vehicle (Object of vehicle class)
    
   - Outputs:
       - best_station (Object of ChargingStation class): Closest available station to EV 

3. *get_station_by_node*  
   Gets the charging station ID based on its node ID

   - Inputs:
       - node_id (int): Node ID of charging station
    
   - Outputs:
       - ChargingStation (Class): Object of ChargingStation class representing the node ID
    
4. *request_charging*  
   Gets the charging station ID based on its node ID

   - Inputs:
       - vehicle (Object of vehicle class)
       - station (Object of ChargingStation class)
    
   - Outputs:
       - True or False (bool): Whether vehicle is charging in that station
    
5. *stop_charging*  
   Checks if vehicle is charging, if so, it will calculate how much it has charged and the cost. It then updates the vehicle to be idle. If the station is not charging, it will just return the charge cost and amount to both be zero

   - Inputs:
       - vehicle (Object of Vehicle Class)

   - Outputs:
       - charge_amount, cost (Tuple)
    
6. *update_charging_progress*  
    Loops through each station then each of its vehicles to update how much each vehicle has charged during a given time step

   - Inputs:
       - dt (float): time step

   - Outputs:
       - charging_updates (Dictionary): Each vehicle's ID and its charge
    
7. *should_vehicle_charge*  
    Determines if vehicle should charge. It will charge if it doesn't have a passenger and battery below threshold

   - Inputs:
       - vehicle (Object of Vehicle Class)

   - Outputs:
       -True or False (bool): Whether vehicle should charge or not

7. *get_statistics*  
    Gets the statistics of the charging system (total stations, total slots, occupied slots, available slots, average utilization rate, total energy delivered, total revenue generated, total vehicles charged, average revenue per station)

   - Inputs: None
     
   - Outputs:
       - Statistics (Dictionary)

7. *get_station_list*  
    Gets a list of all charging stations

   - Inputs: None
     
   - Outputs:
       - List: list of ChargingStation objects

7. *get_busy_stations*  
    Gets a list of all busy charging stations (utilization rate is > 80%)

   - Inputs: None
     
   - Outputs:
     - List: list of all busy ChargingStation objects










   
