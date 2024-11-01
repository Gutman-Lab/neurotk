from dash import callback, Output, Input, State
from os import getenv
from pathlib import Path

from utils import generate_cli_input_components
from utils.utils import read_xml_content, get_mongo_database


@callback(
    [
        Output("cli-dropdown", "value"),
        Output("cli-dropdown", "disabled", allow_duplicate=True),
    ],
    [
        Input("task-dropdown", "value"),
        State("cli-dropdown", "options"),
        State(getenv("LOGIN_STORE_ID"), "data"),
    ],
    prevent_initial_call=True,
)
def set_task_cli(task_id, cli_options, user_data):
    """When the task is changed select the CLI save on this task or choose
    the first of the options task is not set yet.

    """
    if task_id is not None and len(task_id):
        # Get Mongo database.
        mongo_db = get_mongo_database(user_data["user"])

        # Get the task document.
        task_doc = mongo_db["tasks"].find_one({"_id": task_id})

        cli_id = task_doc.get("meta", {}).get("cli_id")

        if cli_id is not None:
            return cli_id, True

    if len(cli_options):
        return cli_options[0]["value"], False

    return None, False


@callback(
    [
        Output("cli-inputs", "children"),
        Output("run-task-output", "children", allow_duplicate=True),
    ],
    [
        Input("cli-dropdown", "value"),
        State(getenv("LOGIN_STORE_ID"), "data"),
        State("task-dropdown", "value"),
    ],
    prevent_initial_call=True,
)
def load_cli_inputs(cli_id, user_store, task_id):
    # Get the CLI metadata from mongodb.
    if (
        cli_id is not None
        and len(cli_id)
        and task_id is not None
        and len(task_id)
    ):
        # Get Mongo database.
        mongo_db = get_mongo_database(user_store["user"])

        # Get the task document.
        task_doc = mongo_db["tasks"].find_one({"_id": task_id})

        params = task_doc.get("meta", {}).get("params")

        cli_metadata = mongo_db["clis"].find_one({"_id": cli_id})

        # Read the XML content from local file.
        xml_content = read_xml_content(
            Path("cli-xmls") / (cli_metadata["name"] + ".xml")
        )

        inputs = generate_cli_input_components(xml_content, params=params)

        return inputs, []

    return [], []
