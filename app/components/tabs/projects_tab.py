from dash import html, dcc
import dash_bootstrap_components as dbc

from components.project_table import project_table
from components.modals.create_project_modal import create_project_modal
from components.modals.delete_project_modal import delete_project_modal
from components.modals.add_dataset_modal import add_dataset_modal

import callbacks.create_project_btn_disabled
import callbacks.delete_project_btn_disabled
import callbacks.add_dataset_btn_disabled
import callbacks.update_project_dropdown
import callbacks.update_project_table


projects_tab = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Button(
                            html.I(className="fa-sharp fa-solid fa-images"),
                            id="add-dataset-btn",
                            color="success",
                            disabled=True,
                        ),
                        dbc.Tooltip(
                            "Add dataset to project.",
                            target="add-dataset-btn",
                        ),
                    ],
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
                    [
                        dbc.Button(
                            html.I(className="fa-regular fa-plus"),
                            id="create-project-btn",
                            className="custom-button",
                            disabled=True,
                        ),
                        dbc.Tooltip(
                            "Create new project.",
                            target="create-project-btn",
                        ),
                    ],
                    width="auto",
                ),
                dbc.Col(
                    [
                        dbc.Button(
                            html.I(className="fa-solid fa-trash"),
                            color="danger",
                            id="delete-project-btn",
                            disabled=True,
                        ),
                        dbc.Tooltip(
                            "Delete project.",
                            target="delete-project-btn",
                        ),
                    ],
                    width="auto",
                ),
            ],
            justify="start",
            align="center",
            style={"marginBottom": 5},
        ),
        html.Div(
            "Images in the project:",
            style={"fontWeight": "bold", "marginLeft": 5, "marginBottom": 5},
            id="project-table-info",
        ),
        dcc.Loading(project_table),
        create_project_modal,
        delete_project_modal,
        add_dataset_modal,
    ],
    style={"margin": 10},
)
