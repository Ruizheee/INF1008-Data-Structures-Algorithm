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
        pd.set_option('display.max_columns', None)
        dataframe = pd.read_csv('hotel.csv')
        #This is to grab the details of the starting point
        new = dataframe[(dataframe.Name.str.contains("Changi Airport Singapore", case=False))]
        hotels_array = []
        # Searching all the values in the different input boxes then concat together into 1 dataframe
        for input_values in input_box: 
            try:
                search = dataframe[(dataframe.Name.str.contains(input_values['props']['value'], case=False))]
                new = pd.concat([new, search])
                #print(new.head(3))
            except:
                pass
        hotels_array.extend(new['Name'].values)
        #print(hotels_array)
        
        new = new.reset_index().rename(columns={"index":"id", "Name":"Name", "Longitude":"x", "Latitude":"y"})
        i = 0; new["base"] = new["id"].apply(lambda x : 1 if x == i else 0)
        #Extract the x and y values of changi airport
        start = new[new["base"] == 1][["y","x"]].values[0] 

        return start, hotels_array, new
            
    def generate_graph(self, start):
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
        breadth_routelist = []
        for i in range(len(hotels_array)):
            try:
                source_coordinates = data[data["Name"] == hotels_array[i]][["y","x"]].values[0]
                nearest_node_to_source = ox.distance.nearest_nodes(G, source_coordinates[1], source_coordinates[0])
                
                destination_coordinates = data[data["Name"] == hotels_array[i + 1]][["y","x"]].values[0]
                nearest_node_to_destination = ox.distance.nearest_nodes(G, destination_coordinates[1], destination_coordinates[0])
                
                breadth_routelist.append(bfs(G, nearest_node_to_source, nearest_node_to_destination))
            except IndexError:
                break
        return breadth_routelist

    def execute_dijkstra(self, data, G, hotels_array, weight: int = 0):
        #for weight, 0 = length of road, 1 = speed of road, 2 = travel time
        dijkstra_routelist = []
        for i in range(len(hotels_array)):
            try:
                source_coordinates = data[data["Name"] == hotels_array[i]][["y","x"]].values[0]
                nearest_node_to_source = ox.distance.nearest_nodes(G, source_coordinates[1], source_coordinates[0])

                destination_coordinates = data[data["Name"] == hotels_array[i + 1]][["y", "x"]].values[0]
                nearest_node_to_destination = ox.distance.nearest_nodes(G, destination_coordinates[1], destination_coordinates[0])
                dijkstra_routelist.append(dijkstra(G, nearest_node_to_source, nearest_node_to_destination, weight))
            except IndexError:
                break
        return dijkstra_routelist
    
    def plot_routes(self, G, breadth_routelist, hotels_array, m):
        route_colors = ['red', 'blue', 'yellow', 'green', 'purple', 'orange', 'pink', 'cyan', 'magenta', 'brown']
        for i in range(len(hotels_array[1:])):
            ox.plot_route_folium(G, route=breadth_routelist[i], route_map = m, color=route_colors[i], weight=1)
        
    def setup_map(self, m, data):
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

    def get_dropdown_value(self, input_box):
        dropdown_value = input_box[1]['props']['value']
        return dropdown_value
    
    def pathfinding(self, G, m, data, hotels_array, dropdown_value):
        final_list_hotel = []

        distance = Distance(data, hotels_array)
        matrix = distance.calculateDistance()
        hotels_array_index = [i for i in range(len(hotels_array))]

        current_state = random_soln(matrix, 0, hotels_array_index, len(hotels_array_index))
        current_state = simulated_annealing_optimize(matrix, 0, current_state)
        final_list_hotel.append(hotels_array[0])

        for i in range(0, len(current_state.route)):
            final_list_hotel.append(hotels_array[current_state.route[i]])
        
        if dropdown_value == 'dijkstra':
            dijkstra_routelist = self.execute_dijkstra(data, G, final_list_hotel, 2)
            self.plot_routes(G, dijkstra_routelist, final_list_hotel, m)
        
        elif dropdown_value == 'bfs':
            breadth_routelist = self.execute_bfs(data, G, final_list_hotel)
            self.plot_routes(G, breadth_routelist, final_list_hotel, m) 

    def draw_map(self, G, start, hotels_array, new, dropdown_value):
        data = new.copy()

        m = folium.Map(location=start,tiles="cartodbpositron",zoom_start = 11)
        self.pathfinding(G, m, data, hotels_array, dropdown_value)
        self.setup_map(m, data)
    
    def submit_inputs(self, n_clicks, input_box):
        dropdown_value = self.get_dropdown_value(input_box)
        start, hotels_array, new = self.setup_dataframe(input_box)
        G = self.generate_graph(start)
        self.draw_map(G, start, hotels_array, new, dropdown_value)
        