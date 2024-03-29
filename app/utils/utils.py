from girder_client import GirderClient
from os import getenv
from pathlib import Path
import numpy as np


def get_current_user():
    """Get the current user based on the local API token."""
    gc = get_gc()

    # Get the user currently authenticated.
    token_info = gc.get("token/current")
    user = ""

    for user_info in token_info["access"]["users"]:
        user = gc.getUser(user_info["id"])["login"]
        return gc, user

    return gc, None


def get_gc():
    """Return an authenticated girder client."""
    gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
    gc.authenticate(apiKey=getenv("DSA_API_TOKEN"))

    return gc


def create_new_task(project_id: str, task_name: str) -> str:
    """Create a new task given a project folder ID, tasks are items.

    Args:
        project_id (str): The project folder ID.
        task_name (str): The name of the new task.

    Returns:
        str: The new task item ID.

    """
    gc = get_gc()

    # Find the task folder.
    task_fld = None

    for fld in gc.listFolder(project_id):
        if fld["name"] == "Tasks":
            task_fld = fld
            break

    if task_fld is None:
        raise ValueError("Task folder not found in project.")

    # Create the new task folder, return the id.
    return gc.createItem(task_fld["_id"], task_name, reuseExisting=True)


def read_xml_content(fp: str):
    """Read an XML file and return the contents as cleaned up string."""
    path = Path(fp)

    if path.is_file():

        with open(path, "r") as fp:
            return fp.read().strip()

    return None


def get_annotation_docs(
    gc: GirderClient, item_id: str, name: str | None = None
) -> list[dict]:
    """Get the list of annotation document metadata for an item. Note that this
    does not return the points of the annotations.

    Args:
        gc (girder_client.GirderClient): Girder client.
        item_id (str): Item id.
        name (str): Only include documents with this name. Defaults to None.

    Returns:
        list[dict]: List of annotation documents.

    """
    "annotation?itemId=641bbfd7867536bb7a22b42e&name=tissue&limit=0&offset=0&sort=lowerName&sortdir=1"

    request = f"annotation?itemId={item_id}&limit=0&offset=0&sort=lowerName&sortdir=1"

    if name is not None:
        request += f"&name={name}"

    return gc.get(request)


def convert_elements_to_regions(
    elements: list[dict], delineator: tuple = (", -1, -1, ")
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

    for el in elements:
        if el.get("type") == "polyline":
            if el.get("points"):
                el_points = np.array(el["points"])[:, :2].astype(str)
                el_points = el_points.flatten().tolist()
                points.append(", ".join(el_points))

    points = delineator.join(points)

    return f"[{points}]"


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
