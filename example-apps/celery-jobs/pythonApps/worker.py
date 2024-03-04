from os import getenv
from celery import Celery
from girder_client import GirderClient
import numpy as np
from PIL import Image
from io import BytesIO
import cv2 as cv
from os.path import join

celery = Celery(__name__)
celery.conf.broker_url = getenv("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379")


@celery.task(name="download_thumbnail")
def download_thumbnail(item_id: str):
    """This is a Celery task that will get a thumbnail from the DSA and save it to the filesystem."""
    item = gc.get(item_id)

    gc = GirderClient(apiUrl=getenv("DSA_API_URL"))
    gc.authenticate(apiKey=getenv("DSA_API_KEY"))

    request = f"item/{item_id}/tiles/region?units=base_pixels&magnification=1.25&exact=false&encoding=JPEG&jpegQuality=95&jpegSubsampling=0"

    thumbnail = np.array(Image.open(BytesIO(gc.get(request, jsonResp=False).content)))

    # Save the thumbnail to file.
    cv.imwrite(join("thumbnails", item["name"]), cv.COLOR_RGB2BGR)

    return True
