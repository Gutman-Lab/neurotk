from dash import html, dcc, callback, Output, Input, State, no_update
import dash_bootstrap_components as dbc
from pathlib import Path
from os.path import join

from utils import generate_cli_input_components
from utils.mongo_utils import get_mongo_db

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
                dbc.Col(dcc.Dropdown(options=[], id="cli-dropdown"), width=4),
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
        Input("cli-dropdown", "value"),
        State("user-store", "data"),
        State("task-dropdown", "value"),
        State("region-dropdown", "options"),
    ],
    prevent_initial_call=True,
)
def load_cli_inputs(cli_fp, user_data, task_id, region_options):
    # Load the appropriate UI for the CLI selected.
    # Read the XML file.
    if len(cli_fp):
        with open(join("cli-xmls", cli_fp + ".xml"), "r") as fp:
            xml_content = fp.read().strip()

        # If the CLI has already been run, pass the information to the UI to set the values.
        task = get_mongo_db()["tasks"].find_one(
            {"_id": task_id, "user": user_data["user"]}
        )

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
        options = [{"value": doc["name"], "label": doc["name"]} for doc in docs]

        return options, options[0]["value"] if len(options) else None

    return [], None
