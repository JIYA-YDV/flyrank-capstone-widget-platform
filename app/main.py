# app/main.py
import logging

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, Response
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.api import auth, widgets, submissions, dashboard
from app.middleware.rate_limiter import limiter
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Embeddable Widget & Lead-Capture Platform",
    description="Create embeddable widgets, capture leads, enrich with geo data.",
    version="1.0.0",
)

# --- Rate Limiter ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Public widget endpoint must accept any origin
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)

# --- Routers ---
app.include_router(auth.router)
app.include_router(widgets.router)
app.include_router(submissions.router)
app.include_router(dashboard.router)


# --- Widget JS endpoint (public, versioned, cached) ---
WIDGET_JS_VERSION = "1"


@app.get("/widget.js")
async def serve_widget_js():
    """Serve the embeddable widget JavaScript with cache headers."""
    try:
        return FileResponse(
            "static/widget.js",
            media_type="application/javascript",
            headers={
                "Cache-Control": f"public, max-age=31536000, immutable",
                "X-Widget-Version": WIDGET_JS_VERSION,
            },
        )
    except FileNotFoundError:
        return JSONResponse(
            status_code=404,
            content={"detail": "Widget script not found"},
        )


@app.get("/widget.v{version}.js")
async def serve_versioned_widget_js(version: str):
    """Serve versioned widget JS — cache forever, bust on new version."""
    try:
        return FileResponse(
            "static/widget.js",
            media_type="application/javascript",
            headers={
                "Cache-Control": "public, max-age=31536000, immutable",
                "X-Widget-Version": version,
            },
        )
    except FileNotFoundError:
        return JSONResponse(
            status_code=404,
            content={"detail": "Widget script not found"},
        )


# --- Global error handlers ---
@app.exception_handler(422)
async def validation_exception_handler(request: Request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Validation error", "errors": str(exc)},
    )


@app.get("/health")
async def health():
    return {"status": "ok"}