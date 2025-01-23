from dash import callback, Output, Input
from os import getenv


@callback(
    Output("delete-dataset-btn", "disabled"),
    Input("dataset-dropdown", "value"),
)
def toggle_delete_dataset_btn(dataset_id):
    # If there is not dataset selected, disable the delete button.
    return dataset_id is None


@callback(
    Output("delete-project-btn", "disabled"),
    Input("project-dropdown", "value"),
)
def toggle_delete_project_btn(project_id):
    # If there is not project selected, disable the delete button.
    return project_id is None


@callback(
    [
        Output("add-dataset-btn", "disabled"),
        Output("create-project-btn", "disabled"),
        Output("sync-datasets-btn", "disabled"),
    ],
    Input(getenv("LOGIN_STORE_ID"), "data"),
)
def toggle_by_user_store_state(user_data):
    # If there is not user data, disable the buttons.
    if user_data is None or not len(user_data):
        return True, True, True

    return False, False, False
