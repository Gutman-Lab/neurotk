from dash import (
    html,
    dcc,
    Input,
    Output,
    State,
    ALL,
    callback_context,
    callback,
    no_update,
)
import dash_bootstrap_components as dbc
import dash_paperdragon
from utils.dashPaperDragon_helpers import get_box_instructions
from components.ppcPanel import ppc_params_controls
import settings as s

## SAMPLE IMAGE is a small thumbnail I am pulling from the DSA prime (upper left)
# store and share data between callbacks.
roiCoords_store = dcc.Store(
    id="roiCoords_store",
    data={"startX": 1000, "startY": 800, "width": 256, "height": 256},
)  # It;s the bounding box we want to select


# ppcControls = html.Div("PPC Controls go here")
# display content within a card-like structure likee images, text, buttons
ppcRoi_img = dbc.Card(
    [
        roiCoords_store,
        html.H4("PPC Roi", className="card-title"),
        dbc.CardImg(
            id="ppcRoi_img",
        ),
    ],
    # loaded image size (w and l)
    style={"width": 256},
)

ppcROI_np_img = dbc.Card(
    [html.H4("PPC NP Image", className="card-title"),
     html.Div(id="ppcROI_np_img")],
    style={"width": 256},
)

ppcResults_img = dbc.Card(
    [html.H4("PPC Image", className="card-title"), html.Div(id="ppcResults_img")],
    style={"width": 256},
)


showRoi = dbc.Button(
    "Show ROI",
    id="show-roi",
    n_clicks=0,
    style={"width": "100px"},
    className="mr-4 btn btn-primary",
)

# These are the parameters like hue saturation, etc.
tuningControls = dbc.Row([ppc_params_controls, showRoi])


# This is the complete WSI with the zoomable tools, from DashpaperDragon
osdViewer = dbc.Card(
    [
        html.H4("Zoomable Image!", className="card-title"),
        dash_paperdragon.DashPaperdragon(
            id="osd-viewer",
            tileSources=[f"{s.dsaBaseUrl}item/{s.sampleImageId}/tiles/dzi.dzi"],
        ),
    ]
)

# Three columns in one row, images and panel. The calues are the size of each element
viewerPanel = dbc.Row(
    [
        dbc.Col([ppcRoi_img, ppcROI_np_img, ppcResults_img], width=3),
        dbc.Col(osdViewer, width=6),
        dbc.Col(tuningControls, width=3),
    ]
)


mainViewer = html.Div(
    [
        viewerPanel,
    ]
)


## Create callbacks to show an ROI on the image, and then also use these coordinates
## to grab an ROI from the DSA Server, which also becomes what we use for
## running PPC


#           src=f"{s.dsaBaseUrl}item/{s.sampleImageId}/tiles/region?left={startX}&top={startY}&regionWidth={width}&regionHeight={height}"
# callback triggers inputToPaper after the button with the ID show-roi is clicked Input("show-roi", "n_clicks")
# It also updates the src part of ppcRoi_img
@callback(
    Output("osd-viewer", "inputToPaper"),
    Output("ppcRoi_img", "src"),
    Input("show-roi", "n_clicks"),
    Input("roiCoords_store", "data"),
)
def show_roi(n_clicks, roiCoords):
    if n_clicks > 0:
        print("clickity clackity")

    startX = roiCoords["startX"]
    startY = roiCoords["startY"]
    width = roiCoords["width"]
    height = roiCoords["height"]

    # extracts the roiCoords data startX, ... from the roiCoords_store. And calls get_box_instructions
    ppcRoi = get_box_instructions(
        startX,
        startY,
        width,
        height,
        "red",
        {"class": "roi", "id": "roi"},
    )

    roiimgSrc = f"{s.dsaBaseUrl}item/{s.sampleImageId}/tiles/region?left={startX}&top={startY}&regionWidth={width}&regionHeight={height}"

    return (
        {
            "actions": [
                {"type": "clearItems"},
                {
                    "type": "drawItems",
                    "itemList": [ppcRoi],
                },
            ]
        },
        roiimgSrc,
    )
    ### For now I am drawing a single box that eventually we can also move around
    ### Which becomes the ROI for PPC