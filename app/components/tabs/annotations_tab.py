from dash import html, dcc
import dash_bootstrap_components as dbc

import callbacks.resync_annotations_btn_disabled
import callbacks.resync_annotations

annotations_tab = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Button(
                            html.I(className="fa-solid fa-arrows-rotate"),
                            id="resync-annotations-btn",
                            className="sync-btns",
                        ),
                        dbc.Tooltip(
                            "Resync annotations from DSA.",
                            target="resync-annotations-btn",
                        ),
                    ],
                    width="auto",
                ),
                dbc.Col(html.Div("Annotation document:"), width="auto"),
                dbc.Col(
                    dcc.Dropdown(
                        options=[], value=None, id="annotation-dropdown"
                    ),
                    width=4,
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
        dbc.Row(
            [
                dbc.Col(
                    html.Div("Resyncing annotation progress:"), width="auto"
                ),
                dbc.Col(
                    html.Progress(
                        id="resync-annotations-progress",
                        value="0",
                        max="100",
                    ),
                    width=4,
                ),
            ],
            id="resync-annotations-progress-row",
            align="center",
            justify="start",
            style={"display": "none"},
        ),
        html.Div(id="annotations-tab-content"),
    ],
    style={"marginTop": 10},
)
