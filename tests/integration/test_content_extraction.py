import os
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.config import Settings
from app.services.content_extraction.jina_extractor import JinaContentExtractor


client = TestClient(app)


@pytest.mark.integration
def test_extract_content_endpoint():
    """
    Integration test for content extraction endpoint.
    Requires a valid Jina API key in the environment.
    
    Skip this test if INTEGRATION_TESTS environment variable is not set to "1".
    """
    if os.environ.get("INTEGRATION_TESTS") != "1":
        pytest.skip("Skipping integration test (INTEGRATION_TESTS != 1)")
    
    # Check if API key is available
    api_key = os.environ.get("APP_JINA_API_KEY")
    if not api_key:
        pytest.skip("Skipping integration test (APP_JINA_API_KEY not set)")
    
    # Make the request
    response = client.post(
        "/extract/url",
        json={"url": "http://neverssl.com"}
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    
    # Verify the response structure
    assert "metadata" in data
    assert "sections" in data
    assert "plain_text" in data
    
    # Verify content was actually extracted
    assert data["metadata"]["title"]
    assert len(data["sections"]) > 0
    assert "NeverSSL" in data["plain_text"]
    
    # Verify metadata
    metadata = data["metadata"]
    assert metadata["url"] == "http://neverssl.com"
    assert "neverssl.com" in metadata["domain"]
    assert metadata["word_count"] > 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_jina_extractor_direct():
    """
    Direct integration test for JinaContentExtractor.
    Requires a valid Jina API key in the environment.
    """
    if os.environ.get("INTEGRATION_TESTS") != "1":
        pytest.skip("Skipping integration test (INTEGRATION_TESTS != 1)")
    
    # Check if API key is available
    api_key = os.environ.get("APP_JINA_API_KEY")
    if not api_key:
        pytest.skip("Skipping integration test (APP_JINA_API_KEY not set)")
    
    # Create the extractor
    extractor = JinaContentExtractor(api_key=api_key)
    
    # Extract content
    result = await extractor.extract_content("http://neverssl.com")
    
    # Verify the result
    assert not isinstance(result, Exception)
    assert result.metadata.title
    assert "NeverSSL" in result.plain_text
    assert len(result.sections) > 0