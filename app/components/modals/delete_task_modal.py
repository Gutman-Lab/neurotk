from dash import html, callback, Output, Input, State, no_update
import dash_bootstrap_components as dbc
from girder_client import GirderClient
from os import getenv
from utils.mongo_utils import get_mongo_db

delete_task_modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div("Delete task?", style={"fontWeight": "bold"}),
                                width="auto",
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Delete",
                                    color="danger",
                                    id="delete-task-modal-btn",
                                ),
                                width="auto",
                            ),
                        ]
                    )
                ),
            ],
            id="delete-task-modal",
            is_open=False,
        )
    ]
)


# Callbacks
@callback(
    Output("delete-task-modal", "is_open", allow_duplicate=True),
    Input("delete-task-btn", "n_clicks"),
    prevent_initial_call=True,
)
def toggle_delete_task_modal(n_clicks):
    return n_clicks


@callback(
    [
        Output("task-dropdown", "options", allow_duplicate=True),
        Output("task-dropdown", "value", allow_duplicate=True),
        Output("delete-task-modal", "is_open", allow_duplicate=True),
    ],
    [
        Input("delete-task-modal-btn", "n_clicks"),
        State("task-dropdown", "value"),
        State("task-dropdown", "options"),
        State("user-store", "data"),
    ],
    prevent_initial_call=True,
)
def delete_task(n_clicks, task_id, task_options, user_data):
    # Delete the selected task.
    if n_clicks:
        # Delete the task.
        gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
        gc.token = user_data["token"]

        _ = gc.delete(f"item/{task_id}")

        # Remove it from the database.
        db = get_mongo_db()["tasks"]

        db.delete_one({"_id": task_id, "user": user_data["user"]})

        # Remove from the options.
        task_options = [task for task in task_options if task["value"] != task_id]

        return (
            task_options,
            task_options[0]["value"] if len(task_options) else None,
            False,
        )

    return no_update, no_update, False
