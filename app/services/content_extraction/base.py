from abc import ABC, abstractmethod
from typing import Optional, Union
import logging

from app.models.content import ExtractedContent, ExtractionError


class ContentExtractor(ABC):
    """Abstract base class for content extraction services."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def extract_content(self, url: str) -> Union[ExtractedContent, ExtractionError]:
        """
        Extract content from a URL.
        
        Args:
            url: The URL to extract content from
            
        Returns:
            Either ExtractedContent if successful or ExtractionError if failed
        """
        pass
    
    @abstractmethod
    async def extract_metadata(self, content: str, url: str) -> dict:
        """
        Extract metadata from content.
        
        Args:
            content: The extracted content
            url: The URL from which the content was extracted
            
        Returns:
            Dictionary containing metadata
        """
        pass
    
    @abstractmethod
    async def parse_structure(self, content: str) -> list:
        """
        Parse content structure (headings, paragraphs, etc.)
        
        Args:
            content: The extracted content
            
        Returns:
            List of ContentSection objects
        """
        pass