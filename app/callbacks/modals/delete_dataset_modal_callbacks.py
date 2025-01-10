from dash import callback, Output, Input, State, no_update
from os import getenv
from girder_client import GirderClient
from utils import get_mongo_database


@callback(
    Output("delete-dataset-modal", "is_open", allow_duplicate=True),
    Input("delete-dataset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def toggle_delete_dataset_modal(n_clicks):
    return n_clicks


@callback(
    [
        Output("dataset-dropdown", "options", allow_duplicate=True),
        Output("dataset-dropdown", "value", allow_duplicate=True),
        Output("delete-dataset-modal", "is_open", allow_duplicate=True),
    ],
    [
        Input("delete-dataset-modal-btn", "n_clicks"),
        State("dataset-dropdown", "value"),
        State("dataset-dropdown", "options"),
        State(getenv("LOGIN_STORE_ID"), "data"),
    ],
    prevent_initial_call=True,
)
def delete_dataset(n_clicks, dataset_id, dataset_options, user_data):
    # Delete the selected dataset.
    if n_clicks:
        # Delete the dataset.
        gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
        gc.token = user_data["token"]

        _ = gc.delete(f"item/{dataset_id}")

        # Remove it from the database.
        dataset_collection = get_mongo_database(user_data["user"])["datasets"]

        dataset_collection.delete_one({"_id": dataset_id})

        # Remove from the options.
        new_options = [
            dataset
            for dataset in dataset_options
            if dataset["value"] != dataset_id
        ]

        return (
            new_options,
            new_options[0]["value"] if len(new_options) else None,
            False,
        )

    return no_update, no_update, False
