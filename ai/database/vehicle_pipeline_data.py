from ...database.connection import mongodb ,mongo_image
from gridfs import GridFS
import cv2
import datetime

x = datetime.datetime.now()
# mongo_image(dicts:dict,frame:str,year,month,time,id:str)
mongo = mongodb["vehicle_pipeline_data"]
def vehicle_pipeline_storage(dicts):
    dicts["eveidnce"]
    year = x.strftime("%Y")
    month = x.strftime("%b")
    time = x.strftime("/H")
    

{
    "camera_id": "CAM_001",
    "frame_id": 100,

    "vehicles": [
        {
            "detection_id": "V001",
            "vehicle": {...},
            "helmet": [...],
            "face": [...],
            "event": None,
            "evidence": {
                "vehicle_frame": "...",
                "helmet_frames": [],
                "face_frames": []
            }
        }
    ]
}