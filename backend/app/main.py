from fastapi import FastAPI

from backend.app.api.event import router as event_router
from backend.app.api.health import router as health_router
from backend.app.api.stream import router as stream_router
from backend.app.api.vendor import router as vendor_router
from backend.app.api.camera import router as camera_router


app = FastAPI(
    title="Camera Management API",
    description="Backend API for camera, vendor, stream and event management",
    version="1.0.0",
)


app.include_router(
    health_router,
    prefix="/api/health",
    tags=["Health"]
)

app.include_router(
    event_router,
    prefix="/api/events",
    tags=["Events"]
)

app.include_router(
    stream_router,
    prefix="/api/streams",
    tags=["Streams"]
)

app.include_router(
    vendor_router,
    prefix="/api/vendors",
    tags=["Vendors"]
)

app.include_router(
    camera_router,
    prefix="/api/camera",
    tags=["Camera"]
)


@app.get("/")
def root():

    return {
        "message": "Camera Management API is running",
        "version": "1.0.0"
    }