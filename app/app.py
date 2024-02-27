# Dash application.
from dash import Dash, html
import dash_bootstrap_components as dbc
from components import header
import config

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div(
    [
        header,
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True, port=8050, host="0.0.0.0")
