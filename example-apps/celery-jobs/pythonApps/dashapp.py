from dash import Dash, html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
from girder_client import GirderClient
from os import getenv
from tqdm import tqdm
from dash_ag_grid import AgGrid
import pandas as pd
import numpy as np
from PIL import Image
from io import BytesIO
import dash_mantine_components as dmc

gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
gc.authenticate(apiKey=getenv("DSA_API_KEY"))


def get_images():
    """Simple function for getting 10 images to run analysis on."""
    return [item["_id"] for item in gc.listItem(getenv("DSA_FLD_ID"), limit=10)]


def get_dsa_thumb(_id):
    """Get the thumbnail of the image."""
    # Get thumbnail image.
    request = f"item/{_id}/tiles/region?units=base_pixels&magnification=1.25&exact=false&encoding=JPEG&jpegQuality=95&jpegSubsampling=0"

    thumbnail = np.array(Image.open(BytesIO(gc.get(request, jsonResp=False).content)))

    return thumbnail


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    [
        dcc.Store(id="img-store", data=get_images()),
        html.Div(
            [
                dmc.Switch(
                    size="lg", radius="sm", label="Enable this option", checked=True
                ),
                dbc.Button(
                    "Callback",
                    id="callback-btn",
                    color="primary",
                    className="mr-1",
                    style={"margin-right": "10px"},
                ),
                dbc.Button(
                    "As celery jobs",
                    color="primary",
                    className="mr-1",
                    style={"margin-right": "10px"},
                ),
                dbc.Button("Celery jobs progress", color="primary", className="mr-1"),
            ],
            style={"display": "flex"},
        ),
        html.Div(id="output"),
    ]
)


@callback(
    Output("output", "children"),
    [Input("callback-btn", "n_clicks")],
    [State("img-store", "data")],
)
def callback_func(n_clicks, data):
    if n_clicks:
        # For each image return the list of names.
        output = ""
        items = []

        for item_id in tqdm(data):
            # Get the thumbnail.
            get_dsa_thumb(item_id)

            items.append(gc.getItem(item_id))

        df = pd.json_normalize(items, sep="-")

        return AgGrid(
            columnDefs=[{"field": col} for col in df.columns],
            rowData=df.to_dict("records"),
            dashGridOptions={
                "pagination": True,
                "paginationAutoPageSize": True,
            },
            style={"height": "75vh"},
        )
    else:
        return []


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
