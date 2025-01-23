from dash import callback, Output, Input, State, ctx
from os import getenv
from utils import get_mongo_database


@callback(
    [
        Output("imgs-with-ann-table", "rowData"),
        Output("imgs-without-ann-table", "rowData"),
    ],
    [
        Input("annotation-dropdown", "value"),
        Input("images-table", "rowData"),
        Input("images-table", "filterModel"),
        Input("images-table", "virtualRowData"),
        Input("trigger-by-sync-ann", "data"),
        State(getenv("LOGIN_STORE_ID"), "data"),
    ],
    prevent_initial_call=True,
)
def update_task_tab_tables(
    ann_doc_name, row_data, filter_model, virtual_row_data, _, user_data
):
    """Update the tables in the task tab based on the selected annotation document."""
    if ann_doc_name and (row_data or virtual_row_data):
        # Set the row data to virtual data if there are filters.
        if filter_model is not None and len(filter_model):
            row_data = virtual_row_data

        # Get the mongo db collection for annotations.
        annotation_collection = get_mongo_database(user_data["user"])[
            "annotations"
        ]

        # If the callback was triggered by the

        # Split the images into two groups: with and without annotations.
        imgs_with_ann = []
        imgs_without_ann = []

        # Return the itemId key value for all records in the annotation collection.
        # But limit to only records that have annotation.name equal the ann_doc_name.
        image_ids_with_doc = list(
            annotation_collection.find(
                {"annotation.name": ann_doc_name}, {"itemId": 1}
            )
        )

        # Put the itemIds in a set.
        image_ids_with_doc = {image["itemId"] for image in image_ids_with_doc}

        # Loop through the row data and split the images into two groups.
        for row in row_data:
            if row["_id"] in image_ids_with_doc:
                imgs_with_ann.append(row)
            else:
                imgs_without_ann.append(row)

        return imgs_with_ann, imgs_without_ann
    return [], []
