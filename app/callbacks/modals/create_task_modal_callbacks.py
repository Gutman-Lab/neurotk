from dash import callback, Output, Input, State, no_update
from os import getenv
from girder_client import GirderClient
from dsa_helpers.mongo_utils import add_many_to_collection
from utils import get_mongo_database


@callback(
    [
        Output("create-task-modal", "is_open", allow_duplicate=True),
        Output("new-task-name", "value", allow_duplicate=True),
        Output("create-task-failed", "hidden", allow_duplicate=True),
    ],
    Input("create-task-btn", "n_clicks"),
    prevent_initial_call=True,
)
def open_create_task_modal(n_clicks):
    # Open the create task modal.
    return n_clicks, "", True


@callback(
    Output("create-task-modal", "is_open", allow_duplicate=True),
    Input("close-create-task-modal", "n_clicks"),
    prevent_initial_call=True,
)
def close_create_task_modal(n_clicks):
    # Close the create task modal.
    return False if n_clicks else True


@callback(
    [
        Output("task-dropdown", "value", allow_duplicate=True),
        Output("task-dropdown", "options", allow_duplicate=True),
        Output("create-task-failed", "children", allow_duplicate=True),
        Output("create-task-failed", "hidden", allow_duplicate=True),
        Output("create-task-modal", "is_open", allow_duplicate=True),
    ],
    [
        Input("create-task-modal-btn", "n_clicks"),
        State("new-task-name", "value"),
        State("task-dropdown", "options"),
        State(getenv("LOGIN_STORE_ID"), "data"),
        State("project-dropdown", "value"),
    ],
    prevent_initial_call=True,
)
def create_task(n_clicks, task_name, task_options, user_data, project_id):
    # Create a new task.
    if n_clicks:
        if not len(task_name):
            return (
                no_update,
                no_update,
                "Task name cannot be empty.",
                False,
                True,
            )

        # Check if the task name already exists.
        if task_name in [option["label"] for option in task_options]:
            return no_update, no_update, "Task name exists.", False, True

        # Create the project on the DSA and append it to the project options in the right order.
        gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
        gc.token = user_data["token"]

        # Create task DSA item.
        task_item = gc.createItem(project_id, task_name)

        # Add task item to the tasks collection.
        task_collection = get_mongo_database(user_data["user"])["tasks"]
        _ = add_many_to_collection(task_collection, [task_item])

        # Append task to options.
        task_options.append({"label": task_name, "value": task_item["_id"]})

        # Sort by the label.
        task_options = sorted(task_options, key=lambda x: x["label"])

        return task_item["_id"], task_options, no_update, True, False

    return no_update, no_update, no_update, no_update, no_update
