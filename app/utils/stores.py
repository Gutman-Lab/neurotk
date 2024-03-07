from girder_client import GirderClient
from os import getenv

from utils.mongo_utils import (
    get_mongo_client,
    add_many_to_collection,
    add_one_to_collection,
)
from utils.utils import get_current_user


def get_projects(resync: bool = False) -> list[dict[str, str]]:
    """Get the projects from Girder.

    Args:
        resync (bool, optional): Whether to resync the projects. Defaults to False.

    Returns:
        dict: A dictionary of projects.

    """
    mongo_collection = get_mongo_client()["projects"]

    gc, user = get_current_user()

    # Check if the data exists in mongo - if so return it.
    projects = list(mongo_collection.find({"user": user}))

    if projects and not resync:
        # Sort the projects by the user then name.
        user_projects = []
        other_projects = []

        for project in projects:
            if project["label"].startswith(user):
                user_projects.append(project)
            else:
                other_projects.append(project)

        # sort and return
        user_projects.sort(key=lambda x: x["label"].split("/")[1])
        other_projects.sort(key=lambda x: x["label"].split("/")[1])
        user_projects.extend(other_projects)

        return user_projects

    # Delete the current mongo document.
    if projects:
        mongo_collection.delete_many({"user": user})

    # Get the projects folder - if it does not exist make sure to create it.
    for fld in gc.listFolder(
        getenv("DSA_NEUROTK_COLLECTION_ID"), parentFolderType="collection"
    ):
        if fld["name"] == "Projects":
            # Sort by user.
            user_projects = []
            other_projects = []

            # Loop to the project names, keeping the user info.
            for type_fld in gc.listFolder(fld["_id"]):
                for user_fld in gc.listFolder(type_fld["_id"]):
                    for project_fld in gc.listFolder(user_fld["_id"]):
                        project = {
                            "value": project_fld["_id"],
                            "label": f"{user_fld['name']}/{project_fld['name']}",
                        }

                        if user_fld["name"] == user:
                            user_projects.append(project)
                        else:
                            other_projects.append(project)

            # Sort each alphabetically.
            user_projects.sort(key=lambda x: x["label"].split("/")[1])
            other_projects.sort(key=lambda x: x["label"].split("/")[1])

            user_projects.extend(other_projects)

            # Reformat to be a dictionary with a unique _id as keys.
            projects = {project["value"]: project for project in user_projects}

            # Run the function to add projects to the mongo collection.
            add_many_to_collection(mongo_collection, projects, user=user, key="value")

            # Return only the values for this user.
            return list(mongo_collection.find({"user": user}))

    # No "Projects" folder found.
    return []


def get_project(project_id: str, resync: bool = False):
    """Get a specific project."""
    mongo_db = get_mongo_client()["projectStore"]

    gc, user = get_current_user()

    # Check if the data exists in mongo - if so return it.
    project_store = list(mongo_db.find({"_id": project_id, "user": user}))

    if project_store and not resync:
        return project_store

    # Delete the current mongo document.
    mongo_db.delete_many({"_id": project_id, "user": user})

    # Get the project from DSA, update mongodb and return.
    data = {"datasets": [], "tasks": {}, "images": {}, "_id": project_id}

    # List the information in this DSA folder.
    for fld in gc.listFolder(project_id):
        if fld["name"] == "Datasets":
            # Folder metadata in the "meta" field.
            meta = fld.get("meta", {})

            data["datasets"].extend(list(meta.keys()))

            for items in meta.values():
                for item in items:
                    if item["_id"] in data["images"]:
                        # Image is already here, update the dictionary.
                        data["images"][item["_id"]].update(item)
                    else:
                        # Add it instead.
                        data["images"][item["_id"]] = item

        elif fld["name"] == "Tasks":
            # List the items, which are the task info.
            for item in gc.listItem(fld["_id"]):
                meta = item.get("meta", {})
                meta["_id"] = item["_id"]
                data["tasks"][item["name"]] = meta

    add_one_to_collection("projectStore", data, user=user)

    return list(mongo_db.find({"user": user, "_id": project_id}))
