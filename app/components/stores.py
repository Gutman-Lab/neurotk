from dash import dcc, html, callback, Output, Input, State, no_update
from utils.stores import get_projects

stores = html.Div(
    [
        dcc.Store(id="projects-dropdown-store", data=[]),
        dcc.Store(id="projects-store", data={}),
        dcc.Store(id="task-store", data={}),
        dcc.Store(id="dummy-store", data={}),
    ]
)
