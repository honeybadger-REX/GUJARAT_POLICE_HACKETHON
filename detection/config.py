from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    model: str = os.getenv("DETECTION_MODEL", "yolo11n.pt")
    device: str = os.getenv("DETECTION_DEVICE", "auto")
    image_size: int = int(os.getenv("DETECTION_IMAGE_SIZE", "640"))
    queue_size: int = int(os.getenv("DETECTION_QUEUE_SIZE", "64"))
    evidence_queue_size: int = int(os.getenv("DETECTION_EVIDENCE_QUEUE_SIZE", "128"))
    evidence_dir: str = os.getenv("DETECTION_EVIDENCE_DIR", "data/detection_evidence")
    default_fps: float = float(os.getenv("DETECTION_DEFAULT_FPS", "5"))
    default_confidence: float = float(os.getenv("DETECTION_CONFIDENCE", "0.35"))
    evidence_cooldown: float = float(os.getenv("DETECTION_EVIDENCE_COOLDOWN", "5"))
    publish_interval: float = float(os.getenv("DETECTION_PUBLISH_INTERVAL", "0.5"))
    api_key: str = os.getenv("DETECTION_API_KEY", "")
settings = Settings()
