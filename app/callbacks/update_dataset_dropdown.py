from dash import callback, Output, Input, State, ctx
from os import getenv
from dsa_helpers.mongo_utils import add_many_to_collection
from utils.utils import get_mongo_database
from girder_client import GirderClient, HttpError


@callback(
    [
        Output("dataset-dropdown", "options"),
        Output("dataset-dropdown", "value"),
    ],
    [
        Input(getenv("LOGIN_STORE_ID"), "data"),
        Input("sync-datasets-btn", "n_clicks"),
        State("dataset-dropdown", "value"),
    ],
)
def update_dataset_dropdown(user_data, n_clicks, dataset_id):
    # Only run if there is user data.
    if user_data is not None and len(user_data):
        # Get datasets collection.
        datasets_collection = get_mongo_database(user_data["user"])["datasets"]

        # Get all the datasets available.
        datasets = list(datasets_collection.find({}))

        if not len(datasets) or (ctx.triggered_id == "sync-datasets-btn" and n_clicks):
            # Look for datasets for my user.
            gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
            gc.token = user_data["token"]

            # Look for the user folder.
            try:
                datasets_fld = gc.get(
                    f"resource/lookup?path=%2Fcollection%2FNeuroTK%2FDatasets%2F{user_data['user']}"
                )

                datasets = list(gc.listItem(datasets_fld["_id"]))

                # Push the datasets to mongo.
                _ = add_many_to_collection(
                    datasets_collection,
                    datasets,
                )
            except HttpError:
                # Could not find the user folder, create it.
                datasets_fld = gc.get(
                    "resource/lookup?path=%2Fcollection%2FNeuroTK%2FDatasets"
                )

                _ = gc.createFolder(
                    datasets_fld["_id"], user_data["user"], public=False
                )

        # List all the dataset items.
        options = [
            {"label": dataset["name"], "value": dataset["_id"]} for dataset in datasets
        ]

        # Set the value of the options to current selected one otherwise choose the first.
        if dataset_id is not None:
            for option in options:
                if option["value"] == dataset_id:
                    return options, dataset_id

        return options, options[0]["value"] if len(options) else None

    return [], None
