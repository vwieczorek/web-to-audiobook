"""Test Pydantic models for UTC datetime handling."""
import pytest
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class TestPydanticModels:
    """Test Pydantic models for proper UTC datetime handling."""
    
    def test_datetime_field_with_utc(self):
        """Test that datetime fields use timezone-aware UTC."""
        
        class ModelWithDatetime(BaseModel):
            created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
        
        # Create an instance
        model = ModelWithDatetime()
        
        # Check that the datetime is timezone-aware
        assert model.created_at.tzinfo is not None
        assert model.created_at.tzinfo.utcoffset(model.created_at).total_seconds() == 0
