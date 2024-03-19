from dash import html, callback, Output, Input, State, no_update
import dash_bootstrap_components as dbc
from dash_ag_grid import AgGrid
import pandas as pd

from utils.mongo_utils import get_mongo_client, add_one_to_collection
from utils.utils import get_annotation_docs, get_current_user

annotations_tab = html.Div(
    [
        dbc.Button(
            "Get Annotations",
            color="primary",
            className="mr-1",
            id="get-annotations-btn",
            style={"fontSize": 30, "fontWeight": "bold", "margin": "10px"},
        ),
        AgGrid(
            id="annotations-table",
            enableEnterpriseModules=True,
            columnDefs=[
                {"field": "Annotation Document Name"},
                {"field": "Image Count"},
            ],
            rowData=[],
            # style={"height": "75vh", "width": "90vw"},
            dashGridOptions={
                "pagination": True,
                "paginationPageSizeSelector": False,
                "animateRows": False,
            },
            style={"height": "80vh", "width": "33vw"},
        ),
    ]
)


@callback(
    output=Output("annotations-table", "rowData"),
    inputs=[
        Input("get-annotations-btn", "n_clicks"),
        State("dataview-table", "rowData"),
        State("dataview-table", "filterModel"),
        State("dataview-table", "virtualRowData"),
    ],
)
def update_annotations_table(
    n_clicks: int,
    dataview_rows: list[dict],
    filter_model: dict,
    dataview_virtual_rows: list[dict],
) -> list[dict]:
    if n_clicks:
        # Logic: get the available annotations on the images selected on the table.
        rows = dataview_virtual_rows if filter_model else dataview_rows

        if rows:
            mongo_collection = get_mongo_client()["annotations"]

            gc, user = get_current_user()

            # Get name of each annotation documents, and unique item ids.
            annotations = {}

            for r in rows:
                # Check if annotations are available for this item, then return.
                docs = list(mongo_collection.find({"itemId": r["_id"]}))

                if not docs:
                    # Get the annotation docs from DSA.
                    name = get_annotation_docs(gc, r["_id"])

                # Get the annotation docs for this item.
                for doc in docs:
                    name = doc.get("annotation", {}).get("name")

                    if name:
                        # Add doc to mongo collection.
                        doc["user"] = user
                        add_one_to_collection("annotations", doc)

                        if name not in annotations:
                            annotations[name] = set()

                        annotations[name].add(r["_id"])

            # Now format the data.
            data = []

            for k, v in annotations.items():
                data.append([k, len(list(v))])

            df = pd.DataFrame(data, columns=["Annotation Document Name", "Image Count"])

            return df.to_dict("records")

    return []
