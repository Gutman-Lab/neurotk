from dash import callback, Output, Input


@callback(
    Output("resync-annotations-btn", "disabled"),
    Input("task-dropdown", "value"),
)
def resync_annotations_btn_disabled(value):
    """Disable resync annotations button if no task is selected."""
    return not (value is not None and len(value))
