from dash import html, dcc, callback, Output, Input, State, no_update
import dash_bootstrap_components as dbc
from pathlib import Path
from utils import generate_cli_input_components

cli_panel = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(html.Div("CLI: "), width="auto"),
                dbc.Col(dcc.Dropdown(options=[], id="cli-dropdown"), width=4),
            ],
            justify="start",
            align="center",
        ),
        dbc.Row(
            [
                dbc.Col(html.Div(id="cli-inputs"), width=5),
                dbc.Col(
                    [
                        html.H4(
                            "Analysis Region (Annotation Doc)",
                            className="card-title",
                            style={
                                "textAlign": "center",
                                "marginBottom": 10,
                                "marginTop": 10,
                            },
                        ),
                        dbc.Row(
                            [
                                dbc.Col(html.Label("Region Annotation:"), width="auto"),
                                dbc.Col(
                                    dcc.Dropdown(
                                        options=[
                                            {"value": "default", "label": "default"}
                                        ],
                                        value="default",
                                        id="region-dropdown",
                                    ),
                                    width=4,
                                ),
                            ],
                            justify="start",
                            align="center",
                            style={"marginTop": 10},
                        ),
                        dbc.Tooltip(
                            "Annotation documents to use as analysis region.",
                            target={"type": "dynamic-input", "index": "region"},
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Label("Add annotation doc:"), width="auto"
                                ),
                                dbc.Col(dbc.Input(type="text"), width="auto"),
                                dbc.Col(dbc.Button("+", color="success"), width="auto"),
                            ],
                            justify="start",
                            align="center",
                            style={"marginTop": 10},
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Button(
                                            "Search image annotations",
                                            className="custom-button",
                                        ),
                                        dbc.Spinner(id="searching-annotations-spinner"),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    width=5,
                ),
            ],
            justify="start",
            style={"marginTop": 10, "marginLeft": 5, "width": "100%"},
        ),
    ],
    style={"marginLeft": 10},
)


# Callbacks
@callback(
    [
        Output("cli-dropdown", "options"),
        Output("cli-dropdown", "value"),
    ],
    Input("user-store", "storage_type"),
)
def start_cli_dropdown(_):
    # Runs at the beginning of the app to load the available CLIs.
    options = []

    for fp in Path("cli-xmls").iterdir():
        # Only check xml files.
        if fp.suffix == ".xml":
            # Add the CLI to the options.
            cli_name = fp.stem

            options.append({"label": fp.stem, "value": str(fp)})

    return options, options[0]["value"] if len(options) else None


@callback(
    Output("cli-inputs", "children"),
    Input("cli-dropdown", "value"),
    prevent_initial_call=True,
)
def load_cli_inputs(cli_fp):
    # Load the appropriate UI for the CLI selected.
    # Read the XML file.
    if len(cli_fp):
        with open(cli_fp, "r") as fp:
            xml_content = fp.read().strip()

        components, region_flag = generate_cli_input_components(xml_content)

        # return components
        if region_flag:
            components.extend(
                [
                    dbc.Row(
                        [
                            dbc.Col(html.Label("Region Annotation:"), width="auto"),
                            dbc.Col(
                                dcc.Dropdown(
                                    options=[{"value": "default", "label": "default"}],
                                    value="default",
                                    id={"type": "dynamic-input", "index": "region"},
                                ),
                                width=4,
                            ),
                        ],
                        justify="start",
                        align="center",
                        style={"marginTop": 10},
                    ),
                    dbc.Tooltip(
                        "Annotation documents to use as analysis region.",
                        target={"type": "dynamic-input", "index": "region"},
                    ),
                ]
            )

        return dbc.Container(
            dbc.Card(
                dbc.CardBody(components),
            ),
        )

    return []
