from dataclasses import dataclass
from queue import Queue, Empty, Full
from typing import Optional
import numpy as np

@dataclass
class FramePacket:
    camera_id: int
    frame_id: int
    captured_at: float
    frame: np.ndarray
    confidence: float
    enabled_classes: tuple[str, ...]

class LatestFrameQueue:
    """One shared bounded queue; discard the oldest frame when full."""
    def __init__(self, maxsize: int = 64):
        self._queue = Queue(maxsize=maxsize)
        self.dropped = 0
    def put_latest(self, packet: FramePacket) -> None:
        try:
            self._queue.put_nowait(packet)
            return
        except Full:
            pass
        try:
            self._queue.get_nowait()
            self._queue.task_done()
            self.dropped += 1
        except Empty:
            pass
        try:
            self._queue.put_nowait(packet)
        except Full:
            self.dropped += 1
    def get(self, timeout: float = 1.0) -> Optional[FramePacket]:
        try: return self._queue.get(timeout=timeout)
        except Empty: return None
    def task_done(self): self._queue.task_done()
    def qsize(self): return self._queue.qsize()
