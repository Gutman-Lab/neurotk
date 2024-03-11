# Dash application.
from dash import Dash, html, DiskcacheManager
import dash_bootstrap_components as dbc
import diskcache
from components import header, tabs, stores

# Configure cache manager for running background callbacks.
background_callback_manager = DiskcacheManager(diskcache.Cache("./cache"))


app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    background_callback_manager=background_callback_manager,
)
app.layout = html.Div([stores, header, tabs])

if __name__ == "__main__":
    app.run_server(debug=True, port=8050, host="0.0.0.0")
