import re
from datetime import datetime
from typing import List, Dict, Union, Optional
import httpx
from urllib.parse import urlparse

from app.models.content import (
    ExtractedContent,
    ExtractionError,
    ContentMetadata,
    ContentSection
)
from app.services.content_extraction.base import ContentExtractor
from app.services.http_client import HttpClient


class JinaContentExtractor(ContentExtractor):
    """Content extractor implementation using Jina.ai API."""
    
    def __init__(self, api_key: str, base_url: str = "https://r.jina.ai/", http_client: Optional[HttpClient] = None):
        """
        Initialize the Jina content extractor.
        
        Args:
            api_key: Jina.ai API key
            base_url: Base URL for Jina.ai API
            http_client: HTTP client to use. If None, a default one will be created.
        """
        super().__init__()
        self.api_key = api_key
        self.base_url = base_url
        self.http_client = http_client or HttpClient(max_retries=3, logger=self.logger)
    
    async def extract_content(self, url: str) -> Union[PlaceholderExtractedContent, PlaceholderExtractionError]:
        """
        Extract content from a URL using Jina.ai.
        
        Args:
            url: The URL to extract content from
            
        Returns:
            ExtractedContent if successful, ExtractionError if failed
        """
        self.logger.info(f"Extracting content from {url}")
        
        # Prepare request
        jina_url = f"{self.base_url.rstrip('/')}/{url}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Retain-Images": "none",
            "X-Return-Format": "text"
        }
        
        # Make request
        response = await self.http_client.request(
            method="GET",
            url=jina_url,
            headers=headers
        )
        
        # Handle errors
        if isinstance(response, Exception):
            error = ExtractionError(
                url=url,
                error_type=type(response).__name__,
                error_message=str(response),
                status_code=None,
                retry_count=getattr(response, 'retry_count', 0)
            )
            self.logger.error(f"Failed to extract content: {error.error_message}")
            return error
        
        if response.status_code != 200:
            error = ExtractionError(
                url=url,
                error_type="HTTPError",
                error_message=f"Jina.ai API returned {response.status_code}",
                status_code=response.status_code,
                retry_count=getattr(response, 'retry_count', 0)
            )
            self.logger.error(f"Failed to extract content: {error.error_message}")
            return error
        
        # Process content
        content_text = response.text
        
        # Extract metadata
        metadata_dict = await self.extract_metadata(content_text, url)
        metadata = ContentMetadata(**metadata_dict)
        
        # Parse content structure
        sections = await self.parse_structure(content_text)
        
        # Create extracted content
        extracted_content = ExtractedContent(
            metadata=metadata,
            sections=sections,
            plain_text=content_text
        )
        
        self.logger.info(f"Successfully extracted content from {url}, title: '{metadata.title}'")
        return extracted_content
    
    async def extract_metadata(self, content: str, url: str) -> Dict:
        """
        Extract metadata from the content.
        
        Args:
            content: The extracted content
            url: The URL from which the content was extracted
            
        Returns:
            Dictionary with metadata
        """
        # Parse URL for domain
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Extract title (first line/heading)
        lines = content.strip().split('\n')
        title = lines[0] if lines else "Unknown Title"
        
        # Simple heuristic for estimating reading time (average reading speed: ~250 words per minute)
        words = content.split()
        word_count = len(words)
        reading_time = max(1, round(word_count / 250))
        
        # Build metadata
        metadata = {
            "title": title,
            "url": url,
            "domain": domain,
            "word_count": word_count,
            "estimated_reading_time": reading_time,
            # Author and publication date would need more sophisticated extraction
            # or additional API responses from Jina
            "author": None,
            "publication_date": None
        }
        
        return metadata
    
    async def parse_structure(self, content: str) -> List[ContentSection]:
        """
        Parse content into structured sections based on headings and paragraphs.
        
        Args:
            content: The extracted content
            
        Returns:
            List of ContentSection objects
        """
        if not content:
            return []
        
        sections = []
        current_section = None
        lines = content.strip().split('\n')
        
        # First line is usually the title, so use it for the main section
        title_line = lines[0] if lines else ""
        
        # Create root section with title as heading
        current_section = ContentSection(
            heading=title_line,
            level=1,
            paragraphs=[]
        )
        sections.append(current_section)
        
        # Process remaining lines
        current_paragraph = []
        
        for i, line in enumerate(lines[1:], start=1):
            line = line.strip()
            
            # Check if it's a heading (simple heuristic)
            # Look for common patterns of headings: 
            # 1. Line followed by an empty line that isn't part of a paragraph
            # 2. Very short lines that appear to be section headers
            # 3. Lines with markdown heading format (# Heading)
            heading_match = re.match(r'^(#+)\s+(.*)', line)
            is_heading = heading_match
            
            # Check if it's a short line that could be a header
            # and is followed by an empty line (if not the last line)
            if (not is_heading and len(line) < 30 and line and 
                (i < len(lines) - 2 and not lines[i+1].strip())):
                is_heading = True
                heading_level = 2  # Default subheading level
                heading_text = line
            elif heading_match:
                heading_level = len(heading_match.group(1))
                heading_text = heading_match.group(2)
            else:
                is_heading = False
            
            if is_heading:
                # Save current paragraph if any
                if current_paragraph:
                    current_section.paragraphs.append(" ".join(current_paragraph))
                    current_paragraph = []
                
                # Create new section
                current_section = ContentSection(
                    heading=heading_text if heading_match else line,
                    level=heading_level if heading_match else 2,  # Default to level 2 for non-markdown headings
                    paragraphs=[]
                )
                sections.append(current_section)
                continue
            
            # Handle paragraph breaks
            if not line and current_paragraph:
                current_section.paragraphs.append(" ".join(current_paragraph))
                current_paragraph = []
                continue
            
            # Add to current paragraph if not empty
            if line:
                current_paragraph.append(line)
        
        # Add final paragraph if any
        if current_paragraph:
            current_section.paragraphs.append(" ".join(current_paragraph))
        
        return sections


# The following is the placeholder implementation
# This can be removed once the full implementation is ready
import logging
from typing import Union, Dict, Any

import httpx
from pydantic import ValidationError

from app.models.content import PlaceholderExtractedContent, PlaceholderExtractionError


logger = logging.getLogger(__name__)


class JinaContentExtractorPlaceholder:
    """
    Content extraction service using Jina.ai API (placeholder implementation).
    """
    
    def __init__(self, api_key: str):
        """Initialize with Jina API key."""
        self.api_key = api_key
        self.base_url = "https://api.jina.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def extract_content(self, url: str) -> Union[ExtractedContent, ExtractionError]:
        """
        Extract content from a URL using Jina.ai API.
        
        Args:
            url: The URL to extract content from
            
        Returns:
            ExtractedContent or ExtractionError
        """
        logger.info(f"Extracting content from URL: {url}")
        
        # This is a placeholder implementation
        # In a real implementation, we would call the Jina API
        try:
            # Simulate a successful extraction
            # In a real implementation, replace with actual API call
            extracted_data = {
                "title": "Sample Article Title",
                "content": "This is a placeholder for the extracted content. In a real implementation, this would be the actual content extracted from the URL.",
                "url": url,
                "author": "Sample Author",
                "published_date": "2023-01-01",
                "summary": "This is a sample summary of the article.",
                "word_count": 150,
                "estimated_reading_time": 1,
                "tags": ["sample", "placeholder"],
                "metadata": {"source": "placeholder"}
            }
            
            return PlaceholderExtractedContent(**extracted_data)
            
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return PlaceholderExtractionError(
                error_message="Failed to validate extracted content",
                details={"validation_errors": str(e)}
            )
        except Exception as e:
            logger.error(f"Error extracting content: {str(e)}")
            return PlaceholderExtractionError(
                error_message=f"Failed to extract content: {str(e)}"
            )
