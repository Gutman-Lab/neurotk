import dash_mantine_components as dmc
from os import getenv
from dash import html

from components.projects_and_tasks_tab import projects_and_tasks_tab
from components.analysis_tab import analysis_tab
from components.annotations_tab import annotations_tab
from components.report_tab import report_tab

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
                    dmc.Tab("Report", value="report-tab", style={"color": "white"}),
                ],
                style={"background-color": getenv("EMORY_BLUE")},
            ),
            dmc.TabsPanel(
                projects_and_tasks_tab,
                value="projects-and-tasks-tab",
            ),
            dmc.TabsPanel(analysis_tab, value="analysis-tab"),
            dmc.TabsPanel(annotations_tab, value="annotations-tab"),
            dmc.TabsPanel(report_tab, value="report-tab"),
        ],
        orientation="horizontal",
        value="report-tab",
        color=getenv("LIGHT_BLUE"),
        variant="outline",
    )
)
