import json, logging, queue, threading
from pathlib import Path
from datetime import datetime, timezone
import cv2
log = logging.getLogger(__name__)

class EvidenceWriter:
    """One consumer writes selected evidence images and JSONL metadata."""
    def __init__(self, evidence_queue, output_dir):
        self.queue, self.root = evidence_queue, Path(output_dir)
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, name="evidence-writer", daemon=True)
    def start(self):
        self.root.mkdir(parents=True, exist_ok=True); self._thread.start()
    def stop(self):
        self._stop.set(); self._thread.join(timeout=8)
    def _run(self):
        metadata_file = self.root / "events.jsonl"
        while not self._stop.is_set() or not self.queue.empty():
            try: item = self.queue.get(timeout=0.5)
            except queue.Empty: continue
            try:
                folder = self.root / str(item["camera_id"]); folder.mkdir(parents=True, exist_ok=True)
                stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
                image_path = folder / f"{stamp}_frame{item['frame_id']}.jpg"
                image = item.pop("image")
                if not cv2.imwrite(str(image_path), image): raise RuntimeError("Could not write evidence image")
                item["evidence_image"] = str(image_path)
                item["stored_at"] = datetime.now(timezone.utc).isoformat()
                with metadata_file.open("a", encoding="utf-8") as stream:
                    stream.write(json.dumps(item, ensure_ascii=False) + "\n")
            except Exception: log.exception("Evidence write failed")
            finally: self.queue.task_done()
