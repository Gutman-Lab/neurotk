from girder_client import GirderClient


def submit_cli_job(gc: GirderClient, task: str, data: list, params: dict, mask: str):
    if task == "PositivePixelCount":
        submit_ppc_job(gc, data, params, mask)
    else:
        print(f'Task "{task}" is not currently supported.')


def submit_ppc_job(gc, data, params, mask_name=None):
    ppc_ext = "slicer_cli_web/dsarchive_histomicstk_latest/PositivePixelCount/run"

    # points = "[5000,5000,1000,1000]"

    # try:
    item = gc.get(f"item/{data['_id']}")

    cliInputData = {
        "inputImageFile": item["largeImage"]["fileId"],
        "outputLabelImage": f"{item['name']}_ppc.tiff",
        "outputLabelImage_folder": "645a5fb76df8ba8751a8dd7d",
        "outputAnnotationFile": f"{item['name']}_ppc.anot",
        "outputAnnotationFile_folder": "645a5fb76df8ba8751a8dd7d",
        "returnparameterfile": f"{item['name']}_ppc.params",
        "returnparameterfile_folder": "645a5fb76df8ba8751a8dd7d",
    }

    # The region should not be estimated like this!
    cliInputData.update(params)
    # cliInputData["region"] = points

    if mask_name is None:
        pass
        # NOTE: get the tile source and run on entire area.
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


# def submit_tissue_detection(data, params, selected_task):
#     """Submit tissue detection CLI to set of images."""
#     cli_ext = f"slicer_cli_web/jvizcar_neurotk_latest/{selected_task}/run"

#     try:
#         item = gc.get(f"item/{data['_id']}")

#         cliInputData = {
#             "in_file": item["largeImage"]["fileId"],  # WSI ID
#             "tissueAnnotationFile": f"{item['name']}_tissue-detection.anot",
#             "tissueAnnotationFile_folder": "6512fb223c737ca0f21dab57",
#         }
#         cliInputData.update(params)

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
