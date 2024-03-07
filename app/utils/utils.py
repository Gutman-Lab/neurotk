from girder_client import GirderClient
from os import getenv
from pathlib import Path


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
