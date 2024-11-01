from dash import html, dcc
import dash_bootstrap_components as dbc

from components.modals import create_task_modal
from components.modals import delete_task_modal
from components.tasks_tab_tabs.images_table_tab import images_table_tab
from components.tasks_tab_tabs.cli_tab import cli_tab
from components.tasks_tab_tabs.annotations_tab import annotations_tab

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
                    ),
                    width=4,
                ),
                dbc.Col(
                    dbc.Button(
                        "Create Task",
                        id="create-task-btn",
                        className="custom-button",
                    ),
                    width="auto",
                ),
                dbc.Col(
                    dbc.Button(
                        "Delete Task",
                        color="danger",
                        id="delete-task-btn",
                    ),
                    width="auto",
                ),
            ],
            justify="start",
            align="center",
            style={"marginBottom": 10},
        ),
        html.Div(
            dcc.Tabs(
                [
                    dcc.Tab(
                        label="Images",
                        value="images",
                        children=images_table_tab,
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
                value="images",
            ),
            id="task_tab_content",
        ),
        create_task_modal,
        delete_task_modal,
    ],
    style={"margin": 10},
)
