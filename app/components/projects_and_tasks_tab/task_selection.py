from dash import html, dcc, Output, Input, State, callback, no_update
import dash_bootstrap_components as dbc
from dash_mantine_components import Select
from utils.utils import get_gc
import pandas as pd

# from components.projects_and_tasks_tab.create_task_menu import create_task_menu


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
        # create_task_menu,
    ],
    id="task-selection",
    # style={"backgroundColor": COLORS["background-secondary"]},
)


@callback(
    Output("tasks-dropdown", "data"),
    # Input("projects-dropdown", "value"),
    Input("project-store", "data"),
    prevent_initial_call=True,
)
def update_task_dropdown(project_data: dict) -> list[dict[str, str]]:
    """Update the options in the task selection.

    Args:
        selected_project (str): DSA folder id for selected project.
        project_data (dict): Data for the selected project.

    Returns:
        list[dict[str, str]]: List of tasks for the selected project, in format taken by
            dash_mantine_components.Select.

    """
    if project_data:
        return [
            {"value": task["_id"], "label": name}
            for name, task in project_data["tasks"].items()
        ]

    return []


@callback(
    Output("task-store", "data"),
    Input("tasks-dropdown", "value"),
    State("project-store", "data"),
    prevent_initial_call=True,
)
def update_task_store(selected_task: str, project_store: list[dict]) -> list[dict]:
    """ "Update the task store."""
    # If this task has been run before, then the task store is immutable so show it.
    # Otherwise leave the task-store empty.
    if selected_task:
        gc = get_gc()

        return []

    return []
