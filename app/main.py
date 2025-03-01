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

logger.info("Application startup complete")
