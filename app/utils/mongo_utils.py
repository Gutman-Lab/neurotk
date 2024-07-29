import pymongo
from os import getenv


def get_mongo_db():
    """Get the mongo database."""
    mc = pymongo.MongoClient(
        f"mongodb://{getenv('MONGO_INITDB_ROOT_USERNAME')}:{getenv('MONGO_INITDB_ROOT_PASSWORD')}@mongodb:27017"
    )

    # Return the specific database.
    return mc[getenv("MONGODB_DB")]


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


# def add_one_task(project_id: str, task_item: dict):
#     """Add a single task to a database already created."""
#     mongo_collection = get_mongo_client()["projectStore"]

#     # Get the current store.
#     user = get_current_user()[1]
#     project_store = list(mongo_collection.find({"_id": project_id, "user": user}))[0]

#     # Add the task.
#     tasks = project_store.get("tasks", {})
#     tasks[task_item["name"]] = {"_id": task_item["_id"]}

#     tasks = {k: tasks[k] for k in sorted(tasks.keys())}

#     project_store["tasks"] = tasks

#     operations = [
#         pymongo.UpdateOne(
#             {"_id": project_store["_id"]}, {"$set": project_store}, upsert=True
#         )
#     ]

#     for chunk in chunks(operations):
#         _ = mongo_collection.bulk_write(chunk)


# def add_one_to_collection(
#     collection_name, item: dict, key: str = "_id", user: str = None
# ):
#     """Add a single item to a mongo collection."""
#     if user is None:
#         user = get_current_user()[1]

#     mc = get_mongo_client()[collection_name]

#     item["user"] = user

#     operations = [pymongo.UpdateOne({"_id": item[key]}, {"$set": item}, upsert=True)]

#     for chunk in chunks(operations):
#         _ = mc.bulk_write(chunk)


def add_many_to_collection(
    mongo_collection: pymongo.collection.Collection,
    user: str,
    docs: dict[str, dict],
):
    """Add items to a mongo collection. For this project we always add items with a unique
    user key.

    Args:
        mongo_collection (pymongo.collection.Collection): The collection to add the items to.
        user (str): The user to add the items to.
        docs (dict): The docs to add to the collection, it should be a dictionary.
        key (str): The key to use as the unique identifier.

    """
    operations = []

    for k, v in docs.items():
        v["user"] = user

        operations.append(pymongo.UpdateOne({"_id": k}, {"$set": v}, upsert=True))

    for chunk in chunks(operations):
        _ = mongo_collection.bulk_write(chunk)

    return docs


# # def get_available_projects():
# #     """Get the current available projects."""
# #     # Get the mongo collection.
# #     collection = get_mongo_client()["projects"]

# #     # Get the projects unique to this user.
# #     user = get_current_user()[1]

# #     projectList = list(collection.find({"projectList": user}))

# #     # if projectList:
# #     #     print("Just return the current status of the project list.")
# #     # else:
# #     #     print("There are no project data - so get the data to return and add to db.")
