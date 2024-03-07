import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import html, Output, Input, State, callback, no_update, ctx
from os.path import join
from os import getenv

from utils.utils import get_current_user
from utils.stores import get_projects, get_project
from utils.mongo_utils import add_one_to_collection, get_mongo_client

create_project_menu = dbc.Modal(
    [
        dbc.ModalHeader("Create Project"),
        dbc.ModalBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dmc.TextInput(
                                id="new-project-name",
                                label="Project name:",
                                placeholder="Input new project name.",
                            )
                        )
                    ]
                ),
                dbc.Row(
                    [dmc.Alert("", color="red", id="create-project-alert", hide=False)]
                ),
                html.Br(),
                dbc.Row(
                    [
                        dbc.Col(
                            dmc.Switch(
                                onLabel="Private",
                                offLabel="Public",
                                size="xl",
                                id="project-type-toggle",
                            )
                        ),
                        dbc.Col(
                            html.Button(
                                "Create Project",
                                style={"background": "#7df097"},
                                id="create-project-bn2",
                                disabled=False,
                            )
                        ),
                    ]
                ),
            ]
        ),
    ],
    id="create-project-popup",
    is_open=False,
    fullscreen=False,
)


@callback(
    Output("create-project-popup", "is_open"),
    Input("create-project-bn", "n_clicks"),
    Input("projects-dropdown-store", "data"),
    prevent_initial_call=True,
)
def open_create_project_popup(n_clicks: int, projects_dropdown):
    """
    Open the window for creating new projects.

    Args:
        n_clicks: Number of times the button to open up the "create projects
            modal" has been clicked.

    Returns:
        None if the button has not been clicked, otherwise returns the input
        n_clicks.

    """
    if ctx.triggered_id == "create-project-bn" and n_clicks:
        return True
    else:
        return False


@callback(
    [
        Output("projects-dropdown-store", "data"),
        Output("create-project-alert", "children"),
        Output("new-project-name", "value"),
    ],
    [
        Input("create-project-bn2", "n_clicks"),
        Input("resync-project-list-btn", "n_clicks"),
    ],
    State("new-project-name", "value"),
    State("projects-dropdown-store", "data"),
    State("project-type-toggle", "checked"),
    # prevent_initial_call=True,
)
def create_new_project(n_clicks, resync_click, new_project_name, projects, type_toggle):
    """
    Logic for creating a new project.

    """
    # Use callback context to decide on the logic.
    context_id = ctx.triggered_id

    if resync_click and context_id == "resync-project-list-btn":
        # Resync the projects.
        mongo_db = get_mongo_client()["projectStore"]

        mongo_db.delete_many({"user": get_current_user()[1]})

        projects = get_projects(resync=True)

        if len(projects):
            _ = get_project(projects[0]["_id"])
        return get_projects(resync=True), "", ""
    elif n_clicks and new_project_name:
        # Find current username.
        gc, user = get_current_user()

        new_project_label = join(user, new_project_name)

        for project in projects:
            if new_project_label == project["label"]:
                return no_update, "Project already exists!"

        # Create the new project!
        type_value = "Private" if type_toggle else "Public"

        for fld in gc.listFolder(
            getenv("DSA_NEUROTK_COLLECTION_ID"), parentFolderType="collection"
        ):
            if fld["name"] == "Projects":
                for type_fld in gc.listFolder(fld["_id"]):
                    if type_fld["name"] == type_value:
                        for user_fld in gc.listFolder(type_fld["_id"]):
                            if user_fld["name"] == user:
                                # Create the project.
                                is_public = True if type_value == "Public" else False

                                new_project_fld = gc.createFolder(
                                    user_fld["_id"], new_project_name, public=is_public
                                )

                                # Create the Datasets and Tasks subdirs.
                                gc.createFolder(
                                    new_project_fld["_id"], "Datasets", public=is_public
                                )
                                gc.createFolder(
                                    new_project_fld["_id"], "Tasks", public=is_public
                                )

                                # Add this project to the collection.
                                add_one_to_collection(
                                    "projects",
                                    {
                                        "value": new_project_fld["_id"],
                                        "label": f"{user}/{new_project_fld['name']}",
                                    },
                                    key="value",
                                    user=user,
                                )

                                return get_projects(), "", ""

    # This is the default return.
    return get_projects(), "", ""


# @callback(
#     Output("create-project-bn", "disabled"),
#     Input("new-project-name", "value"),
#     prevent_initial_call=True,
# )
# def disable_create_project_bn(new_project_name: str):
#     """
#     Disable the button to create a project when the input field (i.e. the name)
#     is empty.

#     Args:
#         new_project_name:

#     Returns:
#         True if there is text in the input project name text box or False
#         otherwise.

#     """
#     return False if new_project_name else True


# @callback(
#     [
#         Output("projects-store", "data", allow_duplicate=True),
#         Output("create-project-popup", "is_open", allow_duplicate=True),
#         Output("create-project-alert", "hide"),
#     ],
#     Input("create-project-bn", "n_clicks"),
#     [
#         State("projects-store", "data"),
#         State("project-type-toggle", "checked"),
#         State("new-project-name", "value"),
#     ],
#     prevent_initial_call=True,
# )
# def create_new_project(n_clicks, data, state, value):
#     """
#     Logic for creating a new project.

#     """
#     # When the create new project button is clicked.
#     if n_clicks:
#         # Check for new project.
#         new_project = f"{USER}/{value}"

#         if new_project in [d["key"] for d in data]:
#             return no_update, True, False
#         else:
#             # Create the new folder.
#             privacy = "Private" if state else "Public"

#             # Create new project folder.
#             type_fld = gc.createFolder(
#                 PROJECTS_ROOT_FOLDER_ID, privacy, reuseExisting=True
#             )

#             user_fld = gc.createFolder(type_fld["_id"], USER, reuseExisting=True)

#             # Create the project folder.
#             _ = gc.createFolder(user_fld["_id"], value)

#             return getProjects(PROJECTS_ROOT_FOLDER_ID, forceRefresh=True), False, True

#     return data if len(data) else [], False, True


# @callback(
#     Output("create-project-alert", "children"),
#     Input("create-project-alert", "hide"),
#     State("new-project-name", "value"),
#     prevent_initial_call=True,
# )
# def alert_existing_project(hide, value):
#     if hide:
#         return ""
#     else:
#         return f"{USER}/{value} project already exists."


############## NOTE: this was already commented out
# @callback(
#     Output("projects-dropdown", "value"),
#     Input("projects-store", "data"),
#     [State("new-project-name", "value"), State("projects-dropdown", "data")],
#     suppress_initial_call=True,
# )
# def update_selected_project(project_store, new_project_name, projects):
#     if len(project_store):
#         # If there is a new project name, make this the value.
#         for project in project_store:
#             if project["name"] == new_project_name:
#                 return project["_id"]

#         # Return the first project.
#         print("Projects", projects)

#         return project_store[0]["_id"]
#     else:
#         return ""
