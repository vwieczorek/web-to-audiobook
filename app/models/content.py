from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class ContentMetadata(BaseModel):
    """Metadata for extracted content."""
    
    title: str = Field(..., description="Title of the article")
    url: HttpUrl = Field(..., description="Original URL of the content")
    author: Optional[str] = Field(None, description="Author of the article if available")
    publication_date: Optional[datetime] = Field(None, description="Publication date if available")
    estimated_reading_time: Optional[int] = Field(None, description="Estimated reading time in minutes")
    word_count: Optional[int] = Field(None, description="Number of words in the content")
    domain: Optional[str] = Field(None, description="Domain of the content source")


class ContentSection(BaseModel):
    """Section of content with heading and paragraphs."""
    
    heading: Optional[str] = Field(None, description="Heading of the section")
    level: int = Field(1, description="Heading level (1-6)")
    paragraphs: List[str] = Field(default_factory=list, description="Paragraphs in this section")
    

class ExtractedContent(BaseModel):
    """Extracted content with metadata and structured content."""
    
    metadata: ContentMetadata = Field(..., description="Metadata of the content")
    sections: List[ContentSection] = Field(default_factory=list, description="Structured content sections")
    plain_text: str = Field(..., description="Full extracted content as plain text")
    extraction_time: datetime = Field(default_factory=datetime.utcnow, description="Time when content was extracted")
    
    @property
    def full_content(self) -> str:
        """Return the full content as a formatted string."""
        result = []
        
        for section in self.sections:
            if section.heading:
                result.append(f"{'#' * section.level} {section.heading}")
                result.append("")  # Empty line after heading
            
            for paragraph in section.paragraphs:
                result.append(paragraph)
                result.append("")  # Empty line between paragraphs
        
        return "\n".join(result).strip()


class ExtractionError(BaseModel):
    """Error information for failed extractions."""
    
    url: HttpUrl = Field(..., description="URL that failed to extract")
    error_type: str = Field(..., description="Type of error encountered")
    error_message: str = Field(..., description="Error message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Time of error")
    status_code: Optional[int] = Field(None, description="HTTP status code if applicable")
    retry_count: int = Field(0, description="Number of retry attempts made")


# The following is the simplified model used by the placeholder implementation
# This can be removed once the full implementation is ready
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ExtractionError(BaseModel):
    """Model for content extraction errors."""
    error_message: str
    status_code: Optional[int] = None
    details: Optional[Dict[str, Any]] = None


class ExtractedContent(BaseModel):
    """Model for extracted content from a URL."""
    title: str
    content: str
    url: str
    author: Optional[str] = None
    published_date: Optional[str] = None
    summary: Optional[str] = None
    word_count: Optional[int] = None
    estimated_reading_time: Optional[int] = Field(
        None, description="Estimated reading time in minutes"
    )
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
