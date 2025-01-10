from dash import callback, Output, Input, State, no_update
from os import getenv
from girder_client import GirderClient
from utils import get_mongo_database
from dsa_helpers.mongo_utils import add_many_to_collection


@callback(
    [
        Output("create-project-modal", "is_open", allow_duplicate=True),
        Output("new-project-name", "value", allow_duplicate=True),
        Output("create-project-failed", "hidden", allow_duplicate=True),
    ],
    Input("create-project-btn", "n_clicks"),
    prevent_initial_call=True,
)
def open_create_project_modal(n_clicks):
    # Open the create project modal.
    return n_clicks, "", True


@callback(
    Output("create-project-modal", "is_open", allow_duplicate=True),
    Input("close-create-project-modal", "n_clicks"),
    prevent_initial_call=True,
)
def close_create_project_modal(n_clicks):
    # Close the create project modal.
    return False if n_clicks else True


@callback(
    [
        Output("project-dropdown", "value", allow_duplicate=True),
        Output("project-dropdown", "options", allow_duplicate=True),
        Output("create-project-failed", "children", allow_duplicate=True),
        Output("create-project-failed", "hidden", allow_duplicate=True),
        Output("create-project-modal", "is_open", allow_duplicate=True),
    ],
    [
        Input("create-project-modal-btn", "n_clicks"),
        State("new-project-name", "value"),
        State("project-dropdown", "options"),
        State(getenv("LOGIN_STORE_ID"), "data"),
    ],
    prevent_initial_call=True,
)
def create_project(n_clicks, project_name, project_options, user_data):
    # Create a new project.
    if n_clicks:
        if not len(project_name):
            return (
                no_update,
                no_update,
                "Project name cannot be empty.",
                False,
                True,
            )

        # Check if the project name already exists.
        if project_name in [option["label"] for option in project_options]:
            return no_update, no_update, "Project name exists.", False, True

        # Create the project on the DSA and append it to the project options in the right order.
        gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
        gc.token = user_data["token"]

        projects_fld_id = gc.get(
            f"resource/lookup?path=%2Fcollection%2FNeuroTK%2FProjects%2F{user_data['user']}"
        )["_id"]

        # Create the projects folder.
        project_fld = gc.createFolder(
            projects_fld_id, project_name, public=False
        )

        # Add the folder to mongo.
        projects_collection = get_mongo_database(user_data["user"])["projects"]

        _ = add_many_to_collection(projects_collection, [project_fld])

        # Append the options.
        project_options.append(
            {"label": project_name, "value": project_fld["_id"]}
        )

        # Sort by the label.
        project_options = sorted(project_options, key=lambda x: x["label"])

        return project_fld["_id"], project_options, no_update, True, False

    return no_update, no_update, no_update, no_update, no_update
