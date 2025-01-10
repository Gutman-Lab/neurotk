from dash import callback, Input, Output


@callback(
    Output("run-task-btn", "disabled"),
    [
        Input("cli-dropdown", "value"),
        Input("images-table", "rowData"),
        Input("images-table", "filterModel"),
        Input("images-table", "virtualRowData"),
    ],
)
def run_task_btn_disabled(cli_id, row_data, filter_model, virtual_row_data):
    """Disable the run task button if no CLI is selected."""
    if filter_model is not None and len(filter_model):
        row_data = virtual_row_data

    if len(row_data) and cli_id:
        return False

    return True
