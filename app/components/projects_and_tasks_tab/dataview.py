"""The component containing the toggle between dataview and datatable."""

import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from dash import html, Output, Input, State, callback
from components.projects_and_tasks_tab.dataview_image import dataview_images
from components.projects_and_tasks_tab.dataview_table import dataview_table
from components.projects_and_tasks_tab.add_dataset_menu import add_dataset_menu

dataview = html.Div(
    [
        add_dataset_menu,
        dmc.Tabs(
            [
                dmc.TabsList(
                    [
                        dbc.Button(
                            "Add Dataset",
                            id="add-dataset",
                            color="primary",
                            className="me-1",
                            style={"display": "none"},
                        ),
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
                    dataview_images,
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


@callback(
    Output("add-dataset", "style"),
    Input("projects-dropdown", "value"),
    prevent_initial_call=True,
)
def toggle_add_dataset_btn_visibility(selected_project: str) -> dict[str, str]:
    """Toggle the visibility of the add dataset button. This button should
    be hidden if a project is not selected.

    Args:
        selected_project (str): The selected project.

    Return:
        dict[str, str]: The style of the button.

    """
    if selected_project:
        return {"display": "block"}
    else:
        return {"display": "none"}
