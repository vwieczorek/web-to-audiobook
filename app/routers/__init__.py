from app.routers import health

# Don't import content_extraction here as it's conditionally loaded in main.py
__all__ = ["health"]
