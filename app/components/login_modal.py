# Modal for login in.
from dash import Input, Output, State, html, callback
import dash_bootstrap_components as dbc
from girder_client import GirderClient
from os import getenv

login_modal = dbc.Modal(
    [
        dbc.ModalHeader("Log in"),
        dbc.ModalBody(
            [
                html.Div("Login or email", style={"margin": 5, "fontWeight": "bold"}),
                dbc.Input(
                    id="login",
                    type="text",
                    placeholder="Enter login",
                    style={"margin": 5},
                ),
                html.Div(
                    "Password",
                    style={"margin": 5, "marginTop": 15, "fontWeight": "bold"},
                ),
                dbc.Input(
                    id="password",
                    type="password",
                    placeholder="Enter password",
                    style={"margin": 5},
                ),
                html.Div(
                    "Login failed.",
                    hidden=True,
                    id="login-failed",
                    style={"color": "red", "fontWeight": "bold", "margin": 10},
                ),
            ],
        ),
        dbc.ModalFooter(
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            "Close",
                            id="close-login-modal",
                            className="me-1",
                            color="light",
                        )
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Login",
                            id="log-in-btn",
                            className="me-1",
                            color="primary",
                        )
                    ),
                ],
            )
        ),
    ],
    is_open=False,
    id="login-modal",
)


# Callbacks
@callback(
    Output("login-modal", "is_open", allow_duplicate=True),
    Input("login-btn", "n_clicks"),
    prevent_initial_call=True,
)
def open_login_modal(n_clicks):
    # Open the log in modal.
    return True if n_clicks else False


@callback(
    [
        Output("user-store", "data"),
        Output("login-failed", "hidden"),
        Output("login-modal", "is_open", allow_duplicate=True),
    ],
    [
        Input("log-in-btn", "n_clicks"),
        State("login", "value"),
        State("password", "value"),
    ],
    prevent_initial_call=True,
)
def login(n_clicks, login, password):
    # Try to login.
    gc = GirderClient(apiUrl=getenv("DSA_API_URL"))

    try:
        gc.authenticate(username=login, password=password)

        user = gc.get("user/me")["login"]

        return {"user": user, "token": gc.token}, True, False
    except:
        return {}, False, True


@callback(
    Output("login-modal", "is_open", allow_duplicate=True),
    Input("close-login-modal", "n_clicks"),
    prevent_initial_call=True,
)
def close_login_modal(n_clicks):
    return False if n_clicks else True
