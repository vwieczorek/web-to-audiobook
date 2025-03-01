import os
import logging
import tempfile
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Union
import io

from app.models.tts import (
    TTSRequest, TTSResponse, TTSError, TTSChunk, 
    TTSProgress, TTSConfig, TTSFormat
)


class TTSService(ABC):
    """Abstract base class for text-to-speech services."""
    
    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        temp_dir: Optional[str] = None
    ):
        """
        Initialize the TTS service.
        
        Args:
            logger: Logger instance for logging
            temp_dir: Directory for temporary files
        """
        self.logger = logger or logging.getLogger(__name__)
        self.temp_dir = temp_dir or tempfile.gettempdir()
        
        # Create temp directory if it doesn't exist
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
    
    @abstractmethod
    async def convert_text_to_speech(
        self, 
        request: TTSRequest
    ) -> Union[TTSResponse, TTSError]:
        """
        Convert text to speech.
        
        Args:
            request: TTS request containing text and configuration
            
        Returns:
            TTSResponse or TTSError
        """
        pass
    
    @abstractmethod
    async def process_chunk(
        self, 
        chunk: TTSChunk,
        config: TTSConfig
    ) -> TTSChunk:
        """
        Process a single text chunk.
        
        Args:
            chunk: Text chunk to process
            config: TTS configuration
            
        Returns:
            Processed chunk with audio data
        """
        pass
    
    def split_text(self, text: str, chunk_size: int) -> List[str]:
        """
        Split text into chunks of appropriate size.
        
        Args:
            text: Text to split
            chunk_size: Maximum characters per chunk
            
        Returns:
            List of text chunks
        """
        # Simple splitting by chunk size, preserving sentences where possible
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        current_pos = 0
        text_length = len(text)
        
        while current_pos < text_length:
            # Try to find a sentence end within the chunk size
            end_pos = min(current_pos + chunk_size, text_length)
            
            # If we're not at the end of the text, try to find a good break point
            if end_pos < text_length:
                # Look for sentence endings (., !, ?)
                sentence_end = max(
                    text.rfind(". ", current_pos, end_pos),
                    text.rfind("! ", current_pos, end_pos),
                    text.rfind("? ", current_pos, end_pos)
                )
                
                # If found, break at sentence end
                if sentence_end > current_pos:
                    end_pos = sentence_end + 2  # Include the period and space
                else:
                    # Look for paragraph breaks
                    para_break = text.rfind("\n\n", current_pos, end_pos)
                    if para_break > current_pos:
                        end_pos = para_break + 2
                    else:
                        # Look for line breaks
                        line_break = text.rfind("\n", current_pos, end_pos)
                        if line_break > current_pos:
                            end_pos = line_break + 1
                        else:
                            # Look for space as last resort
                            space = text.rfind(" ", current_pos, end_pos)
                            if space > current_pos:
                                end_pos = space + 1
            
            # Add the chunk
            chunks.append(text[current_pos:end_pos].strip())
            current_pos = end_pos
        
        return chunks
    
    async def concatenate_audio(
        self, 
        chunks: List[TTSChunk],
        output_format: TTSFormat
    ) -> Tuple[bytes, Optional[str]]:
        """
        Concatenate audio chunks into a single audio file.
        
        Args:
            chunks: List of processed chunks with audio data
            output_format: Desired output format
            
        Returns:
            Tuple of (audio_data, error_message)
        """
        try:
            # Check if we have any successful chunks
            successful_chunks = [c for c in chunks if c.processed and c.audio_data]
            if not successful_chunks:
                return None, "No successful audio chunks to concatenate"
            
            # If only one chunk, return it directly
            if len(successful_chunks) == 1:
                return successful_chunks[0].audio_data, None
            
            # For more complex concatenation, we'll need to use a library like pydub
            # This is a simplified version that works for some formats
            buffer = io.BytesIO()
            for chunk in successful_chunks:
                if chunk.audio_data:
                    buffer.write(chunk.audio_data)
            
            buffer.seek(0)
            return buffer.read(), None
            
        except Exception as e:
            error_msg = f"Error concatenating audio: {str(e)}"
            self.logger.error(error_msg)
            return None, error_msg
    
    def create_progress_tracker(self, total_chunks: int) -> TTSProgress:
        """
        Create a progress tracker for TTS conversion.
        
        Args:
            total_chunks: Total number of chunks to process
            
        Returns:
            Progress tracker
        """
        return TTSProgress(total_chunks=total_chunks)
    
    def update_progress(
        self, 
        progress: TTSProgress, 
        chunk: TTSChunk
    ) -> TTSProgress:
        """
        Update progress tracker with chunk status.
        
        Args:
            progress: Progress tracker
            chunk: Processed chunk
            
        Returns:
            Updated progress tracker
        """
        if chunk.processed:
            progress.processed_chunks += 1
        if chunk.error:
            progress.failed_chunks += 1
        return progress
