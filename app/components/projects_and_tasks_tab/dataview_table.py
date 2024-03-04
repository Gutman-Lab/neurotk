from dash_ag_grid import AgGrid
from dash import html, Output, Input, callback, State, no_update
import dash_bootstrap_components as dbc
from dash_mantine_components import Select
from girder_client import GirderClient
from os import getenv
import pandas as pd

dataview_table = dbc.Spinner(
    html.Div(
        id="dataview-table",
        style={"width": "90vw"},
    )
)


@callback(Output("projects-store", "data"), Input("projects-dropdown", "value"))
def update_projects_store(selected_project: str):
    """Update the projects store."""
    if selected_project:
        # Get the info from the project store.
        gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
        gc.authenticate(apiKey=getenv("DSA_API_TOKEN"))

        data = {"datasets": {}, "tasks": {}}

        # List the information in this DSA folder.
        for fld in gc.listFolder(selected_project):
            if fld["name"] == "Datasets":
                # This should be folder metadata.
                data["datasets"] = fld.get("meta", {})
            elif fld["name"] == "Tasks":
                # List the items, which are the task info.
                for item in gc.listItem(fld["_id"]):
                    data["tasks"][item["name"]] = item.get("meta", {})

        return data

    return {}


@callback(Output("dataview-table", "children"), Input("projects-store", "data"))
def update_dataview_table(data: dict):
    """Update the dataview table."""
    if data:
        # Loop through the datasets.
        items = []

        for dataset_name, dataset_items in data.get("datasets", {}).items():
            items.extend(dataset_items)

        # Format into dataframe.
        df = pd.json_normalize(items, sep="-")

        return AgGrid(
            columnDefs=[{"field": col} for col in df.columns],
            rowData=df.to_dict("records"),
            dashGridOptions={
                "pagination": True,
                "paginationAutoPageSize": True,
            },
            style={"height": "75vh"},
        )

    return AgGrid(rowData=[], columnDefs=[])
