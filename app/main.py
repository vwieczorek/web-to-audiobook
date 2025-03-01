import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings
from app.logging import setup_logging, get_logger
from app.routers import health

# Load settings
settings = Settings()

# Set up logging with rotation
logger = setup_logging(
    settings.log_file, 
    settings.log_level,
    getattr(settings, "log_rotation_max_bytes", 10485760),  # 10MB default
    getattr(settings, "log_rotation_backup_count", 5)
)

# Create an application logger with context
app_logger = get_logger("app.main", service="web_to_audiobook")

# Create FastAPI app
app = FastAPI(
    title="Web to Audiobook Conversion",
    description="Convert web articles to audiobooks",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Log request details
    app_logger.info(
        "Request started",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else None,
        },
    )
    
    # Process the request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response details
    app_logger.info(
        "Request completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "processing_time_ms": round(process_time * 1000, 2),
        },
    )
    
    # Add custom headers to response
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2)) + " ms"
    
    return response

# Include routers
app.include_router(health.router)

# Include TTS router
try:
    from app.routers import tts
    app.include_router(tts.router)
    logger.info("TTS API enabled")
except ImportError as e:
    logger.warning(f"TTS API not available - missing dependencies: {str(e)}")
except Exception as e:
    logger.error(f"Error setting up TTS API: {str(e)}")

# Conditionally include content extraction router if Jina API key is configured
if settings.jina_api_key:
    try:
        from app.routers import content_extraction
        app.include_router(content_extraction.router)
        logger.info("Content extraction API enabled")
    except ImportError as e:
        logger.warning(f"Content extraction API not available - missing dependencies: {str(e)}")
    except Exception as e:
        logger.error(f"Error setting up content extraction API: {str(e)}")
else:
    logger.info("Content extraction API disabled - no Jina API key configured")

app_logger.info("Application startup complete")

# Run the app with Uvicorn when this module is executed directly
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting development server...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8142, reload=True)
