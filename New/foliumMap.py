import pandas as pd
import folium
import webbrowser
import osmnx as ox
import os
from folium import plugins
from optimize import *

class MapCreator:
    def __init__(self, csv_file):
        self.dataframe = pd.read_csv(csv_file)
    
    def setup_dataframe(self, input_box):
        pd.set_option('display.max_columns', None)
        dataframe = pd.read_csv('hotel.csv')
        #This is to grab the details of the starting point
        new = dataframe[(dataframe.Name.str.contains("changi airport singapore", case=False))] 
        # Searching all the values in the different input boxes then concat together into 1 dataframe
        for input_values in input_box: 
            try:
                search = dataframe[(dataframe.Name.str.contains(input_values['props']['value'], case=False))]
                new = pd.concat([new, search])
            except:
                pass
        new = new.reset_index().rename(columns={"index":"id", "Name":"Name", "Longitude":"x", "Latitude":"y"})
        i = 0; new["base"] = new["id"].apply(lambda x : 1 if x == i else 0)
        #Extract the x and y values of changi airport
        start = new[new["base"] == 1][["y","x"]].values[0] 

        #Make a copy of the dataframe to refrain from modifying the original Dataframe
        data = new.copy() 
        return data, start
    
    def generate_graph(self, start):
        graph_filename = "saved_graph.graphml"
        if (os.path.exists(graph_filename)):
            G = ox.load_graphml(graph_filename)
        else:
            G = ox.graph_from_point(start, dist = 25000, network_type = "drive")
            G = ox.add_edge_speeds(G)
            G = ox.add_edge_travel_times(G)
            ox.save_graphml(G, graph_filename)
        
        return G

    def draw_map(self, data, G, start):
        color = "base"
        # Black will represent the hotels in the graph, Red will represent Changi Airport (Starting Point)
        list_colors = ["black", "red"] 
        popup = "Name" 

        m = folium.Map(location=start,tiles="openstreetmap",zoom_start = 11)
        start_test = ox.distance.nearest_nodes(G, start[1], start[0])
        #traversal(G, start_test)
        #print("links: " + str(len(G.edges())) + "\n")
        gdfs = ox.graph_to_gdfs(G, nodes=False, edges=True)
        #print(gdfs.reset_index().head(3)) # we can use number of lanes, length, and travel times for optimization

        list_elements = sorted(list(data[color].unique()))
        data["color"] = data[color].apply(lambda x: list_colors[list_elements.index(x)])

        data.apply(lambda row:
            folium.CircleMarker(
                location=[row["y"], row["x"]], popup = row[popup],
                color=row["color"], fill=True, radius=5).add_to(m),
            axis=1)
        
        plugins.Fullscreen(position="topright", title="Expand",
            title_cancel="Exit", force_separate_button=True).add_to(m)
                    
        m.save('mynewmap.html')
        webbrowser.open('mynewmap.html')

    def submit_inputs(self, n_clicks, input_box):
        if input_box is None:
            return None
        else:
            data, start = self.setup_dataframe(input_box)
            G = self.generate_graph(start)
            self.draw_map(data, G, start)
        