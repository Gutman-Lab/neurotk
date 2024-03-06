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
        columnDefs=[],
        rowData=[],
        style={"height": "75vh", "width": "90vw"},
    )
)


# @callback(Output("dataview-table", "children"), Input("projects-store", "data"))

# @callback(Output("dataview-table", "children"), Input("projects-store", "data"))
# def update_dataview_table(data: dict):
#     """Update the dataview table."""
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
