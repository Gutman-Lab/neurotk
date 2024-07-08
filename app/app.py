# Dash application.
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc
from components import stores, header, projects_tab, datasets_tab, tasks_tab

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)

app.layout = html.Div(
    [
        stores,
        header,
        dcc.Tabs(
            [
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
            value="tasks",
            parent_className="custom-tabs",
            className="custom-tabs-container",
        ),
    ],
)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
