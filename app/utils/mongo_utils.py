"""Utility functions using the Mongo database."""

import pymongo
from os import getenv
from utils.utils import get_current_user


def chunks(lst: list, n=500):
    """Helper function for traversting through a list in chunks.

    Args:
        lst (list): The list to traverse.
        n (int): The size of the chunks.

    Returns:
        generator: A generator of the list in chunks.

    """
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def get_mongo_client():
    """Get the mongo client."""
    mc = pymongo.MongoClient(
        getenv("MONGODB_URI"),
        username=getenv("MONGODB_USERNAME"),
        password=getenv("MONGODB_PASSWORD"),
    )

    return mc[getenv("MONGODB_DB")]


def add_one_task(project_id: str, task_item: dict):
    """Add a single task to a database already created."""
    mongo_collection = get_mongo_client()["projectStore"]

    # Get the current store.
    user = get_current_user()[1]
    project_store = list(mongo_collection.find({"_id": project_id, "user": user}))[0]

    # Add the task.
    tasks = project_store.get("tasks", {})
    tasks[task_item["name"]] = {"_id": task_item["_id"]}

    tasks = {k: tasks[k] for k in sorted(tasks.keys())}

    project_store["tasks"] = tasks

    operations = [
        pymongo.UpdateOne(
            {"_id": project_store["_id"]}, {"$set": project_store}, upsert=True
        )
    ]

    for chunk in chunks(operations):
        _ = mongo_collection.bulk_write(chunk)


def add_one_to_collection(
    collection_name, item: dict, key: str = "_id", user: str = None
):
    """Add a single item to a mongo collection."""
    if user is None:
        user = get_current_user()[1]

    mc = get_mongo_client()[collection_name]

    item["user"] = user

    operations = [pymongo.UpdateOne({"_id": item[key]}, {"$set": item}, upsert=True)]

    for chunk in chunks(operations):
        _ = mc.bulk_write(chunk)


def add_many_to_collection(
    mongo_collection, items: dict, key: str = "_id", user: str = None
):
    """Add items to a mongo collection. For this project we always add items with a unique
    user key.

    """
    if user is None:
        user = get_current_user()[1]

    items = [dict(items[_id], **{"user": user}) for _id in items]

    operations = []

    for item in items:
        operations.append(
            pymongo.UpdateOne({"_id": item[key]}, {"$set": item}, upsert=True)
        )

    for chunk in chunks(operations):
        _ = mongo_collection.bulk_write(chunk)


def get_available_projects():
    """Get the current available projects."""
    # Get the mongo collection.
    collection = get_mongo_client()["projects"]

    # Get the projects unique to this user.
    user = get_current_user()[1]

    projectList = list(collection.find({"projectList": user}))

    # if projectList:
    #     print("Just return the current status of the project list.")
    # else:
    #     print("There are no project data - so get the data to return and add to db.")


def get_annotation_doc(item_id: str, doc_name: str):
    """Get the annotation document from the mongo database or from DSA.
    If getting from DSA, save it to mongo database."""
