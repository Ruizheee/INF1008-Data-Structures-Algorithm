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
        #print(new[new["Name"] == hotels_array[0]][["y","x"]].values[0])
        #print(start)

        #Make a copy of the dataframe to refrain from modifying the original Dataframe
        data = new.copy() 
        return data, start, hotels_array, new
    
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
        G = ox.graph_from_point(start, dist = 25000, network_type = "drive")
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


        
    def draw_map(self, data, G, start, hotels_array, new):
        color = "base"
        # Black will represent the hotels in the graph, Red will represent Changi Airport (Starting Point)
        list_colors = ["black", "red"] 
        popup = "Name" 

        m = folium.Map(location=start,tiles="openstreetmap",zoom_start = 11)
        short = []
        distance = Distance(new, hotels_array)
        matrix = distance.calculateDistance()
        hotels_array_index = [i for i in range(len(hotels_array))]

        current_state = random_soln(matrix, 0, hotels_array_index, 100)
        current_state = simulated_annealing_optimize(matrix, 0, current_state)
        final_list_hotel = []
        final_list_hotel.append(hotels_array[0])
        for i in range(0, len(current_state.route)):
            final_list_hotel.append(hotels_array[current_state.route[i]])
        print(final_list_hotel)
        for i in range(len(final_list_hotel)):
            try:
                hotel_a = new[new["Name"] == final_list_hotel[i]][["y","x"]].values[0]
                location_a = ox.distance.nearest_nodes(G, hotel_a[1], hotel_a[0])
                hotel_b = new[new["Name"] == final_list_hotel[i + 1]][["y","x"]].values[0]
                location_b = ox.distance.nearest_nodes(G, hotel_b[1], hotel_b[0])
                short.append(bfs(G, location_a, location_b))
            except IndexError as e:
                break

        start_test = ox.distance.nearest_nodes(G, start[1], start[0])
        #new[new["Name"] == hotels_array[0]][["y","x"]].values[0]
        #print(start_test)
        #end = data[data["Name"] == "Four Seasons Hotel Singapore"][["y","x"]].values[0]
        #end_test = ox.distance.nearest_nodes(G, end[1], end[0])
        #traversal(G, start_test, end)
        #print("links: " + str(len(G.edges())) + "\n")
        gdfs = ox.graph_to_gdfs(G, nodes=False, edges=True)
        #print(gdfs.reset_index().head(3)) # we can use number of lanes, length, and travel times for optimization

        #fig, ax = ox.plot_route_folium
        #short = bfs(G, start_test, end_test)
        print(short)
        #set_test = set(short)
        #new_short = list(set_test)
        if len(hotels_array) == 2:
            fig, ax = ox.plot_graph_route(G, short[0], route_color="red", route_linewidth = 5, node_size = 1, bgcolor='black', node_color="white", figsize=(16,8))
        else:
            fig, ax = ox.plot_graph_routes(G, short, route_color="red", 
                  route_linewidth=5, node_size=1, 
                  bgcolor='black', node_color="white", 
                  figsize=(16,8))

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

    def submit_inputs(self, n_clicks, input_box):
        if input_box is None:
            return None
        else:
            data, start, hotels_array, new = self.setup_dataframe(input_box)
            G = self.generate_graph(start)
            self.draw_map(data, G, start, hotels_array, new)
        
#test