from dash import callback, Output, Input, State, html, ctx
from utils.utils import get_mongo_database
from dsa_helpers.mongo_utils import add_many_to_collection
from os import getenv
import dash_bootstrap_components as dbc
from girder_client import GirderClient


@callback(
    [
        Output("annotation-dropdown", "options"),
        Output("annotation-dropdown", "value"),
    ],
    [
        Input("resync-annotations-btn", "n_clicks"),
        Input("images-table", "rowData"),
        Input("images-table", "filterModel"),
        Input("images-table", "virtualRowData"),
        State(getenv("LOGIN_STORE_ID"), "data"),
    ],
    prevent_initial_call=True,
)
def update_annotation_dropdown(
    n_clicks, row_data, filter_model, virtual_row_data, user_data
):
    if filter_model is not None and len(filter_model):
        row_data = virtual_row_data

    if row_data is not None and len(row_data):
        # Get the list item ids to check.
        image_ids = [row["_id"] for row in row_data]

        # Get all annotations from the database.
        annotation_collection = get_mongo_database(user_data["user"])[
            "annotations"
        ]

        if ctx.triggered_id == "resync-annotations-btn":
            # Pull the annotations from the database.
            gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
            gc.token = user_data["token"]

            # Remove all annotation documents for these images from database.
            annotation_collection.delete_many({"itemId": {"$in": image_ids}})

            ann_docs = []

            for image_id in image_ids:
                # Get the annotations from Girder.
                ann_docs.extend(gc.get(f"annotation/item/{image_id}"))

            # Update the database with the new annotations.
            _ = add_many_to_collection(annotation_collection, ann_docs)

        ann_docs = list(
            annotation_collection.find(
                {"itemId": {"$in": image_ids}},
                {"_id": 0, "annotation.name": 1},
            )
        )

        # Get the unique annotation names.
        names = set()

        for doc in ann_docs:
            if doc.get("annotation", {}).get("name"):
                names.add(doc["annotation"]["name"])

        # Create the dropdown options.
        dropdown_options = [{"label": name, "value": name} for name in names]

        return dropdown_options, (
            dropdown_options[0]["value"] if len(dropdown_options) else None
        )

    return [], None


@callback(
    Output("annotations-tab-content", "children", allow_duplicate=True),
    [
        State("images-table", "rowData"),
        State("images-table", "filterModel"),
        State("images-table", "virtualRowData"),
        State(getenv("LOGIN_STORE_ID"), "data"),
        Input("annotation-dropdown", "value"),
    ],
    prevent_initial_call=True,
)
def update_annotations_tab_content(
    row_data, filter_model, virtual_row_data, user_data, annotation_name
):
    if filter_model is not None and len(filter_model):
        row_data = virtual_row_data

    if row_data is not None and len(row_data):
        # Get the list item ids to check.
        image_ids = [row["_id"] for row in row_data]

        # Get all annotations from the database.
        annotation_collection = get_mongo_database(user_data["user"])[
            "annotations"
        ]

        ann_docs = list(
            annotation_collection.find(
                {
                    "itemId": {"$in": image_ids},
                    "annotation.name": annotation_name,
                },
                {"_id": 0, "itemId": 1, "annotation.name": 1},
            )
        )

        # Get the number of unique item ids in the docs.
        item_ids = set()
        for doc in ann_docs:
            item_ids.add(doc["itemId"])

        # Return the string.
        out = html.Div(
            [
                html.Div(f"Images with document: {len(item_ids)}"),
                html.Div(
                    f"Images without document: {len(image_ids) - len(item_ids)}"
                ),
            ]
        )

        return out

    return []
