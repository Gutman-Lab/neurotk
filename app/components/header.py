# Header component.
from dash import html, callback, Input, Output, State
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
            "project:",
            style={"margin-right": 10, "fontSize": 20, "color": getenv("COOL_GRAY_1")},
        ),
        html.P(
            "none selected...",
            id="project-name",
            style={"fontSize": 20, "color": getenv("YELLOW"), "marginRight": 20},
        ),
        html.P(
            "task:",
            style={"margin-right": 5, "fontSize": 20, "color": getenv("COOL_GRAY_1")},
        ),
        html.P(
            "none selected...",
            id="task-name",
            style={"margin-right": 20, "fontSize": 20, "color": getenv("YELLOW")},
        ),
    ],
    style={"background-color": getenv("EMORY_BLUE"), "display": "flex"},
)


@callback(
    Output("project-name", "children"),
    Input("projects-dropdown", "value"),
    State("projects-dropdown", "data"),
    prevent_initial_call=True,
)
def show_selected_project(
    selected_project: str, projects_data: list[dict[str, str]]
) -> str:
    # Find the selected project name.
    if selected_project and projects_data:
        for project_data in projects_data:
            if project_data["value"] == selected_project:
                return project_data["label"]

    return "none selected..."


@callback(Output("task-name", "children"), Input("tasks-dropdown", "value"))
def show_selected_task(selected_task: str) -> str:
    return selected_task if selected_task else "none selected..."
