import os
import logging
import asyncio
from typing import Optional, Union, Dict, Any

# Try to import aiohttp, but don't fail if it's not installed
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

from app.models.tts import (
    TTSRequest, TTSResponse, TTSError, TTSChunk, 
    TTSConfig, TTSProvider, TTSModel, TTSVoice
)
from app.services.tts.base import TTSService
from app.services.http_client import HttpClient


class OpenAITTSService(TTSService):
    """Text-to-speech service using OpenAI's API."""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1/audio/speech",
        http_client: Optional[HttpClient] = None,
        logger: Optional[logging.Logger] = None,
        temp_dir: Optional[str] = None
    ):
        """
        Initialize the OpenAI TTS service.
        
        Args:
            api_key: OpenAI API key
            base_url: Base URL for OpenAI API
            http_client: HTTP client for making requests
            logger: Logger instance
            temp_dir: Directory for temporary files
        """
        super().__init__(logger=logger, temp_dir=temp_dir)
        self.api_key = api_key
        self.base_url = base_url
        self.http_client = http_client or HttpClient(
            max_retries=3,
            retry_delay=1.0,
            timeout=30.0,
            logger=self.logger
        )
    
    async def convert_text_to_speech(
        self, 
        request: TTSRequest
    ) -> Union[TTSResponse, TTSError]:
        """
        Convert text to speech using OpenAI's API.
        
        Args:
            request: TTS request containing text and configuration
            
        Returns:
            TTSResponse or TTSError
        """
        try:
            # Validate provider
            if request.config.provider != TTSProvider.OPENAI:
                return TTSError(
                    message=f"Invalid provider: {request.config.provider}. This service only supports OpenAI."
                )
            
            # Split text into chunks
            text_chunks = self.split_text(request.text, request.config.chunk_size)
            chunks = [TTSChunk(id=i, text=text) for i, text in enumerate(text_chunks)]
            
            # Create progress tracker
            progress = self.create_progress_tracker(len(chunks))
            
            # Process chunks concurrently
            tasks = [self.process_chunk(chunk, request.config) for chunk in chunks]
            processed_chunks = await asyncio.gather(*tasks)
            
            # Update progress
            for chunk in processed_chunks:
                progress = self.update_progress(progress, chunk)
            
            # Concatenate audio
            audio_data, error = await self.concatenate_audio(processed_chunks, request.config.output_format)
            
            if error:
                return TTSResponse(
                    audio_data=None,
                    format=request.config.output_format,
                    chunks=processed_chunks,
                    progress=progress,
                    error=error,
                    success=False
                )
            
            return TTSResponse(
                audio_data=audio_data,
                format=request.config.output_format,
                chunks=processed_chunks,
                progress=progress,
                success=True
            )
            
        except Exception as e:
            error_msg = f"Error in TTS conversion: {str(e)}"
            self.logger.error(error_msg)
            return TTSError(message=error_msg)
    
    async def process_chunk(
        self, 
        chunk: TTSChunk,
        config: TTSConfig
    ) -> TTSChunk:
        """
        Process a single text chunk using OpenAI's API.
        
        Args:
            chunk: Text chunk to process
            config: TTS configuration
            
        Returns:
            Processed chunk with audio data
        """
        try:
            # Check if aiohttp is available
            if not AIOHTTP_AVAILABLE:
                chunk.error = "aiohttp library is required for OpenAI TTS service"
                self.logger.error(f"Chunk {chunk.id} failed: aiohttp library not installed")
                return chunk
                
            # Skip empty chunks
            if not chunk.text.strip():
                chunk.processed = True
                return chunk
            
            # Prepare request payload
            payload = {
                "model": config.model,
                "input": chunk.text,
                "voice": config.voice,
                "response_format": config.output_format
            }
            
            # Prepare headers
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Make API request
            response = await self.http_client.request(
                method="POST",
                url=self.base_url,
                headers=headers,
                json=payload,
                retry_codes=[429, 500, 502, 503, 504]
            )
            
            # Process response
            if hasattr(response, 'status_code'):
                if response.status_code == 200:
                    # Read binary audio data
                    chunk.audio_data = response.content
                    chunk.processed = True
                else:
                    # Handle error
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", {}).get("message", f"API error: {response.status_code}")
                    except Exception:
                        error_msg = f"API error: {response.status_code}"
                    chunk.error = error_msg
                    self.logger.error(f"Chunk {chunk.id} failed: {error_msg}")
            elif hasattr(response, 'status'):
                if response.status == 200:
                    # Read binary audio data
                    audio_data = await response.read()
                    chunk.audio_data = audio_data
                    chunk.processed = True
                else:
                    # Handle error
                    try:
                        error_data = await response.json()
                        error_msg = error_data.get("error", {}).get("message", f"API error: {response.status}")
                    except Exception:
                        error_msg = f"API error: {response.status}"
                    chunk.error = error_msg
                    self.logger.error(f"Chunk {chunk.id} failed: {error_msg}")
            elif isinstance(response, Exception):
                chunk.error = str(response)
                self.logger.error(f"Chunk {chunk.id} failed: {str(response)}")
            
            return chunk
            
        except Exception as e:
            error_msg = f"Error processing chunk {chunk.id}: {str(e)}"
            self.logger.error(error_msg)
            chunk.error = error_msg
            return chunk
