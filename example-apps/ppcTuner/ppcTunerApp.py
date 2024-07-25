# Dash application.
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc

import components.mainViewerWindow as mvw


# from components import stores, header, projects_tab, datasets_tab, tasks_tab
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)

app.layout = html.Div([mvw.mainViewer])

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

