from dash import html, callback, Output, Input, State, no_update
import dash_bootstrap_components as dbc
from dash_mantine_components import Select
from components.projects_and_tasks_tab.create_project_menu import create_project_menu
from utils.utils import get_gc
from utils.stores import get_project

project_selection = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        "Re-sync Project List",
                        id="resync-project-list-btn",
                        color="info",
                        style={"width": "auto"},
                        className="me-1",
                    ),
                    width="auto",
                ),
                dbc.Col(
                    html.Div("Select project: ", style={"fontWeight": "bold"}),
                    width="auto",
                ),
                dbc.Col(
                    Select(
                        data=[],
                        id="projects-dropdown",
                        placeholder="No project selected.",
                    )
                ),
                dbc.Col(
                    html.Div(
                        dbc.Button(
                            "Create project",
                            id="create-project-bn",
                            color="success",
                            className="me-1",
                        )
                    ),
                    align="end",
                    width="auto",
                ),
                # dbc.Col(
                #     html.Div(
                #         dbc.Button(
                #             "Delete selected project",
                #             id="delete-project",
                #             color="danger",
                #             className="me-1",
                #         )
                #     ),
                #     align="end",
                #     width="auto",
                # ),
            ]
        ),
        create_project_menu,
    ]
)


@callback(
    [Output("projects-dropdown", "data"), Output("projects-dropdown", "value")],
    Input("projects-dropdown-store", "data"),
    State("projects-dropdown", "value"),
    prevent_initial_call=True,
)
def update_projects_dropdown(projects: list[dict[str, str]], selected_project: str):
    """Update the content of projects dropdown."""
    # Caveat - don't change the current value of the dropdown.
    # NOTE: do I need to specify this?

    if projects:
        if selected_project:
            # There is a selected project, if this project is in the current projects then selected it.
            for project in projects:
                if selected_project == project["value"]:
                    return (
                        projects,
                        no_update,
                    )  # NOTE: might need to explicitly pass this

        # The current selected project does not exist anymore, choose the first on the list.
        return projects, projects[0]["value"]
    else:
        return [], None


@callback(
    Output("project-store", "data"),
    Input("projects-dropdown", "value"),
    prevent_initial_call=True,
)
def update_projects_store(selected_project: str):
    """Update the projects store."""
    if selected_project:
        print(selected_project)
        return get_project(selected_project)[0]

    return {}
