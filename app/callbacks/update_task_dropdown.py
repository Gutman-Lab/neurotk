from dash import callback, Output, Input, State
from utils.utils import get_mongo_database
from os import getenv
from girder_client import GirderClient
from dsa_helpers.mongo_utils import add_many_to_collection


@callback(
    [
        Output("task-dropdown", "options", allow_duplicate=True),
        Output("task-dropdown", "value", allow_duplicate=True),
    ],
    [
        Input("project-dropdown", "value"),
        State(getenv("LOGIN_STORE_ID"), "data"),
    ],
    prevent_initial_call=True,
)
def update_task_dropdown(project_id, user_data):
    if project_id is not None and len(project_id):
        # Get mongodb.
        mongodb = get_mongo_database(user_data["user"])

        # Looks for tasks in this project.
        tasks_collection = mongodb["tasks"]
        task_docs = list(tasks_collection.find({"folderId": project_id}))

        if not len(task_docs):
            # Look for tasks from DSA.
            gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
            gc.token = user_data["token"]

            task_options = list(gc.listItem(project_id))

            if len(task_options):
                # Add these tasks to the database.
                _ = add_many_to_collection(tasks_collection, task_options)

        task_options = [
            {"label": task["name"], "value": task["_id"]} for task in task_docs
        ]

        return task_options, (
            task_options[0]["value"] if len(task_options) else None
        )

    return [], None
