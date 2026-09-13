import mysql.connector
import httpx
import subprocess
from pydantic import BaseModel
from fastapi import APIRouter
from ..database import camera_repository
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



#------------------------------------
#  GET CAMERA DETAIL
#-----------------------------------

@router.get("/")
def get_camera():
    return {"message": "Camera API" ,"Camera_list" :  camera_repository.get_cam_info()}


#---------------------------
# ADD CAMERA
#---------------------
class camADD(BaseModel):
    VendorID: int

@router.post("camera/add")
def add_cam(vendor:camADD):
    camera_added =  camera_repository.add_camera(vendor.VendorID)
    return {"ok" : True, "camera_add":camera_added}


#----------------------------
# DELET CAMERA
#---------------------------

class camDEL(BaseModel):
    camID: int


@router.post("camera/remove")
def remove_cam(camera:camDEL):
    camera =  camera_repository.remove_camera(camera.camID)
    return {"ok" : True, "camera_add":camera}
#----------------------------------
# UPDATE CAMERA
#-------------------------------

class camUP(BaseModel):
    camID: int
    statues : str

@router.post("camera/update")
def remove_cam(camera:camUP):
    camera =  camera_repository.update_statues(camera.camID,camera.statues)
    return {"ok" : True, "camera_add":camera}

