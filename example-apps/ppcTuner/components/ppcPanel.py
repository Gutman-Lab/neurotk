### To hard code.. or not to hard code.. that is the question

import dash_bootstrap_components as dbc
from histomicstk.segmentation import positive_pixel_count
from dash import html, callback, Input, Output, State, ALL, callback_context
import girder_client
import pickle

from utils.dsaHelperFunctions import (
    getImageRegion_as_NP,
    numpy_mask_to_colored_html_img,
    numpy_array_to_html_img,
)
import settings as s


"""Parameters(hue_value, hue_width, saturation_minimum,
    intensity_upper_limit, intensity_weak_threshold,
    intensity_strong_threshold, intensity_lower_limit)

    Attributes
    ----------
    hue_value:
      Center of the hue range in HSI space for the positive color, in
      the range [0, 1]
    hue_width:
      Width of the hue range in HSI space
    saturation_minimum:
      Minimum saturation of positive pixels in HSI space, in the range
      [0, 1]
    intensity_upper_limit:
      Intensity threshold in HSI space above which a pixel is
      considered negative, in the range [0, 1]
    intensity_weak_threshold:
      Intensity threshold in HSI space that separates weak-positive
      pixels (above) from plain positive pixels (below)
    intensity_strong_threshold:
      Intensity threshold in HSI space that separates plain positive
      pixels (above) from strong positive pixels (below)
    intensity_lower_limit:
      Intensity threshold in HSI space below which a pixel is
      considered negative

    """


# Assuming ppc_params_dict is defined as in the previous context
ppc_params_dict = {
    "specific_ppc_results_hue_value": ["PPC Hue Value", 0.1],
    "specific_ppc_results_hue_width": ["PPC Hue Width", 0.5],
    "specific_ppc_results_saturation_minimum": ["PPC Saturation Minimum", 0.2],
    "specific_ppc_results_intensity_upper_limit": [
        "PPC Intensity Upper Limit",
        round((197 / 255), 2),
    ],
    "specific_ppc_results_intensity_weak_threshold": [
        "PPC Intensity Weak Threshold",
        round((175 / 255), 2),
    ],
    "specific_ppc_results_intensity_strong_threshold": [
        "PPC Intensity Strong Threshold",
        round((100 / 255), 2),
    ],
    "specific_ppc_results_intensity_lower_limit": ["PPC Intensity Lower Limit", 0.0],
}

# Changes in dbc.Input triggers the callback
ppc_params_controls = html.Div(
    [
        dbc.Card(
            [
                html.H4("PPC Parameters", className="card-title"),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label(val[0]),
                                dbc.Input(
                                    type="number",
                                    id={"type": "ppcParams", "value": key},
                                    value=val[1],
                                    min=0,
                                    max=1,
                                    step=0.01,
                                ),
                            ],
                            width="auto",
                        )
                        for key, val in ppc_params_dict.items()
                    ]
                ),
            ]
        ),
        html.Div(id="curPPCParams"),  # style={"display": "none"}
    ]
)


@callback(
    Output("curPPCParams", "children"),
    Output("ppcResults_img", "children"),
    Output("ppcROI_np_img", "children"),
    [Input({"type": "ppcParams", "value": ALL}, "value")],
    [Input("roiCoords_store", "data")],#State
)
def updatePPCparams(values, roiCoords):
    # print(values)
    # print(roiCoords)
    ctx = callback_context
    # print(ctx.inputs_list)

    
    paramDict = {"hue_value": 0.1, "hue_width": 0.5, "saturation_minimum": 0.2} 
    # Create a new ppcParams object with the values from dbc.Input
    ppcParams = {
        "specific_ppc_results_hue_value": values[0],
        "specific_ppc_results_hue_width": values[1],
        "specific_ppc_results_saturation_minimum": values[2],
        "specific_ppc_results_intensity_upper_limit": values[3],
        "specific_ppc_results_intensity_weak_threshold": values[4],
        "specific_ppc_results_intensity_strong_threshold": values[5],
        "specific_ppc_results_intensity_lower_limit": values[6],
    }

    ## Things you need to pull out..
    ## It's an array of arrays.. woo hoo
    ## For each proprety, we need id.type.value to get the name of the key/property.. and then just "value" to get the value that was modified
    ## This then needs to be put into a dictionary.. into a namped tumple/param magical thing and passed to the function
    ppcROI = getImageRegion_as_NP(
        s.sampleImageId, # This is our image id number
        roiCoords["startX"],
        roiCoords["startY"],
        roiCoords["width"],
        roiCoords["height"],
    )
    
    # 256x256 mask
    print(roiCoords["startX"])
    ppcResults, ppcOutputImg = runPPC(ppcROI,ppcParams)# paramDict)

    # Convert and display the label mask as an image in Dash
    # image_component = numpy_array_to_html_img(label_mask)

    return (
        values,
        numpy_mask_to_colored_html_img(ppcOutputImg),
        numpy_array_to_html_img(ppcROI),
    )


## Since we are NOT running on the whole slide, we can use the positive_pixel_count
## count_image  and pass it in a params as a named tuple... which has all the input params we need


def runPPC(imgROI, ppcParamsDict):
    # Convert the dictionary of parameters to a Parameters object
    ppcParams = positive_pixel_count.Parameters(
        hue_value=ppcParamsDict["specific_ppc_results_hue_value"],
        hue_width=ppcParamsDict["specific_ppc_results_hue_width"],
        saturation_minimum=ppcParamsDict["specific_ppc_results_saturation_minimum"],
        intensity_upper_limit=ppcParamsDict["specific_ppc_results_intensity_upper_limit"],
        intensity_weak_threshold=ppcParamsDict["specific_ppc_results_intensity_weak_threshold"],
        intensity_strong_threshold=ppcParamsDict["specific_ppc_results_intensity_strong_threshold"],
        intensity_lower_limit=ppcParamsDict["specific_ppc_results_intensity_lower_limit"],
    )

    # Run the positive pixel count algorithm
    ppcResult, ppcOutputImage = positive_pixel_count.count_image(imgROI, ppcParams)

    return ppcResult, ppcOutputImage

# def runPPC(
#     imgROI,
#     #myParamDict,
# ):
#     # Run the positive pixel count algorithm

#     ppcParams = positive_pixel_count.Parameters(
#         hue_value=0.1,
#         hue_width=0.3,
#         saturation_minimum=0.2,
#         intensity_upper_limit=197 / 255,
#         intensity_weak_threshold=175 / 255,
#         intensity_strong_threshold=100 / 255,
#         intensity_lower_limit=0.2,
#     )

#     ppcResult, ppcOutputImage = positive_pixel_count.count_image(imgROI, ppcParams)
#     return ppcResult, ppcOutputImage


def get_region_as_np(imageId, left, top, width, height):
    gc = girder_client.GirderClient(apiUrl=s.dsaBaseUrl)
    gc.authenticate
