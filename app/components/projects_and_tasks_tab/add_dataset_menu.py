import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import html, Output, Input, State, no_update, callback


add_dataset_menu = dbc.Modal(
    [
        dbc.ModalHeader("Add Dataset"),
        dbc.ModalBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dmc.Select(
                                [],
                                id="dataset-dropdown",
                                clearable=True,
                                placeholder="Select dataset.",
                                label="Select dataset:",
                            ),
                        ),
                        dbc.Col(
                            html.Button(
                                "Add",
                                id="add-dataset-bn",
                                title="add dataset to project",
                            ),
                            width="auto",
                        ),
                        dbc.Col(
                            html.Button(
                                "Refresh",
                                id="refresh-dataset-list-bn",
                                title="refresh the dataset list",
                            ),
                            width="auto",
                        ),
                    ]
                ),
                # html.Br(),
                # dmc.Textarea(
                #     placeholder="Dataset metadata.", autosize=True, id="dataset-info"
                # ),
            ]
        ),
    ],
    id="add-dataset-popup",
    is_open=False,
    fullscreen=False,
)


@callback(
    Output("add-dataset-popup", "is_open"),
    Input("add-dataset", "n_clicks"),
    prevent_initial_call=True,
)
def open_add_dataset_popup(n_clicks: int) -> bool:
    """
    Open the add dataset popup and populate the select with available
    datasets.

    Args:
        n_clicks: Number of times button has been clicked.

    Returns:
        Always returns True to open up the menu.
    """
    return True if n_clicks else False


@callback(
    Output("dataset-dropdown", "data"),
    Input("datasets-store", "data"),
    prevent_initial_call=True,
)
def populate_dataset_dropdown(data: list[dict]) -> list[dict]:
    """
    Populate the Dataset dropdown when the dataset item store changes.

    Args:
        data: List of dictionaries with metadata on the datasets.

    Returns:
        List of dictionaries with value key (id of the dataset item) and
        label key (user name and dataset name).

    """
    if data:
        # Populate the dropdown.
        return [{"value": dataset, "label": dataset} for dataset in data]

    return []


@callback(
    [
        Output("project-store", "data"),
        Output("dataview-store", "data", allow_duplicate=True),
    ],
    [
        Input("add-dataset-bn", "n_clicks"),
        State("dataset-dropdown", "value"),
        State("datasets-store", "data"),
        State("tasks-dropdown", "value"),
        State("project-store", "data"),
    ],
    prevent_initial_call=True,
)
def update_project_store(
    n_clicks: int,
    selected_dataset: str,
    datasets: dict,
    selected_task: str,
    project_store: dict,
):
    """Update the project store given I am adding this data."""
    from utils.utils import get_gc
    from utils.stores import get_project

    if n_clicks:
        # Grab the images from project store.
        for dataset in datasets:
            if dataset == selected_dataset:
                # Look for the dataset folder id.
                gc = get_gc()

                for fld in gc.listFolder(project_store["_id"]):
                    if fld["name"] == "Datasets":
                        # Get the metadata.
                        meta = fld.get("meta", {})

                        # Add the dataset to the project store.
                        meta[dataset] = datasets[dataset]["data"]

                        # Update the metadata.
                        _ = gc.addMetadataToFolder(fld["_id"], meta)

                        # Update the mongo database for project.
                        project = get_project(project_store["_id"], resync=True)[0]

                        # NOTE:
                        return project, list(project.get("images", {}).values())

    return no_update, no_update


# @callback("add-dataset-bn", "s)
