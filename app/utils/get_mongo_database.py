from dsa_helpers.mongo_utils import get_mongo_client
from os import getenv


def get_mongo_database(user):
    #  Helper function for getting the mongo database for a user.
    return get_mongo_client()[f"{getenv('MONGODB_DB')}-{user}"]
