import asyncio, logging, queue, threading, time
from collections import defaultdict
import cv2, numpy as np, supervision as sv
from ultralytics import YOLO
from .camera_manager import CameraManager, CameraSpec
from .config import settings
from .evidence_writer import EvidenceWriter
from .frame_queue import LatestFrameQueue
from .tracker import PerCameraTracker
log = logging.getLogger(__name__)

class DetectionRuntime:
    def __init__(self):
        self.frames = LatestFrameQueue(settings.queue_size)
        self.evidence = queue.Queue(maxsize=settings.evidence_queue_size)
        self.cameras = CameraManager(self.frames, self._camera_status)
        self.writer = EvidenceWriter(self.evidence, settings.evidence_dir)
        self.trackers = PerCameraTracker()
        self._stop = threading.Event()
        self._worker = threading.Thread(target=self._inference_loop, name="detection-worker", daemon=True)
        self._loop = None; self._subscribers = set(); self._subscriber_lock = threading.Lock()
        self._model_loaded = False; self._model_error = None
        self._last_publish = defaultdict(float); self._last_evidence = defaultdict(float); self._statuses = {}
    def start(self):
        self._loop = asyncio.get_running_loop(); self.writer.start(); self._worker.start()
    def stop(self):
        self.cameras.stop_all(); self._stop.set()
        if self._worker.is_alive(): self._worker.join(timeout=10)
        self.writer.stop()
    def add_camera(self, camera_id, source_url, enabled_classes=(), fps=None, confidence=None):
        if not source_url or not source_url.strip(): raise ValueError("Camera source URL is empty")
        spec = CameraSpec(camera_id, source_url, tuple(enabled_classes or ()),
            float(fps or settings.default_fps), float(confidence or settings.default_confidence))
        if not 0 < spec.confidence < 1: raise ValueError("confidence must be between 0 and 1")
        if not 0.2 <= spec.fps <= 30: raise ValueError("fps must be between 0.2 and 30")
        self.cameras.add(spec); self.trackers.reset(camera_id)
        return {"camera_id": camera_id, "status": "starting"}
    def remove_camera(self, camera_id):
        removed = self.cameras.remove(camera_id); self.trackers.reset(camera_id); return removed
    def health(self):
        return {"model": settings.model, "model_loaded": self._model_loaded,
            "model_error": self._model_error, "frame_queue_size": self.frames.qsize(),
            "dropped_frames": self.frames.dropped, "evidence_queue_size": self.evidence.qsize(),
            "cameras": self.cameras.list(), "camera_status": dict(self._statuses)}
    def subscribe(self, q):
        with self._subscriber_lock: self._subscribers.add(q)
    def unsubscribe(self, q):
        with self._subscriber_lock: self._subscribers.discard(q)
    def _send(self, payload):
        if not self._loop or self._loop.is_closed(): return
        with self._subscriber_lock: subscribers = list(self._subscribers)
        for target in subscribers:
            def deliver(q=target, data=payload):
                if q.full():
                    try: q.get_nowait()
                    except asyncio.QueueEmpty: pass
                try: q.put_nowait(data)
                except asyncio.QueueFull: pass
            self._loop.call_soon_threadsafe(deliver)
    def _camera_status(self, camera_id, status, error):
        self._statuses[camera_id] = {"status": status, "error": error, "updated_at": time.time()}
        self._send({"type":"camera_status","camera_id":camera_id,"status":status,"error":error})
    def _inference_loop(self):
        try:
            model = YOLO(settings.model); self._model_loaded = True
            log.info("Loaded detection model %s", settings.model)
        except Exception as exc:
            self._model_error = str(exc); log.exception("Could not load detection model"); return
        while not self._stop.is_set():
            packet = self.frames.get(timeout=0.5)
            if packet is None: continue
            try:
                result = model.predict(packet.frame, conf=packet.confidence, imgsz=settings.image_size,
                    device=None if settings.device == "auto" else settings.device, verbose=False)[0]
                detections = sv.Detections.from_ultralytics(result); names = result.names
                if packet.enabled_classes and detections.class_id is not None:
                    allowed = {name.casefold() for name in packet.enabled_classes}
                    mask = np.array([str(names[int(cid)]).casefold() in allowed for cid in detections.class_id], dtype=bool)
                    detections = detections[mask]
                tracked = self.trackers.update(packet.camera_id, detections)
                objects, annotated = [], packet.frame.copy()
                track_ids = tracked.tracker_id if tracked.tracker_id is not None else [None] * len(tracked)
                for box, class_id, confidence, track_id in zip(tracked.xyxy, tracked.class_id, tracked.confidence, track_ids):
                    x1,y1,x2,y2 = [int(v) for v in box]; label = str(names[int(class_id)])
                    objects.append({"class":label,"class_id":int(class_id),"confidence":round(float(confidence),4),
                        "track_id":int(track_id) if track_id is not None else None,"bbox":[x1,y1,x2,y2]})
                    cv2.rectangle(annotated,(x1,y1),(x2,y2),(40,220,90),2)
                    tag = label + " " + format(float(confidence),".2f")
                    if track_id is not None: tag += " ID:" + str(int(track_id))
                    cv2.putText(annotated,tag,(x1,max(18,y1-6)),cv2.FONT_HERSHEY_SIMPLEX,0.5,(40,220,90),2)
                event = {"type":"detections","camera_id":packet.camera_id,"frame_id":packet.frame_id,
                    "timestamp":packet.captured_at,"objects":objects,"object_count":len(objects)}
                now = time.monotonic()
                if now - self._last_publish[packet.camera_id] >= settings.publish_interval:
                    self._send(event); self._last_publish[packet.camera_id] = now
                if objects and now - self._last_evidence[packet.camera_id] >= settings.evidence_cooldown:
                    saved = dict(event); saved["image"] = annotated
                    try:
                        self.evidence.put_nowait(saved); self._last_evidence[packet.camera_id] = now
                    except queue.Full: log.warning("Evidence queue full; dropped camera %s evidence", packet.camera_id)
            except Exception: log.exception("Inference failed for camera %s", packet.camera_id)
            finally: self.frames.task_done()
