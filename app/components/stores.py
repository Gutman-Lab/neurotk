from dash import dcc, html
from utils.stores import get_projects

stores = html.Div(
    [
        dcc.Store(id="projects-dropdown-store", data=get_projects()),
        dcc.Store(id="projects-store", data={}),
        dcc.Store(id="task-store", data={}),
    ]
)
