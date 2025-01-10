# Dash application.
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, CeleryManager
from celery_worker import celery_app
from dsa_helpers.dash.header import get_header
from os import getenv

from components.tabs.datasets_tab import datasets_tab
from components.tabs.projects_tab import projects_tab
from components.tabs.tasks_tab import tasks_tab

app = Dash(
    __name__,
    title="NeuroTK",
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.BOOTSTRAP,
        dbc.icons.FONT_AWESOME,
    ],
    background_callback_manager=CeleryManager(celery_app),
)

app.layout = html.Div(
    [
        get_header(
            getenv("DSA_API_URL"),
            title="NeuroTK",
            store_id=getenv("LOGIN_STORE_ID"),
        ),
        dcc.Tabs(
            value="tasks",
            parent_className="custom-tabs",
            className="custom-tabs-container",
            children=[
                dcc.Tab(
                    label="Datasets",
                    value="datasets",
                    children=datasets_tab,
                    className="custom-tab",
                    selected_className="custom-tab--selected",
                ),
                dcc.Tab(
                    label="Projects",
                    value="projects",
                    children=projects_tab,
                    className="custom-tab",
                    selected_className="custom-tab--selected",
                ),
                dcc.Tab(
                    label="Tasks",
                    value="tasks",
                    children=tasks_tab,
                    className="custom-tab",
                    selected_className="custom-tab--selected",
                ),
            ],
        ),
    ],
)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
