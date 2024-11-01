from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_ag_grid import AgGrid
from components.modals import delete_dataset_modal

dataset_table = AgGrid(
    id="dataset-table",
    columnDefs=[],
    rowData=[],
    enableEnterpriseModules=True,
    dashGridOptions={
        "pagination": True,
        "paginationAutoPageSize": True,
    },
    style={"height": "50vh"},
)

datasets_tab = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Div("Dataset:", style={"fontWeight": "bold"}), width="auto"
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="dataset-dropdown",
                        placeholder="Select dataset",
                        clearable=False,
                    ),
                    width=4,
                ),
                dbc.Col(
                    dbc.Button(
                        "Sync Datasets",
                        id="sync-datasets-btn",
                        className="custom-button",
                        disabled=True,
                    ),
                    width="auto",
                ),
                dbc.Col(
                    dbc.Button(
                        "Delete Dataset",
                        id="delete-dataset-btn",
                        color="danger",
                        disabled=True,
                    ),
                    width="auto",
                ),
            ],
            justify="start",
            align="center",
            style={"marginTop": 5, "marginLeft": 5},
        ),
        dcc.Tabs(
            [
                dcc.Tab(
                    label="Images",
                    value="images_table",
                    children=dataset_table,
                    selected_className="custom-subtab--selected",
                    className="custom-subtab",
                ),
                dcc.Tab(
                    label="Filters",
                    value="dataset_filters",
                    children=html.Div(id="dataset-filters"),
                    selected_className="custom-subtab--selected",
                    className="custom-subtab",
                ),
            ],
            value="images_table",
            style={"marginTop": 5},
        ),
        delete_dataset_modal,
    ],
    style={"margin": 10},
)
