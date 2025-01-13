from dash import callback, Output, Input, State, ctx
from os import getenv
from girder_client import GirderClient
from dsa_helpers.mongo_utils import add_many_to_collection

from utils import get_mongo_database
from utils.girder_utils import get_item_annotation_docs


@callback(
    [
        Output("annotation-dropdown", "options", allow_duplicate=True),
        Output("annotation-dropdown", "value", allow_duplicate=True),
    ],
    [
        Input("resync-annotations-btn", "n_clicks"),
        State("images-table", "rowData"),
        State("images-table", "filterModel"),
        State("images-table", "virtualRowData"),
        State(getenv("LOGIN_STORE_ID"), "data"),
    ],
    prevent_initial_call=True,
)
def sync_annotation_doc_dropdown(
    n_clicks, row_data, filter_model, virtual_row_data, user_data
):
    """
    When the sync annotation button is clicked, check the DSA for
    annotation documents for images currently in the images table.

    """
    if n_clicks and (len(row_data) or len(virtual_row_data)) and user_data:
        # Set the row data based on if filters are being used or not.
        if filter_model is not None and len(filter_model):
            row_data = virtual_row_data

        # Get all the image ids from the table.
        image_ids = [row["_id"] for row in row_data]

        # Get the annotations collection from mongodb.
        mongodb = get_mongo_database(user_data["user"])

        annotations_collection = mongodb["annotations"]

        # Delete all documents that have itemId key in image_ids.
        annotations_collection.delete_many({"itemId": {"$in": image_ids}})

        # Authenticate the girder client to check the DSA for annotations.
        gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
        gc.token = user_data["token"]

        docs = []

        for img_meta in row_data:
            # Get the documents for this image.
            img_docs = get_item_annotation_docs(
                gc, img_meta["_id"], with_elements=False
            )

            # Append the documents to the list.
            docs.extend(img_docs)

        # Add the docs to the database.
        if len(docs):
            _ = add_many_to_collection(annotations_collection, docs)

        # Get the list of unique annotation names.
        doc_names = set()
        for doc in docs:
            if doc_name := doc.get("annotation", {}).get("name"):
                doc_names.add(doc_name)

        # Return the options and the first value.
        doc_names = list(doc_names)

        return list(doc_names), doc_names[0] if len(doc_names) else None

    return [], None
