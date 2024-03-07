from dash import html, dcc, Output, Input, State, callback, no_update
import dash_bootstrap_components as dbc
from dash_mantine_components import Select
from components.projects_and_tasks_tab.create_task_menu import create_task_menu
from time import sleep

from utils.utils import get_current_user
from utils.mongo_utils import get_mongo_client
from utils.stores import get_project

task_selection = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Div("Select task: ", style={"fontWeight": "bold"}),
                    align="start",
                    width="auto",
                ),
                dbc.Col(
                    html.Div(
                        Select(
                            data=[],
                            id="tasks-dropdown",
                            clearable=True,
                            placeholder="No task selected.",
                        )
                    )
                ),
                dbc.Col(
                    html.Div(
                        dbc.Button(
                            "Create task",
                            id="open-create-task-bn",
                            color="success",
                            className="me-1",
                        ),
                    ),
                    align="end",
                    width="auto",
                ),
                # dbc.Col(
                #     html.Div(
                #         dbc.Button(
                #             "Delete selected task",
                #             id="delete-task",
                #             color="danger",
                #             className="me-1",
                #         )
                #     ),
                #     align="end",
                #     width="auto",
                # ),
            ]
        ),
        create_task_menu,
    ],
    id="task-selection",
    # style={"backgroundColor": COLORS["background-secondary"]},
)


@callback(
    Output("tasks-dropdown", "value", allow_duplicate=True),
    Input("projects-dropdown", "value"),
    prevent_initial_call=True,
)
def update_task_selection(selected_project: str):
    """Update the task selection.

    Args:
        selected_project (str): The selected project.

    Returns:
        str: The selected task.

    """
    if selected_project:
        # If the project is changed - then set the task dropdown value to empty.
        return None

    return None


@callback(
    Output("tasks-dropdown", "data", allow_duplicate=True),
    # Output("tasks-dropdown", "value"),
    [
        Input("projects-dropdown", "value"),
    ],
    prevent_initial_call=True,
)
def update_task_dropdown(selected_project: str) -> list[dict[str, str]]:
    """Update the options in the task selection.

    Args:
        selected_project (str): The selected project.

    Returns:
        list[dict[str, str]]: The options for the task dropdown.

    """
    if selected_project:
        # Because changing the selected project triggers the change in project store, we need to get it directly.

        mongo_collection = get_mongo_client()["projectStore"]
        user = get_current_user()[1]

        # Bit of a hack - which waits until the mongo db is obtained.
        while not list(mongo_collection.find({"_id": selected_project, "user": user})):
            sleep(1)

        project_data = list(
            mongo_collection.find({"_id": selected_project, "user": user})
        )[0]

        options = [{"value": name, "label": name} for name in project_data["tasks"]]

        return options

    return []
    # if project_data:
    #     # Check if there is a selected task.
    #     options = [{"value": name, "label": name} for name in project_data["tasks"]]

    #     # If the change happened because we created a new task - then select that new task.
    #     if task_popup_state:
    #         return options, new_task_name

    #     # NOTE: the problem with this is that everytime the project store changes this will change.
    #     # How to deal with this? Do a different type of check.

    #     return options, None

    # return [], None


@callback(
    Output("dataview-store", "data", allow_duplicate=True),
    [
        Input("projects-dropdown", "value"),
        Input("tasks-dropdown", "value"),
        State("project-store", "data"),
    ],
    prevent_initial_call=True,
)
def update_dataview_store(
    selected_project: str, selected_task: str, project_store: dict
) -> list[dict]:
    """Update the dataview store.

    Args:
        selected_project (str): The selected project.
        selected_task (str): DSA folder id for selected task.
        project_store (dict): Data for the selected project.

    Returns:
        list[dict]: Data for the selected task.

    """
    if selected_project:
        if selected_task:
            # Find the task.
            task = None

            for task_name, task_data in project_store["tasks"].items():
                if task_name == selected_task:
                    task = task_data

            if task is None:
                raise ValueError(f"Task {selected_task} not found in project store.")

            # Check if the task has been run before.
            if "images" in task and task["images"]:
                image_ids = task["images"]

                # Pull out the image metadata for this tasks images.
                images = []

                for image_id in image_ids:
                    image = project_store["images"][image_id]
                    images.append(image)

                return images

            # If there is not task run, return the entire project images.
            return list(project_store.get("images", {}).values())
        else:
            # No task is selected so get the project.
            project = get_project(selected_project)[0]

            return list(project.get("images", {}).values())
    return []
