from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
from girder_client import GirderClient, HttpError
from os import getenv
from utils.mongo_utils import get_mongo_db, add_many_to_collection
from components.modals import delete_dataset_modal
from dash_ag_grid import AgGrid
from pandas import json_normalize
import json

dataset_table = AgGrid(
    id="dataset-table",
    columnDefs=[],
    rowData=[],
    dashGridOptions={
        "pagination": True,
        "paginationAutoPageSize": True,
    },
    style={"height": "50vh"},
)

dataset_filters = html.Div(id="dataset-filters")

datasets_tab = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Div("Dataset:", style={"fontWeight": "bold"}), width="auto"
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="dataset-dropdown",
                        placeholder="Select dataset",
                        clearable=False,
                    ),
                    width=4,
                ),
                dbc.Col(
                    dbc.Button(
                        "Sync Datasets",
                        id="sync-datasets-btn",
                        className="custom-button",
                    ),
                    width="auto",
                ),
                dbc.Col(
                    dbc.Button(
                        "Delete Dataset", id="delete-dataset-btn", color="danger"
                    ),
                    width="auto",
                ),
            ],
            justify="start",
            align="center",
            style={"marginTop": 5, "marginLeft": 5},
        ),
        dcc.Tabs(
            [
                dcc.Tab(
                    label="Images",
                    value="images_table",
                    children=dataset_table,
                    selected_className="custom-subtab--selected",
                    className="custom-subtab",
                ),
                dcc.Tab(
                    label="Filters",
                    value="dataset_filters",
                    children=dataset_filters,
                    selected_className="custom-subtab--selected",
                    className="custom-subtab",
                ),
            ],
            value="images_table",
            style={"marginTop": 5},
        ),
        delete_dataset_modal,
    ],
)


@callback(
    [
        Output("dataset-dropdown", "options", allow_duplicate=True),
        Output("dataset-dropdown", "value", allow_duplicate=True),
    ],
    Input("user-store", "data"),
    prevent_initial_call=True,
)
def update_dataset_dropdown(user_data):
    # Update the available datasets.
    if len(user_data):
        # Look for datasets in mongo.
        db = get_mongo_db()

        datasets_db = db["datasets"]

        # Look for datasets for this user.
        datasets = list(datasets_db.find({"user": user_data["user"]}))

        if not len(datasets):
            # Look for datasets for my user.
            gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
            gc.token = user_data["token"]

            # Look for the user folder.
            try:
                datasets_fld = gc.get(
                    f"resource/lookup?path=%2Fcollection%2FNeuroTK%2FDatasets%2F{user_data['user']}"
                )

                datasets = list(gc.listItem(datasets_fld["_id"]))

                # Push the datasets to mongo.
                _ = add_many_to_collection(
                    datasets_db,
                    user_data["user"],
                    {dataset["_id"]: dataset for dataset in datasets},
                )
            except HttpError:
                # Could not find the user folder, create it.
                datasets_fld = gc.get(
                    "resource/lookup?path=%2Fcollection%2FNeuroTK%2FDatasets"
                )

                _ = gc.createFolder(
                    datasets_fld["_id"], user_data["user"], public=False
                )

        # List all the dataset items.
        options = [
            {"label": dataset["name"], "value": dataset["_id"]} for dataset in datasets
        ]

        return options, options[0]["value"] if len(options) else None

    return [], None


@callback(
    [
        Output("dataset-dropdown", "options", allow_duplicate=True),
        Output("dataset-dropdown", "value", allow_duplicate=True),
    ],
    [
        Input("sync-datasets-btn", "n_clicks"),
        State("user-store", "data"),
        State("dataset-dropdown", "value"),
    ],
    prevent_initial_call=True,
)
def sync_projects(n_clicks, user_data, dataset_id):
    # Sync the datasets with those in the DSA.
    db = get_mongo_db()
    datasets_db = db["datasets"]

    # Drop all the documents in the collection.
    datasets_db.drop()

    # Pull the datasets from the DSA.
    gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
    gc.token = user_data["token"]

    datasets_fld = gc.get(
        f"resource/lookup?path=%2Fcollection%2FNeuroTK%2FDatasets%2F{user_data['user']}"
    )

    datasets = list(gc.listItem(datasets_fld["_id"]))

    # Push the datasets to mongo.
    _ = add_many_to_collection(
        datasets_db,
        user_data["user"],
        {dataset["_id"]: dataset for dataset in datasets},
    )

    options = [
        {"label": dataset["name"], "value": dataset["_id"]} for dataset in datasets
    ]

    value = None

    for option in options:
        if option["value"] == dataset_id:
            value = dataset_id
            break

    return options, value


@callback(
    [
        Output("dataset-table", "columnDefs"),
        Output("dataset-table", "rowData"),
        Output("dataset-filters", "children"),
    ],
    [Input("dataset-dropdown", "value"), State("user-store", "data")],
    prevent_initial_call=True,
)
def load_dataset_table(dataset_id, user_data):
    # Load the dataset image data into table.
    if dataset_id:
        # Look for the dataset in mongo.
        db = get_mongo_db()["datasets"]

        dataset = db.find_one({"_id": dataset_id, "user": user_data["user"]})

        df = json_normalize(dataset["meta"]["data"], sep="-")

        # Rename columns with period with a space.
        df.columns = [col.replace(".", " ") for col in df.columns]

        columnDefs = [{"headerName": col, "field": col} for col in df.columns]

        rowData = df.to_dict(orient="records")

        # Get the filters.
        filters = dataset["meta"].get("filters")

        if filters is None:
            markdown_component = "No filters for dataset found."
        else:
            # NOTE: from ChatGPT
            # Convert the dictionary to a pretty-printed JSON string
            pretty_json = json.dumps(filters, indent=2)

            # Using dcc.Markdown for syntax highlighting
            markdown_component = dcc.Markdown(f"```json\n{pretty_json}\n```")

        return columnDefs, rowData, markdown_component

    return [], [], []


@callback(
    Output("delete-dataset-btn", "disabled", allow_duplicate=True),
    Input("dataset-dropdown", "options"),
    prevent_initial_call=True,
)
def disable_delete_button(datasets):
    # Disable the delete button if no dataset is available.
    return False if len(datasets) else True
