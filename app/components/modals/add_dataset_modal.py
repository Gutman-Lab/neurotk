from dash import html, callback, Output, Input, State, no_update, dcc
import dash_bootstrap_components as dbc
from girder_client import GirderClient
from os import getenv
from utils.utils import get_mongo_database, get_project_items

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
                    id="add-dataset-dropdown", options=[], clearable=False
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
    [
        Output("add-dataset-dropdown", "options"),
        Output("add-dataset-dropdown", "value"),
    ],
    Input("dataset-dropdown", "options"),
)
def update_add_dataset_dropdown(dataset_options):
    # Specify the dataset options based on datasets not currently in the project.
    if dataset_options is not None and len(dataset_options):
        # Get project document from database.

        return dataset_options, dataset_options[0]["value"]

    return [], None


@callback(
    Output("add-dataset-modal", "is_open", allow_duplicate=True),
    Input("add-dataset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def open_dataset_modal(n_clicks):
    # Open the dataset modal.
    return True if n_clicks else False


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
        Output("project-table-info", "children", allow_duplicate=True),
    ],
    [
        Input("add-dataset-modal-btn", "n_clicks"),
        State(getenv("LOGIN_STORE_ID"), "data"),
        State("add-dataset-dropdown", "value"),
        State("project-dropdown", "value"),
    ],
    prevent_initial_call=True,
)
def add_dataset_to_project(n_clicks, user_data, dataset_id, project_id):
    if n_clicks:
        # Mongo database.
        mongodb = get_mongo_database(user_data["user"])

        # Get dataset metadata.
        dataset_doc = mongodb["datasets"].find_one({"_id": dataset_id})

        # Authenticate girder client.
        gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
        gc.token = user_data["token"]

        # Get the project metadata.
        project_doc = mongodb["projects"].find_one({"_id": project_id})

        # Add the dataset id to the project metadata.
        if "datasets" not in project_doc["meta"]:
            project_doc["meta"]["datasets"] = []

        if dataset_id not in project_doc["meta"]["datasets"]:
            project_doc["meta"]["datasets"].append(dataset_id)

            # Update this document and its copy on the DSA.
            mongodb["projects"].update_one(
                {"_id": project_id},
                {"$set": {"meta.datasets": project_doc["meta"]["datasets"]}},
            )

            _ = gc.addMetadataToFolder(
                project_id, {"datasets": project_doc["meta"]["datasets"]}
            )

            # Run function to get the project items.
            column_defs, row_data = get_project_items(
                project_id, user_data["user"]
            )

            return (
                column_defs,
                row_data,
                False,
                f"Images in the project (n={len(row_data)}):",
            )

    return no_update, no_update, False, no_update
