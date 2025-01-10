from dash import callback, Output, Input


@callback(
    Output("delete-task-btn", "disabled"),
    Input("task-dropdown", "value"),
)
def delete_task_btn_disabled(task_id):
    """Disable delete task button if no task is selected."""
    return not (task_id is not None and len(task_id))
