from dash import html, callback, Output, Input, State
from dash_ag_grid import AgGrid
from dash_paperdragon import DashPaperdragon
from config import DASH_PAPERDRAGON_CONFIG
from dsa_helpers.dash.dash_paperdragon_utils import get_input_to_paper_dict
from utils.utils import get_mongo_database, dsa_ann_doc_to_input_to_paper

from os import getenv
from os.path import join

images_table = AgGrid(
    id="results-images-table",
    columnDefs=[],
    rowData=[],
    enableEnterpriseModules=False,
    dashGridOptions={
        "pagination": True,
        "paginationAutoPageSize": True,
        "rowSelection": "single",
    },
    style={"height": "25vh", "width": 1000},
)

img_viewer = DashPaperdragon(
    id="img-viewer",
    zoomLevel=0,
    config=DASH_PAPERDRAGON_CONFIG,
    viewportBounds={"x": 0, "y": 0, "width": 0, "height": 0},
    outputFromPaper={},
    curMousePosition={"x": 0, "y": 0},
    viewerWidth=800,
)

results_annotation_tab = html.Div(
    [images_table, img_viewer],
    style={"paddingLeft": 5, "width": "100%"},
)


@callback(
    [
        Output("results-images-table", "columnDefs"),
        Output("results-images-table", "rowData"),
    ],
    [
        Input("images-table", "rowData"),
        Input("images-table", "columnDefs"),
    ],
    prevent_initial_call=True,
)
def link_image_tables(rowData, columnDefs):
    return columnDefs, rowData


@callback(
    [Output("img-viewer", "tileSources"), Output("img-viewer", "inputToPaper")],
    [
        Input("results-images-table", "selectedRows"),
        State(getenv("LOGIN_STORE_ID"), "data"),
    ],
    prevent_initial_call=True,
)
def update_image_viewer(selected_rows, user_data):
    if selected_rows is not None and len(selected_rows):
        selected_row = selected_rows[0]

        tile_source = join(
            getenv("DSA_API_URL"),
            f'item/{selected_row["_id"]}/tiles/dzi.dzi?token={user_data["token"]}',
        )

        # Modify the shift based on the image width, this is the standard for OpenSeaDragon.
        tile_sources = [
            {
                "tileSource": str(tile_source),
                "x": 0,
                "y": 0,
                "opacity": 1,
                "tileSrcIdx": 0,
                "compositeOperation": "screen",
            }
        ]

        annotation_docs = list(
            get_mongo_database(user_data["user"])["annotations"].find(
                {"itemId": selected_row["_id"]}
            )
        )

        actions = []

        if len(annotation_docs):
            for ann_doc in annotation_docs:
                features = dsa_ann_doc_to_input_to_paper(ann_doc)

                if len(features):
                    actions.append({"type": "drawItems", "itemList": features})

        if len(actions):
            actions = [{"type": "clearItems"}] + actions

            input_to_paper = {"actions": actions}
        else:
            input_to_paper = get_input_to_paper_dict()

        return tile_sources, input_to_paper

    return "", get_input_to_paper_dict()
