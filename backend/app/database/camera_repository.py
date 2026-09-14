from .connection import get_db
import mysql.connector
import mysql.connector.errors
import sqlite3
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


def update_statues(camera_id: int,statues : str):
    conn = get_db()
    cursor = conn.cursor()
    try: 
       sql = """UPDATE camera SET enable = %s WHERE CameraID = %s"""
       value = (statues, camera_id)

       cursor.execute(sql, value)
       conn.commit()
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
            cursor.execute(""" DELETE FROM camera WHERE CameraID = %s""",(camera_id,))
            rows = cursor.fetchall()
            conn.commit()

       except mysql.connector.Error as e:
        conn.rollback()
        print(f"Database error: {e}")
        return False
       
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
          cursor.execute("""SELECT VendorID , NUMBER_CAM,URL from vendor where VendorID = %s""",(vendor_id,))
          vendor = cursor.fetchone()
          if not vendor:
               return "vendor id not found"
          
          BASE_URL = vendor[2]
          for i in range(vendor[1]):
               cam_url = f"{BASE_URL}{i:02d}"
               camera_name.append(f"cam{i:02d}")
               camera_url.append(cam_url) 

               
          try:  
                     sql = """ INSERT INTO camera (CameraName, VendorID, CameraURL, enable)VALUES (%s, %s, %s, %s)"""
                     
                     for  url , name in zip(camera_url , camera_name):
                          values.append([name,vendor_id,url,True]) 
                     cursor.executemany(sql, values)

                     conn.commit()

          except mysql.connector.Error as e:
               conn.rollback()
               print(f"Database error: {e}")
               return False

     finally:
        cursor.close()
        conn.close()

     return {
        "message": "new cam added",
        "number_of_cam": len(camera_url),
        "cam_name": camera_name
    }




    
# One important thing about your camera checker

# This function inserts the cameras with:

# enable = True

# Then your background checker changes enable to:

# ONLINE
# OFFLINE

# So you should decide what enable means.

# If enable is supposed to mean camera status, then inserting True is not ideal. Better would be:

# "UNKNOWN"

# initially:

# values.append(
#     [f"cam{i:02d}", vendor_id, cam_url, "UNKNOWN"]
# )

# Then your checker changes:

# UNKNOWN → ONLINE
# UNKNOWN → OFFLINE

# That gives you a clean meaning for the column.

