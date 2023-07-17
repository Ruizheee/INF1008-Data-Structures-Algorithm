import pandas as pd
import folium
import webbrowser
import osmnx as ox
import os
import multiprocessing as mp
from folium import plugins
from optimize import *

class MapCreator:
    def __init__(self, csv_file):
        self.dataframe = pd.read_csv(csv_file)
        self.dist = 25000
    
    def setup_dataframe(self, input_box):
        '''
        Pandas will be used to open and read the values of the CSV file consisting of hotels information
        After that, a brand new dataframe will be created,
        The row consisting of Changi Airport Singapore in the original dataframe will be added to the new dataframe
        For each rows consisting of the hotels that the user is interested in, it will also be added into the new dataframe
        Reduces the number of rows consisting of hotels that we are not interested in too

        Additionally, it extracts the hotel names from the input_box and inserts all of them into an array
        Returns the array of hotel names, 
        Longitude and Latitude values of the Changi Airport (Start), using it as the base point for folium to generate the map around
        and the new dataframe created
        '''
        pd.set_option('display.max_columns', None)
        dataframe = pd.read_csv('hotel.csv')
        new = dataframe[(dataframe.Name.str.contains("Changi Airport Singapore", case=False))]
        hotels_array = []
        for input_values in input_box: 
            try:
                search = dataframe[(dataframe.Name.str.contains(input_values['props']['value'], case=False))]
                new = pd.concat([new, search])
            except:
                pass
        hotels_array.extend(new['Name'].values)
        
        new = new.reset_index().rename(columns={"index":"id", "Name":"Name", "Longitude":"x", "Latitude":"y"})
        i = 0; new["base"] = new["id"].apply(lambda x : 1 if x == i else 0)
        start = new[new["base"] == 1][["y","x"]].values[0] 

        return start, hotels_array, new
            
    def generate_graph(self, start):
        '''
        Checks if there is an existing saved graph file, if not generate one
        Makes use of multiprocessing if possible to generate the graph if there is no existing graphs saved
        '''
        graph_filename = "saved_graph.graphml"
        if (os.path.exists(graph_filename)):
            G = ox.load_graphml(graph_filename)
        else:
            max_processes = 4
            cpu_count = mp.cpu_count()
            processes = min(max_processes, cpu_count)
            print("Using " + str(processes) + " number of CPUs ")

            if (processes == 1):
                G = self.generate_graph_single_processor(start, graph_filename)            
            else:
                G = self.generate_graph_multi_processors(start, graph_filename, processes)
        return G

    def generate_graph_single_processor(self, start, graph_filename):
        G = ox.graph_from_point(start, dist = self.dist, network_type = "drive")
        G = ox.add_edge_speeds(G)
        G = ox.add_edge_travel_times(G)
        
        with mp.Lock() as lock:
            ox.save_graphml(G, graph_filename)

        return G

    def generate_graph_multi_processors(self, start, graph_filename, processes):
        with mp.Pool(processes=processes) as pool:
            args = [(start, graph_filename)] * processes
            results = pool.starmap(self.generate_graph_single_processor, args)
        G = results[0]
        return G

    def execute_bfs(self, data, G, hotels_array):
        '''
        Extract the longitude and latitude of the hotels
        Using Breadth First Search, finds the shortest route
        '''
        breadth_routelist = []
        total_calculated_distance = 0
        for i in range(len(hotels_array)):
            try:
                source_coordinates = data[data["Name"] == hotels_array[i]][["y","x"]].values[0]
                nearest_node_to_source = ox.distance.nearest_nodes(G, source_coordinates[1], source_coordinates[0])
                
                destination_coordinates = data[data["Name"] == hotels_array[i + 1]][["y","x"]].values[0]
                nearest_node_to_destination = ox.distance.nearest_nodes(G, destination_coordinates[1], destination_coordinates[0])
                
                #breadth_routelist.append(bfs(G, nearest_node_to_source, nearest_node_to_destination))
                breadth_routelist_temp, total_calculated_distance_temp = bfs(G, nearest_node_to_source, nearest_node_to_destination)
                breadth_routelist.append(breadth_routelist_temp)
                total_calculated_distance += total_calculated_distance_temp
                
            except IndexError:
                break
        print("Total Distance: ", str(total_calculated_distance))
        return breadth_routelist

    def execute_dijkstra(self, data, G, hotels_array, weight: int = 0):
        '''
        Extract the longitude and latitude of the hotels
        Using Breadth First Search, finds the shortest route

        For weight, there are three types of weight available:
        - Length of Road
        - Speed of Road
        - Travel Time
        '''
        #print(G[1363263572][26778809])
        dijkstra_routelist = []
        total_calculated_distance = 0
        for i in range(len(hotels_array)):
            try:
                source_coordinates = data[data["Name"] == hotels_array[i]][["y","x"]].values[0]
                nearest_node_to_source = ox.distance.nearest_nodes(G, source_coordinates[1], source_coordinates[0])

                destination_coordinates = data[data["Name"] == hotels_array[i + 1]][["y", "x"]].values[0]
                nearest_node_to_destination = ox.distance.nearest_nodes(G, destination_coordinates[1], destination_coordinates[0])
                #dijkstra_routelist.append(dijkstra(G, nearest_node_to_source, nearest_node_to_destination, weight))
                dijkstra_routelist_temp, total_calculated_distance_temp = dijkstra(G, nearest_node_to_source, nearest_node_to_destination, weight)
                dijkstra_routelist.append(dijkstra_routelist_temp)
                total_calculated_distance +=  total_calculated_distance_temp
                
            except IndexError:
                break
        print("Total Distance: ", str(total_calculated_distance))
        return dijkstra_routelist
    
    def plot_routes(self, G, breadth_routelist, hotels_array, m):
        '''
        Plots the route on folium, with each route between the nodes having a different colour to differentiate easily
        '''
        route_colors = ['red', 'blue', 'yellow', 'green', 'purple', 'orange', 'pink', 'cyan', 'magenta', 'brown']
        for i in range(len(hotels_array[1:])):
            ox.plot_route_folium(G, route=breadth_routelist[i], route_map = m, color=route_colors[i], weight=1)
        
    def setup_map(self, m, data):
        '''
        Setup the folium map with markers, plugins and tiles
        '''
        color = "base"
        list_colors = ["black", "red"]
        popup = "Name"

        layers = ["cartodbpositron", "openstreetmap", "Stamen Terrain", "Stamen Water Color", "Stamen Toner", "cartodbdark_matter"]
        for tile in layers:
            folium.TileLayer(tile).add_to(m)
        folium.LayerControl(position='bottomright').add_to(m)

        list_elements = sorted(list(data[color].unique()))
        data["color"] = data[color].apply(lambda x: list_colors[list_elements.index(x)])

        data.apply(lambda row:
            folium.CircleMarker(
                location=[row["y"], row["x"]], popup = row[popup],
                color=row["color"], fill=True, radius=5).add_to(m),
            axis=1)
        
        plugins.Fullscreen(position="topright", title="Expand",
            title_cancel="Exit", force_separate_button=True).add_to(m)
        
        m.save('mynewmap2.html')
        webbrowser.open('mynewmap2.html')
    
    def pathfinding(self, G, m, data, hotels_array, dropdown_value, weight_values):
        '''
        Performs Simulated Annealing to determine the orders of the hotels
        Appends the new or final order of hotels into an array
        
        Depending on the methods selected, uses BFS or Dijkstra to find the routelist
        '''
        final_list_hotel = []

        distance = Distance(data, hotels_array)
        matrix = distance.calculateDistance()
        hotels_array_index = [i for i in range(len(hotels_array))]

        current_state = random_soln(matrix, 0, hotels_array_index, len(hotels_array_index))
        #current_state = solution_by_distance(matrix, 0)
        current_state = simulated_annealing_optimize(matrix, 0, current_state)
        final_list_hotel.append(hotels_array[0])

        for i in range(0, len(current_state.route)):
            final_list_hotel.append(hotels_array[current_state.route[i]])
        
        if dropdown_value == 'dijkstra':
            dijkstra_routelist = self.execute_dijkstra(data, G, final_list_hotel, weight_values)
            self.plot_routes(G, dijkstra_routelist, final_list_hotel, m)
        
        elif dropdown_value == 'bfs':
            breadth_routelist = self.execute_bfs(data, G, final_list_hotel)
            self.plot_routes(G, breadth_routelist, final_list_hotel, m) 

    def draw_map(self, G, start, hotels_array, new, dropdown_value, weight_values):
        '''
        Starts up Folium to generate a visualisation of the Singapore Map
        Calls the Pathfinding function to plot the routes on the map
        Calls setup_map function to mark the hotels and Changi Airport (Start) with markers
        '''
        data = new.copy()

        m = folium.Map(location=start,tiles="cartodbpositron",zoom_start = 11)
        self.pathfinding(G, m, data, hotels_array, dropdown_value, weight_values)
        self.setup_map(m, data)
    
    def submit_inputs(self, n_clicks, input_box, dropdown_value, weight_values):
        '''
        This function is called when the user first clicks on the submit button, 
        Which calls upon all the other functions to generate the map
        '''
        if input_box is None:
            return None
        else:
            start, hotels_array, new = self.setup_dataframe(input_box)
            G = self.generate_graph(start)
            self.draw_map(G, start, hotels_array, new, dropdown_value, weight_values)
        