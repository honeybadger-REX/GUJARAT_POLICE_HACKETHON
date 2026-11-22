"""Resolve a registered camera source, supporting current and legacy schemas."""
from backend.app.database.camera_repository import get_db, get_camera_source as legacy_lookup

def get_camera_source(camera_id: int):
    # Current init.sql stores stream URLs in camera_stream.SourceURL.
    conn = get_db()
    cursor = conn.cursor()
    try:
        try:
            cursor.execute(
                "SELECT c.CameraID, cs.SourceURL "
                "FROM camera c JOIN camera_stream cs ON cs.CameraID = c.CameraID "
                "WHERE c.CameraID = %s AND c.enable = 1 AND cs.enable = 1 "
                "ORDER BY cs.StreamID DESC LIMIT 1",
                (camera_id,),
            )
            row = cursor.fetchone()
            if row and row[1]:
                return {"camera_id": int(row[0]), "source_url": str(row[1])}
        except Exception:
            # Older deployments may not have camera_stream yet.
            pass
    finally:
        cursor.close()
        conn.close()

    # Compatibility path for the older Python repository schema.
    try:
        row = legacy_lookup(camera_id)
        if row:
            return {"camera_id": row["CameraID"], "source_url": row["CameraURL"]}
    except Exception:
        pass
    return None
