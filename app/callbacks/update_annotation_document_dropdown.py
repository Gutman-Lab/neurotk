from dash import callback, Input, Output, State
from os import getenv
from utils import get_mongo_database


@callback(
    [
        Output("annotation-dropdown", "options", allow_duplicate=True),
        Output("annotation-dropdown", "value", allow_duplicate=True),
    ],
    [
        Input("images-table", "rowData"),
        Input("images-table", "filterModel"),
        Input("images-table", "virtualRowData"),
        State(getenv("LOGIN_STORE_ID"), "data"),
    ],
    prevent_initial_call=True,
)
def update_ann_doc_dropdown(
    row_data, filter_model, virtual_row_data, user_data
):
    """When the task images table changes, the available annotation
    documents shown in the dropdown menu should be updated to reflect this.
    """
    if (row_data or virtual_row_data) and user_data:
        # Set the row data to virtual data if there are filters.
        if filter_model is not None and len(filter_model):
            row_data = virtual_row_data

        # Get the annotations collection from mongodb.
        annotation_collection = get_mongo_database(user_data["user"])[
            "annotations"
        ]

        # Get the image ids from the table.
        image_ids = [row["_id"] for row in row_data]

        """Use mongo aggregation queries to speed this up when dealing 
        with large number of files. Generated with help of chatgpt."""
        available_docs = list(
            annotation_collection.aggregate(
                [
                    {
                        "$match": {
                            "itemId": {
                                "$in": image_ids
                            }  # Filter documents based on itemId
                        }
                    },
                    {
                        "$unwind": "$annotation"  # Flatten the annotation array (if it's an array)
                    },
                    # Step 3: Filter to include only `annotation.name` that is a non-empty string
                    {
                        "$match": {
                            "annotation.name": {
                                "$type": "string",  # Ensure the value is a string
                                "$ne": "",  # Exclude empty strings
                            }
                        }
                    },
                    {
                        "$group": {
                            "_id": None,  # No grouping key, we just want a list of unique values
                            "unique_annotation_names": {
                                "$addToSet": "$annotation.name"
                            },  # Collect unique names
                        }
                    },
                ]
            )
        )

        unique_names = (
            available_docs[0]["unique_annotation_names"]
            if available_docs
            else []
        )

        return unique_names, unique_names[0] if unique_names else None

    return [], None
