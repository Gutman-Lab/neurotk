# Configuration file for the application.
AVAILABLE_CLI_TASKS = {
    "TissueSegmentation": {
        "name": "TissueSegmentation",
        "dsa_name": "TissueSegmentation",
        "roi": False,
    },
    "TissueSegmentationV2": {
        "name": "TissueSegmentationV2",
        "dsa_name": "TissueSegmentationV2",
        "roi": False,
    },
    "PositivePixelCount": {
        "name": "Positive Pixel Count",
        "dsa_name": "PPC",
        "roi": True,
    },
    "NFTDetection": {"name": "NFTDetection", "dsa_name": "NFTDetection", "roi": True},
}
