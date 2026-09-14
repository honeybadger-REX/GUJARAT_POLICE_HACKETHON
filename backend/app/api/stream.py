import mysql.connector
import httpx
import subprocess
from fastapi import APIRouter
from ..services import stream_service
from pydantic import BaseModel

  # browser-facing WebRTC player (MediaMTX serves this itself)

router = APIRouter()


@router.get("/")
def get_streams():
    return {
        "message": "Streams API"
    }

#----------------------------------
# VENDOR START 
#----------------------------------


@router.post("/camera/{camera_id}/start")
async def start_camera(camera_id: int):
    stream_add = await stream_service.start_camera(camera_id)
    return {"ok" : True,"steaming_cam":stream_add}


#----------------------------------------
# VENDOR STREAM 
#---------------------------------------


@router.get("/camera/{camera_id}/stream")
def get_camera_stream(camera_id: int):
    stream_get = stream_service.get_camera_stream(camera_id)
    return {"ok" : True,"steaming_cam":stream_get}
    


#-----------------------------------------
#  VENDOR STOP
#---------------------------------------


@router.post("/camera/{camera_id}/stop")
async def stop_camera(camera_id: int):
    stream_stop = await stream_service.stop_camera(camera_id)
    return {"ok" : True,"steaming_cam":stream_stop}
  


