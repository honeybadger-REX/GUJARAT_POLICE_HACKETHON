from ...database.connection import mongodb
from gridfs import GridFS
import cv2
import datetime

x = datetime.datetime.now()



mongo = mongodb["CCTV_vehicle"]
fs = GridFS(mongo)


def vehicle_storage(dicts):

    # Generate auto-increment frame ID
    result = mongo.counters.find_one_and_update(
        {"_id": "vehicale_id"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    year = x.strftime("%Y")
    month = x.strftime("%b")
    time = x.strftime("/H")

    vehicle_id = result["sequence_value"]

    # Convert OpenCV frame to JPEG bytes
    success, buffer = cv2.imencode(".jpg", dicts["vehicleframe"])

    if not success:
        raise ValueError("Could not encode frame")

    # Store image in GridFS
    gridfs_id = fs.put(
        buffer.tobytes(),
        filename=f"{dicts["cam_id"]}_{vehicle_id}_{year}_{month}_{time}.jpg",
        cam_id=dicts["cam_id"],
        vehicle_id= vehicle_id
    )

    # Store metadata
    mongo.frames.insert_one({
        "vehicle_id": vehicle_id,
        "cam_id": dicts["cam_id"],
        "confidence": dicts["conf"],
        "class_name":dicts["class"],
        "bbox":dicts["bbox"],
        "gridfs_id": gridfs_id
    })

    return vehicle_id,dicts["cam_id"]

