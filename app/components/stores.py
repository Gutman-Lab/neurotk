from dash import dcc, html, callback, Output, Input, State, no_update
from utils.stores import get_projects

stores = html.Div(
    [
        dcc.Store(id="projects-dropdown-store", data=[]),
        dcc.Store(id="project-store", data={}),
        dcc.Store(id="dataview-store", data=[]),
        dcc.Store(id="datasets-store", data={}),
    ]
)


@callback(Output("datasets-store", "data"), Input("datasets-store", "clear_data"))
def initiate_dataset_store(_):
    from utils.utils import get_current_user
    from os import getenv

    gc, user = get_current_user()

    # Get the dataset directory.
    data = {}

    for fld in gc.listFolder(
        getenv("DSA_NEUROTK_COLLECTION_ID"), parentFolderType="collection"
    ):
        if fld["name"] == "Datasets":
            # Loop through public and private datasets.
            for type_fld in gc.listFolder(fld["_id"]):
                for user_fld in gc.listFolder(type_fld["_id"]):
                    if user_fld["name"] == user:
                        # List the dataset items.
                        for item in gc.listItem(user_fld["_id"]):
                            meta = item.get("meta", {})
                            data[item["name"]] = {
                                "data": meta.get("data", []),
                                "filters": meta.get("filters", {}),
                            }

    return data
