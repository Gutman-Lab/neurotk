from dash import html, dcc
import dash_bootstrap_components as dbc

annotations_tab = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(html.Div("Annotation document:"), width="auto"),
                dbc.Col(
                    dcc.Dropdown(
                        options=[], value=None, id="annotation-dropdown"
                    ),
                    width=4,
                ),
                dbc.Col(
                    dbc.Button(
                        "Resync Annotations",
                        id="resync-annotations-btn",
                        className="custom-button",
                    ),
                    width="auto",
                ),
                dbc.Col(
                    dbc.Button(
                        "Cancel",
                        id="cancel-resync-annotations-btn",
                        className="custom-button",
                        style={"display": "none"},
                    ),
                    width="auto",
                ),
            ],
            justify="start",
            align="center",
            style={"marginBottom": 10},
        ),
        html.Div(id="annotations-tab-content"),
    ],
    style={"marginTop": 10},
)
