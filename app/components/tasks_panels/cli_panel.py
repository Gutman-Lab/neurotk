from dash import html, dcc, callback, Output, Input, State, no_update, ALL
import dash_bootstrap_components as dbc
from pathlib import Path
from pprint import pprint
from girder_client import GirderClient
import json
from utils.cli_functions import submit_cli_job

from os import getenv
from os.path import join

from utils import generate_cli_input_components
from utils.mongo_utils import get_mongo_db, add_many_to_collection

JOB_STATUS_CODES = {
    0: "Pending",
    1: "Queued",
    2: "Running",
    3: "Complete",
    4: "Failed",
    "submit_error": "submit_error",
}

annotations_panel = dbc.Container(
    dbc.Card(
        dbc.CardBody(
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
                                options=[],
                                id="region-dropdown",
                                clearable=False,
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
                    target="region-dropdown",
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Label("Add annotation doc:"), width="auto"),
                        dbc.Col(
                            dbc.Input(
                                type="text",
                                id="add-annotation-doc-input",
                            ),
                            width="auto",
                        ),
                        dbc.Col(
                            dbc.Button(
                                "+",
                                color="success",
                                id="add-annotation-doc-btn",
                            ),
                            width="auto",
                        ),
                    ],
                    justify="start",
                    align="center",
                    style={"marginTop": 10},
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Button(
                                "Search image annotations",
                                className="custom-button",
                                id="search-annotations-btn",
                            ),
                            width="auto",
                        ),
                        dbc.Col(
                            dbc.Spinner(
                                id="searching-annotations-spinner",
                            ),
                            width="auto",
                            id="spinner-col",
                            style={"display": "none"},
                        ),
                    ],
                    justify="start",
                    align="center",
                    style={"marginTop": 10},
                ),
            ]
        )
    )
)

cli_panel = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(html.Div("CLI: "), width="auto"),
                dbc.Col(
                    dcc.Dropdown(options=[], id="cli-dropdown", clearable=False),
                    width=4,
                ),
                dbc.Col(
                    html.Div(
                        id="cli-images-count",
                        style={"marginLeft": 10, "fontWeight": "bold"},
                    ),
                    width="auto",
                ),
            ],
            justify="start",
            align="center",
        ),
        dbc.Row(
            [
                dbc.Col(html.Div(id="cli-inputs"), width=5),
                dbc.Col(annotations_panel, width=5, id="region-panel"),
            ],
            justify="start",
            style={"marginTop": 10, "marginLeft": 5, "width": "100%"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        "Run Task",
                        id="run-task-btn",
                        color="success",
                        class_name="me-1",
                    ),
                    width="auto",
                ),
                dbc.Col(
                    dbc.Button(
                        "Cancel Task",
                        id="cancel-run-task",
                        color="danger",
                        class_name="me-1",
                        style={"display": "none"},
                    ),
                    width="auto",
                ),
                dbc.Col(html.Div(id="task-progress"), width="auto"),
            ],
            justify="start",
            style={"marginTop": 10, "marginLeft": 15},
        ),
    ],
    style={"marginLeft": 10},
)


# Callbacks
@callback(
    Output("cli-dropdown", "options"),
    Input("user-store", "storage_type"),
)
def start_cli_dropdown(_):
    # Runs at the beginning of the app to load the available CLIs.
    # NOTE: This could be defined at the component level, does not need to be a callback.
    options = []

    for fp in Path("cli-xmls").iterdir():
        # Only check xml files.
        if fp.suffix == ".xml":
            # Add the CLI to the options.
            options.append({"label": fp.stem, "value": fp.stem})

    return options


@callback(
    [Output("cli-dropdown", "value"), Output("cli-dropdown", "disabled")],
    [
        Input("task-dropdown", "value"),
        State("user-store", "data"),
        State("cli-dropdown", "options"),
    ],
    prevent_initial_call=True,
)
def choose_cli_from_selected_task(task_id, user_data, cli_options):
    # If the task has a CLI run, choose the CLI from dropdown.
    if task_id and len(user_data):
        task = get_mongo_db()["tasks"].find_one(
            {"_id": task_id, "user": user_data["user"]}
        )

        cli = task.get("meta", {}).get("cli")

        if cli:
            return cli, True

    return (
        (
            cli_options[0]["value"]
            if cli_options is not None and len(cli_options)
            else None
        ),
        False,
    )


@callback(
    Output("task-store", "data", allow_duplicate=True),
    [
        Input("task-dropdown", "value"),
        State("user-store", "data"),
    ],
    prevent_initial_call=True,
)
def update_task_store(task_id, user_data):
    # Update the task store.
    task = get_mongo_db()["tasks"].find_one({"_id": task_id, "user": user_data["user"]})

    return task


@callback(
    [
        Output("cli-inputs", "children"),
        Output("region-panel", "style"),
        Output("region-dropdown", "options", allow_duplicate=True),
        Output("region-dropdown", "value", allow_duplicate=True),
        Output("region-dropdown", "disabled"),
        Output("add-annotation-doc-input", "disabled"),
        Output("add-annotation-doc-btn", "disabled"),
        Output("search-annotations-btn", "disabled"),
    ],
    [
        Input("task-store", "data"),
        State("cli-dropdown", "value"),
        State("task-dropdown", "value"),
        State("region-dropdown", "options"),
    ],
    prevent_initial_call=True,
)
def load_cli_inputs(task, cli_fp, task_id, region_options):
    # Load the appropriate UI for the CLI selected.
    # Read the XML file.
    if task_id and cli_fp is not None and len(cli_fp):
        with open(join("cli-xmls", cli_fp + ".xml"), "r") as fp:
            xml_content = fp.read().strip()

        params = task.get("meta", {}).get("params")

        components, region_flag = generate_cli_input_components(
            xml_content, params=params
        )

        display_style = {"display": "block"} if region_flag else {"display": "none"}

        region_name = task.get("meta", {}).get("roi")

        if region_flag and region_name is not None:
            # If the region is not in the options, add it.
            if region_name not in [opt["value"] for opt in region_options]:
                region_options.append({"value": region_name, "label": region_name})
        else:
            region_name = region_options[0]["value"] if len(region_options) else None

        disabled_flag = params is not None

        return (
            dbc.Container(
                dbc.Card(
                    dbc.CardBody(components),
                ),
            ),
            display_style,
            region_options,
            region_name,
            disabled_flag,
            disabled_flag,
            disabled_flag,
            disabled_flag,
        )

    return (
        [],
        no_update,
        region_options,
        region_options[0]["value"] if len(region_options) else None,
        False,
        False,
        False,
        False,
    )


@callback(
    [
        Output("region-dropdown", "options", allow_duplicate=True),
        Output("region-dropdown", "value", allow_duplicate=True),
    ],
    [
        State("project-dropdown", "value"),
        State("user-store", "data"),
        Input("project-images-table", "rowData"),
    ],
    prevent_initial_call=True,
)
def load_available_docs_for_project(project_id, user_data, project_data):
    # Load the available annotation documents for the project selected from database.
    # Get a list of item ids for the project.
    if project_id and len(project_data):
        item_ids = [item["_id"] for item in project_data]

        # Search the annotation database collection for all docs with the itemId key in the item_ids.
        db = get_mongo_db()["annotations"]

        docs = list(db.find({"itemId": {"$in": item_ids}, "user": user_data["user"]}))

        # Get the list of document names that are unique.
        options = [
            {"value": doc["annotation"]["name"], "label": doc["annotation"]["name"]}
            for doc in docs
        ]

        return options, options[0]["value"] if len(options) else None

    return [], None


@callback(
    [
        Output("cli-images-count", "children"),
        Output("run-task-btn", "disabled"),
    ],
    [
        Input("images-table", "rowData"),
        Input("images-table", "virtualRowData"),
    ],
    prevent_initial_call=True,
)
def update_cli_images_count(row_data, selected_rows):
    # Update the number of images the CLI will be run on if the "Run Task" button is clicked.
    count = 0

    if selected_rows is None:
        if row_data is not None:
            count = len(row_data)
    else:
        count = len(selected_rows)

    if count:
        return f"Images: {count}", False
    else:
        return "", True


@callback(
    [Output("task-progress", "children"), Output("task-store", "data")],
    [
        Input("run-task-btn", "n_clicks"),
        State("images-table", "rowData"),
        State("images-table", "virtualRowData"),
        State("user-store", "data"),
        State("cli-dropdown", "value"),
        State("task-dropdown", "value"),
        State({"type": "dynamic-input", "index": ALL}, "value"),
        State({"type": "dynamic-input", "index": ALL}, "id"),
    ],
    prevent_initial_call=True,
)
def run_task(
    n_clicks, row_data, selected_rows, user_data, selected_cli, task_id, *args
):
    # Run task on selected rows.
    if n_clicks:
        """NOTE: logic

        If selected rows is not None, then filters have been used. Use the
        selected row data for deciding what images to push. Otherwise use
        the row data in general.

        """
        gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
        gc.token = user_data["token"]

        # Find the task that is being run from database.
        mongo_db = get_mongo_db()
        tasks_collection = mongo_db["tasks"]
        task_record = tasks_collection.find_one(
            {"_id": task_id, "user": user_data["user"]}
        )

        # Extract the task queue dictionary.
        task_queue = task_record.get("meta", {}).get("task_queue", {})

        # Format the args, which are the CLI params.
        params = {}

        for index, value in zip(args[1], args[0]):
            params[index["index"]] = value

        # Loop through each image (row).
        rows = row_data if selected_rows is None else selected_rows

        ann_collection = mongo_db["annotations"]

        """
        JOB_STATUS_CODES = {
            0: "Pending",
            1: "Queued",
            2: "Running",
            3: "Complete",
            4: "Failed",
            "submit_error": "submit_error",
        }
        """

        for row in rows:
            # Check if the image is already in the task queue.
            if row["_id"] in task_queue:
                # Check if the task is in queue.
                if task_queue[row["_id"]]["status"] in ("Pending", "Queued", "Running"):
                    # Check its status now.
                    response = gc.get(f"job/{task_queue[row['_id']]['_id']}")

                    status = JOB_STATUS_CODES.get(response["status"], "unknown")

                    task_queue[row["_id"]] = {
                        "status": status,
                        "_id": response.get("_id"),
                    }
                else:
                    # Later will append to a list that will plot the PIE chart.
                    pass

                # Don't need to do this again.
                continue

            # Check local database for an annotation document that matches this task.
            query = {
                "itemId": row["_id"],
                "annotation.name": params["docname"],
                "annotation.attributes.cli": selected_cli,
            }

            for k, v in params.items():
                query[f"annotation.attributes.params.{k}"] = v

            doc = ann_collection.find_one(query)

            if doc is None:
                # Add all annotations that have this name to the database.
                ann_docs = gc.get(
                    f"annotation?itemId={row['_id']}&name={params['docname']}&limit=0&offset=0&sort=lowerName&sortdir=1"
                )

                if len(ann_docs):
                    _ = add_many_to_collection(
                        ann_collection,
                        user_data["user"],
                        {doc["_id"]: doc for doc in ann_docs},
                    )

                # Query the database again.
                doc = ann_collection.find_one(query)

            # If the doc is still not found, then the task needs to be submitted.
            if doc is None:
                # Submitting the job.
                response = submit_cli_job(
                    selected_cli, row["_id"], params, gc, user_data["user"]
                )

                status = JOB_STATUS_CODES.get(response["status"], "unknown")

                task_queue[row["_id"]] = {"status": status, "_id": response.get("_id")}
            else:
                # The doc was found and thus the task has been run.
                task_queue[row["_id"]] = {"status": "complete", "_id": None}

        # Update the the task item in the DSA and also in the database.
        image_ids = task_record.get("meta", {}).get("images", [])

        for r in rows:
            if r["_id"] not in image_ids:
                image_ids.append(r["_id"])

        metadata = {
            "cli": selected_cli,
            "images": image_ids,
            "params": params,
            "task_queue": task_queue,
        }

        item = gc.addMetadataToItem(task_id, metadata)

        # Update the task in the database.
        _ = tasks_collection.update_one(
            {"_id": task_id, "user": user_data["user"]},
            {"$set": {"meta": metadata}},
        )

        item["user"] = user_data["user"]

        return "Task submitted.", item

    return "", no_update
