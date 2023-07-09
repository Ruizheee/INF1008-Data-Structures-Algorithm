import pandas as pd
import folium
import webbrowser
import numpy as np
import osmnx as ox
import networkx as nx
from dash import Dash, html, dcc
from dash.dependencies import Output, State, Input
from folium import plugins

if __name__ == '__main__':
    dataframe = pd.read_csv(r'C:\Users\Admin\Downloads\hotel.csv')
    app = Dash(__name__)
    app.layout = html.Div([
        html.Div(id='input-container'),
        html.Button('Add location', id='add-location-button', n_clicks=0),
        html.Button('Submit', id = 'submit-button', n_clicks=0),
        html.Div(id='output-container')
    ])

    @app.callback(
        Output('input-container','children'),
        [Input('add-location-button', 'n_clicks')],
        [State('input-container','children')]
    )

    def add_input(n_clicks, children):
        if n_clicks is not None:
            inputs = [dcc.Input(id='user-input', type='text', value='', placeholder='Enter location here')]
            for i in range(n_clicks):
                inputs.append(html.Br())
                inputs.append(dcc.Input(id={'type': 'dynamic-input', 'index': i}, type='text', value = '', placeholder='Enter location2 here'))
            return inputs
    
    @app.callback(
    Output('output-container', 'children'),
    [Input('submit-button', 'n_clicks')],
    [State('input-container', 'children')]
)
    def submit_inputs(n_clicks, input_box):
        end_array = []
        end_node_array = []
        if input_box is None:
            return None
        else:
            #This is to grab the details of the starting point
            new = dataframe[(dataframe.Name.str.contains("Changi Airport Singapore", case=False))] 
            # Searching all the values in the different input boxes then concat together into 1 dataframe
            for input_values in input_box: 
                try:
                    search = dataframe[(dataframe.Name.str.contains(input_values['props']['value'], case=False))]
                    new = pd.concat([new, search])
                    end_array.extend(search['Name'].values)
                except:
                    pass
            new = new.reset_index().rename(columns={"index":"id", "Name":"Name", "Longitude":"x", "Latitude":"y"})
            i = 0; new["base"] = new["id"].apply(lambda x : 1 if x == i else 0)
            #Extract the x and y values of changi airport
            start = new[new["base"] == 1][["y","x"]].values[0] 

            #Make a copy of the dataframe to refrain from modifying the original Dataframe
            data = new.copy() 
            color = "base" 
            #Black will be representing the hotels and red will be representing changi airport (starting point)
            marker_colours = ["black", "red"] 
            #Values from the "Name" column will be displayed as pop-up information when you click on the different markers on the map
            popup = "Name" 

            m = folium.Map(location=start,tiles="openstreetmap",zoom_start = 11)
            #Network Graph
            g = ox.graph_from_point(start, dist=30000, network_type="drive")
            g = ox.add_edge_speeds(g)
            g = ox.add_edge_travel_times(g)

            start_node = ox.distance.nearest_nodes(g, start[1], start[0])
            for places in end_array:
                end = data[data["Name"] == places][["y","x"]].values[0]
                end_node = ox.distance.nearest_nodes(g, end[1], end[0])
                #print("The node for " + places + " is " + str(end_node))
                ###algo###
                path_lenght = nx.shortest_path(g, source=start_node, target=end_node, 
                                method='dijkstra', weight='lenght')     
                print(path_lenght)


                fig, ax = ox.plot_graph_route(g, path_lenght, route_color="red", 
                              route_linewidth=5, node_size=1, 
                              bgcolor='black', node_color="white", 
                              figsize=(16,8))

            list_elements = sorted(list(data[color].unique()))
            data["color"] = data[color].apply(lambda x: marker_colours[list_elements.index(x)])

            data.apply(lambda row:
                folium.CircleMarker(
                    location=[row["y"], row["x"]], popup = row[popup],
                    color=row["color"], fill=True, radius=5).add_to(m),
                axis=1)
            
            plugins.Fullscreen(position="topright", title="Expand",
                title_cancel="Exit", force_separate_button=True).add_to(m)
                      
            #m.save('mynewmap.html')
            fig.save('test.html')
            webbrowser.open('test.html')
        
    app.run(debug=True)
