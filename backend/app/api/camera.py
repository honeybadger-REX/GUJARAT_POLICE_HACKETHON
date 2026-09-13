import mysql.connector
import httpx
import subprocess
from fastapi import APIRouter

MEDIAMTX_API = "http://127.0.0.1:9997"
MEDIAMTX_WEBRTC = "http://127.0.0.1:8889"  # browser-facing WebRTC player (MediaMTX serves this itself)

router = APIRouter()


# ---------------------------------------------
# DB CONNECTION — one NEW connection per request.
# A single shared global cursor breaks under concurrent
# requests (Commands out of sync). This is still a prototype
# pattern — a real connection pool (see guide's database/connection.py)
# is the next step, but this alone fixes the intermittent 500s.
# ---------------------------------------------
def get_db():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="gujarat_police"
    )
    return conn


@router.get("/")
def get_camera():
    return {"message": "Camera API"}


# ---------------------------------------------
# DASHBOARD — GET /cameras (per setup guide section 12)
# Joins camera + vendor so the operator doesn't have to pick
# a vendor just to see the camera list.
# ---------------------------------------------
@router.get("/cameras")
def list_all_cameras():
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT c.CameraID, c.CameraName, c.VendorID, v.VendorName, c.enable
            FROM camera c
            JOIN vendor v ON v.VendorID = c.VendorID
            ORDER BY c.CameraID
        """)
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return [
        {
            "CameraID": row[0],
            "CameraName": row[1],
            "VendorID": row[2],
            "VendorName": row[3],
            "status": "ONLINE" if row[4] else "OFFLINE"
        }
        for row in rows
    ]


# ---------------------------------------------
# START — creates the MediaMTX path, returns the WebRTC
# playback URL so the frontend has something to actually render.
# ---------------------------------------------
@router.post("/camera/{camera_id}/start")
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


@router.get("/camera/{camera_id}/stream")
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


@router.post("/camera/{camera_id}/stop")
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


def check_camera(url: str) -> str:
    """FFmpeg RTSP health check. 5s of stream requested, 15s hard timeout."""
    command = [
        "ffmpeg",
        "-rtsp_transport", "tcp",
        "-i", url,
        "-t", "5",
        "-f", "null",
        "-"
    ]
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=15
        )
        return "ONLINE" if result.returncode == 0 else "OFFLINE"
    except subprocess.TimeoutExpired:
        return "OFFLINE"