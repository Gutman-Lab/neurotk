from dash import callback, Output, Input


@callback(
    Output("delete-dataset-btn", "disabled"),
    Input("dataset-dropdown", "value"),
)
def delete_dataset_btn_disabled(value):
    # Disable the dataset button if no dataset is selected.
    return not (value is not None and len(value))
