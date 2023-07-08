import pandas as pd
import folium
import webbrowser
import osmnx as ox
from dash import Dash, html, dcc
from dash.dependencies import Output, State, Input
from folium import plugins

class StackNode:
    def __init__(self, value=None):
        self.value = value
        self.next = None

class Stack:
    def __init__(self):
        self.head = None
        self.size = 0

    def push(self, value):
        if self.head == None:
            self.head = StackNode(value)
        else:
            new_node = StackNode(value)
            new_node.next = self.head
            self.head = new_node
        self.size += 1

    def pop(self):
        if self.head == None:
            return None
        else:
            popped = self.head
            self.head = self.head.next
            popped.next = None
            return popped.value
        self.size -= 1

    def display(self):
        node = self.head

        while (node != None):
            print(node.value, end="")
            node = node.next
            if (node != None):
                print("->", end="")
        return

def traversal(graph, start_node):
    stack = Stack()
    stack.push(start_node)
    visited = set([start_node])
    route_list = []

    while stack.size > 0:
        start_node = stack.pop()

        try:
            neighbors = list(graph[start_node].keys())
        except:
            break

        for neighbor in neighbors:
            if neighbor not in visited:
                stack.push(neighbor)
                visited.add(neighbor)

        iter_neighbour = iter(neighbors)
        for i in iter_neighbour:
            try:
                next_node = next(iter_neighbour)
            except StopIteration:
                break

            if graph[start_node][i][0]['length'] <= graph[start_node][next_node][0]['length']:
                route_list.append(graph[start_node][i])

    return route_list

if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    dataframe = pd.read_csv('hotel.csv')
    app = Dash(__name__)
    app.layout = html.Div([
        html.Div(id='input-container'),
        html.Button('Add location', id='add-location-button', n_clicks=0),
        html.Button('Submit', id='submit-button', n_clicks=0),
        html.Div(id='output-container')
    ])

    @app.callback(
        Output('input-container', 'children'),
        [Input('add-location-button', 'n_clicks')],
        [State('input-container', 'children')]
    )
    def add_input(n_clicks, children):
        if n_clicks is not None:
            inputs = [dcc.Input(id='user-input', type='text', value='', placeholder='Enter location here')]
            for i in range(n_clicks):
                inputs.append(html.Br())
                inputs.append(dcc.Input(id={'type': 'dynamic-input', 'index': i}, type='text', value='', placeholder='Enter location2 here'))
            return inputs

    @app.callback(
        Output('output-container', 'children'),
        [Input('submit-button', 'n_clicks')],
        [State('input-container', 'children')]
    )
    def submit_inputs(n_clicks, input_box):
        if input_box is None:
            return None
        else:
            # This is to grab the details of the starting point
            new = dataframe[(dataframe.Name.str.contains("changi airport singapore", case=False))]
            # Searching all the values in the different input boxes then concat together into 1 dataframe
            for input_values in input_box:
                try:
                    search = dataframe[(dataframe.Name.str.contains(input_values['props']['value'], case=False))]
                    new = pd.concat([new, search])
                except:
                    pass
            new = new.reset_index().rename(columns={"index": "id", "Name": "Name", "Longitude": "x", "Latitude": "y"})
            i = 0
            new["base"] = new["id"].apply(lambda x: 1 if x == i else 0)
            # Extract the x and y values of changi airport
            start = new[new["base"] == 1][["y", "x"]].values[0]

            # Make a copy of the dataframe to refrain from modifying the original DataFrame
            data = new.copy()
            color = "base"
            # Black will be representing the hotels and red will be representing changi airport (starting point)
            list_colors = ["black", "red"]
            # Values from the "Name" column will be displayed as pop-up information when you click on the different markers on the map
            popup = "Name"

            m = folium.Map(location=start, tiles="openstreetmap", zoom_start=11)
            G = ox.graph_from_point(start, dist=10000, network_type="drive")
            G = ox.add_edge_speeds(G)
            G = ox.add_edge_travel_times(G)

            start_test = ox.distance.nearest_nodes(G, start[1], start[0])
            traversal(G, start_test)

            gdfs = ox.graph_to_gdfs(G, nodes=False, edges=True)

            list_elements = sorted(list(data[color].unique()))
            data["color"] = data[color].apply(lambda x: list_colors[list_elements.index(x)])

            data.apply(lambda row:
                       folium.CircleMarker(
                           location=[row["y"], row["x"]], popup=row[popup],
                           color=row["color"], fill=True, radius=5).add_to(m),
                       axis=1)

            plugins.Fullscreen(position="topright", title="Expand",
                              title_cancel="Exit", force_separate_button=True).add_to(m)

            m.save('mynewmap.html')
            webbrowser.open('mynewmap.html')

    app.run(debug=True)
