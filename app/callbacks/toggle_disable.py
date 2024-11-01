# Callbacks for disabling and enabling components.
from dash import callback, Output, Input


@callback(
    [
        Output("task-dropdown", "disabled"),
        Output("create-task-btn", "disabled"),
        Output("delete-task-btn", "disabled"),
    ],
    [
        Input("task-dropdown", "value"),
        Input("project-dropdown", "value"),
    ],
)
def disable_task_tab_controls(task_id, project_id):
    if project_id is not None and len(project_id):
        # Project is selected.
        if task_id is not None and len(task_id):
            # Task selected.
            return False, False, False
        else:
            # No task selected.
            return False, False, True
    else:
        # No project selected.
        return True, True, True


@callback(
    Output("task_tab_content", "style"),
    Input("task-dropdown", "value"),
)
def hide_images_tab(task_id):
    if task_id is not None and len(task_id):
        return {"display": "block"}
    else:
        return {"display": "none"}


@callback(
    Output("add-dataset-btn", "disabled", allow_duplicate=True),
    Input("project-dropdown", "value"),
    prevent_initial_call=True,
)
def disable_add_dataset_btn(project_id):
    if project_id is not None and len(project_id):
        return False
    else:
        return True
