from ...database.connection import mongodb
from gridfs import GridFS
import cv2
import datetime

x = datetime.datetime.now()



mongo = mongodb["CCTV_face"]
fs = GridFS(mongo)


def frame_storage(frame, cam_id):

    # Generate auto-increment frame ID
    result = mongo.counters.find_one_and_update(
        {"_id": "frame_id"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    year = x.strftime("%Y")
    month = x.strftime("%b")
    time = x.strftime("/H")

    frame_id = result["sequence_value"]

    # Convert OpenCV frame to JPEG bytes
    success, buffer = cv2.imencode(".jpg", frame)

    if not success:
        raise ValueError("Could not encode frame")

    # Store image in GridFS
    gridfs_id = fs.put(
        buffer.tobytes(),
        filename=f"{cam_id}_{frame_id}_{year}_{month}_{time}.jpg",
        cam_id=cam_id,
        frame_id=frame_id
    )

    # Store metadata
    mongo.frames.insert_one({
        "frame_id": frame_id,
        "cam_id": cam_id,
        "gridfs_id": gridfs_id
    })

    return frame_id