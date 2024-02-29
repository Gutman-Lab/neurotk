import dash_mantine_components as dmc
from os import getenv
from dash import html
from components.dataview import dataview

tabs = html.Div(
    dmc.Tabs(
        [
            dmc.TabsList(
                [
                    dmc.Tab("Images", value="images-tab", style={"color": "white"}),
                ],
                style={"background-color": getenv("EMORY_BLUE")},
            ),
            dmc.TabsPanel(
                dataview,
                value="images-tab",
            ),
        ],
        orientation="horizontal",
        value="images-tab",
        color=getenv("LIGHT_BLUE"),
    )
)
