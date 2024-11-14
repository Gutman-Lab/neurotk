import pandas as pd
from pathlib import Path
import numpy as np
from utils import get_mongo_database


def get_project_items(project_id, user):
    """For a selected project get all the items from the datasets, with
    metadata combined from all the datasets for each itemm.

    """
    # Mongo database.
    mongodb = get_mongo_database(user)

    # Get the project mongodb doc.
    project_doc = mongodb["projects"].find_one({"_id": project_id})

    # Check the datasets id.
    dataset_ids = project_doc["meta"].get("datasets", [])

    if not len(dataset_ids):
        return [], []

    # Get the collection of datasets.
    datasets_collection = mongodb["datasets"]

    # Loop through each dataset in project.
    items = {}  # track all the items

    for dataset_id in dataset_ids:
        # Get the mongodb dataset doc.
        dataset_doc = datasets_collection.find_one({"_id": dataset_id})

        # Loop through the data.
        for item in dataset_doc["meta"]["dataset"]:
            # Check if item is already on the dictionary.
            if item["_id"] in items:
                # Update the item metadata.
                items[item["_id"]].update(item)
            else:
                # Add the item metadata.
                items[item["_id"]] = item

    # Turn the dictionary into a list of dictionaries.
    items = list(items.values())

    # Normalize the list of dictionaries.
    df = pd.json_normalize(items, sep=":")

    # Replace periods in column names with spaces.
    df.columns = [col.replace(".", " ") for col in df.columns]

    columnDefs = [
        {"headerName": col, "field": col, "filter": "agSetColumnFilter"}
        for col in df.columns
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
                points.append(f"{x1}, {y1}, {x2}, {y1}, {x2}, {y2}, {x1}, {y2}")

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
