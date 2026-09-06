from pathlib import Path


# ============================================================
# Project name
# ============================================================

project = Path("gujarat-police-camera-system")


# ============================================================
# Folders
# ============================================================

folders = [
    # Backend
    project / "backend" / "app" / "api",
    project / "backend" / "app" / "services",
    project / "backend" / "app" / "database",
    project / "backend" / "app" / "models",
    project / "backend" / "app" / "schemas",
    project / "backend" / "app" / "core",
    project / "backend" / "app" / "utils",
    project / "backend" / "tests",

    # Frontend
    project / "frontend" / "pages",
    project / "frontend" / "css",
    project / "frontend" / "js",
    project / "frontend" / "assets" / "images",
    project / "frontend" / "assets" / "icons",
    project / "frontend" / "assets" / "fonts",

    # Database
    project / "database" / "migrations",

    # Streaming
    project / "streaming" / "mediamtx",
    project / "streaming" / "ffmpeg",

    # AI
    project / "ai" / "detection",
    project / "ai" / "inference",
    project / "ai" / "models",
    project / "ai" / "tracking",

    # Scripts
    project / "scripts",

    # Documentation
    project / "docs",

    # Deployment
    project / "deployment" / "docker",
    project / "deployment" / "nginx",
]


# ============================================================
# Files
# ============================================================

files = [
    # --------------------------------------------------------
    # Backend
    # --------------------------------------------------------

    project / "backend" / "app" / "main.py",

    # API
    project / "backend" / "app" / "api" / "camera.py",
    project / "backend" / "app" / "api" / "vendor.py",
    project / "backend" / "app" / "api" / "stream.py",
    project / "backend" / "app" / "api" / "health.py",
    project / "backend" / "app" / "api" / "event.py",
    project / "backend" / "app" / "api" / "auth.py",

    # Services
    project / "backend" / "app" / "services" / "camera_service.py",
    project / "backend" / "app" / "services" / "vendor_service.py",
    project / "backend" / "app" / "services" / "stream_service.py",
    project / "backend" / "app" / "services" / "mediamtx_service.py",
    project / "backend" / "app" / "services" / "health_service.py",
    project / "backend" / "app" / "services" / "event_service.py",
    project / "backend" / "app" / "services" / "auth_service.py",

    # Database
    project / "backend" / "app" / "database" / "connection.py",
    project / "backend" / "app" / "database" / "camera_repository.py",
    project / "backend" / "app" / "database" / "vendor_repository.py",
    project / "backend" / "app" / "database" / "event_repository.py",
    project / "backend" / "app" / "database" / "user_repository.py",

    # Models
    project / "backend" / "app" / "models" / "camera.py",
    project / "backend" / "app" / "models" / "vendor.py",
    project / "backend" / "app" / "models" / "event.py",
    project / "backend" / "app" / "models" / "user.py",

    # Schemas
    project / "backend" / "app" / "schemas" / "camera.py",
    project / "backend" / "app" / "schemas" / "vendor.py",
    project / "backend" / "app" / "schemas" / "stream.py",
    project / "backend" / "app" / "schemas" / "health.py",
    project / "backend" / "app" / "schemas" / "event.py",
    project / "backend" / "app" / "schemas" / "auth.py",

    # Core
    project / "backend" / "app" / "core" / "config.py",
    project / "backend" / "app" / "core" / "security.py",
    project / "backend" / "app" / "core" / "constants.py",

    # Utils
    project / "backend" / "app" / "utils" / "logger.py",
    project / "backend" / "app" / "utils" / "validators.py",
    project / "backend" / "app" / "utils" / "helpers.py",

    # Backend tests
    project / "backend" / "tests" / "test_camera.py",
    project / "backend" / "tests" / "test_vendor.py",
    project / "backend" / "tests" / "test_stream.py",
    project / "backend" / "tests" / "test_health.py",
    project / "backend" / "tests" / "test_auth.py",

    # Backend configuration
    project / "backend" / "requirements.txt",
    project / "backend" / ".env",


    # --------------------------------------------------------
    # Frontend
    # --------------------------------------------------------

    project / "frontend" / "index.html",

    # Pages
    project / "frontend" / "pages" / "dashboard.html",
    project / "frontend" / "pages" / "cameras.html",
    project / "frontend" / "pages" / "vendors.html",
    project / "frontend" / "pages" / "events.html",
    project / "frontend" / "pages" / "login.html",
    project / "frontend" / "pages" / "settings.html",

    # CSS
    project / "frontend" / "css" / "main.css",
    project / "frontend" / "css" / "dashboard.css",
    project / "frontend" / "css" / "cameras.css",
    project / "frontend" / "css" / "events.css",
    project / "frontend" / "css" / "login.css",
    project / "frontend" / "css" / "settings.css",

    # JavaScript
    project / "frontend" / "js" / "api.js",
    project / "frontend" / "js" / "dashboard.js",
    project / "frontend" / "js" / "cameras.js",
    project / "frontend" / "js" / "vendors.js",
    project / "frontend" / "js" / "events.js",
    project / "frontend" / "js" / "login.js",
    project / "frontend" / "js" / "settings.js",


    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------

    project / "database" / "schema.sql",
    project / "database" / "seed.sql",
    project / "database" / "migrations" / "README.md",


    # --------------------------------------------------------
    # Streaming
    # --------------------------------------------------------

    project / "streaming" / "mediamtx" / "mediamtx.yml",
    project / "streaming" / "mediamtx" / "README.md",

    project / "streaming" / "ffmpeg" / "README.md",


    # --------------------------------------------------------
    # AI
    # --------------------------------------------------------

    project / "ai" / "detection" / "detector.py",
    project / "ai" / "detection" / "README.md",

    project / "ai" / "inference" / "inference.py",
    project / "ai" / "inference" / "README.md",

    project / "ai" / "models" / "README.md",

    project / "ai" / "tracking" / "tracker.py",
    project / "ai" / "tracking" / "README.md",

    project / "ai" / "README.md",


    # --------------------------------------------------------
    # Scripts
    # --------------------------------------------------------

    project / "scripts" / "setup_database.py",
    project / "scripts" / "seed_cameras.py",
    project / "scripts" / "health_check.py",
    project / "scripts" / "cleanup_streams.py",


    # --------------------------------------------------------
    # Documentation
    # --------------------------------------------------------

    project / "docs" / "architecture.md",
    project / "docs" / "database.md",
    project / "docs" / "api.md",
    project / "docs" / "camera-management.md",
    project / "docs" / "streaming.md",
    project / "docs" / "health-monitoring.md",
    project / "docs" / "ai-system.md",
    project / "docs" / "deployment.md",
    project / "docs" / "team-contribution.md",


    # --------------------------------------------------------
    # Deployment
    # --------------------------------------------------------

    project / "deployment" / "docker" / "backend.Dockerfile",
    project / "deployment" / "docker" / "frontend.Dockerfile",
    project / "deployment" / "docker" / "mediamtx.Dockerfile",

    project / "deployment" / "nginx" / "nginx.conf",

    project / "deployment" / "docker-compose.yml",


    # --------------------------------------------------------
    # Root files
    # --------------------------------------------------------

    project / ".gitignore",
    project / "README.md",
    project / "LICENSE",
]


# ============================================================
# Create folders
# ============================================================

for folder in folders:
    folder.mkdir(parents=True, exist_ok=True)


# ============================================================
# Create empty files
# ============================================================

for file in files:
    file.touch(exist_ok=True)


print("==========================================")
print("Project structure created successfully!")
print("==========================================")
print(f"Location: {project.resolve()}")
print(f"Folders created: {len(folders)}")
print(f"Files created:   {len(files)}")
print("All files are empty.")