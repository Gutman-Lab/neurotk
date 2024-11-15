from dash import callback, Output, Input
from os import getenv


@callback(
    Output("create-project-btn", "disabled"),
    Input(getenv("LOGIN_STORE_ID"), "data"),
)
def create_project_btn_disabled(user_data):
    # Disable the create project button if the user is not logged in.
    return not (user_data is not None and len(user_data))
