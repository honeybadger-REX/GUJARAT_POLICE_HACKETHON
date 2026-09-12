import mysql.connector
import httpx
from fastapi import FastAPI , APIRouter
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

vendor_list = []


router = APIRouter()



@router.get("/")
def get_vendors():
    return {
        "message": "Vendors API"
    }

#---------------------------------------------
# VENDOR API
#--------------------------------------------

@router.post("/vendor/{status}")
def vendor_status(status: bool):

    vendor_list.clear()

    if status is True:
        cursor.execute(
            "SELECT VendorName FROM vendor WHERE enable = 'true'"
        )
    else:
        cursor.execute(
            "SELECT VendorName FROM vendor WHERE enable = 'false'"
        )

    rows = cursor.fetchall()

    for row in rows:
        vendor_list.append(row[0])

    return vendor_list ;

@router.get("/vendor/{status}")
def vendor_status(status: bool):

    return {
        "message": "Vendor list prepared",
        "count": len(vendor_list)
    }




cam_url = []
cam_id = []
@router.post("/vendor/{vendorID}/cameras")
def get_cam_url(vendorID: int):

    cursor.execute(
        """
        SELECT CameraID, CameraName, CameraURL
        FROM camera
        WHERE VendorID = %s
        ORDER BY CameraID
        """,
        (vendorID,)
    )

    rows = cursor.fetchall()

    if not rows:
        return {
            "message": "No cameras found for this vendor",
            "vendor_id": vendorID,
            "cameras": []
        }

    cameras = []

    for row in rows:
        cameras.append({
            "CameraID": row[0],
            "CameraName": row[1],
            "CameraURL": row[2]
        })

    return {
        "message": "Vendor camera list",
        "vendor_id": vendorID,
        "count": len(cameras),
        "cameras": cameras
    }


camera_resultss = []

@router.post("/vendor/{vendorID}/check-cameras")
def check_vendor_cameras(vendorID: int):

    cursor.execute(
        """
        SELECT CameraID, CameraName, CameraURL
        FROM camera
        WHERE VendorID = %s
        """,
        (vendorID,)
    )

    cameras = cursor.fetchall()
    vendors =  camera_resultss.vendor_ID = vendorID

    if len(cameras) == vendors.total:
        return camera_resultss

    if not cameras:
        return {
            "message": "No cameras found for this vendor",
            "vendor_id": vendorID
        }

    def check_one_camera(camera):
        camera_id = camera[0]
        camera_name = camera[1]
        camera_url = camera[2]

        print(f"Checking {camera_name}...")

        status = check_camera(camera_url)

        return camera_id, camera_name, status

    results = []
   

    # Check cameras concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        camera_results = executor.map(check_one_camera, cameras)

        for camera_id, camera_name, status in camera_results:

            cursor.execute(
                """
                UPDATE camera
                SET enable = %s
                WHERE CameraID = %s
                """,
                (status, camera_id)
            )

            results.append({
                "CameraID": camera_id,
                "CameraName": camera_name,
                "status": status
            })

    conn.commit()

    online_count = sum(
        1 for camera in results
        if camera["status"] == "ONLINE"
    )

    offline_count = sum(
        1 for camera in results
        if camera["status"] == "OFFLINE"
    )


 
    return camera_resultss.append(    {
        "vendor_id": vendorID,
        "total": len(results),
        "online": online_count,
        "offline": offline_count,
        "cameras": results
    })


@router.get("/vendor/{vendorID}/check-cameras")
def  send_vendor_data(vendorID: str):
    if vendorID == all:
        return camera_resultss

    filter =  [x for x in camera_resultss if x["vendor_id"] == vendorID]
    if vendorID == filter[0]:
        return filter
    else:
        return {
            "message":"vendor not  found"
        }



