
from utils.dsaHelperFunctions import get_item_large_image_metadata, get_thumbnail, get_region
from girder_client import GirderClient
import argparse
import histomicstk.segmentation.positive_pixel_count as ppc
import large_image
import json


#https://digitalslidearchive.github.io/HistomicsTK/examples/positive_pixel_count.html
params= {
    'hue_value': 0.05,
    'hue_width':0.15,
    'saturation_minimum': 0.05,
    'intensity_upper_limit': 0.95,
    'intensity_weak_threshold':0.65,
    'intensity_strong_threshold':0.35,
    'intensity_lower_limit':0.05}


def runPPC(imgROI, ppcParamsDict):
    # Convert the dictionary of parameters to a Parameters object
    ppcParams = ppc.Parameters(
        hue_value=ppcParamsDict["hue_value"],
        hue_width=ppcParamsDict["hue_width"],
        saturation_minimum=ppcParamsDict["saturation_minimum"],
        intensity_upper_limit=ppcParamsDict["intensity_upper_limit"],
        intensity_weak_threshold=ppcParamsDict["intensity_weak_threshold"],
        intensity_strong_threshold=ppcParamsDict["intensity_strong_threshold"],
        intensity_lower_limit=ppcParamsDict["intensity_lower_limit"],
    )

    # Run the positive pixel count algorithm
    ppcResult, ppcOutputImage = ppc.count_image(imgROI, ppcParams)

    return ppcResult, ppcOutputImage
    


# ------------------------------------
#  WSI PPC Computation Tile Approach
# ------------------------------------

def run_wsi_roi_ppc(img_type:str, unique_id:str):
    """ 
    Run ppc on either WSI or a Region of the wsi. 
    args:
        - image_type: wsi or roi
        - unique_id: uid as found in dsa 
    output:
        - saves results as txt according to the uid.
    """
    
    dsaBaseURL = "https://wsi-deid.pathology.emory.edu/api/v1/"
    #dsaBaseURL = "https://megabrain.neurology.emory.edu/api/v1/"
    identification = unique_id# '6477c032309a9ffde668964a'

    gc = GirderClient(apiUrl=dsaBaseURL)
    meta_dict = get_item_large_image_metadata(gc, item_id=identification)# 642603e023a7e18ea331d7fd 6477c038309a9ffde6689686
    print(meta_dict)

    img = get_thumbnail(
        gc,
        item_id=identification,# 642603e023a7e18ea331d7fd 6477c038309a9ffde6689686
    ) 

    print(img.shape)
    if img_type == 'roi':
        left=700
        top=700
        width=200
        height=200
    else:
        left=0
        top=0
        width=500000
        height=500000
        
    small_roi = get_region(
        gc,
        item_id=identification, #642603e023a7e18ea331d7fd 6477c038309a9ffde6689686
        left=left,
        top=top,
        width=width,
        height=height
    )
    print(small_roi.shape)

    ppc_result, ppc_output_image = runPPC(small_roi, params)

    print(ppc_result, ppc_output_image.shape)
    with open(f"results/{unique_id}_result.txt", "w")as writer:
        writer.write(str(ppc_result))
       


def main():

    parser = argparse.ArgumentParser(description="PPC processing.")

    # Add the arguments
    parser.add_argument('-t','--type_image', type=str, choices=['wsi', 'roi'],
		            help='Type of the image (wsi or region)')
    parser.add_argument('-id','--unique_id', type=str,
		            help='Unique ID')
    # Parse the arguments
    args = parser.parse_args()
    img_type = args.type_image
    unique_id = args.unique_id
    run_wsi_roi_ppc(img_type, unique_id)
    '''
    # ------------------------------------
    #  WSI PPC Computation Full SVS Approach
    # ------------------------------------
    
    region = dict(
        left=5000, top=5000,#left=5000, top=5000
        width=2500, height=2500,#width=2500, height=2500
    )

    templateParams = ppc.Parameters(**params)
    print(f"Params: {templateParams}")

    ppc_Output = ppc.count_slide("./A21-29_1_ABETA.svs",templateParams)
    print(ppc_Output)
    with open(f"results/{unique_id}_result.txt", "w")as writer:
        writer.write(str(ppc_Output))
    #smallRegion_ppcOutput= ppc.count_slide("./A21-29_1_ABETA.svs",templateParams,)#region=region
    #print(smallRegion_ppcOutput)
    '''

if __name__ == "__main__":
    main()
    

   
