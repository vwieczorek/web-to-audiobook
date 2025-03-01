"""Test datetime compatibility across Python versions."""
import pytest
from datetime import datetime, timezone


def test_utc_timezone_compatibility():
    """
    Test that we can get UTC time in a way that's compatible with both Python 3.10 and 3.11+.
    
    In Python 3.11+, datetime.UTC is available.
    In Python 3.10 and earlier, we need to use datetime.timezone.utc.
    """
    # This should work in all Python versions
    now_utc = datetime.now(timezone.utc)
    assert now_utc.tzinfo is not None
    assert now_utc.tzinfo.utcoffset(now_utc).total_seconds() == 0
    
    # Test formatting
    iso_format = now_utc.isoformat()
    assert "+" in iso_format or "Z" in iso_format  # Should have timezone info
    
    # Test that we can parse it back
    parsed = datetime.fromisoformat(iso_format)
    assert parsed.tzinfo is not None
