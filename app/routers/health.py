import logging
from fastapi import APIRouter

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check():
    """Health check endpoint to verify the API is running."""
    logger.debug("Health check endpoint called")
    return {"status": "ok"}