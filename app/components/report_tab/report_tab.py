from dash import html, callback, Output, Input, no_update, State
import dash_bootstrap_components as dbc

from components.report_tab.ppc_report import ppc_report

from utils.mongo_utils import get_mongo_client
from utils.utils import get_current_user
from utils.cli_functions import check_for_doc

report_tab = html.Div(
    [
        html.Div(
            [
                dbc.Button(
                    "Load Report",
                    id="load-report-btn",
                    color="primary",
                    className="mb-3",
                    style={"margin-left": 10},
                ),
                html.Progress(
                    id="results-progress", value="0", style={"margin-left": 10}
                ),
            ],
            style={"display": "flex"},
        ),
        html.Div(id="report-content"),
    ]
)


@callback(Output("load-report-btn", "disabled"), Input("cli-select", "disabled"))
def disable_load_report_btn(cli_disabled: bool):
    """Disable the load report button when the CLI select is not disabled.

    Args:
        cli_disabled (bool): Whether the CLI select is disabled.

    Returns:
        bool: Whether the load report button should be disabled.

    """
    return not cli_disabled


@callback(
    output=Output("report-store", "data"),
    inputs=[
        Input("load-report-btn", "n_clicks"),
        State("cli-select", "value"),
        State("dataview-table", "rowData"),
        State("dataview-table", "filterModel"),
        State("dataview-table", "virtualRowData"),
        State("current-cli-params", "data"),
    ],
    suppress_initial_call=True,
    background=True,
    progress=[Output("results-progress", "value"), Output("results-progress", "max")],
)
def update_report_store(
    set_progress,
    n_clicks: int,
    selected_cli: str,
    dataview_rows: list[dict],
    filter_model: dict,
    dataview_virtual_rows: list[dict],
    cli_params,
):
    """Update the report panel based on the data and CLI selected.

    Args:
        n_clicks (int): The number of times the button has been clicked.
        selected_cli (str): The selected CLI.

    """
    if n_clicks and selected_cli == "PositivePixelCount":
        # Get the current selected images in the datatable.
        rows = dataview_virtual_rows if filter_model else dataview_rows

        mongo_collection = get_mongo_client()["annotations"]
        gc, user = get_current_user()

        # Add CLI results to the a dictionary.
        data = []

        total = len(rows)
        for i, r in enumerate(rows):
            record = check_for_doc(
                mongo_collection, gc, r["_id"], "Positive Pixel Count", user
            )

            if record:
                # Get the results.
                results = (
                    record.get("annotation", {}).get("attributes", {}).get("stats")
                )

                if results:
                    r["results"] = results
                    data.append(r)

            set_progress((str(i), str(total)))

        return data

    return []


@callback(
    Output("report-content", "children"),
    [
        Input("report-store", "data"),
        State("cli-select", "value"),
    ],
    prevent_initial_call=True,
)
def load_report_panel(results_store: list[dict], selected_cli: str):
    """Return the report panel."""
    if selected_cli == "PositivePixelCount":
        return ppc_report

    return []
