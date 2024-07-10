# The tab containing the project selection / creation / deletion. Includes adding images to project.
from dash import html, dcc, callback, Output, Input, State, no_update
import dash_bootstrap_components as dbc
from girder_client import GirderClient, HttpError
from os import getenv
from utils.mongo_utils import get_mongo_db, add_many_to_collection
from dash_ag_grid import AgGrid
from components.modals import (
    create_project_modal,
    delete_project_modal,
    add_dataset_modal,
)
from pandas import json_normalize

images_table = AgGrid(
    id="project-images-table",
    columnDefs=[],
    rowData=[],
    dashGridOptions={
        "pagination": True,
        "paginationAutoPageSize": True,
        "rowSelection": "multiple",
        "suppressRowClickSelection": True,
    },
    style={"height": "50vh"},
)

projects_tab = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button("Add Dataset", id="add-dataset-btn", color="success"),
                    width="auto",
                ),
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
            align="center",
            style={"marginTop": 5, "marginLeft": 5, "marginBottom": 5},
        ),
        images_table,
        create_project_modal,
        delete_project_modal,
        add_dataset_modal,
    ],
)


# Callbacks
@callback(
    [
        Output("project-dropdown", "options", allow_duplicate=True),
        Output("project-dropdown", "value", allow_duplicate=True),
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

                # To speed up the process get the Datasets and Tasks folder ids for each project.
                projects = []

                for project in gc.listFolder(projects_fld["_id"]):
                    project["datasets_id"] = None
                    project["tasks_id"] = None

                    for fld in gc.listFolder(project["_id"]):
                        if fld["name"] == "Datasets":
                            project["datasets_id"] = fld["_id"]
                        elif fld["name"] == "Tasks":
                            project["tasks_id"] = fld["_id"]

                    projects.append(project)

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

        # Sort by the label.
        options = sorted(options, key=lambda x: x["label"])

        return options, options[0]["value"] if len(options) else None

    return [], None


@callback(
    Output("delete-project-btn", "disabled", allow_duplicate=True),
    Input("project-dropdown", "options"),
    prevent_initial_call=True,
)
def disable_delete_button(projects):
    # Disable the delete button if no projects are available.
    return False if len(projects) else True


@callback(
    [
        Output("project-images-table", "columnDefs"),
        Output("project-images-table", "rowData"),
        Output("project-images-table", "paginationGoTo"),
    ],
    [Input("project-dropdown", "value"), State("user-store", "data")],
    prevent_initial_call=True,
)
def update_project_images_table(project_id, user_data):
    # Return the images for the project.
    if project_id:
        # Get the project from mongo.
        db = get_mongo_db()["projects"]

        project = db.find_one({"_id": project_id, "user": user_data["user"]})

        # Check if there are datasets and tasks, if not get them from DSA and update mongo.
        if project.get("datasets") is None:
            # These have not been pulled from the DSA yet.
            gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
            gc.token = user_data["token"]

            project_fld = gc.getFolder(project_id)

            for fld in gc.listFolder(project_fld["_id"]):
                if fld["name"] == "Datasets":
                    # Add this to the project and update the database.
                    dataset_metadata = fld.get("meta", {})
                    project["datasets"] = dataset_metadata

                    db.update_one(
                        {"_id": project_id, "user": user_data["user"]},
                        {"$set": {"datasets": dataset_metadata}},
                    )
                    break

        """Combine the dataset images into a single set - note that the same images
        can be in multiple datasets but with different metadata.
        
        """
        items = {}

        for images in project["datasets"].values():
            for image in images:
                if image["_id"] in items:
                    items[image["_id"]].update(image)
                else:
                    items[image["_id"]] = image

        # Now reformat them into a list of dictionaries and format into dataframe.
        items = list(items.values())

        df = json_normalize(items, sep="-")

        # Replace periods in column names with spaces.
        df.columns = [col.replace(".", " ") for col in df.columns]

        columnDefs = [{"headerName": col, "field": col} for col in df.columns]

        if len(columnDefs):
            columnDefs[0]["checkboxSelection"] = True

        rowData = df.to_dict(orient="records")

        return columnDefs, rowData, "first"

    return [], [], no_update


@callback(
    Output("add-dataset-btn", "disabled"),
    [
        Input("project-dropdown", "value"),
        State("dataset-dropdown", "options"),
    ],
    prevent_initial_call=True,
)
def disable_add_dataset_button(project_id, dataset_options):
    # Disable the add dataset button if no project is selected or no datasets are available.
    if project_id and dataset_options is not None and len(dataset_options):
        return False
    else:
        return True
