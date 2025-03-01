import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.models.content import ExtractedContent, ContentMetadata, ContentSection


# Create a test client
client = TestClient(app)


@pytest.fixture
def mock_settings():
    """Mock settings with a dummy API key."""
    with patch("app.routers.content_extraction.Settings") as mock_settings:
        settings_instance = MagicMock()
        settings_instance.jina_api_key = MagicMock()
        settings_instance.jina_api_key.get_secret_value.return_value = "test_api_key"
        mock_settings.return_value = settings_instance
        yield settings_instance


@pytest.fixture
def mock_jina_extractor():
    """Create a mock JinaContentExtractor."""
    with patch("app.services.content_extraction.jina_extractor.JinaContentExtractor", autospec=True) as mock:
        extractor_instance = mock.return_value
        extractor_instance.extract_content = AsyncMock()
        yield extractor_instance


@pytest.fixture
def sample_extracted_content():
    """Create a sample ExtractedContent object."""
    return ExtractedContent(
        metadata=ContentMetadata(
            title="Test Article",
            url="https://example.com/article",
            domain="example.com",
            word_count=100,
            estimated_reading_time=1
        ),
        sections=[
            ContentSection(
                heading="Test Article",
                level=1,
                paragraphs=["This is a test paragraph."]
            )
        ],
        plain_text="Test Article\n\nThis is a test paragraph."
    )


@pytest.mark.skip(reason="Router test needs more complex mocking of FastAPI dependencies")
def test_extract_from_url(mock_jina_extractor, mock_settings, sample_extracted_content):
    """Test the extract_from_url endpoint."""
    # Configure the mock to return our sample content
    mock_jina_extractor.extract_content.return_value = sample_extracted_content
    
    # Make a request to the endpoint
    response = client.post(
        "/extract/url",
        json={"url": "https://example.com/article"}
    )
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    
    # Verify the response structure
    assert "metadata" in data
    assert "sections" in data
    assert "plain_text" in data
    
    # Verify the content
    assert data["metadata"]["title"] == "Test Article"
    assert data["metadata"]["url"] == "https://example.com/article"
    assert len(data["sections"]) == 1
    assert data["sections"][0]["heading"] == "Test Article"
    assert len(data["sections"][0]["paragraphs"]) == 1
    assert data["sections"][0]["paragraphs"][0] == "This is a test paragraph."