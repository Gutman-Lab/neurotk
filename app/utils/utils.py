from dsa_helpers.mongo_utils import get_mongo_client
from os import getenv
import pandas as pd
from pathlib import Path
import numpy as np


def get_mongo_database(user):
    #  Helper function for getting the mongo database for a user.
    return get_mongo_client()[f"{getenv('MONGODB_DB')}-{user}"]


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


# def get_annotation_docs(
#     gc: GirderClient, item_id: str, name: str | None = None
# ) -> list[dict]:
#     """Get the list of annotation document metadata for an item. Note that this
#     does not return the points of the annotations.

#     Args:
#         gc (girder_client.GirderClient): Girder client.
#         item_id (str): Item id.
#         name (str): Only include documents with this name. Defaults to None.

#     Returns:
#         list[dict]: List of annotation documents.

#     """
#     "annotation?itemId=641bbfd7867536bb7a22b42e&name=tissue&limit=0&offset=0&sort=lowerName&sortdir=1"

#     request = f"annotation?itemId={item_id}&limit=0&offset=0&sort=lowerName&sortdir=1"

#     if name is not None:
#         request += f"&name={name}"

#     return gc.get(request)


# def convert_elements_to_regions(
#     elements: list[dict], delineator: tuple = (", -1, -1, ")
# ) -> list[int]:
#     """Convert the elements in an annotation document to a list of ints corresponding to the
#     vertices of the elements. Multiple elements are separated appropriately so they can be passed
#     to the DSA CLI API.

#     Args:
#         elements (list[dict]): List of annotation elements.

#     Returns:
#         list[int]: List of vertices.

#     """
#     points = []

#     for el in elements:
#         if el.get("type") == "polyline":
#             if el.get("points"):
#                 el_points = np.array(el["points"])[:, :2].astype(str)
#                 el_points = el_points.flatten().tolist()
#                 points.append(", ".join(el_points))

#     points = delineator.join(points)

#     return f"[{points}]"


# def get_annotations_documents(
#     gc: GirderClient,
#     item_id: str,
#     doc_names: str | list[str] = None,
#     groups: str | list[str] = None,
# ) -> list[dict]:
#     """Get Histomics annotations for an image.

#     Args:
#         gc: Girder client.
#         item_id: Item id.
#         doc_names: Only include documents with given names.
#         groups : Only include annotation documents that contain at least one
#             annotation of these set of groups.

#     Returns:
#         List of annotation documents.

#     """
#     if isinstance(doc_names, str):
#         doc_names = [doc_names]

#     if isinstance(groups, str):
#         groups = [groups]

#     annotation_docs = []

#     # Get information about annotation documents for item.
#     for doc in gc.get(f"annotation?itemId={item_id}"):
#         # If needed only keep documents of certain names.
#         if doc_names is not None and doc["annotation"]["name"] not in doc_names:
#             continue

#         # Filter out documents with no annotation groups.
#         if "groups" not in doc or not len(doc["groups"]):
#             continue

#         # Ignore document if it does not contain elements in the group list.
#         if groups is not None:
#             ignore_flag = True

#             for group in doc["groups"]:
#                 if group in groups:
#                     ignore_flag = False
#                     break

#             if ignore_flag:
#                 continue

#         # Get the full document with elements.
#         doc = gc.get(f"annotation/{doc['_id']}")

#         # Filter document for elements in group only.
#         elements_kept = []
#         doc_groups = set()

#         for element in doc["annotation"]["elements"]:
#             # Remove element without group.
#             if "group" not in element:
#                 continue

#             if groups is None or element["group"] in groups:
#                 elements_kept.append(element)
#                 doc_groups.add(element["group"])

#         doc["groups"] = list(doc_groups)
#         doc["annotation"]["elements"] = elements_kept

#         # Add doc if there were elements.
#         if len(elements_kept):
#             annotation_docs.append(doc)

#     return annotation_docs
