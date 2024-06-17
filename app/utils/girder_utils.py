from os import getenv
from girder_client import GirderClient


def get_current_user(gc: GirderClient | None = None) -> str:
    """Get the current user.

    Args:
        gc (girder_client.GirderClient, optional): The GirderClient to get user from,
            if it is not passed it is obtained from get_gc(). Defaults to None.

    Returns:
        str: The current user.

    """
    if gc is None:
        gc = get_gc()

    # Get the user currently authenticated.
    token_info = gc.get("token/current")

    for user_info in token_info["access"]["users"]:
        user = gc.getUser(user_info["id"])["login"]
        return gc, user

    return gc, None


def get_gc() -> GirderClient:
    """Return the authenticated GirderClient.

    Returns:
        girder_client.GirderClient: The authenticated GirderClient.

    """
    gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
    gc.authenticate(apiKey=getenv("DSA_API_TOKEN"))

    return gc
