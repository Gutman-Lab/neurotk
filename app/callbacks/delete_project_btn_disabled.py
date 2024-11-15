from dash import callback, Output, Input


@callback(
    Output("delete-project-btn", "disabled"), Input("project-dropdown", "value")
)
def delete_project_btn_disabled(project_id):
    # Disable delete project button if no project is selected.
    return not (project_id is not None and len(project_id))
