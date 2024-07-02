# Dash application.
import dash_bootstrap_components as dbc
from celery import Celery
from dash import Dash, html, CeleryManager
from os import getenv
from components import stores, header

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)

app.layout = html.Div([stores, header])

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
