from girder_client import GirderClient
from os import getenv


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
