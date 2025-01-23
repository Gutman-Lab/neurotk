import pandas as pd
from pathlib import Path
import numpy as np
from girder_client import GirderClient
from os import getenv
from dsa_helpers.mongo_utils import add_many_to_collection
from utils import get_mongo_database


def get_project_items(item_ids, user, token=None):
    """For a selected project get all the items from the datasets, with
    metadata combined from all the datasets for each itemm.

    """
    # Mongo database.
    mongodb = get_mongo_database(user)

    # Get the project mongodb doc.
    items_collection = mongodb["items"]
    items = list(items_collection.find({"_id": {"$in": item_ids}}))

    if token is not None:
        # Extract the _id values of the found items
        found_item_ids = [item["_id"] for item in items]

        # Determine the missing item_ids
        missing_item_ids = set(item_ids) - set(found_item_ids)

        if len(missing_item_ids):
            # Authenticate girder client.
            gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
            gc.token = token

            # Get every item from the DSA.
            new_items = []

            for item_id in missing_item_ids:
                item = gc.getItem(item_id)

                items.append(item)
                new_items.append(item)

            # Add these new items to the mongo database.
            _ = add_many_to_collection(items_collection, new_items)

    # Normalize the list of dictionaries.
    df = pd.json_normalize(items, sep=":")

    # Replace periods in column names with spaces.
    df.columns = [col.replace(".", " ") for col in df.columns]

    columnDefs = [
        {"headerName": col, "field": col, "filter": "agSetColumnFilter"}
        for col in df.columns
        if col
        != "id"  # bug in Faceted Search app, this is an internal mongo id
    ]

    return columnDefs, df.to_dict(orient="records")


def read_xml_content(fp: str):
    """Read an XML file and return the contents as cleaned up string."""
    path = Path(fp)

    if path.is_file():

        with open(path, "r") as fp:
            return fp.read().strip()

    return None


def return_region_for_cli(
    annotation_docs, delineator: tuple = (", -1, -1, ")
) -> list[int]:
    """Convert the elements in an annotation document to a list of ints corresponding to the
    vertices of the elements. Multiple elements are separated appropriately so they can be passed
    to the DSA CLI API.

    Args:
        elements (list[dict]): List of annotation elements.

    Returns:
        list[int]: List of vertices.

    """
    points = []

    for doc in annotation_docs:
        for el in doc.get("annotation", {}).get("elements", []):
            if el.get("type") == "polyline":
                if el.get("points"):
                    el_points = np.array(el["points"])[:, :2].astype(str)
                    el_points = el_points.flatten().tolist()
                    points.append(", ".join(el_points))
            elif el.get("type") == "rectangle":
                xc, yc = el["center"][:2]
                w, h = el["width"], el["height"]

                x1, y1 = int(xc - w / 2), int(yc - h / 2)
                x2, y2 = int(xc + w / 2), int(yc + h / 2)
                points.append(
                    f"{x1}, {y1}, {x2}, {y1}, {x2}, {y2}, {x1}, {y2}"
                )

    points = delineator.join(points)

    return f"[{points}]"


def dsa_ann_doc_to_input_to_paper(ann_doc):
    features = []

    for element in ann_doc.get("annotation", {}).get("elements", []):
        # Format the coordinates.
        coordinates = []

        if element["type"] == "polyline":
            coordinates = [
                [[int(point[0]), int(point[1])] for point in element["points"]]
            ]
        else:
            continue

        # Setup the properties.
        properties = {
            "rescale": {"strokeWidth": element["lineWidth"]},
            "strokeColor": element["lineColor"],
        }

        feature = {
            "properties": properties,
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [coordinates],
            },
        }

        features.append(feature)

    return features


def format_geojson_doc_to_input_to_paper_fts(doc):
    """DG: This is a function to take the geoJson from the DSA and modify it to be more
    in line with the format that the paperdragon expects. I think the paperdragon
    expects the geojson to be in a feature collection format with the features being
    the actual annotations. I think the DSA is just returning the features, so I
    need to wrap it in a feature collection and then also add the type:
    "FeatureCollection" to the top of the object. Currrently just getting the geojson
    doc will eventually do sometihng with it! TO DO: MEET WITH TOM AND SEE IF I
    CAN get rid of the strokeWidth thing. Currently do not appear to need to set
    strokeWidth.. but do need to set rescale."""
    # NOTE: hard-coded to only do the first doc.
    if "features" in doc:
        features = doc["features"]

        for a in features:
            geometry_type = a["geometry"]["type"]
            coordinates = a["geometry"]["coordinates"]

            a["properties"]["rescale"] = {"strokeWidth": 2}
            a["properties"]["fillOpacity"] = 0.1
            a["properties"]["strokeColor"] = a["properties"]["lineColor"]
            a["properties"]["userdata"] = {
                "objectId": a["properties"]["id"],
                "class": a["properties"]["label"]["value"],
                "shapeSource": "dsa",
            }

            ## Note required conversion as paperjs doesn't currently render polygons properly
            if geometry_type == "Polygon":
                a["geometry"]["type"] = "MultiPolygon"
                adjusted_coordinates = [
                    [
                        [
                            [int(coord) for coord in point[:2]]
                            for point in coordinates[0]
                        ]
                    ]
                ]
                a["geometry"]["coordinates"] = adjusted_coordinates

        return features

    return []
