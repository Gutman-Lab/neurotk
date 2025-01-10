from dash import Output, Input, State, callback


@callback(
    Output("task_tab_project_name", "children"),
    [
        Input("project-dropdown", "value"),
        State("project-dropdown", "options"),
    ],
    prevent_initial_call=True,
)
def update_task_tab_project_name(project_id, project_dropdown_options):
    if project_id is not None and len(project_id):
        # Get the name of the project.
        for project in project_dropdown_options:
            if project["value"] == project_id:
                return project["label"]

    return ""
