from dash import Dash, html, dcc
from dash.dependencies import Output, State, Input
from foliumMap import MapCreator

class MyApp:
    def __init__(self):
        self.app = Dash(__name__)
        self.app.layout = html.Div([
            html.Div(id='input-container'),
            html.Button('Add location', id='add-location-button', n_clicks=0),
            html.Button('Submit', id = 'submit-button', n_clicks=0),
            html.Div(id='output-container')
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
            inputs = [dcc.Input(id='user-input', type='text', value='', placeholder='Enter location here')]
            for i in range(n_clicks):
                inputs.append(html.Br())
                inputs.append(dcc.Input(id={'type': 'dynamic-input', 'index': i}, type='text', value = '', placeholder='Enter location2 here'))
            return inputs
        
    def submit_input_callback(self, n_clicks, input_box):
        map_creator = MapCreator('hotel.csv')
        return map_creator.submit_inputs(n_clicks, input_box)
    
    def run(self):
        self.app.run(debug=True)

if __name__ == '__main__':
    my_app = MyApp()
    my_app.run()

