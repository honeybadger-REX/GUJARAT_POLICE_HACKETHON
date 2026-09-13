from .connection import get_db
import mysql.connector
import mysql.connector.errors
import httpx
import subprocess
from fastapi import APIRouter

from concurrent.futures import ThreadPoolExecutor
import pandas as pd

MEDIAMTX_API = "http://127.0.0.1:9997"
MEDIAMTX_WEBRTC = "http://127.0.0.1:8889"

#-------------------------------------
# STATUES UPDATED  
#------------------------------



async def update_statues(camera_id: int,statues : str):
    conn = get_db()
    cursor = conn.cursor()
    try: 
        cursor.execute(""" UPDATE camera SET enable = "ONLINE" where CameraID = %s """,(camera_id,statues))
        
        rows = cursor.fetchall()
    finally: 
        cursor.close()
        conn.close()

    return {"message":'statues updated'}
         
# ---------------------------------------------      
# GET CAMERA INFO
#----------------------------------------------
def get_cam_info():
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

#--------------------------------------------------------
# REMOVE  CAMERA 
#----------------------------------------------------

def remove_camera(camera_id:int):
       conn = get_db()
       cursor = conn.cursor()
       try:
            cursor.exicute(""" DELECT FROM camera WHERE Camera_id = %s""",(camera_id,))
            rows = cursor.fetchall()
       finally:
            cursor.close()
            conn.close()

       return{'message' : "row delecte"}



#-------------------------------------------
# ADD CAMERA INTO LIST 
#------------------------------------------

def add_camera(vendor_id: int):
     conn = get_db()
     cursor = conn.cursor()
     camera_url = []
     camera_name =  []
     values = []
     try:
          cursor.exicute("""SELECT VendorID , NUMBER_CAM,URL from vendor where VendorID = %S""",(vendor_id,))
          vendor = cursor.fetchone()
          if not vendor:
               return "vendor id not found"
          
          BASE_URL = vendor[2]
          for i in range(vendor[1]):
               cam_url = f"{BASE_URL}{i:02d}"
               camera_name.append(f"cam{i:02d}")
               camera_url.append(cam_url) 

               
          try:  
                     sql = """INSEART INTO camera values (CameraName,VendorID,CameraURL,enable) """
                     
                     for  url , name in zip(camera_url , camera_name):
                          values.append([name,vendor_id,url,"CHECHINK"]) 
                     cursor.execute(sql,values)

          except sqlite3.IntegrityError as e:
               # Duplicate key, NOT NULL violation, foreign key failure
                      conn.rollback()
                      print(f"Integrity error: {e}")
                      return False
          except sqlite3.DataError as e:
               # Wrong data type or value too long
                      conn.rollback()
                      print(f"Data error: {e}")
                      return False
          except sqlite3.OperationalError as e:
               # Connection lost, disk full, etc.
                      conn.rollback()
                      print(f"Operational error: {e}")
                      return False
          except sqlite3.Error as e:
        # Catch-all for other DB errors
                      conn.rollback()
                      print(f"Database error: {e}")
                      return False
     finally:
            cursor.close()
            conn.close()
    
     return {
           "message":"new  cam  added",
           "number_of_cam": len(camera_url),
           "cam_name" : camera_name
      }   
            

