from dataclasses import dataclass, field
import logging, threading, time
import cv2
from .frame_queue import FramePacket, LatestFrameQueue
log = logging.getLogger(__name__)

@dataclass
class CameraSpec:
    camera_id: int
    source_url: str
    enabled_classes: tuple[str, ...] = ()
    fps: float = 5.0
    confidence: float = 0.35
    running: bool = False
    last_error: str | None = None
    _stop: threading.Event = field(default_factory=threading.Event, repr=False)
    _thread: threading.Thread | None = field(default=None, repr=False)

class CameraManager:
    """One supervisor manages cameras; blocking OpenCV reads use per-camera reader threads.
    All readers send frames to one shared queue and one inference worker.
    """
    def __init__(self, frame_queue: LatestFrameQueue, on_status=None):
        self.frame_queue, self.on_status = frame_queue, on_status
        self._cameras = {}
        self._lock = threading.RLock()
    def add(self, spec: CameraSpec):
        with self._lock:
            old = self._cameras.get(spec.camera_id)
            if old: old._stop.set()
            spec._stop.clear(); spec.running = True
            self._cameras[spec.camera_id] = spec
            spec._thread = threading.Thread(target=self._reader, args=(spec,),
                name=f"camera-reader-{spec.camera_id}", daemon=True)
            spec._thread.start()
    def remove(self, camera_id: int):
        with self._lock: spec = self._cameras.pop(camera_id, None)
        if not spec: return False
        spec._stop.set()
        if spec._thread and spec._thread.is_alive(): spec._thread.join(timeout=3)
        spec.running = False
        if self.on_status: self.on_status(camera_id, "stopped", None)
        return True
    def list(self):
        with self._lock:
            return [{"camera_id": s.camera_id, "running": s.running, "fps": s.fps,
                     "enabled_classes": list(s.enabled_classes), "last_error": s.last_error}
                    for s in self._cameras.values()]
    def stop_all(self):
        with self._lock: ids = list(self._cameras)
        for camera_id in ids: self.remove(camera_id)
    def _reader(self, spec):
        frame_id, backoff = 0, 1.0
        interval = 1.0 / max(0.2, min(spec.fps, 30.0))
        while not spec._stop.is_set():
            cap = None
            try:
                cap = cv2.VideoCapture(spec.source_url)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                if not cap.isOpened(): raise RuntimeError("Video source could not be opened")
                spec.last_error = None; backoff = 1.0
                if self.on_status: self.on_status(spec.camera_id, "online", None)
                next_at = 0.0
                while not spec._stop.is_set():
                    ok, frame = cap.read()
                    if not ok or frame is None: raise RuntimeError("Frame read failed; reconnecting")
                    now_mono = time.monotonic()
                    if now_mono < next_at: continue
                    next_at = now_mono + interval; frame_id += 1
                    self.frame_queue.put_latest(FramePacket(spec.camera_id, frame_id, time.time(),
                        frame, spec.confidence, spec.enabled_classes))
            except Exception as exc:
                spec.last_error = str(exc)
                if self.on_status: self.on_status(spec.camera_id, "reconnecting", spec.last_error)
                log.warning("Camera %s: %s", spec.camera_id, exc)
            finally:
                if cap is not None: cap.release()
            if not spec._stop.is_set():
                spec._stop.wait(backoff); backoff = min(backoff * 2, 15.0)
        spec.running = False
