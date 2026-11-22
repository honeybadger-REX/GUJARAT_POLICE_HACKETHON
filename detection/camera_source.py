"""Read camera URLs through the existing repository helper."""
from backend.app.database.camera_repository import get_camera_source as lookup

def get_camera_source(camera_id: int):
    row = lookup(camera_id)
    if not row: return None
    return {"camera_id": row["CameraID"], "source_url": row["CameraURL"]}
