from ..database import camera_repository
from ..database.connection import get_db
import mysql.connector
import mysql.connector.errors
import httpx
import subprocess
from fastapi import APIRouter
from concurrent.futures import ThreadPoolExecutor
import pandas as pd




#--------------------------------------------
# CEACK CAMERA ONLINE  OR  OFFLINE
#----------------------------------------------

def check_camera(url: str):
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

#--------------------------------------------
# CHECK  STATUES
#----------------------------------------------
def chech_cameras():
    conn = get_db()
    cursor = conn.cursor()
    try:
          cursor.exicute("""Select CameraName , CameraURL,CameraID from camera """ )
          camera = pd.list(cursor.featchall())

          def check_one_camera(camera):
            camera_name, camera_url,cameraid = camera
            status = check_camera(camera_url)
            return  camera_name, status ,camera_url,cameraid
               
          results = []
          with ThreadPoolExecutor(max_workers=10) as executor:
            for  camera_name, status , camera_url ,cameraid in executor.map(check_one_camera, camera):
                 camera_repository.update_statues(cameraid,status)
                 results.append({
                        
                                   "CameraName": camera_name,
                                   "status": status,
                                   "url" : camera_url
                               })
               
          conn.commit()
    finally:
        cursor.close()
        conn.close()
    return {"message": "done", "checked": len(results), "cameras": results}
