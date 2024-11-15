from dash import html, dcc
import dash_bootstrap_components as dbc

cli_tab = html.Div(
    dbc.Row(
        [
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader("CLI"),
                        dbc.CardBody(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(html.Div("CLI:"), width="auto"),
                                        dbc.Col(
                                            dcc.Dropdown(
                                                id="cli-dropdown",
                                                options=[],
                                                clearable=False,
                                            ),
                                            width=6,
                                        ),
                                    ],
                                    align="center",
                                    justify="start",
                                    style={"marginBottom": 10},
                                ),
                                html.Div(id="cli-inputs"),
                            ]
                        ),
                        dbc.CardFooter(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            html.Div("Progress:"), width="auto"
                                        ),
                                        dbc.Col(
                                            html.Progress(
                                                id="task-progress",
                                                max="100",
                                                value="0",
                                            ),
                                            width=4,
                                        ),
                                    ],
                                    id="task-progress-row",
                                    align="center",
                                    justify="start",
                                    style={
                                        "marginBottom": 10,
                                        "display": "none",
                                    },
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dbc.Button(
                                                "Run Task",
                                                id="run-task-btn",
                                                color="success",
                                            ),
                                            width="auto",
                                        ),
                                        dbc.Col(
                                            dbc.Button(
                                                "Cancel Task",
                                                id="cancel-run-task-btn",
                                                color="danger",
                                                style={"display": "none"},
                                            ),
                                            width="auto",
                                        ),
                                    ],
                                    justify="start",
                                    align="center",
                                ),
                                html.Div(id="test-output"),
                            ]
                        ),
                    ],
                ),
                width=6,
            ),
            dbc.Col(html.Div(id="run-task-output"), width=6),
        ]
    ),
    style={"margin": 10},
)
