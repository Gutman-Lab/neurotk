from dash import callback, Output, Input
from os import getenv
from girder_client import GirderClient
from utils.utils import get_mongo_database
from pathlib import Path
from dsa_helpers.mongo_utils import add_many_to_collection


@callback(
    Output("cli-dropdown", "options"),
    Input(getenv("LOGIN_STORE_ID"), "data"),
)
def load_available_clis(user_data):
    if user_data is not None and len(user_data):
        # Check mongodb for available CLIs.
        cli_collection = get_mongo_database(user_data["user"])["clis"]

        # List of available CLIs.
        available_clis = list(cli_collection.find())

        if not len(available_clis):
            gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
            gc.token = user_data["token"]

            available_clis = []

            # Create location to save the xml file.
            xml_dir = Path("cli-xmls")
            xml_dir.mkdir(exist_ok=True)

            for cli in gc.get("slicer_cli_web/cli"):
                if cli["image"] == getenv("CLI_IMAGE"):
                    # Get its xml file.
                    cli_xml = gc.get(
                        f"slicer_cli_web/cli/{cli['_id']}/xml", jsonResp=False
                    )

                    fn = cli["name"] + ".xml"
                    with open(xml_dir / fn, "wb") as fh:
                        fh.write(cli_xml.content)

                    available_clis.append(cli)

            # Add the available CLIs to the database.
            _ = add_many_to_collection(cli_collection, available_clis)

        # Return the available CLIs.
        options = [
            {"label": cli["name"], "value": cli["_id"]}
            for cli in available_clis
        ]

        return options

    return []
