# Header component.
from dash import html
from os import getenv
import dash_mantine_components as dmc

header = html.Div(
    [
        html.H4(
            "NeuroTK",
            style={
                "color": getenv("COOL_GRAY_1"),
                "fontSize": 50,
                "fontWeight": "bold",
            },
        ),
        dmc.Tabs(
            [
                dmc.TabsList(
                    [
                        dmc.Tab("Images", value="images-tab", style={"color": "red"}),
                    ],
                    style={"fontColor": "red"},
                ),
                dmc.TabsPanel(
                    html.Div(
                        "Images tab content.",
                    ),
                    value="projects",
                ),
            ],
            orientation="horizontal",
            value="images-tab",
            color=getenv("LIGHT_BLUE"),
            # inverted=True,
            # variant="pills",
        ),
    ],
    style={"background-color": getenv("EMORY_BLUE"), "display": "flex"},
)
