from dash import callback, Output, Input, State, no_update
from os import getenv

from utils import get_mongo_database
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
def update_project_table(project_id, user_data):
    if project_id:
        # Get the list of item ids for the project.
        mongo_db = get_mongo_database(user_data["user"])

        item_ids = (
            mongo_db["projects"]
            .find_one({"_id": project_id})
            .get("meta", {})
            .get("images", [])
        )

        column_defs, row_data = get_project_items(
            item_ids, user_data["user"], token=user_data["token"]
        )

        return (
            column_defs,
            row_data,
            "first",
            f"Images in the project (n={len(row_data)}):",
        )

    return [], [], no_update, ""
