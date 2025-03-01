import pytest
import pytest_asyncio
from unittest.mock import MagicMock, patch, AsyncMock
import httpx

from app.services.content_extraction.jina_extractor import JinaContentExtractor
from app.services.http_client import HttpClient
from app.models.content import ExtractedContent, ExtractionError


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client."""
    client = MagicMock(spec=HttpClient)
    client.request = AsyncMock()
    return client


@pytest.fixture
def jina_extractor(mock_http_client):
    """Create a Jina extractor with a mock HTTP client."""
    return JinaContentExtractor(api_key="test_api_key", http_client=mock_http_client)


@pytest.fixture
def sample_content():
    """Sample content from neverssl.com."""
    return """NeverSSL
What?

This website is for when you try to open Facebook, Google, Amazon, etc on a wifi network, and nothing happens. Type "http://neverssl.com" into your browser's url bar, and you'll be able to log on.

How?

neverssl.com will never use SSL (also known as TLS). No encryption, no strong authentication, no HSTS, no HTTP/2.0, just plain old unencrypted HTTP and forever stuck in the dark ages of internet security.

Why?

Normally, that's a bad idea. You should always use SSL and secure encryption when possible. In fact, it's such a bad idea that most websites are now using https by default.

And that's great, but it also means that if you're relying on poorly-behaved wifi networks, it can be hard to get online. Secure browsers and websites using https make it impossible for those wifi networks to send you to a login or payment page. Basically, those networks can't tap into your connection just like attackers can't. Modern browsers are so good that they can remember when a website supports encryption and even if you type in the website name, they'll use https.

And if the network never redirects you to this page, well as you can see, you're not missing much.

Follow @neverssl"""


@pytest.mark.asyncio
async def test_extract_content_success(jina_extractor, mock_http_client, sample_content):
    """Test successful content extraction."""
    # Mock the response
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.text = sample_content
    mock_http_client.request.return_value = mock_response
    
    # Call the method
    result = await jina_extractor.extract_content("https://example.com")
    
    # Check request was made correctly
    mock_http_client.request.assert_called_once_with(
        method="GET",
        url="https://r.jina.ai/https://example.com",
        headers={
            "Authorization": "Bearer test_api_key",
            "X-Retain-Images": "none",
            "X-Return-Format": "text"
        }
    )
    
    # Check result
    assert isinstance(result, ExtractedContent)
    assert result.metadata.title == "NeverSSL"
    assert str(result.metadata.url).startswith("https://example.com")
    assert result.plain_text == sample_content
    assert len(result.sections) > 0


@pytest.mark.asyncio
async def test_extract_content_http_error(jina_extractor, mock_http_client):
    """Test extraction with HTTP error."""
    # Mock the response
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 403
    mock_http_client.request.return_value = mock_response
    
    # Call the method
    result = await jina_extractor.extract_content("https://example.com")
    
    # Check result
    assert isinstance(result, ExtractionError)
    assert result.error_type == "HTTPError"
    assert "403" in result.error_message
    assert result.status_code == 403


@pytest.mark.asyncio
async def test_extract_content_exception(jina_extractor, mock_http_client):
    """Test extraction with exception."""
    # Mock the error
    error = httpx.RequestError("Connection error", request=None)
    mock_http_client.request.return_value = error
    
    # Call the method
    result = await jina_extractor.extract_content("https://example.com")
    
    # Check result
    assert isinstance(result, ExtractionError)
    assert result.error_type == "RequestError"
    assert "Connection error" in result.error_message


@pytest.mark.asyncio
async def test_extract_metadata(jina_extractor, sample_content):
    """Test metadata extraction."""
    # Call the method
    metadata = await jina_extractor.extract_metadata(
        content=sample_content,
        url="https://neverssl.com"
    )
    
    # Check result
    assert metadata["title"] == "NeverSSL"
    assert metadata["url"] == "https://neverssl.com"
    assert metadata["domain"] == "neverssl.com"
    assert metadata["word_count"] > 0
    assert metadata["estimated_reading_time"] > 0


@pytest.mark.asyncio
async def test_parse_structure(jina_extractor, sample_content):
    """Test content structure parsing."""
    # Call the method
    sections = await jina_extractor.parse_structure(sample_content)
    
    # Check result
    assert len(sections) > 0
    
    # First section should have title as heading
    assert sections[0].heading == "NeverSSL"
    assert sections[0].level == 1
    
    # Check that we have at least some sections
    assert len(sections) >= 2
    
    # Check paragraphs contain expected content
    all_paragraphs = [p for section in sections for p in section.paragraphs]
    assert any("This website is for when you try to open" in p for p in all_paragraphs)
    assert any("neverssl.com will never use SSL" in p for p in all_paragraphs)
    
    # Check that at least one section has "What?", "How?", or "Why?" as heading or in paragraphs
    topic_found = False
    for section in sections:
        if any(topic in section.heading for topic in ["What", "How", "Why"]):
            topic_found = True
            break
        for para in section.paragraphs:
            if any(topic in para for topic in ["What?", "How?", "Why?"]):
                topic_found = True
                break
    
    assert topic_found, "No sections with expected topics found"