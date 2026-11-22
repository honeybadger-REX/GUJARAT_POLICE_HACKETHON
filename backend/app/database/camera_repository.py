# Private source lookup for the detection service. Never expose CameraURL in list APIs.
def get_camera_source(camera_id: int):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT CameraID, CameraURL FROM camera WHERE CameraID = %s AND enable = 1", (camera_id,))
        row = cursor.fetchone()
        if not row or not row[1]:
            return None
        return {"CameraID": int(row[0]), "CameraURL": str(row[1])}
    finally:
        cursor.close()
        conn.close()

undefined