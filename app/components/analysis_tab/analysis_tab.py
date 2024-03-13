from dash import html

"""
The analysis tab / frame. This div contains the CLI tab, the HistomicsUI iFrame,
and the reports tab - unsure what kind of UI these will be in.
"""
from dash import html, dcc, Input, Output, State, ALL, callback, no_update, ctx
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from typing import List
from pandas import DataFrame
import plotly.express as px
from config import AVAILABLE_CLI_TASKS
from pathlib import Path
from pprint import pprint

from utils.cli_functions import submit_cli_job
from utils.utils import read_xml_content, get_current_user
from utils import generate_cli_input_components

# Constants
CLI_SELECTOR_STYLE = {
    "marginLeft": "30px",
    # "backgroundColor": COLORS["background-secondary"],
}
# CARD_CLASS = "mb-3"
# MT3_CLASS = "mt-3"
CLI_OUTPUT_STYLE = {
    "border": "1px solid #ddd",
    "padding": "10px",
    "marginTop": "10px",
    "borderRadius": "5px",
    "boxShadow": "2px 2px 12px #aaa",
    # "backgroundColor": COLORS["background-secondary"],
}


cli_button_controls = html.Div(
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
            # disabled=True,
            style={"display": "none"},
        ),
    ],
    className="d-grid gap-2 d-md-flex justify-content-md-begin",
    # style={"backgroundColor": COLORS["background-secondary"]},
)


def create_cli_selector():
    return dbc.Container(
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
                        data=[
                            "",
                            "gray-matter-from-xmls",
                            "gray-matter-fixed",
                            "tissue",
                            "tissueV2",
                            "tissue-unet",
                        ],
                        style={"maxWidth": 300},
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dmc.Text(
                            id="selected-cli-task",
                            children=[html.Div(id="cli-output"), cli_button_controls],
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        [
                            html.Progress(id="submitting-clis-progress", value="0"),
                            html.Div(id="submitting-clis-stats"),
                        ],
                        # [
                        #     html.Div(
                        #         [
                        #             html.Div("Submitting jobs progress:"),
                        #             dbc.Progress(
                        #                 value=0,
                        #                 id="submitting-clis-progress",
                        #                 style={
                        #                     "width": "50%",
                        #                     "margin-left": 10,
                        #                 },
                        #             ),
                        #         ],
                        #         id="progress-div",
                        #         style={"display": "none"},
                        #     ),
                        #     html.Div(id="submitting-clis-stats"),
                        # ],
                        width=6,
                    ),
                ]
            ),
        ],
        style=CLI_SELECTOR_STYLE,
    )


analysis_tab = dbc.Container(
    [
        dbc.Row(create_cli_selector()),
    ]
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
        Output("mask-name-for-cli", "value"),
        Output("mask-name-for-cli", "disabled"),
    ],
    [Input("tasks-dropdown", "value"), State("project-store", "data")],
    prevent_initial_call=True,
)
def select_cli_from_task(selected_task, project_store):
    """When choosing a new task, if the task has already been run then
    switch the CLI select to the correct value.
    """
    if selected_task:
        task_item = project_store["tasks"][selected_task]

        if task_item.get("cli"):
            return task_item["cli"], True, task_item["roi"], True

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


@callback(
    Output("mask-name-for-cli", "style"),
    [Input("cli-select", "value")],
    prevent_initial_call=True,
)
def toggle_mask_name_visibility(selected_cli):
    """Some CLI tasks don't require an ROI / mask input. So hide it when
    this is specified. In configs.py is where we specify this for each task."""
    if selected_cli:
        if AVAILABLE_CLI_TASKS[selected_cli]["roi"]:
            return {"display": "block", "maxWidth": 300}
        else:
            return {"display": "none", "maxWidth": 300}
    else:
        return {"display": "none", "maxWidth": 300}


@callback(
    output=Output("submitting-clis-stats", "children"),
    inputs=[
        Input("cli-submit-button", "n_clicks"),
        Input("cli-submit-button-failed", "n_clicks"),
        State("dataview-table", "rowData"),
        State("cli-select", "value"),
        State("current-cli-params", "data"),
        State("mask-name-for-cli", "value"),
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
    dataview_table_rows,
    selected_cli: str,
    cli_params: dict,
    mask_name: str,
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

        responses = []

        # NOTE: For debugging, only run the first 10 rows.
        dataview_table_rows = dataview_table_rows[:10]

        n_rows = len(dataview_table_rows)

        for i, row_data in enumerate(dataview_table_rows):
            set_progress((str(i + 1), str(n_rows)))
            kwargs["item_id"] = row_data["_id"]
            response = responses.append(submit_cli_job(**kwargs))

            # v = (i + 1) / n_rows * 100
            # set_progress((v, f"{v:.2f}%"))

            responses.append(response)

    return html.Div("Hello World")


# @callback()
#         print(selected_task)

#     # Decide if the UI should be in disabled or enabled.
#     # if selected_task:
#     #     task = task_store.get(selected_task)

#     #     if task is None:
#     #         raise Exception("Selected task is not in task store, there is a BUG!")

#     #     meta = task.get("meta", {})

#     #     if meta.get("images"):
#     #         if "params" not in meta:
#     #             raise Exception(
#     #                 "Images list saved to task without params, this is a BUG!"
#     #             )

#     #         params = meta["params"]

#     #         disabled = False  ## CHANGED LOGIC
#     #     else:
#     #         disabled = False
#     # else:
#     #     disabled = False

#     dsa_cli_task_layout = generate_cli_input_components(
#         xml_content, disabled=False, params=params
#     )

#     return [dsa_cli_task_layout]


### Update this cliItems from the main table data.
## TO DO-- DO NOT ALLOW THE CLI TO bE SUBMITTED IF THERE ARE NO ACTUAL]
## ITEMS TO RUN.. its confusing..
# @callback(Output("cliItems_store", "data"), Input("filteredItem_store", "data"))
# def updateCliTasks(filtered_store):
#     # If the task is selected, but there is not filtered item store. Then
#     return filtered_store if filtered_store else []


# @callback(
#     Output("cliItemStats", "children"),
#     Input("cliItems_store", "data"),
# )
# def displayImagesForCLI(data):
#     # print(len(data), "items in imagelist..")
#     ## This gets the data from the itemSet store, it really needs to be the
#     ## filtered version based on the task you are trying to run, will be integrated
#     ## This is what I will dump in the imagelist for now.. will expand over time
#     outputData = "Should show item count..."
#     if data:
#         ## TO DO ... ADD SOME MORE MATH TO DISPLAY OTHER PROPERTIES
#         return html.Div(f"Items in Task List: {len(data)} ")
#     else:
#         return html.Div()


# @callback(
#     [
#         Output("cli-select", "value"),
#         Output("mask-name-for-cli", "value"),
#         Output("cli-select", "disabled"),
#         Output("mask-name-for-cli", "disabled"),
#     ],
#     [Input("tasks-dropdown", "value"), Input("task-store", "data")],
# )
# def select_task_cli(selected_task, task_store):
#     """When choosing a new task, if the task has already been run then
#     switch the CLI select to the correct value.
#     """
#     if selected_task:
#         task = task_store.get(selected_task)

#         if task is None:
#             raise Exception("Selected task is not in task store, there is a BUG!")

#         # Set the cli select and annotation mask dropdown to options if needed.
#         meta = task.get("meta", {})

#         if meta.get("images"):
#             return meta["cli"], meta["roi"], True, True

#     return no_update, no_update, False, False


# @callback(
#     Output("curCLI_params", "data"),
#     [Input({"type": "dynamic-input", "index": ALL}, "value")],
#     [State({"type": "dynamic-input", "index": ALL}, "id")],
# )
# def update_json_output(*args):
#     names = args[::2]  # Take every other item starting from 0
#     values = args[1::2]  # Take every other item starting from 1
#     result = {value["index"]: name for name, value in zip(names[0], values[0])}
#     return result


# @app.long_callback(
#     output=[
#         # Output("cli-output-status", "children"),
#         Output("task-store", "data", allow_duplicate=True),
#         Output("taskJobQueue_store", "data"),
#         Output("task-pie-chart", "style"),
#         Output("task-pie-chart", "figure"),
#     ],
#     inputs=[
#         Input("cli-submit-button", "n_clicks"),
#         State("curCLI_params", "data"),
#         State("cliItems_store", "data"),
#         State("mask-name-for-cli", "value"),
#         State("tasks-dropdown", "value"),
#         State("task-store", "data"),
#         State("cli-select", "value"),
#     ],
#     running=[
#         (Output("cli-submit-button", "disabled"), True, False),
#         (Output("cli-job-cancel-button", "disabled"), False, True),
#         (
#             Output("job-submit-progress-bar", "style"),
#             {"visibility": "visible", "width": "25vw"},
#             {"visibility": "visible", "width": "25vw"},
#         ),
#     ],
#     cancel=[Input("cli-job-cancel-button", "n_clicks")],
#     progress=[
#         Output("job-submit-progress-bar", "value"),
#         Output("job-submit-progress-bar", "label"),
#         Output("job-submit-progress-bar", "max"),
#     ],
#     prevent_initial_call=True,
# )
# def submitCLItasks(
#     set_progress,
#     n_clicks: int,
#     curCLI_params: dict,
#     itemsToRun: List[dict],
#     maskName: str,
#     selected_task: str,
#     task_store: List[dict],
#     selected_cli: str,
# ):
#     """
#     Submit a CLI task - though right now this will only work with ppc.

#     Args:
#         n_clicks: This is the button to submit CLI task. Check if positive to run.
#         curCLI_params: Dictionary of the params in the CLI panel.
#         itemsToRun: List of DSA items to run.
#         maskName: Name of mask which is used to determine the region to run CLI on.
#         selected_task: CLI is tied to a task, this is the current selected task.
#         task_store: Selected task is just the task name, not the id of it. The id is
#             stored in the task_store.

#     """
#     if n_clicks:
#         task_id = None

#         for task in task_store:
#             if selected_task == task:
#                 task_id = task_store[task]["_id"]
#                 break

#         if not task_id:
#             raise Exception("Task not found in task store, but alert.")

#         # Submit metadata to the task.
#         task_metadata = {
#             "images": [item["_id"] for item in itemsToRun],
#             "cli": selected_cli,
#             "params": curCLI_params,
#             "roi": maskName,
#         }

#         item = gc.addMetadataToItem(task_id, metadata=task_metadata)

#         # Update this item on the task store.
#         task_store[item["name"]] = item

#         # Submit the jobs
#         jobSubmitList = []
#         n_jobs = len(itemsToRun)

#         print(f"This is the selected task: {selected_cli}")
#         for i, item in enumerate(itemsToRun):
#             if selected_cli == "PositivePixelCount":
#                 jobOutput = submit_ppc_job(item, curCLI_params, maskName)
#             elif selected_cli in ("TissueSegmentation", "TissueSegmentationV2"):
#                 jobOutput = submit_tissue_detection(item, curCLI_params, selected_cli)
#             elif selected_cli == "NFTDetection":
#                 jobOutput = submit_nft_inference(item, curCLI_params, maskName)
#             else:
#                 raise Exception(f"{selected_cli} does not have a submit function!")

#             jobSubmitList.append(jobOutput)

#             jobStatuspercent = ((i + 1) / n_jobs) * 100

#             set_progress((str(i + 1), f"{jobStatuspercent:.2f}%", n_jobs))

#         submissionStatus = [x["status"] for x in jobSubmitList]

#         # Get the job status for every job.
#         currentJobStatusInfo = []

#         for x in jobSubmitList:
#             if x.get("girderResponse") is None:
#                 currentJobStatusInfo.append("unknown")
#             else:
#                 currentJobStatusInfo.append(
#                     x.get("girderResponse").get("status", "no status found")
#                 )

#         # Convert the current job status info into a dataframe for graphing
#         df = []

#         for status in currentJobStatusInfo:
#             if status == "JobSubmitFailed":
#                 df.append(["Broken Image", -1, 1])
#             elif status == 0:
#                 df.append(["Inactive", status, 1])
#             elif status == 1:
#                 df.append(["Queued", status, 1])
#             elif status == 2:
#                 df.append(["Running", status, 1])
#             elif status == 3:
#                 df.append(["Complete", status, 1])
#             elif status == 4:
#                 df.append(["Fail", status, 1])
#             else:
#                 df.append(["Unknown", status, 1])

#         df = DataFrame(df, columns=["Label", "Status Code", "Counts"])

#         fig = px.pie(df, values="Counts", names="Label", hole=0.3)

#         return task_store, jobSubmitList, {"visibility": "visible"}, fig


# @callback(
#     Output("projectItem_store", "data", allow_duplicate=True),
#     Input("cli-submit-button", "n_clicks"),
#     [
#         State("projects-dropdown", "data"),
#         State("projects-dropdown", "value"),
#     ],
#     prevent_initial_call=True,
# )
# def update_task_list(n_clicks, available_projects, project_id):
#     if n_clicks:
#         # Update the project list.
#         projectItemSet = []

#         for project in available_projects:
#             if project["value"] == project_id:
#                 projectName = project["label"]

#                 projectItemSet = getProjectDataset(
#                     projectName, project_id, forceRefresh=True
#                 )

#                 return projectItemSet


# @callback(
#     Output("cli-submit-button", "disabled"),
#     Input("tasks-dropdown", "value"),
#     State("task-store", "data"),
# )
# def toggle_cli_bn_state(selected_task, task_store):
#     """
#     Disable the submit CLI button when no task is selected.
#     """
#     if selected_task:
#         # There is a task selected, get this task.
#         task = task_store.get(selected_task)

#         if task is None:
#             raise Exception("Selected task is not in task store, there is a BUG!")

#         # DEBUG - always return False
#         return False

#         # # Check the metadata for images - if it exists then the button should disable.
#         # if task.get("meta", {}).get("images"):
#         #     return True
#         # else:
#         #     return False

#     return True
