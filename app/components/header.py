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
                "fontSize": 30,
                "fontWeight": "bold",
                "margin-right": 50
            },
        ),
    ],
    style={"background-color": getenv("EMORY_BLUE"), "display": "flex"},
)
