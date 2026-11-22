# Multi-camera detection pipeline

This service is separate from the repository's ai/ folder. It connects to the existing FastAPI app and reads camera URLs from the existing camera table.

## Design

- One reader thread per camera. OpenCV network reads can block, so a thread per source is the reliable option. A camera supervisor manages all readers.
- Every reader sends sampled frames to ONE shared bounded frame queue.
- ONE YOLO model instance and ONE inference worker process frames from all cameras.
- ByteTrack has separate tracking state per camera.
- Selected evidence frames go to ONE universal evidence queue and a separate writer stores JPEGs plus JSONL metadata.
- Detection events are published over a WebSocket.

This does not create one model or one inference worker per camera. When the queue fills, the oldest frame is dropped so the system favors current video over stale backlog.

## Install and run

From the repository root:

    pip install -r requirements-detection.txt
    set DETECTION_DEVICE=cpu
    set DETECTION_DEFAULT_FPS=3
    uvicorn backend.app.main:app --host 127.0.0.1 --port 8000

PowerShell uses $env:DETECTION_DEVICE="cpu" and $env:DETECTION_DEFAULT_FPS="3" instead. The first run downloads yolo11n.pt automatically. For CUDA, install a PyTorch build compatible with the machine's CUDA driver and set DETECTION_DEVICE=0.

## Environment variables

- DETECTION_MODEL: default yolo11n.pt
- DETECTION_DEVICE: default auto; use cpu or 0 for first CUDA GPU
- DETECTION_IMAGE_SIZE: default 640
- DETECTION_DEFAULT_FPS: default 5 frames per second per camera
- DETECTION_CONFIDENCE: default 0.35
- DETECTION_QUEUE_SIZE: default 64
- DETECTION_EVIDENCE_QUEUE_SIZE: default 128
- DETECTION_EVIDENCE_DIR: default data/detection_evidence
- DETECTION_EVIDENCE_COOLDOWN: default 5 seconds per camera
- DETECTION_PUBLISH_INTERVAL: default 0.5 seconds per camera
- DETECTION_API_KEY: optional shared key; set a long random value before exposing this API outside localhost

## API

Start detection for a camera already registered in MySQL:

    POST /api/detection/cameras/12/start
    {"enabled_classes":["person","car","motorcycle","bus","truck"],"fps":5,"confidence":0.35}

An empty enabled_classes list means all classes supported by the model. Stop with DELETE /api/detection/cameras/12/stop. Inspect GET /api/detection/health and GET /api/detection/cameras. Live events: ws://127.0.0.1:8000/api/detection/ws.

If DETECTION_API_KEY is configured, send it in the X-Detection-Key HTTP header and the same header during the WebSocket handshake. Do not put secrets in URLs or commit them.

## Existing database compatibility warning

The current Python repositories and stream service query camera.CameraURL, but the committed database/init.sql defines camera_stream.SourceURL instead and does not define CameraURL. This integration follows the current Python repository convention. Before starting detection, reconcile the actual deployed database schema with the code. Do not run a destructive database reset on live camera data. The camera URL is deliberately not returned by the public camera-list endpoint.

The detection reader opens the registered RTSP URL directly and does not depend on browser WebRTC viewing. A camera vendor may limit concurrent RTSP sessions; for those devices, use a relay or shared decoded stream in a later optimization.

## Operations and safety

Detection is an observation, not proof of identity or wrongdoing. Restrict API and WebSocket access, configure an API key, protect evidence files with filesystem permissions and retention controls, and audit evidence access. Confirm the model/dependency licensing is suitable for the intended deployment. This is a prototype integration, not a hardened high-availability deployment.
