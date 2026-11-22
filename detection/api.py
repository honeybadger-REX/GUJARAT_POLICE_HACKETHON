import asyncio, hmac, logging
from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect, Header
from pydantic import BaseModel, Field
from .config import settings
from .camera_source import get_camera_source
log = logging.getLogger(__name__)
router = APIRouter()

class StartDetectionRequest(BaseModel):
    enabled_classes: list[str] = Field(default_factory=list)
    fps: float | None = Field(default=None, ge=0.2, le=30)
    confidence: float | None = Field(default=None, gt=0, lt=1)

def authorize(key):
    if settings.api_key and not hmac.compare_digest(key or "", settings.api_key):
        raise HTTPException(401, "Invalid detection API key")
def runtime(request):
    value = getattr(request.app.state, "detection_runtime", None)
    if value is None: raise HTTPException(503, "Detection service is not running")
    return value

@router.get("/health")
def health(request: Request, x_detection_key: str | None = Header(default=None)):
    authorize(x_detection_key); return runtime(request).health()
@router.get("/cameras")
def cameras(request: Request, x_detection_key: str | None = Header(default=None)):
    authorize(x_detection_key); return {"cameras":runtime(request).cameras.list()}
@router.post("/cameras/{camera_id}/start")
def start(camera_id: int, body: StartDetectionRequest, request: Request,
          x_detection_key: str | None = Header(default=None)):
    authorize(x_detection_key); service = runtime(request)
    try:
        source = get_camera_source(camera_id)
        if not source: raise HTTPException(404, "Camera not found, disabled, or missing CameraURL")
        return service.add_camera(camera_id, source["source_url"], body.enabled_classes, body.fps, body.confidence)
    except HTTPException: raise
    except ValueError as exc: raise HTTPException(422, str(exc))
    except Exception as exc:
        log.exception("Detection start failed for camera %s", camera_id)
        raise HTTPException(500, "Could not start camera detection") from exc
@router.delete("/cameras/{camera_id}/stop")
def stop(camera_id: int, request: Request, x_detection_key: str | None = Header(default=None)):
    authorize(x_detection_key); return {"camera_id":camera_id,"stopped":runtime(request).remove_camera(camera_id)}
@router.websocket("/ws")
async def websocket_feed(websocket: WebSocket):
    if settings.api_key and not hmac.compare_digest(websocket.headers.get("x-detection-key",""), settings.api_key):
        await websocket.close(code=1008); return
    service = getattr(websocket.app.state, "detection_runtime", None)
    if service is None: await websocket.close(code=1013); return
    await websocket.accept(); q = asyncio.Queue(maxsize=50); service.subscribe(q)
    try:
        await websocket.send_json({"type":"connected"})
        while True: await websocket.send_json(await q.get())
    except WebSocketDisconnect: pass
    finally: service.unsubscribe(q)
