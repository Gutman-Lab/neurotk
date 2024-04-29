from dash import html, dcc, Input, Output, State, ALL, callback, no_update, ctx
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
import plotly.express as px
from config import AVAILABLE_CLI_TASKS, PIE_CHART_COLORS
from pathlib import Path
from collections import Counter
import pandas as pd

from utils import generate_cli_input_components
from utils.cli_functions import submit_cli_job
from utils.utils import read_xml_content, get_current_user
from utils.mongo_utils import get_mongo_client, add_one_to_collection
from utils.stores import get_project

from pprint import pprint  # NOTE: remove this when done debugging.


analysis_tab = dbc.Container(
    [
        dbc.Row(
            [
                dmc.Select(
                    label="Analysis Workflow",
                    id="cli-select",
                    data=list(AVAILABLE_CLI_TASKS.keys()),
                    style={"maxWidth": 300},
                ),
                dmc.Select(
                    label="ROI Annotation Document",
                    id="mask-name-for-cli",
                    value="gray-matter-from-xmls",
                    creatable=True,
                    searchable=True,
                    data=[{"value": "tissue", "label": "tissue"}],
                    style={"maxWidth": 300},
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dmc.Text(
                        id="selected-cli-task",
                        children=[
                            html.Div(id="cli-output"),
                            html.Div(
                                id="cli-img-count",
                                style={"fontSize": 20, "fontWeight": "bold"},
                            ),
                            html.Div(
                                [
                                    html.Button(
                                        "Run Jobs",
                                        id="cli-submit-button",
                                        className="mr-2 btn btn-warning",
                                        disabled=True,
                                    ),
                                    html.Button(
                                        "Run & Re-run Failed Jobs",
                                        id="cli-submit-button-failed",
                                        className="mr-2 btn btn-warning",
                                        disabled=True,
                                    ),
                                    html.Button(
                                        id="cli-job-cancel-button",
                                        className="mr-2 btn btn-danger",
                                        children="Cancel Running Job!",
                                        style={"display": "none"},
                                        disabled=True,
                                    ),
                                ],
                                className="d-grid gap-2 d-md-flex justify-content-md-begin",
                            ),
                        ],
                    ),
                    width=6,
                ),
                dbc.Col(
                    [
                        html.Progress(id="submitting-clis-progress", value="0"),
                        html.Div(id="submitting-clis-stats"),
                    ],
                    width=6,
                ),
            ]
        ),
    ],
)


@callback(
    Output("current-cli-params", "data"),
    [Input({"type": "dynamic-input", "index": ALL}, "value")],
    [State({"type": "dynamic-input", "index": ALL}, "id")],
)
def update_json_output(*args):
    names = args[::2]  # Take every other item starting from 0
    values = args[1::2]  # Take every other item starting from 1
    result = {value["index"]: name for name, value in zip(names[0], values[0])}

    return result


@callback(
    [
        Output("cli-submit-button", "disabled"),
        Output("cli-submit-button-failed", "disabled"),
    ],
    Input("tasks-dropdown", "value"),
    prevent_initial_call=True,
)
def toggle_cli_bn_state(selected_task):
    if selected_task:
        return False, False
    else:
        return True, True


@callback(
    [
        Output("cli-select", "value"),
        Output("cli-select", "disabled"),
        Output("mask-name-for-cli", "value", allow_duplicate=True),
        Output("mask-name-for-cli", "disabled"),
    ],
    [
        Input("tasks-dropdown", "value"),
        State("project-store", "data"),
        State("mask-name-for-cli", "data"),
    ],
    prevent_initial_call=True,
)
def select_cli_from_task(selected_task, project_store, roi_selection_data):
    """When choosing a new task, if the task has already been run then
    switch the CLI select to the correct value.
    """
    if selected_task:
        task_item = project_store["tasks"][selected_task]

        if task_item.get("cli"):
            return (
                task_item["cli"],
                True,
                task_item["roi"],
                True,
            )

    return list(AVAILABLE_CLI_TASKS.keys())[0], False, "", False


@callback(
    Output("cli-output", "children"),
    [
        Input("cli-select", "value"),
        Input("tasks-dropdown", "value"),
        State("project-store", "data"),
    ],
    prevent_initial_call=True,
)
def update_cli_input_panel(
    selected_cli_task: str, selected_task: str, project_store: dict
):
    """Update the CLI input panel. The panel is based on the selected task
    or user choice when the task has not been run yet.

    """
    path = Path("cli-xmls").joinpath(f"{selected_cli_task}.xml")
    xml_content = read_xml_content(str(path))

    # Default values to send back when on new task.
    params = {}

    # Get the project database.
    disabled = False

    if selected_task:
        # Get the task information from project store.
        task_item = project_store["tasks"][selected_task]

        if task_item.get("params"):
            # The task has been run, so get the params.
            params = task_item["params"]
            disabled = True  # UI should not have changeable params.

        return generate_cli_input_components(
            xml_content, disabled=disabled, params=params
        )

    return html.Div("Please choose a task to run CLIs.")


# @callback(
#     [
#         Output("mask-name-for-cli", "style"),
#         Output("mask-name-for-cli", "value", allow_duplicate=True),
#     ],
#     [Input("cli-select", "value")],
#     prevent_initial_call=True,
# )
# def toggle_mask_name_visibility(selected_cli):
#     """Some CLI tasks don't require an ROI / mask input. So hide it when
#     this is specified. In configs.py is where we specify this for each task."""
#     if selected_cli:
#         if AVAILABLE_CLI_TASKS[selected_cli]["roi"]:
#             return {"display": "block", "maxWidth": 300}, ""
#         else:
#             return {"display": "none", "maxWidth": 300}, ""
#     else:
#         return {"display": "none", "maxWidth": 300}, ""


@callback(
    output=[
        Output("submitting-clis-stats", "children"),
        Output("project-store", "data", allow_duplicate=True),
    ],
    inputs=[
        Input("cli-submit-button", "n_clicks"),
        Input("cli-submit-button-failed", "n_clicks"),
        State("dataview-table", "filterModel"),
        State("dataview-table", "rowData"),
        State("dataview-table", "virtualRowData"),
        State("cli-select", "value"),
        State("current-cli-params", "data"),
        State("mask-name-for-cli", "value"),
        State("projects-dropdown", "value"),
        State("tasks-dropdown", "value"),
    ],
    background=True,
    running=[
        (
            Output("cli-submit-button", "disabled"),
            True,
            False,
        ),
        (
            Output("cli-submit-button-failed", "disabled"),
            True,
            False,
        ),
        (
            Output("cli-job-cancel-button", "style"),
            {},
            {"display": "none"},
        ),
    ],
    progress=[
        Output("submitting-clis-progress", "value"),
        Output("submitting-clis-progress", "max"),
    ],
    cancel=Input("cli-job-cancel-button", "n_clicks"),
    prevent_initial_call=True,
)
def submit_cli_tasks(
    set_progress,
    n_clicks,
    n_clicked_failed,
    datatable_filtered_model: dict,
    datatable_rows: list[dict],
    datatable_filtered_rows: list[dict],
    selected_cli: str,
    cli_params: dict,
    mask_name: str,
    project_fld_id: str,
    selected_task: str,
):
    if n_clicks or n_clicked_failed:
        if ctx.triggered_id == "cli-submit-button-failed":
            rerun = True
        else:
            rerun = False
        # Get the girder client and user once to pass to every iteration.
        gc, user = get_current_user()

        kwargs = {
            "gc": gc,
            "user": user,
            "cli": selected_cli,
            "params": cli_params,
            "roi": mask_name,
            "rerun": rerun,
        }

        # Get the current task item info from mongo.
        mongo_collection = get_mongo_client()["projectStore"]

        records = list(mongo_collection.find({"_id": project_fld_id, "user": user}))

        if not all([records, records[0].get("tasks", {}).get(selected_task)]):
            return html.Div(
                "Could not find the task of interest, something is off....",
                style={"color": "red", "fontWeight": "bold", "fontSize": 20},
            )

        record = records[0]
        task_info = record["tasks"][selected_task]

        # Get the list of images.
        img_id_list = task_info.get("images", [])

        n = len(img_id_list)

        # Use filtered rows if there is a filter model.
        rows = datatable_filtered_rows if datatable_filtered_model else datatable_rows

        # Append to this list.
        for row in rows:
            if row["_id"] not in img_id_list:
                img_id_list.append(row["_id"])

        if len(img_id_list) > n:
            # New images were added.
            task_info["images"] = img_id_list

        # Add cli was already there, you don't have to add any more!
        if not task_info.get("cli"):
            # Add the cli part.
            task_info["cli"] = selected_cli
            task_info["params"] = cli_params
            task_info["roi"] = mask_name

        responses = []

        n_rows = len(rows)

        for i, row_data in enumerate(rows):
            set_progress((str(i + 1), str(n_rows)))
            kwargs["item_id"] = row_data["_id"]
            responses.append(submit_cli_job(**kwargs))

        # Push the changes to task.
        meta = {
            "cli": task_info["cli"],
            "images": task_info["images"],
            "params": task_info["params"],
            "roi": mask_name,
        }
        _ = gc.addMetadataToItem(task_info["_id"], metadata=meta)
        add_one_to_collection("projectStore", record)

        statuses = Counter([x["status"] for x in responses])

        df = []

        for k, v in statuses.items():
            df.append([k, v])

        df = pd.DataFrame(df, columns=["Status", "Count"])

        fig = px.pie(
            df,
            values="Count",
            names="Status",
            color="Status",
            color_discrete_map=PIE_CHART_COLORS,
        )
        return dcc.Graph(figure=fig), get_project(record["_id"])[0]

    return html.Div(), no_update


@callback(
    Output("cli-img-count", "children"),
    [
        Input("dataview-table", "rowData"),
        Input("dataview-table", "filterModel"),
        State("dataview-table", "virtualRowData"),
    ],
    prevent_initial_call=True,
)
def display_table_image_count(
    rows: list[dict], filter_model: dict, filtered_rows: list[dict]
) -> str:
    """Display the number of images in the table.

    Args:
        rows: The rows of the table.
        filter_model: The filter model of the table.
        filtered_rows: The filtered rows of the table.

    Returns:
        str: The message containing the number of images in the table.

    """
    n = len(filtered_rows) if filter_model else len(rows)
    return f"Will run on {n} images."


# @callback(
#     Output("mask-name-for-cli", "data"),
#     [Input("annotations-table", "rowData")],
#     prevent_initial_call=True,
# )
# def update_roi_dropdown(annotations_row_data: list[dict]) -> list[dict[str, str]]:
#     """Based on the annotations table, update the ROI dropdown."""
#     if annotations_row_data:
#         return [
#             {
#                 "label": x["Annotation Document Name"],
#                 "value": x["Annotation Document Name"],
#             }
#             for x in annotations_row_data
#         ]

#     return [{"label": "tissue", "value": "tissue"}]
#     return no_update
