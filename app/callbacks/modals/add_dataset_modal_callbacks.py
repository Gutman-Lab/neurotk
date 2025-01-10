from dash import callback, Output, Input, State, no_update
from os import getenv
from girder_client import GirderClient

from utils import get_mongo_database
from utils.utils import get_project_items


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

        # Get all the item ids in the dataset.
        item_ids = [item["_id"] for item in dataset_doc["meta"]["dataset"]]

        # Check if project document has metadata.
        if "meta" not in project_doc:
            project_doc["meta"] = {}

        if "item_ids" not in project_doc["meta"]:
            project_doc["meta"]["item_ids"] = []

        # Add the new and current item ids.
        project_doc["meta"]["item_ids"] = list(
            set(project_doc["meta"]["item_ids"] + item_ids)
        )

        # Update the project document.
        mongodb["projects"].update_one(
            {"_id": project_id},
            {"$set": {"meta.images": project_doc["meta"]["item_ids"]}},
        )

        # Update the project metadata on the DSA.
        _ = gc.addMetadataToFolder(
            project_id, {"images": project_doc["meta"]["item_ids"]}
        )

        # Run function to get the project items.
        column_defs, row_data = get_project_items(
            project_doc["meta"]["item_ids"], user_data["user"]
        )

        return (
            column_defs,
            row_data,
            False,
            f"Images in the project (n={len(row_data)}):",
        )

    return no_update, no_update, False, no_update
