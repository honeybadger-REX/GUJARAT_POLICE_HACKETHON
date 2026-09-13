import mysql.connector
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter

from .camera import check_camera  # reuse the FFmpeg health check from camera.py

router = APIRouter()


def get_db():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="gujarat_police"
    )
    return conn


@router.get("/")
def get_vendors():
    return {"message": "Vendors API"}


# ---------------------------------------------
# VENDOR LIST — read-only, so GET (not POST as before).
# ---------------------------------------------
@router.get("/vendor/{status}")
def get_vendor_list(status: bool):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT VendorName FROM vendor WHERE enable = %s",
            ("true" if status else "false",)
        )
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    vendor_list = [row[0] for row in rows]
    return {
        "message": "Vendor list prepared",
        "count": len(vendor_list),
        "vendors": vendor_list
    }


# ---------------------------------------------
# CAMERAS FOR A VENDOR — read-only, so GET (was POST before;
# camera.html was calling it with method: "POST" to match the bug —
# update the fetch call there too, see camera.html).
# ---------------------------------------------
@router.get("/vendor/{vendorID}/cameras")
def get_cam_url(vendorID: int):
    conn = get_db()
    cursor = conn.cursor()
    try:
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
    finally:
        cursor.close()
        conn.close()

    if not rows:
        return {
            "message": "No cameras found for this vendor",
            "vendor_id": vendorID,
            "cameras": []
        }

    cameras = [
        {"CameraID": r[0], "CameraName": r[1], "CameraURL": r[2]}
        for r in rows
    ]

    return {
        "message": "Vendor camera list",
        "vendor_id": vendorID,
        "count": len(cameras),
        "cameras": cameras
    }


# ---------------------------------------------
# CHECK CAMERAS — real side effect (runs ffmpeg, writes status to
# MySQL), so POST is correct. This was commented out and buggy
# before (referenced camera_resultss.vendor_ID which doesn't exist).
# ---------------------------------------------
@router.post("/vendor/{vendorID}/check-cameras")
def check_vendor_cameras(vendorID: int):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT CameraID, CameraName, CameraURL
            FROM camera
            WHERE VendorID = %s
            """,
            (vendorID,)
        )
        cameras = cursor.fetchall()

        if not cameras:
            return {"message": "No cameras found for this vendor", "vendor_id": vendorID}

        def check_one_camera(camera):
            camera_id, camera_name, camera_url = camera
            status = check_camera(camera_url)
            return camera_id, camera_name, status

        results = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            for camera_id, camera_name, status in executor.map(check_one_camera, cameras):
                cursor.execute(
                    "UPDATE camera SET enable = %s WHERE CameraID = %s",
                    (status == "ONLINE", camera_id)
                )
                results.append({
                    "CameraID": camera_id,
                    "CameraName": camera_name,
                    "status": status
                })

        conn.commit()
    finally:
        cursor.close()
        conn.close()

    online_count = sum(1 for r in results if r["status"] == "ONLINE")
    offline_count = sum(1 for r in results if r["status"] == "OFFLINE")

    return {
        "vendor_id": vendorID,
        "total": len(results),
        "online": online_count,
        "offline": offline_count,
        "cameras": results
    }