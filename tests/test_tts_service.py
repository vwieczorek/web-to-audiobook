import pytest
import os
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from io import BytesIO

# Import the modules we're testing
from app.services.tts.base import TTSService
from app.services.tts.openai_tts import OpenAITTSService
from app.services.tts.local_tts import LocalTTSService

from app.models.tts import (
    TTSRequest, TTSResponse, TTSError, TTSChunk, 
    TTSConfig, TTSProvider, TTSModel, TTSVoice, TTSFormat
)
from app.services.tts import TTSService, OpenAITTSService, LocalTTSService
from app.services.http_client import HttpClient


class TestTTSService:
    """Tests for the base TTSService class."""
    
    def test_split_text_small_chunk(self):
        """Test splitting text when it fits in a single chunk."""
        # Create a concrete subclass for testing
        class TestTTS(TTSService):
            async def convert_text_to_speech(self, request):
                pass
            
            async def process_chunk(self, chunk, config):
                pass
        
        service = TestTTS()
        text = "This is a short text."
        chunks = service.split_text(text, 100)
        
        assert len(chunks) == 1
        assert chunks[0] == text
    
    def test_split_text_multiple_chunks(self):
        """Test splitting text into multiple chunks."""
        # Create a concrete subclass for testing
        class TestTTS(TTSService):
            async def convert_text_to_speech(self, request):
                pass
            
            async def process_chunk(self, chunk, config):
                pass
        
        service = TestTTS()
        text = "This is the first sentence. This is the second sentence. This is the third sentence."
        chunks = service.split_text(text, 30)
        
        assert len(chunks) > 1
        # Check that we have all the content
        assert ''.join(chunks).replace(' ', '') == text.replace(' ', '')
    
    def test_create_progress_tracker(self):
        """Test creating a progress tracker."""
        # Create a concrete subclass for testing
        class TestTTS(TTSService):
            async def convert_text_to_speech(self, request):
                pass
            
            async def process_chunk(self, chunk, config):
                pass
        
        service = TestTTS()
        progress = service.create_progress_tracker(5)
        
        assert progress.total_chunks == 5
        assert progress.processed_chunks == 0
        assert progress.failed_chunks == 0
        assert progress.progress_percentage == 0.0
    
    def test_update_progress(self):
        """Test updating progress tracker."""
        # Create a concrete subclass for testing
        class TestTTS(TTSService):
            async def convert_text_to_speech(self, request):
                pass
            
            async def process_chunk(self, chunk, config):
                pass
        
        service = TestTTS()
        progress = service.create_progress_tracker(5)
        
        # Process a successful chunk
        chunk1 = TTSChunk(id=1, text="Test", processed=True)
        progress = service.update_progress(progress, chunk1)
        
        assert progress.processed_chunks == 1
        assert progress.failed_chunks == 0
        assert progress.progress_percentage == 20.0
        
        # Process a failed chunk
        chunk2 = TTSChunk(id=2, text="Test", processed=True, error="Error")
        progress = service.update_progress(progress, chunk2)
        
        assert progress.processed_chunks == 2
        assert progress.failed_chunks == 1
        assert progress.progress_percentage == 40.0
    
    @pytest.mark.asyncio
    async def test_concatenate_audio(self):
        """Test concatenating audio chunks."""
        # Create a concrete subclass for testing
        class TestTTS(TTSService):
            async def convert_text_to_speech(self, request):
                pass
            
            async def process_chunk(self, chunk, config):
                pass
        
        service = TestTTS()
        
        # Create test chunks with audio data
        chunks = [
            TTSChunk(id=1, text="Chunk 1", processed=True, audio_data=b"audio1"),
            TTSChunk(id=2, text="Chunk 2", processed=True, audio_data=b"audio2"),
            TTSChunk(id=3, text="Chunk 3", processed=True, audio_data=b"audio3")
        ]
        
        # Test concatenation
        audio_data, error_message = await service.concatenate_audio(chunks, TTSFormat.MP3)
        
        # Verify result
        assert audio_data == b"audio1audio2audio3"
        assert error_message is None
        
        # Test with a failed chunk
        chunks.append(TTSChunk(id=4, text="Failed chunk", processed=False, error="Error"))
        audio_data, error_message = await service.concatenate_audio(chunks, TTSFormat.MP3)
        
        # Verify result (should skip failed chunks)
        assert audio_data == b"audio1audio2audio3"
        assert error_message is None


@pytest.mark.asyncio
class TestOpenAITTSService:
    """Tests for the OpenAITTSService class."""
    
    @pytest.fixture
    def mock_http_client(self):
        """Create a mock HTTP client."""
        client = MagicMock(spec=HttpClient)
        client.request = AsyncMock()
        return client
    
    @pytest.fixture
    def service(self, mock_http_client):
        """Create an OpenAITTSService instance with a mock HTTP client."""
        return OpenAITTSService(
            api_key="test_api_key",
            http_client=mock_http_client
        )
    
    async def test_process_chunk_success(self, service, mock_http_client):
        """Test processing a chunk successfully."""
        # Mock response with status_code attribute
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"audio_data"
        mock_http_client.request.return_value = mock_response
        
        # Create chunk and config
        chunk = TTSChunk(id=1, text="Test text")
        config = TTSConfig(
            provider=TTSProvider.OPENAI,
            model=TTSModel.TTS_1,
            voice=TTSVoice.NOVA,
            output_format=TTSFormat.MP3
        )
        
        # Process chunk
        result = await service.process_chunk(chunk, config)
        
        # Verify result
        assert result.processed is True
        assert result.audio_data == b"audio_data"
        assert result.error is None
        
        # Verify API call
        mock_http_client.request.assert_called_once_with(
            method="POST",
            url="https://api.openai.com/v1/audio/speech",
            headers={
                "Authorization": "Bearer test_api_key",
                "Content-Type": "application/json"
            },
            json={
                "model": "tts-1",
                "input": "Test text",
                "voice": "nova",
                "response_format": "mp3"
            },
            retry_codes=[429, 500, 502, 503, 504]
        )
    
    async def test_process_chunk_error(self, service, mock_http_client):
        """Test processing a chunk with an error."""
        # Mock error response with status_code attribute
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {"message": "Invalid request"}
        }
        mock_http_client.request.return_value = mock_response
        
        # Create chunk and config
        chunk = TTSChunk(id=1, text="Test text")
        config = TTSConfig(
            provider=TTSProvider.OPENAI,
            model=TTSModel.TTS_1,
            voice=TTSVoice.NOVA,
            output_format=TTSFormat.MP3
        )
        
        # Process chunk
        result = await service.process_chunk(chunk, config)
        
        # Verify result
        assert result.processed is False
        assert result.audio_data is None
        assert result.error == "Invalid request"
    
    async def test_convert_text_to_speech(self, service, mock_http_client):
        """Test converting text to speech."""
        # Mock successful response for chunks with status_code attribute
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"audio_data"
        mock_http_client.request.return_value = mock_response
        
        # Create request
        request = TTSRequest(
            text="This is a test text for TTS conversion.",
            config=TTSConfig(
                provider=TTSProvider.OPENAI,
                model=TTSModel.TTS_1,
                voice=TTSVoice.NOVA,
                output_format=TTSFormat.MP3,
                chunk_size=100
            )
        )
        
        # Convert text to speech
        result = await service.convert_text_to_speech(request)
        
        # Verify result
        assert isinstance(result, TTSResponse)
        assert result.success is True
        assert result.audio_data is not None
        assert result.format == TTSFormat.MP3
        assert result.progress.total_chunks == 1
        assert result.progress.processed_chunks == 1
        assert result.progress.failed_chunks == 0
    
    async def test_convert_text_to_speech_invalid_provider(self, service):
        """Test converting text with invalid provider."""
        # Create request with invalid provider
        request = TTSRequest(
            text="This is a test text.",
            config=TTSConfig(
                provider=TTSProvider.LOCAL,  # Not supported by OpenAITTSService
                model=TTSModel.TTS_1,
                voice=TTSVoice.NOVA,
                output_format=TTSFormat.MP3
            )
        )
        
        # Convert text to speech
        result = await service.convert_text_to_speech(request)
        
        # Verify result
        assert isinstance(result, TTSError)
        assert "Invalid provider" in result.message


@pytest.mark.asyncio
class TestLocalTTSService:
    """Tests for the LocalTTSService class."""
    
    @pytest.fixture
    def service(self):
        """Create a LocalTTSService instance."""
        return LocalTTSService(logger=MagicMock())
    
    @patch("asyncio.sleep")
    async def test_process_chunk(self, mock_sleep, service):
        """Test processing a chunk with local TTS."""
        # Create chunk and config
        chunk = TTSChunk(id=1, text="Test text")
        config = TTSConfig(
            provider=TTSProvider.LOCAL,
            model=TTSModel.LOCAL_DEFAULT,
            voice=TTSVoice.DEFAULT_LOCAL,
            output_format=TTSFormat.MP3
        )
        
        # Process chunk
        result = await service.process_chunk(chunk, config)
        
        # Verify result
        assert result.processed is True
        assert result.audio_data is not None
        assert result.error is None
        
        # Verify that sleep was called
        mock_sleep.assert_called_once()
    
    @patch("asyncio.sleep")
    async def test_convert_text_to_speech(self, mock_sleep, service):
        """Test converting text to speech with local TTS."""
        # Create request
        request = TTSRequest(
            text="This is a test text for local TTS conversion.",
            config=TTSConfig(
                provider=TTSProvider.LOCAL,
                model=TTSModel.LOCAL_DEFAULT,
                voice=TTSVoice.DEFAULT_LOCAL,
                output_format=TTSFormat.MP3,
                chunk_size=100
            )
        )
        
        # Convert text to speech
        result = await service.convert_text_to_speech(request)
        
        # Verify result
        assert isinstance(result, TTSResponse)
        assert result.success is True
        assert result.audio_data is not None
        assert result.format == TTSFormat.MP3
        assert result.progress.total_chunks == 1
        assert result.progress.processed_chunks == 1
        assert result.progress.failed_chunks == 0
        
        # Verify that sleep was called
        mock_sleep.assert_called()
    
    async def test_convert_text_to_speech_invalid_provider(self, service):
        """Test converting text with invalid provider."""
        # Create request with invalid provider
        request = TTSRequest(
            text="This is a test text.",
            config=TTSConfig(
                provider=TTSProvider.OPENAI,  # Not supported by LocalTTSService
                model=TTSModel.TTS_1,
                voice=TTSVoice.NOVA,
                output_format=TTSFormat.MP3
            )
        )
        
        # Convert text to speech
        result = await service.convert_text_to_speech(request)
        
        # Verify result
        assert isinstance(result, TTSError)
        assert "Invalid provider" in result.message
