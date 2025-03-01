import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import HttpUrl

from app.config import Settings
from app.models.content import ExtractedContent, ExtractionError, PlaceholderExtractedContent
from app.services.content_extraction.jina_extractor import JinaContentExtractor, JinaContentExtractorPlaceholder


router = APIRouter(prefix="/extract", tags=["content-extraction"])
logger = logging.getLogger(__name__)


def get_settings():
    """Get application settings."""
    return Settings()


async def get_jina_extractor(settings: Settings = Depends(get_settings)):
    """
    Get the Jina content extractor service.
    Raises an exception if API key is not configured.
    """
    if not settings.jina_api_key:
        logger.error("Jina API key not configured")
        raise HTTPException(
            status_code=500,
            detail="Content extraction service not properly configured. Missing API key."
        )
    
    # Use the placeholder implementation for now
    # TODO: Switch to the full implementation when ready
    return JinaContentExtractorPlaceholder(api_key=settings.jina_api_key.get_secret_value())


@router.post("/url", response_model=PlaceholderExtractedContent)
async def extract_from_url(
    url: HttpUrl = Body(..., embed=True),
    extractor: JinaContentExtractor = Depends(get_jina_extractor)
):
    """
    Extract content from a URL.
    """
    logger.info(f"Extracting content from URL: {url}")
    
    result = await extractor.extract_content(url=str(url))
    
    if isinstance(result, ExtractionError):
        status_code = result.status_code or 500
        logger.error(f"Content extraction failed: {result.error_message}")
        raise HTTPException(
            status_code=status_code,
            detail=f"Failed to extract content: {result.error_message}"
        )
    
    return result


@router.get("/")
async def extract_content_placeholder():
    """
    Placeholder endpoint for content extraction.
    This will be implemented with Jina.ai integration.
    """
    logger.info("Content extraction endpoint called")
    return {"message": "Content extraction placeholder - will be implemented with Jina.ai"}
