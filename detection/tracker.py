import supervision as sv

class PerCameraTracker:
    """Each camera has its own ByteTrack state; inference model is still shared."""
    def __init__(self): self._trackers = {}
    def update(self, camera_id: int, detections: sv.Detections):
        tracker = self._trackers.get(camera_id)
        if tracker is None:
            tracker = sv.ByteTrack()
            self._trackers[camera_id] = tracker
        return tracker.update_with_detections(detections)
    def reset(self, camera_id: int): self._trackers.pop(camera_id, None)
