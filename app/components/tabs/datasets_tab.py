from dash import html, dcc
import dash_bootstrap_components as dbc

import callbacks.update_dataset_dropdown
import callbacks.sync_dataset_btn_disabled
import callbacks.delete_dataset_btn_disabled
import callbacks.update_dataset_table

from components.dataset_table import dataset_table
from components.modals.delete_dataset_modal import delete_dataset_modal

datasets_tab = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Button(
                            html.I(className="fa-solid fa-arrows-rotate"),
                            id="sync-datasets-btn",
                            disabled=True,
                            className="sync-btns",
                        ),
                        dbc.Tooltip(
                            "Sync datasets from DSA.",
                            target="sync-datasets-btn",
                        ),
                    ],
                    width="auto",
                ),
                dbc.Col(
                    html.Div("Dataset:", style={"fontWeight": "bold"}),
                    width="auto",
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
                    [
                        dbc.Button(
                            html.I(className="fa-solid fa-trash"),
                            id="delete-dataset-btn",
                            color="danger",
                            disabled=True,
                        ),
                        dbc.Tooltip(
                            "Delete dataset.",
                            target="delete-dataset-btn",
                        ),
                    ],
                    width="auto",
                ),
            ],
            justify="start",
            align="center",
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
