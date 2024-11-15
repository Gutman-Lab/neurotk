from dash import callback, Output, Input


@callback(
    Output("add-dataset-btn", "disabled"),
    Input("project-dropdown", "value"),
)
def add_dataset_btn_disabled(project_id):
    # Disable the add dataset button if no project is selected.
    return not (project_id is not None and len(project_id))
