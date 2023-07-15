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
                            [
                                html.Label('Select Algorithm'),
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
                                        'marginLeft': '10px',
                                        'position': 'relative',  # Add relative positioning
                                    }
                                ),
                                html.Div(
                                    className='dropdown-arrow',  # Add class for styling
                                    style={
                                        'position': 'absolute',
                                        'right': '10px',
                                        'top': '50%',
                                        'transform': 'translateY(-50%)',
                                        'width': '0',
                                        'height': '0',
                                        'borderLeft': '6px solid transparent',
                                        'borderRight': '6px solid transparent',
                                        'borderTop': '6px solid #999',
                                        'cursor': 'pointer',  # Add cursor style for clickability
                                    },
                                    children=[
                                        html.A(
                                            '',  # Empty content, can be replaced with an icon or text
                                            href='#',  # Set the href attribute to a valid link or '#' for no action
                                            style={'display': 'block', 'height': '100%', 'width': '100%'},  # Adjust size to match parent div
                                        )
                                    ]
                                )
                            ],
                            style={'position': 'relative'}  # Set relative positioning for the container div
                        ),
                        html.Div(id='input-container', style={'margin': '20px'}),
                        html.Div(id='dropdown-value', style={'display': 'none'}),
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
                                'margin-top': '10px',
                                'margin-right': '10px',  # Add right margin for spacing
                                'margin-bottom': '10px',
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
                                'margin-top': '10px',
                                'border-radius': '10px',
                            }
                        ),
                        html.Div(id='output-container', style={'margin-top': '20px'}),
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
            Output('output-container', 'children'),
            [Input('submit-button', 'n_clicks')],
            [State('input-container', 'children')]
        )(self.submit_input_callback)

    def add_input_callback(self, n_clicks, children):
        if n_clicks is not None:
            inputs = [
                dcc.Input(
                    id='user-input',
                    type='text',
                    value='',
                    placeholder='Enter location here',
                    style={'height': '20px', 'padding': '5px', 'width': '200px', 'border-radius': '3px'}
                ),
            ]

            for i in range(n_clicks):
                inputs.append(html.Br())
                inputs.append(dcc.Input(
                    id={'type': 'dynamic-input', 'index': i},
                    type='text',
                    value='',
                    placeholder='Enter location here',
                    style={'height': '20px', 'padding': '5px', 'width': '200px', 'border-radius': '3px'}
                ))

            return inputs
        else:
            return []

    def submit_input_callback(self, n_clicks, input_box):
        if input_box is not None:
            map_creator = MapCreator('hotel.csv')
            return map_creator.submit_inputs(n_clicks, input_box)

    def run(self):
        self.app.run(debug=True)

if __name__ == '__main__':
    my_app = MyApp()
    my_app.run()
