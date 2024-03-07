"""
Component with popup windows to create new task.
"""

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import html, Output, Input, State, callback, no_update

from utils.utils import create_new_task
from utils.mongo_utils import add_one_task
from utils.stores import get_project

create_task_menu = dbc.Modal(
    [
        dbc.ModalHeader("Create Task"),
        dbc.ModalBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dmc.TextInput(
                                id="new-task-name",
                                label="Task name:",
                                placeholder="Input new task name.",
                            )
                        ),
                        dbc.Col(
                            html.Button(
                                "Create Task",
                                style={"background": "#7df097"},
                                id="create-task-bn",
                                disabled=False,
                            )
                        ),
                    ]
                ),
                dbc.Row([dmc.Alert("", id="create-task-alert", hide=False)]),
            ]
        ),
    ],
    id="create-task-popup",
    is_open=False,
    fullscreen=False,
)


@callback(
    Output("create-task-popup", "is_open", allow_duplicate=True),
    Input("open-create-task-bn", "n_clicks"),
    prevent_initial_call=True,
)
def open_create_task_popup(n_clicks):
    """
    Open the create task popup window.

    """
    if n_clicks:
        return True


@callback(
    [
        Output(
            "project-store",
            "data",
            allow_duplicate=True,
        ),
        Output("create-task-alert", "children"),
        Output("tasks-dropdown", "data", allow_duplicate=True),
        Output("tasks-dropdown", "value", allow_duplicate=True),
        Output("create-task-popup", "is_open", allow_duplicate=True),
    ],
    [
        Input("create-task-bn", "n_clicks"),
        State("new-task-name", "value"),
        State("project-store", "data"),
        State("tasks-dropdown", "data"),
    ],
    prevent_initial_call=True,
)
def create_task(n_clicks, new_task, project_data, tasks_options):
    """Create the task if it does not exist."""
    if n_clicks:
        if not new_task:
            return no_update, "Task name cannot be empty.", no_update, no_update, True
        elif new_task in project_data.get("tasks", []):
            return no_update, "Task already exists.", no_update, no_update, True

        # Create the new task by creating it in the DSA and update the mongo database.
        task_item = create_new_task(project_data["_id"], new_task)

        # Updating the mongo db.
        add_one_task(project_data["_id"], task_item)

        # Update the task options and value.
        tasks_options.append({"value": new_task, "label": new_task})

        # Return the updated project.
        return (
            get_project(project_data["_id"])[0],
            "Task created.",
            tasks_options,
            new_task,
            False,
        )

    return no_update, "", no_update, no_update, False
