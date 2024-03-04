from girder_client import GirderClient
from os import getenv


def get_projects() -> list[dict[str, str]]:
    """Get the projects from Girder.

    Returns:
        dict: A dictionary of projects.

    """
    gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
    gc.authenticate(apiKey=getenv("DSA_API_TOKEN"))

    # Get the user currently authenticated.
    token_info = gc.get("token/current")
    user = ""

    for user_info in token_info["access"]["users"]:
        user = gc.getUser(user_info["id"])["login"]
        break

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

            return user_projects

    # The projects folder does not exist.
    return []
