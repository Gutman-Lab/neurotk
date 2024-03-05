from dash import html, dcc, Output, Input, State, callback, no_update
import dash_bootstrap_components as dbc
from dash_mantine_components import Select
from typing import List

# from ...utils.settings import gc, AVAILABLE_CLI_TASKS, dbConn, COLORS
# from .create_task_popup import create_task_popup

task_selection = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Div("Select task: ", style={"fontWeight": "bold"}),
                    align="start",
                    width="auto",
                ),
                dbc.Col(
                    html.Div(
                        Select(
                            data=[],
                            id="tasks-dropdown",
                            clearable=True,
                            placeholder="No task selected.",
                        )
                    )
                ),
                dbc.Col(
                    html.Div(
                        dbc.Button(
                            "Create task",
                            id="open-create-task-bn",
                            color="success",
                            className="me-1",
                        ),
                    ),
                    align="end",
                    width="auto",
                ),
                # dbc.Col(
                #     html.Div(
                #         dbc.Button(
                #             "Delete selected task",
                #             id="delete-task",
                #             color="danger",
                #             className="me-1",
                #         )
                #     ),
                #     align="end",
                #     width="auto",
                # ),
            ]
        ),
        # create_task_popup,
    ],
    id="task-selection",
    # style={"backgroundColor": COLORS["background-secondary"]},
)
