from dash import html, callback, Output, Input, State, no_update, dcc
import dash_bootstrap_components as dbc
from utils.mongo_utils import get_mongo_db
from girder_client import GirderClient
from os import getenv
from pandas import json_normalize

add_dataset_modal = dbc.Modal(
    [
        dbc.ModalHeader("Add Dataset"),
        dbc.ModalBody(
            [
                html.Div(
                    "Dataset",
                    style={"margin": 5, "marginTop": 5, "fontWeight": "bold"},
                ),
                dcc.Dropdown(
                    id="add-dataset-dropdown",
                    options=[],
                ),
            ]
        ),
        dbc.ModalFooter(
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            "Close",
                            className="me-1",
                            color="light",
                            id="close-add-dataset-modal",
                        )
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Add",
                            className="me-1",
                            color="primary",
                            id="add-dataset-modal-btn",
                        )
                    ),
                ]
            )
        ),
    ],
    id="add-dataset-modal",
    is_open=False,
)


# Callbacks
@callback(
    Output("add-dataset-modal", "is_open", allow_duplicate=True),
    Input("add-dataset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def open_dataset_modal(n_clicks):
    # Open the dataset modal.
    return True if n_clicks else False


@callback(
    [
        Output("add-dataset-dropdown", "options"),
        Output("add-dataset-dropdown", "value"),
    ],
    Input("dataset-dropdown", "options"),
)
def update_add_dataset_dropdown(dataset_options):
    # Update the options of the dataset dropdown.
    if dataset_options is not None and len(dataset_options):
        return dataset_options, dataset_options[0]["value"]

    return [], None


@callback(
    Output("add-dataset-modal", "is_open", allow_duplicate=True),
    Input("close-add-dataset-modal", "n_clicks"),
    prevent_initial_call=True,
)
def close_add_dataset_modal(n_clicks):
    # Close the dataset modal.
    return False if n_clicks else True


@callback(
    [
        Output("project-images-table", "columnDefs", allow_duplicate=True),
        Output("project-images-table", "rowData", allow_duplicate=True),
        Output("add-dataset-modal", "is_open", allow_duplicate=True),
    ],
    [
        Input("add-dataset-modal-btn", "n_clicks"),
        State("user-store", "data"),
        State("project-dropdown", "value"),
        State("add-dataset-dropdown", "value"),
    ],
    prevent_initial_call=True,
)
def add_dataset_to_project(n_clicks, user_data, project_id, dataset_id):
    # Add the dataset to this project.
    if n_clicks:
        gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
        gc.token = user_data["token"]

        # Get the project from the database.
        db = get_mongo_db()
        projects_col = db["projects"]
        project = projects_col.find_one({"_id": project_id, "user": user_data["user"]})

        # Find the dataset from database.
        dataset = db["datasets"].find_one(
            {"_id": dataset_id, "user": user_data["user"]}
        )

        # Check if the dataset is already in the project.
        if dataset["name"] in project["datasets"]:
            # Update the entry in the project.
            images = {img["_id"]: img for img in project["datasets"][dataset["name"]]}

            for img in dataset["meta"]["data"]:
                if img["_id"] in images:
                    images[img["_id"]].update(img)
                else:
                    images[img["_id"]] = img

            _ = gc.addMetadataToFolder(
                project["datasets_id"], {dataset["name"]: list(images.values())}
            )

            project["datasets"][dataset["name"]] = list(images.values())
        else:
            # Add it as a new one.
            _ = gc.addMetadataToFolder(
                project["datasets_id"], {dataset["name"]: dataset["meta"]["data"]}
            )

            # Update the project.
            project["datasets"][dataset["name"]] = dataset["meta"]["data"]

        projects_col.update_one(
            {"_id": project_id, "user": user_data["user"]},
            {"$set": {"datasets": project["datasets"]}},
        )

        # Return the columns and row definitions.
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

        rowData = df.to_dict(orient="records")

        return columnDefs, rowData, False

    return no_update, no_update, no_update
