# Dash application.
import dash_bootstrap_components as dbc
from components import header, tabs, stores
from celery import Celery

from dash import Dash, html, CeleryManager

# Configure cache manager for running background callbacks.
celery_app = Celery(
    __name__,
    broker="amqp://guest:guest@rabbitmq:5672//",
    backend="redis://redis:6379/0",
)
background_callback_manager = CeleryManager(celery_app)

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    background_callback_manager=background_callback_manager,
)
app.layout = html.Div([stores, header, tabs])

if __name__ == "__main__":
    app.run(debug=True, port=8050, host="0.0.0.0")
