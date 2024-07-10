from dash import html, dcc, callback, Output, Input, State, no_update
import dash_bootstrap_components as dbc
from utils.mongo_utils import get_mongo_db, add_many_to_collection
from os import getenv
from girder_client import GirderClient

from components.tasks_panels import cli_panel, images_panel
from components.modals import create_task_modal, delete_task_modal

tasks_tab = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(html.Div("Task:", style={"fontWeight": "bold"}), width="auto"),
                dbc.Col(
                    dcc.Dropdown(
                        id="task-dropdown",
                        placeholder="Select task",
                        clearable=False,
                    ),
                    width=4,
                ),
                dbc.Col(
                    dbc.Button(
                        "Create Task",
                        id="create-task-btn",
                        className="custom-button",
                    ),
                    width="auto",
                ),
                dbc.Col(
                    dbc.Button(
                        "Delete Task",
                        color="danger",
                        id="delete-task-btn",
                    ),
                    width="auto",
                ),
            ],
            justify="start",
            align="center",
            style={"marginTop": 5, "marginLeft": 5, "marginBottom": 5},
        ),
        dcc.Tabs(
            [
                dcc.Tab(
                    label="Images",
                    value="images",
                    children=images_panel,
                    selected_className="custom-subtab--selected",
                    className="custom-subtab",
                ),
                dcc.Tab(
                    label="CLI",
                    value="cli",
                    children=cli_panel,
                    selected_className="custom-subtab--selected",
                    className="custom-subtab",
                ),
                dcc.Tab(
                    label="Results",
                    value="results",
                    children=html.Div("Results"),
                    selected_className="custom-subtab--selected",
                    className="custom-subtab",
                ),
            ],
            value="images",
            style={"marginTop": 5},
        ),
        create_task_modal,
        delete_task_modal,
    ]
)


# Callbacks
@callback(
    [
        Output("task-dropdown", "options", allow_duplicate=True),
        Output("task-dropdown", "value", allow_duplicate=True),
    ],
    [Input("project-dropdown", "value"), State("user-store", "data")],
    prevent_initial_call=True,
)
def update_task_dropdown(project_id, user_data):
    if project_id is None:
        return [], None

    # Look for tasks in database.
    project = get_mongo_db()["projects"].find_one(
        {"_id": project_id, "user": user_data["user"]}
    )

    # Look for tasks for this project.
    tasks_collection = get_mongo_db()["tasks"]

    tasks = list(
        tasks_collection.find({"project_id": project_id, "user": user_data["user"]})
    )

    if not len(tasks):
        # Pull from the DSA the tasks and add them to database.
        gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
        gc.token = user_data["token"]

        items = list(gc.listItem(project["tasks_id"]))

        # Add them to the database.
        tasks = {}

        for item in items:
            item["project_id"] = project_id

            tasks[item["_id"]] = item

        tasks = add_many_to_collection(tasks_collection, user_data["user"], tasks)

        tasks = list(tasks.values())

    options = [{"label": task["name"], "value": task["_id"]} for task in tasks]
    options = sorted(options, key=lambda x: x["label"])  # sort by label

    return options, options[0]["value"]
