from dash import Dash, html, dcc
from dash.dependencies import Output, State, Input, ALL
from foliumMap import MapCreator

class MyApp:
    def __init__(self):
        self.app = Dash(__name__)
        self.app.layout = html.Div(
            style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'height': '100vh'},
            children=[
                html.Div(
                    style={'background-color': '#f0f0f0', 'padding': '20px', 'border-radius': '10px'},
                    children=[
                        html.Div(
                            style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'},  # Set flex display, alignment, and bottom margin
                            children=[
                                html.Label('Select Algorithm', style={'marginRight': '10px'}),  # Add margin-right for spacing
                                dcc.Dropdown(
                                    id='user-dropdown',
                                    options=[
                                        {'label': 'Dijkstra', 'value': 'dijkstra'},
                                        {'label': 'Breadth First Search', 'value': 'bfs'},
                                    ],
                                    value='dijkstra',
                                    placeholder='Select Algorithm',
                                    style={
                                        'height': '25px',
                                        'width': '150px',
                                        'display': 'inline-block',
                                        'verticalAlign': 'top',
                                    }
                                ),
                            ]
                        ),
                        html.Div(id='input-container', style={'margin': '20px'}),
                        html.Div(id='dropdown-value', style={'display': 'none'}),
                        html.Div(
                            style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'marginBottom': '10px'},  # Set flex display, alignment, justify content, and bottom margin
                            children=[
                                html.Button(
                                    'Add location',
                                    id='add-location-button',
                                    n_clicks=0,
                                    style={
                                        'background-color': '#10559A',
                                        'color': 'white',
                                        'padding': '10px 20px',
                                        'border': 'none',
                                        'cursor': 'pointer',
                                        'margin-right': '10px',  # Add right margin for spacing
                                        'border-radius': '10px',
                                    }
                                ),
                                html.Button(
                                    'Submit',
                                    id='submit-button',
                                    n_clicks=0,
                                    style={
                                        'background-color': '#DB4C77',
                                        'color': 'white',
                                        'padding': '10px 20px',
                                        'border': 'none',
                                        'cursor': 'pointer',
                                        'border-radius': '10px',
                                    }
                                ),
                            ]
                        ),
                        html.Div(id='output-container', style={'margin-top': '20px'}),
                        html.Div(id='weight-dropdown-container'),
                        dcc.Store(id='weight-values-store')
                    ]
                )
            ]
        )

        self.app.callback(
            Output('input-container', 'children'),
            [Input('add-location-button', 'n_clicks')],
            [State('input-container', 'children')]
        )(self.add_input_callback)

        self.app.callback(
            Output('weight-dropdown-container', 'children'),
            [Input('user-dropdown', 'value')]
        )(self.add_weight_dropdown)

        self.app.callback(
            Output('weight-values-store', 'data'),
            [Input({'type': 'weight-dropdown', 'index': ALL}, 'value')],
            [State('user-dropdown', 'value')]
        )(self.update_weight_values)

        self.app.callback(
            Output('output-container', 'children'),
            [Input('submit-button', 'n_clicks')],
            [State('input-container', 'children'), State('user-dropdown', 'value'), State('weight-values-store', 'data')]
        )(self.submit_input_callback)

    def add_input_callback(self, n_clicks, children):
        inputs = children if children is not None else []
        inputs.append(dcc.Input(id={'type': 'dynamic-input', 'index': n_clicks}, type='text', value='',
                                placeholder='Enter location here', style={'height': '20px'}))
        return inputs

    def add_weight_dropdown(self, dropdown_value):
        if dropdown_value == 'dijkstra':
            weight_dropdown = html.Div(
                children=[
                    html.Label('Select Factor', style={'marginRight': '10px'}),  # Add label for "Factor" with right margin
                    dcc.Dropdown(
                        id={'type': 'weight-dropdown', 'index': 0},
                        options=[
                            {'label': 'Length of Road', 'value': 'option 1'},
                            {'label': 'Speed Limit of Road', 'value': 'option 2'},
                            {'label': 'Travel Time', 'value': 'option 3'},
                        ],
                        value='option 1',
                        style={'width': '200px'}  # Adjust the width of the dropdown box
                    ),
                ],
                style={'display': 'flex', 'alignItems': 'center', 'marginLeft': '10px'}  # Adjust display and alignment
            )
            return weight_dropdown
        else:
            return html.Div(id='weight-dropdown-container')



    def update_weight_values(self, weight_values, dropdown_value):
        if dropdown_value == 'dijkstra':
            return weight_values
        else:
            return []

    def submit_input_callback(self, n_clicks, input_box, dropdown_value, weight_values):
        if input_box is not None:
            weight_values = weight_values[0]
            map_creator = MapCreator('hotel.csv')
            return map_creator.submit_inputs(n_clicks, input_box, dropdown_value, weight_values)

    def run(self):
        self.app.run(debug=True)

if __name__ == '__main__':
    my_app = MyApp()
    my_app.run()
