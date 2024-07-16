"""These are helper functions to make the communication between python, DSA and the Dash-Paperdragon app
less painful.  These should be common functions that will be reused across app"""

import random
from dash import html
import dash_bootstrap_components as dbc
from utils.girder_utils import login


def getId():
    global globalId
    globalId = globalId + 1
    return globalId


def get_box_instructions(x, y, w, h, color, userdata={}):
    # Define the coordinates of the rectangle (polygon in GeoJSON)
    coordinates = [
        [x, y],  # Bottom left corner
        [x + w, y],  # Bottom right corner
        [x + w, y + h],  # Top right corner
        [x, y + h],  # Top left corner
        [x, y],  # Back to bottom left corner to close the polygon
    ]

    ## HACK!
    userdata["centroid"] = [x + w / 2, y + h / 2]
    userdata["dsaShapeType"] = "box"
    userdata["x"] = x
    userdata["y"] = y
    userdata["width"] = w
    userdata["height"] = h

    # Create the GeoJSON object
    geojson = {
        "type": "Feature",
        "geometry": {
            "type": "MultiPolygon",
            "coordinates": [[coordinates]],
        },
        "properties": {
            "fillColor": color,
            "strokeColor": color,
            "userdata": userdata,
            "fillOpacity": 0.1,
            "strokeWidth": 2,
            "rescale": {"strokeWidth": 2},
        },
        "userdata": userdata,
    }

    return geojson


colors = ["red", "orange", "yellow", "green", "blue", "purple"]
classes = ["a", "b", "c", "d", "e", "f"]


def generate_random_boxes(num_points, bounds):
    out = []

    x = int(bounds["x"])
    w = int(bounds["width"])
    y = int(bounds["y"])
    h = int(bounds["height"])

    for idx, _ in enumerate(range(num_points)):

        className, color = random.choice(list(zip(classes, colors)))
        # color = random.choice(colors)
        userdata = {"class": className}

        bx = random.randint(x, x + w)
        by = random.randint(y, y + h)
        bw = random.randint(int(w / 150), int(w / 50))
        bh = random.randint(int(h / 150), int(h / 50))
        instructions = get_box_instructions(bx, by, bw, bh, color, userdata)

        out.append(instructions)

    return out


def get_circle_instructions(x, y, r, color, opacity, userdata={}):
    props = {
        "center": [x, y],
        "radius": r,
        "fillColor": color,
        "strokeColor": color,
        "fillOpacity": opacity,
    }
    userdata["objectId"] = getId()
    userdata["centroid"] = f"{x},{y}"
    command = {"paperType": "Path.Circle", "args": [props], "userdata": userdata}
    return command


def get_annotations_forExpt(imgList):
    """For an experiment, we want all of the images associated with it, but use
    the first image from the list or day 1 and then get the annotations associated
    with that document.

    """
    if imgList:
        img_id = imgList[0]["_id"]
        boxes = []  # append the boxes to show

        gc = login()

        # annotationGeoJsonDoc = gc.get("annotation/662149acf68c6ec6ee887d7d/geojson")

        for doc in gc.get(f"annotation/item/{img_id}"):
            for element in doc.get("annotation", {}).get("elements", []):
                if element["type"] == "rectangle":
                    # For PaperJS app, x & y are the top left of the box not the center.
                    x = int(element["center"][0] - element["width"] / 2)
                    y = int(element["center"][1] - element["height"] / 2)

                    boxes.append(
                        {
                            "x": x,
                            "y": y,
                            "id": element["id"],
                            "width": int(element["width"]),
                            "height": int(element["height"]),
                            "color": element["lineColor"],
                            "objectClass": element.get("label", {}).get(
                                "value", "unknown"
                            ),
                            "objectId": element["id"],
                            "shapeSource": "dsa",
                        }
                    )

        ## NEED TO UPDATE THIS AND GET RID OF THIS POINTLIST THING
        return boxes
    else:
        return []


def generate_cellBounds(dsaAnnotationObject):
    """This should be given the DSA annotatio data and dump all of the neurons
    into the proper format for paperJS to use this custom function will allow
    me to modify colors and other things, and potentially also standardize the
    box size and/or do other fancy stuff.

    """
    out = []
    for a in dsaAnnotationObject:
        # # print("Received bounds:", bounds, num_points)
        x = int(a["x"])
        w = int(a["width"])
        y = int(a["y"])
        h = int(a["height"])
        color = a["color"]

        userdata = {"class": a["objectClass"], "id": a["id"]}
        instructions = get_box_instructions(x, y, w, h, color, userdata)
        out.append(instructions)

    return out


def convertPaperOutputEditItem_to_AnnotationStore(editedItem):
    newObject = {
        "x": editedItem["data"]["point"]["x"],
        "y": editedItem["data"]["point"]["y"],
        "id": editedItem["data"]["userdata"]["id"],
        "width": editedItem["data"]["size"]["width"],
        "height": editedItem["data"]["size"]["height"],
        "color": "rgb({},{},{})".format(
            int(editedItem["data"]["origRef"][1]["strokeColor"][0] * 255),
            int(editedItem["data"]["origRef"][1]["strokeColor"][1] * 255),
            int(editedItem["data"]["origRef"][1]["strokeColor"][2] * 255),
        ),
        "objectClass": editedItem["data"]["userdata"]["class"],
        "objectId": editedItem["data"]["userdata"]["id"],
        "shapeSource": editedItem["callback"],
    }
    return newObject


def update_annotation_and_get_row(annotations, edited_item):
    """Annotation Store is currently using a different non GeoJSON format.
    This will be updated when the DSA gets fixed to emit the shapes correctly.

    """
    edited_item = convertPaperOutputEditItem_to_AnnotationStore(edited_item)

    for row_number, annotation in enumerate(annotations):
        if annotation["objectId"] == edited_item.get("objectId", None):
            # Update the annotation data
            # print(annotation, "----->", edited_item)
            annotation.update(edited_item)
            return row_number, annotations  ## # annotations is the entire object..
    return None, None
