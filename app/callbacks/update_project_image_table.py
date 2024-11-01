from dash import callback, Output, Input, State, no_update
from os import getenv
from utils.utils import get_project_items


@callback(
    [
        Output("project-images-table", "columnDefs", allow_duplicate=True),
        Output("project-images-table", "rowData", allow_duplicate=True),
        Output("project-images-table", "paginationGoTo"),
        Output("project-table-info", "children", allow_duplicate=True),
    ],
    [
        Input("project-dropdown", "value"),
        State(getenv("LOGIN_STORE_ID"), "data"),
    ],
    prevent_initial_call=True,
)
def update_project_images_table(project_id, user_data):
    if project_id:
        column_defs, row_data = get_project_items(project_id, user_data["user"])

        return (
            column_defs,
            row_data,
            "first",
            f"Images in the project (n={len(row_data)}):",
        )

    return [], [], no_update, ""
