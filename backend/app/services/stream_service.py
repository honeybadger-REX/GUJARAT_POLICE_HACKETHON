import mysql.connector
import httpx
import subprocess
from fastapi import APIRouter
from ..database.connection import get_db

MEDIAMTX_API = "http://gujarat_police_mediamtx:9997"
MEDIAMTX_WEBRTC = "http://127.0.0.1:8889"  # browser-facing WebRTC player (MediaMTX serves this itself)

router = APIRouter()



#----------------------------------
# VENDOR START 
#----------------------------------


async def start_camera(camera_id: int):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT CameraName, CameraURL FROM camera WHERE CameraID = %s",
            (camera_id,)
        )
        camera = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if camera is None:
        return {"message": "Camera not found"}

    camera_name = camera[0]
    camera_url = camera[1]
    stream_name = camera_name.lower()

    mediamtx_data = {
        "source": camera_url,
        "rtspTransport": "tcp"
    }

    async with httpx.AsyncClient() as client:
        # Idempotent-ish: if the path already exists, MediaMTX returns
        # an error here (see guide's troubleshooting table, "Path already
        # exists"). Treat that case as success instead of failing the request.
        response = await client.post(
            f"{MEDIAMTX_API}/v3/config/paths/add/{stream_name}",
            json=mediamtx_data
        )

    path_already_existed = response.status_code == 400 and "already exists" in response.text.lower()

    if response.status_code not in (200, 201) and not path_already_existed:
        return {
            "message": "Failed to create MediaMTX stream",
            "status_code": response.status_code,
            "response": response.text
        }

    return {
        "message": "Camera stream started",
        "camera_id": camera_id,
        "camera_name": camera_name,
        "stream_name": stream_name,
        "webrtc_url": f"{MEDIAMTX_WEBRTC}/{stream_name}/"
    }

#----------------------------------------
# VENDOR STREAM 
#---------------------------------------



def get_camera_stream(camera_id: int):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT CameraName FROM camera WHERE CameraID = %s",
            (camera_id,)
        )
        camera = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if camera is None:
        return {"message": "Camera not found"}

    camera_name = camera[0]
    stream_name = camera_name.lower()

    return {
        "camera_id": camera_id,
        "camera_name": camera_name,
        "stream_name": stream_name,
        "protocol": "webrtc",
        "webrtc_url": f"{MEDIAMTX_WEBRTC}/{stream_name}/"
    }


#-----------------------------------------
#  VENDOR STOP
#---------------------------------------



async def stop_camera(camera_id: int):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT CameraName, CameraURL FROM camera WHERE CameraID = %s",
            (camera_id,)
        )
        camera = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if camera is None:
        return {"message": "Camera not found"}

    camera_name = camera[0]
    stream_name = camera_name.lower()

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{MEDIAMTX_API}/v3/config/paths/delete/{stream_name}"
        )

    if response.status_code not in (200, 201):
        return {
            "message": "Failed to stop MediaMTX stream",
            "status_code": response.status_code,
            "response": response.text
        }

    return {
        "message": "Camera stream stopped",
        "camera_id": camera_id,
        "camera_name": camera_name,
        "stream_name": stream_name
    }


