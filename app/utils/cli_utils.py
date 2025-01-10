from pprint import pprint
from pathlib import Path
from os import getenv
from utils.utils import get_mongo_database, return_region_for_cli
from dsa_helpers.mongo_utils import add_many_to_collection
import json, hashlib
from girder_client import HttpError
from girder_client import GirderClient

DSA_JOB_STATUS = {
    0: "Inactive",
    1: "Queued",
    2: "Running",
    3: "Success",
    4: "Error",
    5: "Canceled",
}


def compare_doc_params(doc, params):
    """Compare the parameters of a document with a dictionary of parameters.
    Note that this checks that every key / value pair in params appers in the
    doc parameter dictionary. The doc may have additional keys in its parameter
    dictionary that do not appear in params, but that is not checked.

    """
    # Check that every key in params has the same value in doc.
    doc_params = (
        doc.get("annotation", {}).get("attributes", {}).get("params", {})
    )

    for key, value in params.items():
        if key in doc_params:
            if doc_params[key] == value:
                continue

        return False

    return True


def check_job_status(gc, task_id):
    """Check the status of a job."""
    # Check the status of the job.
    try:
        task_status = gc.get(f"job/{task_id}")["status"]

        return DSA_JOB_STATUS[task_status]
    except HttpError as e:
        # Could not get the task status of this job, return it as missing.
        return "Error"


def submit_cli(gc, cli_metadata, user, params, item, output_fld_id):
    """Submit a CLI task."""
    # Avoid referencing the params.
    params = params.copy()

    request_url = f"slicer_cli_web/cli/{cli_metadata['_id']}/run"

    # Get mongo database.
    mongo_db = get_mongo_database(user)

    # Check if region is part of the params.
    if "region_name" in params:
        region_name = params["region_name"]

        if len(region_name):
            # Must check mongodb for this annotation document(s) to create the
            # region of analysis parameter.
            annotation_collection = get_mongo_database(user)["annotations"]

            # Look for documents for this item and region name.
            annotation_docs = list(
                annotation_collection.find(
                    {"itemId": item["_id"], "annotation.name": region_name}
                )
            )

            if not len(annotation_docs):
                # Look in the DSA for annotation docs.
                annotation_docs = gc.get(
                    "annotation",
                    parameters={
                        "itemId": item["_id"],
                        "name": region_name,
                        "limite": 0,
                    },
                )

                # Get the full annotations.
                annotation_docs = [
                    gc.get(f"annotation/{doc['_id']}")
                    for doc in annotation_docs
                ]

                if len(annotation_docs):
                    # Add these to the database.
                    _ = add_many_to_collection(
                        annotation_collection, annotation_docs
                    )

            if len(annotation_docs):
                region = return_region_for_cli(annotation_docs)

                if region == "[]":
                    return "Doc found but no valid regions."
                else:
                    # Convert and add the region to the params.
                    params["region"] = region
            else:
                return {"status": "Error", "job_id": None}
        else:
            # Should do the whole image.
            params["region"] = "[-1, -1, -1, -1]"

    # Submit the CLI.
    try:
        # Add needed parameters outside of the CLI panel.
        params["inputImageFile"] = item["largeImage"]["fileId"]
        params["outputAnnotationFile_folder"] = output_fld_id
        params["outputLabelImage_folder"] = output_fld_id

        serialized_params = json.dumps(params, sort_keys=True)

        # Hash the serialized string using SHA-256
        unique_key = hashlib.sha256(serialized_params.encode()).hexdigest()

        params["outputAnnotationFile"] = f"{unique_key}.anot"
        params["outputLabelImage"] = f"{unique_key}.tiff"

        response = gc.post(request_url, data=params)
        return {
            "job_id": response["_id"],
            "status": DSA_JOB_STATUS[response["status"]],
        }
    except HttpError as e:
        return {"status": "Error", "job_id": None}


def look_for_doc(
    gc: GirderClient, item_id: str, params: dict, annotation_collection
):
    """Look for annotation document for item that has the params of the CLI.

    Args:
        gc (girder_client.GirderClient): The GirderClient instance.
        item_id (str): The item id.
        params (dict): The parameters of the CLI.
        annotation_collection: The Mongo database collection for
            the annotations.

    Returns:
        bool: True if the document was found, False otherwise.
        str: The document id if found, None otherwise.

    """
    # Look for annotation docs in the database.
    ann_docs = list(
        annotation_collection.find(
            {"itemId": item_id, "annotation.name": params["docname"]}
        )
    )

    # Check each document for matching parameters.
    for doc in ann_docs:
        if compare_doc_params(doc, params):
            return True, doc["_id"]

    # It was not found, query the DSA for the annotations.
    ann_docs = []

    for doc in gc.get(
        "annotation",
        parameters={"itemId": item_id, "name": params["docname"], "limit": 0},
    ):
        # Check if params match.
        if compare_doc_params(doc, params):
            # Get the full annotation.
            ann_docs.append(gc.get(f"annotation/{doc['_id']}"))

            # Add to the database.
            _ = add_many_to_collection(annotation_collection, ann_docs)
            return True, doc["_id"]

    if len(ann_docs):
        # Add the documents obtained to the database, even though they are not the matching ones.
        _ = add_many_to_collection(annotation_collection, ann_docs)

    return False, None
