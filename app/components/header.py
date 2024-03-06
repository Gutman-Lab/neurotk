# Header component.
from dash import html
from os import getenv
from utils.utils import get_current_user

header = html.Div(
    [
        html.H4(
            "NeuroTK",
            style={
                "color": getenv("COOL_GRAY_1"),
                "fontSize": 30,
                "fontWeight": "bold",
                "margin-right": 50,
            },
        ),
        html.P(
            f"user: {get_current_user()[1]}",
            style={"margin-right": 20, "fontSize": 20, "color": getenv("COOL_GRAY_1")},
        ),
        html.P(
            "task:",
            style={"margin-right": 5, "fontSize": 20, "color": getenv("COOL_GRAY_1")},
        ),
        html.P(
            "none selected...",
            id="task-name",
            style={"margin-right": 20, "fontSize": 20, "color": getenv("COOL_GRAY_1")},
        ),
        html.P(
            "project:",
            style={"margin-right": 20, "fontSize": 20, "color": getenv("COOL_GRAY_1")},
        ),
        html.P(
            "none selected...",
            id="project-name",
            style={"fontSize": 20, "color": getenv("COOL_GRAY_1")},
        ),
    ],
    style={"background-color": getenv("EMORY_BLUE"), "display": "flex"},
)
