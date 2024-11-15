from dash import html, dcc
import dash_bootstrap_components as dbc

import callbacks.update_task_tab_project_name
import callbacks.create_task_btn_disabled
import callbacks.delete_task_btn_disabled
import callbacks.update_task_dropdown

from components.modals.create_task_modal import create_task_modal
from components.modals.delete_task_modal import delete_task_modal
from components.tabs.images_tab import images_tab
from components.tabs.annotations_tab import annotations_tab
from components.tabs.cli_tab import cli_tab

tasks_tab = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(html.Div("Project:"), width="auto"),
                dbc.Col(html.Div(id="task_tab_project_name"), width=4),
            ],
            justify="start",
            align="center",
            style={"marginBottom": 10, "fontWeight": "bold", "color": "orange"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div("Task:", style={"fontWeight": "bold"}),
                    width="auto",
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="task-dropdown",
                        placeholder="Select task",
                        clearable=False,
                        options=[],
                    ),
                    width=4,
                ),
                dbc.Col(
                    [
                        dbc.Button(
                            html.I(className="fa-regular fa-plus"),
                            id="create-task-btn",
                            className="custom-button",
                        ),
                        dbc.Tooltip(
                            "Create new task.",
                            target="create-task-btn",
                        ),
                    ],
                    width="auto",
                ),
                dbc.Col(
                    [
                        dbc.Button(
                            html.I(className="fa-solid fa-trash"),
                            color="danger",
                            id="delete-task-btn",
                        ),
                        dbc.Tooltip(
                            "Delete task.",
                            target="delete-task-btn",
                        ),
                    ],
                    width="auto",
                ),
            ],
            justify="start",
            align="center",
            style={"marginBottom": 10},
        ),
        html.Div(
            dcc.Tabs(
                value="cli",
                children=[
                    dcc.Tab(
                        label="Images",
                        value="images",
                        children=images_tab,
                        selected_className="custom-subtab--selected",
                        className="custom-subtab",
                    ),
                    dcc.Tab(
                        label="Annotations",
                        value="annotations",
                        children=annotations_tab,
                        selected_className="custom-subtab--selected",
                        className="custom-subtab",
                    ),
                    dcc.Tab(
                        label="CLI",
                        value="cli",
                        children=cli_tab,
                        selected_className="custom-subtab--selected",
                        className="custom-subtab",
                    ),
                ],
            ),
            id="task_tab_content",
        ),
        create_task_modal,
        delete_task_modal,
    ],
    style={"margin": 10, "width": "100%"},
)
