"""The component containing the toggle between dataview and datatable."""

import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from dash import html
from components.dataview.dataview_table import dataview_table

dataview = html.Div(
    [
        dmc.Tabs(
            [
                dmc.TabsList(
                    [
                        dmc.Tab(
                            "Table",
                            value="dataview-table-tab",
                        ),
                        dmc.Tab(
                            "Images",
                            value="dataview-images-tab",
                        ),
                    ],
                    style={"margin-right": 10},
                ),
                dmc.TabsPanel(
                    dataview_table,
                    value="dataview-table-tab",
                ),
                dmc.TabsPanel(
                    html.Div(
                        "Dataview component.",
                    ),
                    value="dataview-images-tab",
                ),
            ],
            orientation="vertical",
            value="dataview-table-tab",
            inverted=True,
            variant="pills",
        ),
    ],
    style={"display": "flex"},
)
