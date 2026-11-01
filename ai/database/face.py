from ...database.connection import mongodb

from gridfs import GridFS
from pymongo import ReturnDocument
from datetime import datetime


mongo = mongodb["CCTV_face"]
fs = GridFS(mongo)


def face_storage(name, cam_id, vehicle_id):

    # -----------------------------
    # 1. Generate face_id
    # -----------------------------
    result = mongo.counters.find_one_and_update(
        {"_id": "face_id"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )

    face_id = result["sequence_value"]

    # -----------------------------
    # 2. Store face image in GridFS
    # -----------------------------
    face_image = name["face"]

    gridfs_id = fs.put(
        face_image,
        filename=f"{cam_id}_{face_id}.jpg",
        face_id=face_id,
        vehicle_id=vehicle_id,
        cam_id=cam_id
    )

    # -----------------------------
    # 3. Store face information
    # -----------------------------
    mongo.face_raw.insert_one({

        "face_id": face_id,

        "vehicle_id": vehicle_id,

        "cam_id": cam_id,

        "detected": True,

        "face_encoding": name["face_dimension"]["encoding"],

        "recognition_status": name["status"],

        "confidence": name["confidence"],

        "bbox": name["face_dimension"]["bbox"],

        "gridfs_id": gridfs_id,

        "timestamp": datetime.utcnow()
    })

    return face_id