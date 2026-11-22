from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx
import logging
from detection.runtime import DetectionRuntime

log = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.mediamtx_client = httpx.AsyncClient(timeout=10.0)
    detection_runtime = DetectionRuntime()
    app.state.detection_runtime = detection_runtime
    detection_runtime.start()
    log.info("Detection runtime started")
    try:
        yield
    finally:
        detection_runtime.stop()
        await app.state.mediamtx_client.aclose()
        log.info("Detection runtime stopped")

app = FastAPI(title="Camera Management API",
    description="Camera, vendor, stream, event and detection management",
    version="1.1.0", lifespan=lifespan)

from backend.app.api.event import router as event_router
from backend.app.api.health import router as health_router
from backend.app.api.stream import router as stream_router
from backend.app.api.vendor import router as vendor_router
from backend.app.api.camera import router as camera_router
from detection.api import router as detection_router

app.add_middleware(CORSMiddleware, allow_origins=[
    "http://127.0.0.1:3000", "http://localhost:3000",
    "http://127.0.0.1:5500", "http://localhost:5500", "null"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(health_router, prefix="/api/health", tags=["Health"])
app.include_router(event_router, prefix="/api/events", tags=["Events"])
app.include_router(stream_router, prefix="/api/streams", tags=["Streams"])
app.include_router(vendor_router, prefix="/api/vendors", tags=["Vendors"])
app.include_router(camera_router, prefix="/api/camera", tags=["Camera"])
app.include_router(detection_router, prefix="/api/detection", tags=["Detection"])

@app.get("/")
def root():
    return {"message":"Camera Management API is running","version":"1.1.0"}
