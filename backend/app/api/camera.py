import mysql.connector
import httpx
from fastapi import FastAPI ,APIRouter
import subprocess
from concurrent.futures import ThreadPoolExecutor
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MEDIAMTX_API = "http://127.0.0.1:9997"



#----------------------------------------------
#DATA BASE CONECTION 
#---------------------------------------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="gujarat_police"
)

cursor = conn.cursor()

router = APIRouter()

@router.get("/")
def get_camera():
    return {
        "message": "Vendors API"
    }


#---------------------------------------------
# CAMERA API
#---------------------------------------------

@router.post("/camera/{camera_id}/start")
async def start_camera(camera_id:int):

    cursor.execute("""select CameraName, CameraURL from camera where CameraID = %s""",(camera_id,))

    camera = cursor.fetchone()

    if camera is None:
        return {
            "message":"camera not  found"
        }

    camera_name = camera[0]
    camera_url = camera[1]
    stream_name = camera_name.lower()

    mediamtx_data = {
        "source": camera_url,
        "rtspTransport": "tcp"
    }

    async with httpx.AsyncClient() as client:

        response = await client.post(
            f"{MEDIAMTX_API}/v3/config/paths/add/{stream_name}",
            json=mediamtx_data
        )

    if response.status_code not in [200, 201]:

        return {
            "message": "Failed to create MediaMTX stream",
            "status_code": response.status_code,
            "response": response.text
        }

    return {
        "message": "Camera stream started",
        "camera_id": camera_id,
        "camera_name": camera_name,
        "stream_name": stream_name
    }

@router.get("/camera/{camera_id}/stream")
def get_camera_stream(camera_id: int):

    cursor.execute(
        """
        SELECT CameraName
        FROM camera
        WHERE CameraID = %s
        """,
        (camera_id,)
    )

    camera = cursor.fetchone()

    if camera is None:
        return {
            "message": "Camera not found"
        }

    camera_name = camera[0]
    stream_name = camera_name.lower()

    return {
        "camera_id": camera_id,
        "camera_name": camera_name,
        "stream_name": stream_name,
        "protocol": "webrtc"
    }




@router.post("/camera/{camera_id}/stop")
async def stop_camera(camera_id:int):

    cursor.execute("""select CameraName, CameraURL from camera where CameraID = %s""",(camera_id,))

    camera = cursor.fetchone()

    if camera is None:
        return {
            "message":"camera not  found"
        }

    camera_name = camera[0]
    camera_url = camera[1]
    stream_name = camera_name.lower()


    async with httpx.AsyncClient() as client:

        response = await client.delete(
            f"{MEDIAMTX_API}/v3/config/paths/delete/{stream_name}"
           
        )

    if response.status_code not in [200, 201]:

        return {
            "message": "Failed to stop MediaMTX stream",
            "status_code": response.status_code,
            "response": response.text
        }

    return {
        "message": "Camera stream stop",
        "camera_id": camera_id,
        "camera_name": camera_name,
        "stream_name": stream_name
    }


def check_camera(url):
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

        if result.returncode == 0:
            return "ONLINE"

        return "OFFLINE"

    except subprocess.TimeoutExpired:
        return "OFFLINE"

