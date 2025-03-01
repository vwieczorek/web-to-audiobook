from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, Field


class TTSProvider(str, Enum):
    """Supported TTS providers."""
    OPENAI = "openai"
    LOCAL = "local"


class TTSVoice(str, Enum):
    """Available voices for TTS."""
    # OpenAI voices
    ALLOY = "alloy"
    ECHO = "echo"
    FABLE = "fable"
    ONYX = "onyx"
    NOVA = "nova"
    SHIMMER = "shimmer"
    # Local voices can be added here
    DEFAULT_LOCAL = "default_local"


class TTSModel(str, Enum):
    """Available TTS models."""
    # OpenAI models
    TTS_1 = "tts-1"
    TTS_1_HD = "tts-1-hd"
    # Local models can be added here
    LOCAL_DEFAULT = "local_default"


class TTSFormat(str, Enum):
    """Supported audio formats."""
    MP3 = "mp3"
    WAV = "wav"
    OGG = "ogg"
    FLAC = "flac"


class TTSConfig(BaseModel):
    """Configuration for TTS processing."""
    provider: TTSProvider = Field(default=TTSProvider.OPENAI)
    model: TTSModel = Field(default=TTSModel.TTS_1)
    voice: TTSVoice = Field(default=TTSVoice.NOVA)
    output_format: TTSFormat = Field(default=TTSFormat.MP3)
    chunk_size: int = Field(default=4000, description="Maximum characters per chunk")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_delay: float = Field(default=1.0, description="Delay between retries in seconds")
    timeout: float = Field(default=30.0, description="Request timeout in seconds")
    temp_dir: Optional[str] = Field(default=None, description="Directory for temporary files")


class TTSRequest(BaseModel):
    """Request for TTS conversion."""
    text: str = Field(..., description="Text to convert to speech")
    config: TTSConfig = Field(default_factory=TTSConfig)


class TTSChunk(BaseModel):
    """A chunk of text for TTS processing."""
    id: int = Field(..., description="Chunk identifier")
    text: str = Field(..., description="Text content")
    audio_data: Optional[bytes] = Field(default=None, description="Processed audio data")
    processed: bool = Field(default=False, description="Whether the chunk has been processed")
    error: Optional[str] = Field(default=None, description="Error message if processing failed")


class TTSProgress(BaseModel):
    """Progress information for TTS conversion."""
    total_chunks: int = Field(..., description="Total number of chunks")
    processed_chunks: int = Field(default=0, description="Number of processed chunks")
    failed_chunks: int = Field(default=0, description="Number of failed chunks")
    
    @property
    def progress_percentage(self) -> float:
        """Calculate the progress percentage."""
        if self.total_chunks == 0:
            return 100.0
        return (self.processed_chunks / self.total_chunks) * 100


class TTSResponse(BaseModel):
    """Response from TTS conversion."""
    audio_data: Optional[bytes] = Field(default=None, description="Processed audio data")
    format: TTSFormat = Field(..., description="Audio format")
    duration: Optional[float] = Field(default=None, description="Audio duration in seconds")
    chunks: List[TTSChunk] = Field(default_factory=list, description="Processed chunks")
    progress: TTSProgress = Field(..., description="Processing progress")
    error: Optional[str] = Field(default=None, description="Error message if processing failed")
    success: bool = Field(default=True, description="Whether the conversion was successful")


class TTSError(BaseModel):
    """Error response from TTS conversion."""
    message: str = Field(..., description="Error message")
    details: Optional[str] = Field(default=None, description="Detailed error information")
    chunk_id: Optional[int] = Field(default=None, description="ID of the chunk that failed")
