from dash import Dash, html, dcc
from dash.dependencies import Output, State, Input, ALL
from foliumMap import MapCreator

class MyApp:
    def __init__(self):
        self.app = Dash(__name__)
        self.app.layout = html.Div([
            html.Div(id='input-container'),
            html.Div(id='dropdown-value', style={'display': 'none'}),
            html.Button('Add location', id='add-location-button', n_clicks=0),
            html.Button('Submit', id = 'submit-button', n_clicks=0),
            html.Div(id='output-container'),
        ])
        
        self.app.callback(
            Output('input-container','children'),
            [Input('add-location-button', 'n_clicks')],
            [State('input-container','children')]
        )(self.add_input_callback)

        self.app.callback(
            Output('output-container', 'children'),
            [Input('submit-button', 'n_clicks')],
            [State('input-container', 'children')]
        )(self.submit_input_callback)

    def add_input_callback(self, n_clicks, children):
        if n_clicks is not None:
            inputs = [
                dcc.Input(id='user-input', type='text', value='', placeholder='Enter location here', style={'height':'20px'}),
                dcc.Dropdown(
                    id='user-dropdown',
                    options=[
                        {'label': 'Dijkstra', 'value': 'dijkstra'},
                        {'label': 'Breadth First Search', 'value': 'bfs'},
                    ],
                    value = 'dijkstra',
                    placeholder='Select Algorithm',
                    style={'height': '25px','width': '150px', 'display': 'inline-block', 'verticalAlign': 'top', 'marginLeft': '10px'}
                )
            ]
            
            for i in range(n_clicks):
                inputs.append(html.Br())
                inputs.append(dcc.Input(id={'type': 'dynamic-input', 'index': i}, type='text', value = '', placeholder='Enter location here', style={'height':'20px'}))
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
