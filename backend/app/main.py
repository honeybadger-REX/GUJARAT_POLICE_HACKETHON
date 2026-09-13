from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# NOTE: event.py, health.py and stream.py must exist in backend/app/api/
# (even as minimal stub routers) or this import will crash on startup.
# They weren't in your upload — add them or comment these two lines out.
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

# CORS lives here once, at the app level — not duplicated inside
# camera.py / vendor.py (they no longer create their own FastAPI() app).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000", "http://127.0.0.1:5500", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/health", tags=["Health"])
app.include_router(event_router, prefix="/api/events", tags=["Events"])
app.include_router(stream_router, prefix="/api/streams", tags=["Streams"])
app.include_router(vendor_router, prefix="/api/vendors", tags=["Vendors"])
app.include_router(camera_router, prefix="/api/camera", tags=["Camera"])


@app.get("/")
def root():
    return {"message": "Camera Management API is running", "version": "1.0.0"}