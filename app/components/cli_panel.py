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
        ),
        dbc.Row(
            [],
            id="cli-inputs",
            justify="start",
            style={"marginTop": 10, "marginLeft": 5, "width": "75%"},
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

        components = generate_cli_input_components(xml_content)

        return dbc.Container(
            dbc.Card(
                dbc.CardBody(components),
            ),
        )

    return []
