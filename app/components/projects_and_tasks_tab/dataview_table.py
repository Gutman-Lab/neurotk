from dash_ag_grid import AgGrid
from dash import html, Output, Input, callback, State, no_update
import dash_bootstrap_components as dbc
from dash_mantine_components import Select
from girder_client import GirderClient
from os import getenv
import pandas as pd

dataview_table = dbc.Spinner(
    AgGrid(
        id="dataview-table",
        enableEnterpriseModules=True,
        columnDefs=[],
        rowData=[],
        style={"height": "75vh", "width": "90vw"},
        dashGridOptions={
            "pagination": True,
            "paginationPageSizeSelector": False,
            "animateRows": False,
        },
    )
)


@callback(
    [Output("dataview-table", "columnDefs"), Output("dataview-table", "rowData")],
    [Input("dataview-store", "data")],
    prevent_initial_call=True,
)
def update_dataview_table(data_store: list[dict]):
    """Update the dataview table."""
    # Convert to dataframe.
    df = pd.json_normalize(data_store, sep="-")

    cols = list(df.columns)

    # Always put the filename and id first.
    cols_org = []

    if "name" in cols:
        cols_org.append("name")
        cols.remove("name")

    if "_id" in cols:
        cols_org.append("_id")
        cols.remove("_id")

    cols_org.extend(cols)

    # Create col defs
    col_defs = []

    for col in cols_org:
        if col in ("_id", "name"):
            col_defs.append({"field": col})
        else:
            # Allow filtering and sorting.
            col_defs.append(
                {"field": col, "filter": "agSetColumnFilter", "sortable": True}
            )

    # Return the column defs and rows.
    return col_defs, df.to_dict("records")


#     if data:
#         # Loop through the datasets.
#         items = []

#         for dataset_name, dataset_items in data.get("datasets", {}).items():
#             items.extend(dataset_items)

#         # Format into dataframe.
#         df = pd.json_normalize(items, sep="-")

#         return AgGrid(
#             columnDefs=[{"field": col} for col in df.columns],
#             rowData=df.to_dict("records"),
#             dashGridOptions={
#                 "pagination": True,
#                 "paginationAutoPageSize": True,
#             },
#             style={"height": "75vh"},
#         )

# return AgGrid(rowData=[], columnDefs=[])
