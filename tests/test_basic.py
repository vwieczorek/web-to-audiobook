"""Basic tests to verify pytest is working correctly."""
import pytest


def test_simple_assertion():
    """Test that pytest is working with a simple assertion."""
    assert True


@pytest.mark.unit
def test_with_unit_marker():
    """Test that the unit marker is working."""
    assert 1 + 1 == 2


@pytest.fixture
def sample_data():
    """Fixture that provides sample data."""
    return {"key": "value"}


def test_with_fixture(sample_data):
    """Test that fixtures are working."""
    assert sample_data["key"] == "value"


@pytest.mark.asyncio
async def test_async_function():
    """Test that async tests are working."""
    result = await async_operation()
    assert result == "done"


async def async_operation():
    """Sample async operation for testing."""
    return "done"
