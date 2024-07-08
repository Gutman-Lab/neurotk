# Header component.
from dash import html, callback, Input, Output, State
import dash_bootstrap_components as dbc
from os import getenv
from config import COLORS
from components.login_modal import login_modal, logout_modal

header = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.H1(
                        "NeuroTK",
                        style={
                            "fontWeight": "bold",
                            "color": COLORS["COOL_GRAY_1"],
                            "marginLeft": 5,
                        },
                    ),
                    width=4,
                ),
                dbc.Col(
                    dbc.Button(
                        "Log in",
                        id="login-btn",
                        color=COLORS["EMORY_BLUE"],
                        style={"color": COLORS["YELLOW"]},
                        className="me-1",
                    ),
                    width=4,
                ),
            ],
            justify="between",
        ),
        login_modal,
        logout_modal,
    ],
    style={"backgroundColor": COLORS["EMORY_BLUE"]},
)


@callback(Output("login-btn", "children"), Input("user-store", "data"))
def check_user_store(data):
    # Check if the user store has user info or if no one is logged in.
    return data["user"] if len(data) else "Log in"


@callback(
    [
        Output("delete-dataset-btn", "disabled"),
        Output("sync-datasets-btn", "disabled"),
        Output("create-project-btn", "disabled"),
        Output("delete-project-btn", "disabled"),
    ],
    Input("user-store", "data"),
)
def disable_enable_buttons(user_data):
    # Disable buttons if the user data is not available.
    if len(user_data):
        return False, False, False, False
    else:
        return True, True, True, True
