from dash import callback, Output, Input, State
from os import getenv
from utils.utils import get_mongo_database


@callback(
    [
        Output("images-table", "rowData", allow_duplicate=True),
        Output("images-table", "columnDefs"),
    ],
    [
        Input("images-radio", "value"),
        Input("project-images-table", "rowData"),
        Input("project-images-table", "columnDefs"),
        State("task-dropdown", "value"),
        State(getenv("LOGIN_STORE_ID"), "data"),
    ],
    prevent_initial_call=True,
)
def update_images_table_data(
    radio_value, project_data, col_defs, task_id, user_data
):
    # Update image row data when the task is changed or when the radio button is changed.
    if radio_value == "All Project Images":
        return project_data, col_defs
    else:
        # Get the mongodb task document.
        task_doc = get_mongo_database(user_data["user"])["tasks"].find_one(
            {"_id": task_id}
        )

        task_img_ids = task_doc["meta"].get("images", {})

        if radio_value == "Images not in Task":
            # Get the images that are not in the task.
            row_data = [
                img for img in project_data if img["_id"] not in task_img_ids
            ]
        else:
            # Get images that are in the task
            row_data = [
                img for img in project_data if img["_id"] in task_img_ids
            ]

        return row_data, col_defs
