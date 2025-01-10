from dash import callback, Output, Input


@callback(
    Output("run-task-count", "children"),
    [
        Input("images-table", "rowData"),
        Input("images-table", "filterModel"),
        Input("images-table", "virtualRowData"),
    ],
)
def update_run_task_count(row_data, filter_model, virtual_row_data):
    if filter_model is not None and len(filter_model):
        row_data = virtual_row_data

    if row_data is not None:
        n = len(row_data)

        if n == 1:
            return "1 image"
        else:
            return f"{len(row_data)} images"

    return "No images"
