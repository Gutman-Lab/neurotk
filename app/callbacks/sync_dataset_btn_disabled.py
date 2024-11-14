from dash import callback, Input, Output
from os import getenv


@callback(
    Output("sync-datasets-btn", "disabled"),
    Input(getenv("LOGIN_STORE_ID"), "data"),
)
def sync_dataset_btn_disabled(user_data):
    """If user is not logged in, the sync datasets button is disabled."""
    return not (user_data is not None and len(user_data))
