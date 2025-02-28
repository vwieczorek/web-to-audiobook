import logging

from fastapi import FastAPI

from app.config import Settings
from app.logging import setup_logging
from app.routers import health

# Load settings
settings = Settings()

# Set up logging
logger = setup_logging(settings.log_file, settings.log_level)

# Create FastAPI app
app = FastAPI(
    title="Web to Audiobook Conversion",
    description="Convert web articles to audiobooks",
    version="0.1.0",
)

# Include routers
app.include_router(health.router)

logger.info("Application startup complete")

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        reload=True
    )