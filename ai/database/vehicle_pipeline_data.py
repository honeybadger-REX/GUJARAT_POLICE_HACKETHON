from ...database.connection import mongodb
from gridfs import GridFS
import cv2
import datetime

x = datetime.datetime.now()

mongo = mongodb["vehicle_pipeline_data"]
def vehicle_pipeline_storage(dicts):
    dicts["eveidnce"]

