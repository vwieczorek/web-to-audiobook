import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel

from app.config import Settings
from app.models.tts import (
    TTSRequest, TTSResponse, TTSError, TTSProvider
)
from app.services.tts.openai_tts import OpenAITTSService
from app.services.tts.local_tts import LocalTTSService
from app.services.http_client import HttpClient


router = APIRouter(prefix="/tts", tags=["text-to-speech"])
logger = logging.getLogger(__name__)


def get_settings():
    """Get application settings."""
    return Settings()


async def get_tts_service(
    provider: TTSProvider,
    settings: Settings = Depends(get_settings)
):
    """
    Get the appropriate TTS service based on the provider.
    Raises an exception if required API keys are not configured.
    """
    if provider == TTSProvider.OPENAI:
        if not settings.openai_api_key:
            logger.error("OpenAI API key not configured")
            raise HTTPException(
                status_code=500,
                detail="OpenAI TTS service not properly configured. Missing API key."
            )
        
        # Create an HTTP client for the service
        http_client = HttpClient(logger=logger)
        
        return OpenAITTSService(
            api_key=settings.openai_api_key.get_secret_value(),
            http_client=http_client,
            logger=logger
        )
    
    elif provider == TTSProvider.LOCAL:
        return LocalTTSService(logger=logger)
    
    else:
        logger.error(f"Unsupported TTS provider: {provider}")
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported TTS provider: {provider}"
        )


class TTSRequestBody(BaseModel):
    """Request body for TTS endpoint."""
    request: TTSRequest


@router.post("/convert", response_model=TTSResponse)
async def convert_text_to_speech(
    request_body: TTSRequestBody = Body(...),
):
    """
    Convert text to speech using the specified provider.
    """
    request = request_body.request
    logger.info(f"Converting text to speech using provider: {request.config.provider}")
    
    try:
        # Get the appropriate TTS service
        service = await get_tts_service(request.config.provider)
        
        # Convert text to speech
        result = await service.convert_text_to_speech(request)
        
        if isinstance(result, TTSError):
            logger.error(f"TTS conversion failed: {result.message}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to convert text to speech: {result.message}"
            )
        
        return result
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        logger.exception("Unexpected error in TTS conversion")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error in TTS conversion: {str(e)}"
        )
