import numpy as np
from detection.frame_queue import FramePacket, LatestFrameQueue

def packet(frame_id):
    return FramePacket(1, frame_id, 1.0, np.zeros((2,2,3), dtype=np.uint8), 0.3, ())

def test_queue_drops_oldest_when_full():
    q = LatestFrameQueue(maxsize=2)
    q.put_latest(packet(1)); q.put_latest(packet(2)); q.put_latest(packet(3))
    assert q.qsize() == 2
    assert q.dropped == 1
    assert q.get().frame_id == 2
    assert q.get().frame_id == 3
