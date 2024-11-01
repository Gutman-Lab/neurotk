from dash import callback, Output, Input, State, no_update, dcc
from os import getenv
from utils.utils import get_mongo_database
from pandas import json_normalize
import json


@callback(
    [
        Output("dataset-table", "columnDefs"),
        Output("dataset-table", "rowData"),
        Output("dataset-filters", "children"),
    ],
    [
        Input("dataset-dropdown", "value"),
        State(getenv("LOGIN_STORE_ID"), "data"),
    ],
    prevent_initial_call=True,
)
def load_dataset_table(dataset_id, user_data):
    # Load the dataset image data into table.
    if dataset_id is not None:
        # Get dataset mongo collection.
        dataset_collection = get_mongo_database(user_data["user"])["datasets"]

        # Find the dataset.
        dataset = dataset_collection.find_one({"_id": dataset_id})

        # Flatten the nested dataset metadata.
        df = json_normalize(dataset["meta"]["dataset"], sep=":")

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
