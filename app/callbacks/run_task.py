from dash import callback, Output, Input, State, ALL, no_update, dcc
from utils import get_mongo_database
from os import getenv
from dsa_helpers.mongo_utils import add_many_to_collection
from utils import cli_utils
from girder_client import GirderClient
from collections import Counter
import plotly.express as px
from config import PIE_CHART_COLOR_MAP


@callback(
    output=[
        Output("cli-dropdown", "disabled", allow_duplicate=True),
        Output(
            {"type": "dynamic-input", "index": ALL},
            "disabled",
            allow_duplicate=True,
        ),
        Output("run-task-output", "children", allow_duplicate=True),
    ],
    inputs=[
        Input("run-task-btn", "n_clicks"),
        State("images-table", "rowData"),
        State("images-table", "filterModel"),
        State("images-table", "virtualRowData"),
        State("cli-dropdown", "value"),
        State("task-dropdown", "value"),
        State(getenv("LOGIN_STORE_ID"), "data"),
        State({"type": "dynamic-input", "index": ALL}, "value"),
        State({"type": "dynamic-input", "index": ALL}, "id"),
    ],
    running=[
        (
            Output("run-task-btn", "style"),
            {"display": "none"},
            {"display": "inline"},
        ),
        (
            Output("cancel-run-task-btn", "style"),
            {"display": "inline"},
            {"display": "none"},
        ),
    ],
    cancel=[Input("cancel-run-task-btn", "n_clicks")],
    prevent_initial_call=True,
    progress=[
        Output("task-progress", "value"),
        Output("task-progress", "max"),
    ],
    background=True,
)
def run_task(
    set_progress,
    n_clicks,
    row_data,
    filter_model,
    virtual_row_data,
    cli_id,
    task_id,
    user_data,
    input_values,
    input_ids,
):
    if n_clicks:
        set_progress(("0", "100"))

        # Set the images to run based on the filters if any used.
        if filter_model is not None and len(filter_model):
            # Filters are being used.
            row_data = virtual_row_data

        # Get mongodb.
        mongodb = get_mongo_database(user_data["user"])

        # Mongo collection storing annotations.
        annotation_collection = mongodb["annotations"]

        cli_metadata = mongodb["clis"].find_one({"_id": cli_id})

        # Authenticate girder client.
        gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
        gc.token = user_data["token"]

        # Get NeuroTK collection.
        outputs_fld = gc.get(
            "resource/lookup",
            parameters={"path": "/collection/NeuroTK/Outputs"},
        )

        # Create user directory.
        user_fld = gc.createFolder(
            outputs_fld["_id"],
            user_data["user"],
            parentType="folder",
            reuseExisting=True,
            public=False,
        )

        # Setup the params.
        params = {k["index"]: v for k, v in zip(input_ids, input_values)}

        # Get task document from the database.
        task_doc = mongodb["tasks"].find_one({"_id": task_id})

        if task_doc.get("meta"):
            # Task has been previously run, add any new images to meta.
            for row in row_data:
                if row["_id"] not in task_doc["meta"]["images"]:
                    task_doc["meta"]["images"][row["_id"]] = {
                        "job_id": None,
                        "status": None,
                        "doc_id": None,
                    }
        else:
            # New task, add the metadata for the task.
            task_doc["meta"] = {
                "cli_id": cli_id,
                "cli_name": cli_metadata["name"],
                "params": params,
                "images": {
                    row["_id"]: {
                        "job_id": None,
                        "status": None,
                        "doc_id": None,
                    }
                    for row in row_data
                },
            }

        # Update DSA task item metadata.
        task_doc = gc.addMetadataToItem(task_id, task_doc["meta"])

        # Update the task document in local database.
        mongodb["tasks"].update_one({"_id": task_id}, {"$set": task_doc})

        # Local database collection for items.
        item_collection = mongodb["items"]

        items = []
        new_items = []  # track new items to update on the local database

        for row in row_data:
            # Look for the item in the db.
            item = item_collection.find_one({"_id": row["_id"]})

            if item is None:
                item = gc.getItem(row["_id"])
                new_items.append(item)

            items.append(item)

        # Update the database with the new items.
        if len(new_items):
            _ = add_many_to_collection(item_collection, new_items)

        # Get the dictionary of job ids for the items.
        images_job_info = task_doc["meta"]["images"]

        task_statuses = []  # track task status, returns from callback

        n_items = len(items)

        set_progress(("0", str(n_items)))

        # Loop through each image metadata.
        for idx, item in enumerate(items):
            item_id = item["_id"]
            job_status = images_job_info[item_id]["status"]

            if job_status is not None:
                # There is a current status for the image.
                if job_status in (
                    "Queued",
                    "Running",
                    "Inactive",
                ):
                    # Update its status.
                    job_status = cli_utils.check_job_status(
                        gc, images_job_info[item_id]["job_id"]
                    )

                    images_job_info[item_id]["status"] = job_status

                if job_status == "Success":
                    # Status says complete - double check by looking for doc.
                    doc_found, doc_id = cli_utils.look_for_doc(
                        gc, item_id, params, annotation_collection
                    )

                    if doc_found:
                        images_job_info[item_id]["doc_id"] = doc_id
                        task_statuses.append(job_status)
                        continue

                if job_status in ("Queued", "Running", "Inactive"):
                    # Still working on it.
                    task_statuses.append(job_status)
                    continue

                # Job needs to be submitted again.
                response = cli_utils.submit_cli(
                    gc,
                    cli_metadata,
                    user_data["user"],
                    params,
                    item,
                    user_fld["_id"],
                )
                response["doc_id"] = None

                # Update the job metadata.
                images_job_info[item_id] = response
                task_statuses.append(response["status"])
                continue

            # No status for the image found, look for the CLI output doc.
            doc_found, doc_id = cli_utils.look_for_doc(
                gc, item_id, params, annotation_collection
            )

            if doc_found:
                images_job_info[item_id] = {
                    "status": "Success",
                    "job_id": None,
                    "doc_id": doc_id,
                }
                task_statuses.append("Success")
                continue

            # Not found, submit.
            response = cli_utils.submit_cli(
                gc,
                cli_metadata,
                user_data["user"],
                params,
                item,
                user_fld["_id"],
            )
            response["doc_id"] = None

            images_job_info[item_id] = response
            task_statuses.append(response["status"])

            set_progress((str(idx + 1), str(n_items)))

        task_doc["meta"]["images"] = images_job_info

        mongodb["tasks"].update_one({"_id": task_id}, {"$set": task_doc})

        # Update the metadata on the DSA end.
        _ = gc.addMetadataToItem(task_id, {"images": images_job_info})

        # Disable all properties.
        set_progress(("0", "100"))

        # Count the occurrences of each status
        status_counts = Counter(task_statuses)

        # Create a pie chart using plotly.express
        fig = px.pie(
            names=list(status_counts.keys()),
            values=list(status_counts.values()),
            title="Task Status Distribution",
            color=list(status_counts.keys()),
            color_discrete_map=PIE_CHART_COLOR_MAP,
        )
        return True, ([True] * len(input_ids)), dcc.Graph(figure=fig)

    # Do not modify the disabled states.
    set_progress(("0", "100"))

    return no_update, ([no_update] * len(input_ids)), []
