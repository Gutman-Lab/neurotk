# The tab containing the project selection / creation / deletion. Includes adding images to project.
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
from girder_client import GirderClient, HttpError
from os import getenv
from utils.mongo_utils import get_mongo_db, add_many_to_collection


projects_tab = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Div("Project:", style={"fontWeight": "bold"}), width="auto"
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
                    ),
                    width="auto",
                ),
                dbc.Col(
                    dbc.Button(
                        "Delete Project",
                        color="danger",
                        id="delete-project-btn",
                    ),
                    width="auto",
                ),
            ],
            justify="start",
            style={"marginTop": 5, "marginLeft": 5},
        )
    ],
)


@callback(
    [
        Output("project-dropdown", "options"),
        Output("project-dropdown", "value"),
    ],
    Input("user-store", "data"),
    prevent_initial_call=True,
)
def update_project_dropdown(user_data):
    if len(user_data):
        # Look for datasets in mongo.
        db = get_mongo_db()

        projects_db = db["projects"]

        # Look for datasets for this user.
        projects = list(projects_db.find({"user": user_data["user"]}))

        if not len(projects):
            # Look for projects for my user.
            gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
            gc.token = user_data["token"]

            # Look for the user folder.
            options = []

            try:
                projects_fld = gc.get(
                    f"resource/lookup?path=%2Fcollection%2FNeuroTK%2FProjects%2F{user_data['user']}"
                )

                projects = list(gc.listFolder(projects_fld["_id"]))

                # Push the datasets to mongo.
                _ = add_many_to_collection(
                    projects_db,
                    user_data["user"],
                    {project["_id"]: project for project in projects},
                )
            except HttpError:
                # Could not find the user folder, create it.
                projects_fld = gc.get(
                    "resource/lookup?path=%2Fcollection%2FNeuroTK%2FProjects"
                )

                _ = gc.createFolder(
                    projects_fld["_id"], user_data["user"], public=False
                )

        # List all the folders.
        options = [
            {"label": project["name"], "value": project["_id"]} for project in projects
        ]

        return options, options[0]["value"] if len(options) else None

    return [], None
