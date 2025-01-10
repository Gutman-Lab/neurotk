from dash import callback, Output, Input, State, ctx
from os import getenv
from utils import get_mongo_database
from girder_client import GirderClient
from dsa_helpers.mongo_utils import add_many_to_collection


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
def update_annotation_dropdown_from_mongo(
    row_data, filter_model, virtual_row_data, user_data
):
    #
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
                {"itemId": {"$in": image_ids}},
                {"_id": 0, "annotation.name": 1},
            )
        )

        # Get the unique annotation names.
        doc_names = set([doc["annotation"]["name"] for doc in ann_docs])

        # Create the dropdown options.
        options = [name for name in doc_names]

        return options, options[0] if len(options) else None

    return [], None


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
    running=[
        (Output("resync-annotations-btn", "disabled"), True, False),
        (
            Output("resync-annotations-progress-row", "style"),
            {"display": "block"},
            {"display": "none"},
        ),
    ],
    progress=[
        Output("resync-annotations-progress", "value"),
        Output("resync-annotations-progress", "max"),
    ],
    prevent_initial_call=True,
    background=True,
)
def resync_annotations(
    set_progress, n_clicks, row_data, filter_model, virtual_row_data, user_data
):
    if n_clicks:
        set_progress(("0", "100"))

        if filter_model is not None and len(filter_model):
            row_data = virtual_row_data

        if row_data is not None and len(row_data):
            # Pull the annotations from the database.
            gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
            gc.token = user_data["token"]

            # Get the list item ids to check.
            image_ids = [row["_id"] for row in row_data]

            # Get all annotations from the database.
            annotation_collection = get_mongo_database(user_data["user"])[
                "annotations"
            ]

            # Remove all annotation documents for these images from database.
            annotation_collection.delete_many({"itemId": {"$in": image_ids}})

            ann_docs = []

            n_str = str(len(image_ids))
            set_progress(("0", n_str))

            for idx, image_id in enumerate(image_ids):
                # Get the annotations from DSA.
                ann_docs = gc.get(
                    "annotation", parameters={"itemId": image_id, "limit": 0}
                )

                for ann_doc in ann_docs:
                    if ann_doc.get("annotation", {}).get("name"):
                        ann_docs.append(ann_doc)

                set_progress((str(idx + 1), n_str))

            if len(ann_docs):
                # Update the database with the new annotations.
                _ = add_many_to_collection(annotation_collection, ann_docs)

            # Get the unique annotation names.
            doc_names = set([doc["annotation"]["name"] for doc in ann_docs])

            # Create the dropdown options.
            options = [name for name in doc_names]

            return options, options[0] if len(options) else None

    return [], None


# @callback(
#     Output("annotations-tab-content", "children", allow_duplicate=True),
#     [
#         State("images-table", "rowData"),
#         State("images-table", "filterModel"),
#         State("images-table", "virtualRowData"),
#         State(getenv("LOGIN_STORE_ID"), "data"),
#         Input("annotation-dropdown", "value"),
#     ],
#     prevent_initial_call=True,
# )
# def update_annotations_tab_content(
#     row_data, filter_model, virtual_row_data, user_data, annotation_name
# ):
#     if filter_model is not None and len(filter_model):
#         row_data = virtual_row_data

#     if row_data is not None and len(row_data):
#         # Get the list item ids to check.
#         image_ids = [row["_id"] for row in row_data]

#         # Get all annotations from the database.
#         annotation_collection = get_mongo_database(user_data["user"])[
#             "annotations"
#         ]

#         ann_docs = list(
#             annotation_collection.find(
#                 {
#                     "itemId": {"$in": image_ids},
#                     "annotation.name": annotation_name,
#                 },
#                 {"_id": 0, "itemId": 1, "annotation.name": 1},
#             )
#         )

#         # Get the number of unique item ids in the docs.
#         item_ids = set()
#         for doc in ann_docs:
#             item_ids.add(doc["itemId"])

#         # Return the string.
#         out = html.Div(
#             [
#                 html.Div(f"Images with document: {len(item_ids)}"),
#                 html.Div(
#                     f"Images without document: {len(image_ids) - len(item_ids)}"
#                 ),
#             ]
#         )

#         return out

#     return []
