import dash_mantine_components as dmc
from os import getenv
from dash import html
from components.projects_and_tasks_tab import projects_and_tasks_tab
from components.analysis_tab import analysis_tab
from components.annotations_tab import annotations_tab

tabs = html.Div(
    dmc.Tabs(
        [
            dmc.TabsList(
                [
                    dmc.Tab(
                        "Projects & Tasks",
                        value="projects-and-tasks-tab",
                        style={"color": "white"},
                    ),
                    dmc.Tab(
                        "Analysis",
                        value="analysis-tab",
                        style={"color": "white"},
                    ),
                    dmc.Tab(
                        "Annotations", value="annotations-tab", style={"color": "white"}
                    ),
                ],
                style={"background-color": getenv("EMORY_BLUE")},
            ),
            dmc.TabsPanel(
                projects_and_tasks_tab,
                value="projects-and-tasks-tab",
            ),
            dmc.TabsPanel(analysis_tab, value="analysis-tab"),
            dmc.TabsPanel(annotations_tab, value="annotations-tab"),
        ],
        orientation="horizontal",
        value="projects-and-tasks-tab",
        color=getenv("LIGHT_BLUE"),
        variant="outline",
    )
)
