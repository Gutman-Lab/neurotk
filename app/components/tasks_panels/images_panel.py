from dash import html, dcc, callback, Output, Input, State, no_update, ctx
import dash_bootstrap_components as dbc
from dash_ag_grid import AgGrid
from utils.mongo_utils import get_mongo_db

images_table = AgGrid(
    id="images-table",
    columnDefs=[],
    rowData=[],
    enableEnterpriseModules=True,
    dashGridOptions={
        "pagination": True,
        "paginationAutoPageSize": True,
        "rowSelection": "multiple",
        "suppressRowClickSelection": True,
        "sideBar": {
            "toolPanels": [
                {
                    "id": "filters",
                    "labelDefault": "Filters",
                    "labelKey": "filters",
                    "iconKey": "filter",
                    "toolPanel": "agFiltersToolPanel",
                },
                # Include other tool panels as needed
            ],
            "defaultToolPanel": "filters",
        },
    },
    style={"height": "50vh"},
)

images_panel = html.Div(
    [
        dbc.Row(
            dcc.RadioItems(
                ["All Project Images", "Task Images", "Images not in Task"],
                inline=True,
                inputStyle={"marginLeft": 15, "marginRight": 5},
                value="All Project Images",
                id="images-radio",
            )
        ),
        images_table,
    ],
    style={"margin": 10},
)


# Callbacks
# @callback(
#     Output("images-radio", "value"),
#     [Input("task-dropdown", "value"), State("user-store", "data")],
#     prevent_initial_call=True,
# )
# def update_images_radio_options(task_id, user_data):
#     # When changing to a new task, set the value of the radio button.
#     if task_id:
#         # Look for the images in database.
#         task = get_mongo_db()["tasks"].find_one(
#             {"_id": task_id, "user": user_data["user"]}
#         )

#         images = task.get("meta", {}).get("images", [])

#         if len(images):
#             return "Task Images"
#         else:
#             return "All Experiment Images"

#     return no_update


@callback(
    [
        Output("images-table", "columnDefs", allow_duplicate=True),
        Output("images-table", "rowData"),
    ],
    [
        Input("project-images-table", "columnDefs"),
        Input("project-images-table", "rowData"),
    ],
    prevent_initial_call=True,
)
def update_images_table(columnDefs, rowData):
    # Add "filter" to each column definition.
    # for col in columnDefs:
    #     col["filter"] = "agSetColumnFilter"

    return columnDefs, rowData


@callback(
    Output("images-table", "rowData", allow_duplicate=True),
    [
        Input("images-radio", "value"),
        Input("task-dropdown", "value"),
        State("images-table", "rowData"),
        State("project-images-table", "rowData"),
        State("user-store", "data"),
    ],
    prevent_initial_call=True,
)
def update_images_table_data(
    radio_value, task_id, current_data, project_data, user_data
):
    if radio_value == "All Project Images":
        return project_data
    else:
        # Only get the images for the selected task.
        task = get_mongo_db()["tasks"].find_one(
            {"_id": task_id, "user": user_data["user"]}
        )

        task_img_ids = task.get("meta", {}).get("images", [])

        if radio_value == "Images not in Task":
            # Get the images that are not in the task.
            images = [img for img in project_data if img["_id"] not in task_img_ids]
        else:
            # Get images that are in the task
            images = [img for img in project_data if img["_id"] in task_img_ids]

        return images
