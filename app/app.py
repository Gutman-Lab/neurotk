# Dash application.
from dash import Dash, html
import dash_bootstrap_components as dbc

# import config
from components import header, tabs, stores

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([stores, header, tabs])

if __name__ == "__main__":
    app.run_server(debug=True, port=8050, host="0.0.0.0")
