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

PIE_CHART_COLORS = dict(
    error="rgb(255, 0, 0)",
    cancelled="rgb(209, 207, 202)",
    inactive="rgb(0, 255, 238)",
    success="rgb(14, 153, 0)",
    queued="rgb(0, 141, 255)",
    running="rgb(0, 0, 255)",
    exists="rgb(181, 215, 0)",
    Submitted="rgb(255, 217, 0)",
)

COLORS = {
    "COOL_GRAY_1": "#d9d9d6",
    "EMORY_BLUE": "#012169",
    "LIGHT_BLUE": "#007dba",
    "YELLOW": "#f2a900",
}