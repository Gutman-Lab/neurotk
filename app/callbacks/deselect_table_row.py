from dash import callback, Input, Output, State, ctx, no_update


@callback(
    [
        Output("imgs-with-ann-table", "selectedRows", allow_duplicate=True),
        Output("imgs-without-ann-table", "selectedRows", allow_duplicate=True),
    ],
    [
        Input("imgs-with-ann-table", "selectedRows"),
        Input("imgs-without-ann-table", "selectedRows"),
    ],
    prevent_initial_call=True,
)
def deselect_a_row(table1, table2):
    if table2 and table1:
        if ctx.triggered_id == "imgs-with-ann-table":
            return no_update, []
        else:
            return [], no_update

    return no_update, no_update
