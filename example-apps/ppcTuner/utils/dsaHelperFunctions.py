from settings import gc
import pickle
import numpy as np

import numpy as np
from PIL import Image
import base64
from io import BytesIO
from dash import html


# class Labels:
#     """Labels for the output image of the positive pixel count routines."""
#     NEGATIVE = 0
#     WEAK = 1
#     PLAIN = 2
#     STRONG = 3


def numpy_mask_to_colored_html_img(array):
    # Define a color map: 0 -> black, 1 -> red, 2 -> green
    color_map = {
        0: [0, 0, 0],  # Black
        1: [255, 0, 0],  # Red
        2: [0, 255, 0],  # Green
        3: [0, 0, 255],  # Blue
    }

    # Apply the color map
    # Create an empty RGB image with the same width and height as the input array
    colored_array = np.zeros((array.shape[0], array.shape[1], 3), dtype=np.uint8)

    # Map each label to its corresponding color
    for label, color in color_map.items():
        colored_array[array == label] = color

    # Convert the colored array to a PIL Image object
    img = Image.fromarray(colored_array)

    # Save the image object to a bytes buffer
    buffer = BytesIO()
    img.save(buffer, format="PNG")

    # Encode the bytes buffer to Base64 and decode to UTF-8 for HTML embedding
    encoded_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # Create an HTML img element with the Base64 encoded image
    img_html = html.Img(src=f"data:image/png;base64,{encoded_image}")

    return img_html


def numpy_array_to_html_img(array):
    # Convert the NumPy array to a PIL Image object
    img = Image.fromarray(array.astype(np.uint8))

    # Save the image object to a bytes buffer
    buffer = BytesIO()
    img.save(buffer, format="PNG")

    # Encode the bytes buffer to Base64 and decode to UTF-8 for HTML embedding
    encoded_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # Create an HTML img element with the Base64 encoded image
    img_html = html.Img(src=f"data:image/png;base64,{encoded_image}")

    return img_html


# Assuming `label_mask` is your NumPy array label mask
# label_mask = ...


# @memory.cache
def getImageThumb_as_NP(imageId, imageWidth=512):
    try:
        pickledItem = gc.get(
            f"item/{imageId}/tiles/thumbnail?encoding=pickle", jsonResp=False
        )

        ## Need to have or cache the baseImage size as well... another feature to add
        baseImage_as_np = pickle.loads(pickledItem.content)
    except:
        return None

    return baseImage_as_np


def getImageRegion_as_NP(imageId, startX, startY, regionWidth, regionHeight):
    try:
        pickledItem = gc.get(
            f"item/{imageId}/tiles/region?top={startX}&left={startY}&regionWidth={regionWidth}&regionHeight={regionHeight}&encoding=pickle",
            jsonResp=False,
        )

        ## Need to have or cache the baseImage size as well... another feature to add
        baseImage_as_np = pickle.loads(pickledItem.content)
    except:
        return None

    return baseImage_as_np
