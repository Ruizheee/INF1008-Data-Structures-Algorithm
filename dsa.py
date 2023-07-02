from dash import Dash, html, dcc
from dash.dependencies import Output, State, Input
import pandas as pd
import folium
from folium import plugins
import webbrowser

if __name__ == '__main__':
    df = pd.read_csv(r'C:\Users\Admin\Downloads\hotel.csv')
    app = Dash(__name__)
    app.layout = html.Div([
        dcc.Input(id='endlocation', value = '', type = 'text', placeholder='Enter final location here'),
        html.Button(id='submit-button',type='submit',children='Submit'),
        html.Div(id='output_div')
    ])

    @app.callback(Output('output_div', 'children'),
                [Input('submit-button','n_clicks')],
                State('endlocation', 'value'),
                  )
    
    def draw_graph(clicks, input_value):
        if clicks is not None:
            newdf = df[(df.Name.str.contains("changi airport singapore", case=False) | (df.Name.str.contains(input_value, case=False)))]
            newdf = newdf.reset_index().rename(columns={"index":"id", "Name":"Name", "Longitude":"x", "Latitude":"y"})
            i = 0
            newdf["base"] = newdf["id"].apply(lambda x : 1 if x==i else 0)
            start = newdf[newdf["base"] == 1][["y","x"]].values[0]

            data = newdf.copy()
            color = "base"
            lst_colors = ["black", "red"]
            popup = "id"

            m = folium.Map(location=start,tiles="openstreetmap",zoom_start = 11)

            lst_elements = sorted(list(data[color].unique()))
            data["color"] = data[color].apply(lambda x: lst_colors[lst_elements.index(x)])

            data.apply(lambda row:
                folium.CircleMarker(
                    location=[row["y"], row["x"]], popup = row[popup],
                    color=row["color"], fill=True, radius=5).add_to(m),
                axis=1)
            
            plugins.Fullscreen(position="topright", title="Expand",
                title_cancel="Exit", force_separate_button=True).add_to(m)
                      
            m.save('mynewmap.html')
            webbrowser.open('mynewmap.html')
        
    app.run(debug=True)
    

    