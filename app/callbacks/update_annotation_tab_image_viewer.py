from dash import callback, Output, Input, State, no_update, ctx
from girder_client import GirderClient
from pprint import pprint

from utils import get_mongo_database
from utils.utils import format_geojson_doc_to_input_to_paper_fts

from os import getenv
from os.path import join


@callback(
    [
        Output("ann-tab-img-viewer", "tileSources"),
        Output("ann-tab-img-viewer", "inputToPaper"),
    ],
    [
        Input("imgs-with-ann-table", "selectedRows"),
        Input("imgs-without-ann-table", "selectedRows"),
        Input("show-ann-btn", "n_clicks"),
        State("annotation-dropdown", "value"),
        State(getenv("LOGIN_STORE_ID"), "data"),
    ],
    prevent_initial_call=True,
)
def update_ann_tab_img_viewer(
    with_doc_row, without_doc_row, _, ann_doc_name, user_data
):
    """Update the tile source property of image viewer in the annotation
    tab, based on the selected row in the last selected table.
    """
    if without_doc_row and with_doc_row:
        # If both are currently selected, then ignore the callback.
        return no_update

    if with_doc_row or without_doc_row:
        input_to_paper = {"actions": [{"type": "clearItems"}]}

        if with_doc_row:
            features = []
            row = with_doc_row[0]

            # Check the local mongo database for annotations of the selected image.
            ann_collection = get_mongo_database(user_data["user"])[
                "annotations"
            ]

            ann_docs = list(
                ann_collection.find(
                    {"itemId": row["_id"], "annotation.name": ann_doc_name}
                )
            )

            gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
            gc.token = user_data["token"]

            # Loop through each doc.
            for ann_doc in ann_docs:
                # Check if the annotation doc has geojson key.
                if "geojson" not in ann_doc:
                    # Get it from DSA.
                    geojson_doc = gc.get(
                        f"annotation/{ann_doc['_id']}/geojson"
                    )

                    # Format the geojson doc to inputToPaper.
                    features.extend(
                        format_geojson_doc_to_input_to_paper_fts(geojson_doc)
                    )

            input_to_paper["actions"].append(
                {"type": "drawItems", "itemList": features}
            )

        else:
            row = without_doc_row[0]

        # Form the tile source.
        tilesource = join(
            getenv("DSA_API_URL"),
            f"item/{row['_id']}/tiles/dzi.dzi?token={user_data['token']}",
        )

        pprint(input_to_paper)

        return [{"tileSource": tilesource}], input_to_paper

    return [], {}
