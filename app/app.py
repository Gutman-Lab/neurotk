# Dash application.
import dash_bootstrap_components as dbc
from celery import Celery
from dash import Dash, html, CeleryManager
from os import getenv
from components import stores

# Configure cache manager for running background callbacks.
celery_app = Celery(
    __name__,
    broker=getenv("CELERY_BROKER_URL"),
    backend=getenv("CELERY_RESULT_BACKEND"),
)
background_callback_manager = CeleryManager(celery_app)

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    background_callback_manager=background_callback_manager,
)

app.layout = html.Div([stores])
# app.layout = html.Div([stores, header, tabs])

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
