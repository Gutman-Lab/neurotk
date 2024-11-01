from dash import html, dcc
import dash_bootstrap_components as dbc

from components.modals import (
    create_project_modal,
    delete_project_modal,
    add_dataset_modal,
)
from components.projects_tab_table import projects_tab_table

projects_tab = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        "Add Dataset",
                        id="add-dataset-btn",
                        color="success",
                        disabled=True,
                    ),
                    width="auto",
                ),
                dbc.Col(
                    html.Div("Project:", style={"fontWeight": "bold"}),
                    width="auto",
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="project-dropdown",
                        placeholder="Select project",
                        clearable=False,
                    ),
                    width=4,
                ),
                dbc.Col(
                    dbc.Button(
                        "Create Project",
                        id="create-project-btn",
                        className="custom-button",
                        disabled=True,
                    ),
                    width="auto",
                ),
                dbc.Col(
                    dbc.Button(
                        "Delete Project",
                        color="danger",
                        id="delete-project-btn",
                        disabled=True,
                    ),
                    width="auto",
                ),
            ],
            justify="start",
            align="center",
            style={"marginTop": 5, "marginLeft": 5, "marginBottom": 5},
        ),
        html.Div(
            "Images in the project:",
            style={"fontWeight": "bold", "marginLeft": 5, "marginBottom": 5},
            id="project-table-info",
        ),
        projects_tab_table,
        create_project_modal,
        delete_project_modal,
        add_dataset_modal,
    ],
    style={"margin": 10},
)
