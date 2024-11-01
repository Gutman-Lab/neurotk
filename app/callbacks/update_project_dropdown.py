from dash import callback, Output, Input
from os import getenv
from dsa_helpers.mongo_utils import add_many_to_collection
from utils.utils import get_mongo_database
from girder_client import GirderClient, HttpError


@callback(
    [
        Output("project-dropdown", "options", allow_duplicate=True),
        Output("project-dropdown", "value", allow_duplicate=True),
    ],
    Input(getenv("LOGIN_STORE_ID"), "data"),
    prevent_initial_call=True,
)
def update_project_dropdown(user_data):
    if len(user_data):
        # Get the mongodb project collection.
        projects_collection = get_mongo_database(user_data["user"])["projects"]

        # Get project mongodb documents.
        project_docs = list(projects_collection.find({}))

        if not len(project_docs):
            # No projects in the database, get them from DSA.
            gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
            gc.token = user_data["token"]

            try:
                # Get the user's project folder.
                user_project_fld = gc.get(
                    f"resource/lookup?path=%2Fcollection%2FNeuroTK%2FProjects%2F{user_data['user']}"
                )

                # List all the project subfolders.
                project_docs = list(gc.listFolder(user_project_fld["_id"]))

                if len(project_docs):
                    # Add to the database.
                    _ = add_many_to_collection(
                        projects_collection,
                        project_docs,
                    )
            except HttpError:
                # Create user folder.
                projects_fld = gc.get(
                    "resource/lookup?path=%2Fcollection%2FNeuroTK%2FProjects"
                )

                _ = gc.createFolder(
                    projects_fld["_id"], user_data["user"], public=False
                )

        # List all the folders.
        options = [
            {"label": project["name"], "value": project["_id"]}
            for project in project_docs
        ]

        # Sort by the label.
        options = sorted(options, key=lambda x: x["label"])

        return options, options[0]["value"] if len(options) else None

    return [], None
