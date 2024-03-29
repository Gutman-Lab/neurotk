from girder_client import GirderClient, HttpError
from pprint import pprint
from copy import deepcopy
from pymongo.database import Database

from utils.utils import (
    get_current_user,
    get_gc,
    get_annotation_docs,
    convert_elements_to_regions,
)
from utils.mongo_utils import get_mongo_client, add_one_to_collection


def submit_cli_job(
    cli: str,
    item_id: str,
    params: dict,
    gc: GirderClient | None = None,
    user: str | None = None,
    roi: str | None = None,
    rerun: bool = False,
):
    """Submit one of the CLI tasks.

    Args:
        cli: The CLI name to submit.
        item_id: DSA item id. .
        params: Parameters to submit with CLI.
        gc: The GirderClient to use. Default is None and will be obtained.
        user: The user currently used.
        roi: Annotation document to use for region of analysis.
        rerun: If True, will rerun the CLI task if it had prevously failed.

    """
    # Get girder client and the user if not provided.
    if gc is None:
        gc = get_gc()

    if user is None:
        user = get_current_user()[1]

    # Check the queue collection if a task for this item and parameteres has been submitted.
    queue_collection = get_mongo_client()["girderQueue"]
    records = list(
        queue_collection.find({"params": params, "itemId": item_id, "roi": roi})
    )

    if records:
        # There are records for this.
        for record in records:
            # Get the status from database.
            status = record.get("status")

            """Status map:
            0: inactive = delete from mongo and run
            1: queued = check againskip
            2: running = skip
            3: success = skip
            4: error = delete from mongo and run
            5: cancelled = delete from mongo and run
            """
            if status is None or status not in (3, 4, 5):
                # Get the job response.
                job_response = gc.get(f"job/{record['_id']}")
                status = job_response.get("status")

            if status in (4, 5):
                # Failed to run.
                if rerun:
                    # Delete and run it again.
                    queue_collection.delete_one({"_id": record["_id"]})
                else:
                    if status == 4:
                        return {"status": "error", "girderResponse": job_response}
                    else:
                        return {"status": "cancelled", "girderResponse": job_response}
            elif status == 0:
                return {"status": "inactive", "girderResponse": job_response}
            elif status == 3:
                return {"status": "success", "girderResponse": job_response}
            elif status == 1:
                return {"status": "queued", "girderResponse": job_response}
            elif status == 2:
                return {"status": "running", "girderResponse": job_response}

    kwargs = dict(
        item_id=item_id,
        params=params,
        mongo_collection=get_mongo_client()["annotations"],
        user=user,
        gc=gc,
        roi=roi,
    )

    if cli in ("TissueSegmentation", "TissueSegmentationV2"):
        # These are CLIs that follow standard conventions for analysis that does not use ROI as input.
        kwargs["cli_api"] = f"slicer_cli_web/jvizcar_neurotk_latest/{cli}/run"

        return submit_non_roi_task(**kwargs)
    elif cli == "PositivePixelCount":
        # PPC is a unique case, because it always outputs a doc of the same name, but can also use input area.
        kwargs["cli_api"] = (
            "slicer_cli_web/dsarchive_histomicstk_latest/PositivePixelCount/run"
        )

        return submit_ppc_task(**kwargs)

    print("CLI not found.")
    return {"status": "not a valid CLI", "girderResponse": None}


def submit_non_roi_task(
    cli_api: str,
    item_id: str,
    params: dict,
    gc: GirderClient,
    mongo_collection,
    user: str,
    roi: str | None = None,
) -> dict:
    """Submit tissue detection CLI to set of images."""
    # Check if the output annotation doc exists, first in Mongo then in DSA.
    records = list(
        mongo_collection.find({"user": user, "params": params, "itemId": item_id})
    )

    if records:
        # Found so return it!
        return {"status": "exists", "girderResponse": None}

    # Request annotation docs from DSA and check if the params are the same.
    annotation_docs = get_annotation_docs(gc, item_id, name=params["docname"])

    # The params should be the same.
    for doc in annotation_docs:
        doc_params = doc.get("annotation", {}).get("attributes", {}).get("params", {})

        doc_dict = {k: doc_params[k] for k in params if k in doc_params}

        if doc_dict == params:
            # Found it, add it to database and return.
            doc["params"] = params

            add_one_to_collection("annotations", doc, user=user)

            return {"status": "exists", "girderResponse": None}

    # Could not find it anywhere, so submit the job.
    item = gc.get(f"item/{item_id}")

    cliInputData = {
        "in_file": item["largeImage"]["fileId"],  # WSI ID
        "tissueAnnotationFile": f"{item['name']}_tissue-detection.anot",
        "tissueAnnotationFile_folder": "6512fb223c737ca0f21dab57",
    }
    cliInputData.update(params)

    try:
        girder_response = gc.post(cli_api, data=cliInputData)

        # Add this the girderQueue database.
        girder_response["params"] = params
        girder_response["itemId"] = item_id
        girder_response["roi"] = roi

        add_one_to_collection("girderQueue", girder_response, user=user)

        return {"status": "submitted", "girderResponse": girder_response}

    except HttpError as e:
        # Failed, return the error.
        return {"status": "error", "girderResponse": e.response.json()}


def check_for_doc(
    mongo_collection: Database,
    gc: GirderClient,
    item_id: str,
    docname: str,
    user: str,
    params: dict | None = None,
    roi: str | None = None,
) -> dict | None:
    """Check the database for an annotation document, pull from DSA is not found.

    Args:
        mongo_collection (pymongo.database.Database): The mongo collection to check for document.
        gc (girdler_client.GirderClient): The GirderClient to use.
        item_id (str): The DSA item id to check.
        docname (str): The name of the annotation document.
        user (str): The user to check for.
        params (dict): The parameters to check for, to get specific version of document. Defaults to None.
        roi (str): The region of interest to check for. Defaults to None.

    Returns:
        dict | None: The annotation document if found, None otherwise.

    """
    # Search for the document.
    search_query = {"annotation.name": docname, "itemId": item_id, "user": user}

    if params:
        search_query["annotation.attributes.params"] = params

    if roi:
        search_query["roi"] = roi

    records = list(mongo_collection.find(search_query))

    if records:
        # NOTE: this function does not account for finding multiple documents that match the query.
        return records[0]
    else:
        # Look in the DSA for the document.
        print("Looking for roi document", docname)
        annotation_docs = gc.get(
            f"annotation?itemId={item_id}&name={docname}&limit=0&offset=0&sort=lowerName&sortdir=1"
        )

        if annotation_docs:
            print("There are some docs to look for!")
            for doc in annotation_docs:
                # Get params from the annotation document.
                doc_params = (
                    doc.get("annotation", {}).get("attributes", {}).get("params", {})
                )

                # Filter by roi if it was given.
                if params:
                    param_flag = False

                    # Check if the params given match.
                    for k, v in params.items():
                        if doc_params.get(k) != v:
                            param_flag = True
                            break

                    if param_flag:
                        continue

                add_one_to_collection("annotations", doc, user=user)
                doc["user"] = user

                return doc

        return None


def check_doc_for_elemenets(
    mongo_collection: Database, gc: GirderClient, doc: dict, user: str
) -> dict:
    """Check an annotation document for elements.

    Args:
        mongo_collection (pymongo.database.Database): The mongo collection, for updating record.
        gc (girdler_client.GirderClient): The GirderClient to use, to pull the elements.
        doc (dict): The annotation document to check.
        user (str): The user to check for.

    Returns:
        dict: The updated annotation document.

    """
    elements = doc.get("annotation", {}).get("elements")

    if elements:
        return doc
    else:
        # Pull the elements from the DSA.
        doc = gc.get(f"annotation/{doc['_id']}?offset=0&sort=_id&sortdir=1")

        # Update the database.
        add_one_to_collection("annotations", doc, user=user)

        return doc


def submit_ppc_task(
    cli_api: str,
    item_id: str,
    params: dict,
    gc: GirderClient,
    mongo_collection,
    user: str,
    roi: str | None = None,
) -> dict:
    """Submit a PPC CLI task."""
    # Check if database has ROI points.
    record = check_for_doc(mongo_collection, gc, item_id, roi, user)

    if record:
        # Found the record, get it with elements.
        record = check_doc_for_elemenets(mongo_collection, gc, record, user)

        # Now format the elements to submit as the region in CLI.
        regions = convert_elements_to_regions(
            record.get("annotation", {}).get("elements", [])
        )

        item = gc.getItem(item_id)

        # CLI inputs for PPC.
        cliInputData = {
            "inputImageFile": item["largeImage"]["fileId"],
            "outputLabelImage": f"{item['name']}_ppc.tiff",
            "outputLabelImage_folder": "645a5fb76df8ba8751a8dd7d",
            "outputAnnotationFile": f"{item['name']}_ppc.anot",
            "outputAnnotationFile_folder": "645a5fb76df8ba8751a8dd7d",
            "returnparameterfile": f"{item['name']}_ppc.params",
            "returnparameterfile_folder": "645a5fb76df8ba8751a8dd7d",
        }
        cliInputData.update(params)
        cliInputData["region"] = regions

        try:
            girder_response = gc.post(cli_api, data=cliInputData)

            # Add this the girderQueue database.
            girder_response["params"] = params
            girder_response["itemId"] = item_id
            girder_response["roi"] = roi

            add_one_to_collection("girderQueue", girder_response, user=user)

            return {"status": "submitted", "girderResponse": girder_response}
        except HttpError as e:
            # Failed, return the error.
            return {"status": "error", "girderResponse": e.response.json()}
    else:
        return {"status": "missing roi", "girderResponse": None}

    # if records:
    #     # An annotation document with the ROI name exists, check if the points have been pulled.
    #     record = records[0]

    #     if not record.get("annotation", {}).get("elements"):
    #         # The elements are not there - so get them.
    #         elements =

    #     # Format the annotation elements into points to pass as the region parameter.
    #     regions = convert_elements_to_regions(record["annotation"]["elements"])

    # return {"status": "success", "girderResponse": None}

    # # Check if the output annotation doc is in the Mongo database.
    # records = list(
    #     mongo_collection.find({"user": user, "params": params, "itemId": item_id})
    # )

    # if records:
    #     # It is in database, return this message.
    #     return {"status": "exists", "girderResponse": None}

    # # Try to find it in DSA, note that PPC CLI from HistomicsTK always creates a doc of the same name.
    # annotation_docs = get_annotation_docs(gc, item_id, name="Positive Pixel Count")

    # for doc in annotation_docs:
    # Params will not match

    # points = "[5000,5000,1000,1000]"

    #
    # item = gc.get(f"item/{data['_id']}")

    # cliInputData = {
    #     "inputImageFile": item["largeImage"]["fileId"],
    #     "outputLabelImage": f"{item['name']}_ppc.tiff",
    #     "outputLabelImage_folder": "645a5fb76df8ba8751a8dd7d",
    #     "outputAnnotationFile": f"{item['name']}_ppc.anot",
    #     "outputAnnotationFile_folder": "645a5fb76df8ba8751a8dd7d",
    #     "returnparameterfile": f"{item['name']}_ppc.params",
    #     "returnparameterfile_folder": "645a5fb76df8ba8751a8dd7d",
    # }

    # # The region should not be estimated like this!
    # cliInputData.update(params)
    # # cliInputData["region"] = points

    # if mask_name is None:
    #     pass
    #     # NOTE: get the tile source and run on entire area.
    # else:
    # Get the points based on the annotation, if it exists only though!

    # if maskName:
    # print("Should be fetching point set from", maskName, "for", item["_id"])
    ## Lookup annotation data for this image..
    # print(item)
    ## TO DO.. what if there is more than one mask with the same name.. to be fixed
    # maskPointSet = dbConn["annotationData"].find_one(
    #     {"itemId": item["_id"], "annotation.name": maskName},
    #     {"annotation.elements": 1},
    # )

    # if maskPointSet:
    #     maskRegionPoints = get_points(maskPointSet["annotation"]["elements"])

    #     cliInputData["region"] = maskRegionPoints
    #         else:
    #             return {
    #                 "status": "FAILED",
    #                 "girderResponse": {"status": "JobSubmitFailed"},
    #             }

    # except KeyError:
    #     return {"status": "FAILED", "girderResponse": {"status": "JobSubmitFailed"}}

    # record = lookup_job_record(cliInputData, USER)

    # if record:
    #     return {"status": "CACHED", "girderResponse": None}
    # else:
    #     jobSubmission_response = gc.post(ppc_ext, data=cliInputData)

    #     jobSubmission_response["user"] = USER

    #     dbConn["dsaJobQueue"].insert_one(jobSubmission_response)

    #     return {"status": "SUBMITTED", "girderResponse": jobSubmission_response}


# def submit_nft_inference(data, params, maskName):
#     """Submit tissue detection CLI to set of images."""
#     cli_ext = "slicer_cli_web/jvizcar_neurotk_latest/NFTDetection/run"

#     try:
#         item = gc.get(f"item/{data['_id']}")

#         cliInputData = {
#             "in_file": item["largeImage"]["fileId"],  # WSI ID
#             "tissueAnnotationFile": f"{item['name']}_tissue-detection.anot",
#             "tissueAnnotationFile_folder": "6512fb223c737ca0f21dab57",
#         }
#         cliInputData.update(params)

#         if maskName:
#             # print("Should be fetching point set from", maskName, "for", item["_id"])
#             ## Lookup annotation data for this image..
#             # print(item)
#             ## TO DO.. what if there is more than one mask with the same name.. to be fixed
#             maskPointSet = dbConn["annotationData"].find_one(
#                 {"itemId": item["_id"], "annotation.name": maskName},
#                 {"annotation.elements": 1},
#             )

#             if maskPointSet:
#                 maskRegionPoints = get_points(maskPointSet["annotation"]["elements"])

#                 cliInputData["region"] = maskRegionPoints
#             else:
#                 return {
#                     "status": "FAILED",
#                     "girderResponse": {"status": "JobSubmitFailed"},
#                 }

#     except KeyError:
#         return {"status": "FAILED", "girderResponse": {"status": "JobSubmitFailed"}}
#         ## TO DO Figure out how we want to report these...

#     if not lookup_job_record(cliInputData, USER):
#         jobSubmission_response = gc.post(cli_ext, data=cliInputData)
#         ## Should I add the userID here as well?

#         jobSubmission_response["user"] = USER

#         dbConn["dsaJobQueue"].insert_one(jobSubmission_response)
#         return {"status": "SUBMITTED", "girderResponse": jobSubmission_response}

#     else:
#         # print("Job  was already submitted")
#         # JC: jobCached_info is not even defined!
#         # return {"status": "CACHED", "girderResponse": jobCached_info}
#         return {"status": "CACHED", "girderResponse": None}
