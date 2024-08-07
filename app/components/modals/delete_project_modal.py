from dash import html, Output, Input, State, no_update, callback
import dash_bootstrap_components as dbc
from girder_client import GirderClient
from os import getenv
from utils.mongo_utils import get_mongo_db

delete_project_modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    "Delete project?", style={"fontWeight": "bold"}
                                ),
                                width="auto",
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Delete",
                                    color="danger",
                                    id="delete-project-modal-btn",
                                ),
                                width="auto",
                            ),
                        ]
                    )
                ),
            ],
            id="delete-project-modal",
            is_open=False,
        )
    ]
)


# Callbacks
@callback(
    Output("delete-project-modal", "is_open", allow_duplicate=True),
    Input("delete-project-btn", "n_clicks"),
    prevent_initial_call=True,
)
def toggle_delete_project_modal(n_clicks):
    return n_clicks


@callback(
    [
        Output("project-dropdown", "options", allow_duplicate=True),
        Output("project-dropdown", "value", allow_duplicate=True),
        Output("delete-project-modal", "is_open", allow_duplicate=True),
    ],
    [
        Input("delete-project-modal-btn", "n_clicks"),
        State("project-dropdown", "value"),
        State("project-dropdown", "options"),
        State("user-store", "data"),
    ],
    prevent_initial_call=True,
)
def delete_project(n_clicks, project_id, project_options, user_data):
    # Delete the selected project.
    if n_clicks:
        # Delete the project.
        gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
        gc.token = user_data["token"]

        _ = gc.delete(f"folder/{project_id}")

        # Remove it from the database.
        db = get_mongo_db()["projects"]

        db.delete_one({"_id": project_id, "user": user_data["user"]})

        # Remove from the options.
        project_options = [
            project for project in project_options if project["value"] != project_id
        ]

        return (
            project_options,
            project_options[0]["value"] if len(project_options) else None,
            False,
        )

    return no_update, no_update, False
