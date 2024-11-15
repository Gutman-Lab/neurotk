from dash import callback, Output, Input


@callback(
    Output("create-task-btn", "disabled"),
    Input("project-dropdown", "value"),
)
def create_task_btn_disabled(project_id):
    """Disable create task button if no project is selected."""
    return not (project_id is not None and len(project_id))
