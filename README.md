# Web to Audiobook Conversion Tool

This application converts web articles to audiobooks by extracting content using Jina.ai and converting it to speech using various TTS providers including OpenAI's TTS API. The service is built with FastAPI and can be deployed using Docker.

## Features

- Extract content from web articles using Jina.ai's extraction API
- Convert text to speech using multiple TTS providers:
  - OpenAI TTS API
  - Local TTS engines
- Process audio into various formats
- Containerized deployment with Docker
- API-first design with FastAPI
- Comprehensive error handling and logging
- Progress tracking for TTS conversion

## Requirements

- Python 3.10+
- Docker and Docker Compose (for containerized deployment)
- Dependencies:
  - FastAPI v0.103.1
  - Uvicorn v0.23.2
  - Pydantic v2.3.0
  - pydantic-settings v2.0.3
  - python-dotenv v1.0.0
  - httpx v0.24.1
  - aiohttp v3.8.5+

## Installation

### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd web-to-audiobook
   ```

2. Create a `.env` file based on the `.env.example` file:
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file to add your API keys for Jina.ai and OpenAI.

4. Build and start the container:
   ```bash
   docker-compose up -d
   ```

5. The API will be available at `http://localhost:8142`

### Manual Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd web-to-audiobook
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on the `.env.example` file:
   ```bash
   cp .env.example .env
   ```

5. Edit the `.env` file to add your API keys for Jina.ai and OpenAI.

6. Start the application:
   ```bash
   python -m app.main
   ```

7. The API will be available at `http://localhost:8142`

## API Documentation

Once the application is running, you can access the Swagger UI at `http://localhost:8142/docs` to explore and test the API endpoints.

### Main Endpoints

- **GET /health**: Check the health status of the service
- **POST /extract/url**: Extract content from a URL
- **POST /tts/convert**: Convert text to speech using the configured TTS provider

The API supports different TTS providers and configurations that can be specified in the request body. See the Swagger documentation for detailed request and response formats.

## Development

### Project Structure

```
project/
├── app/                           # Application code
│   ├── __init__.py
│   ├── main.py                    # Entry point for FastAPI
│   ├── config.py                  # Configuration management
│   ├── logging.py                 # Logging setup
│   ├── models/                    # Pydantic models
│   │   ├── content.py             # Content extraction models
│   │   └── tts.py                 # TTS models
│   ├── routers/                   # API routes
│   │   ├── content_extraction.py  # Content extraction endpoints
│   │   ├── health.py              # Health check endpoints
│   │   └── tts.py                 # TTS endpoints
│   ├── services/                  # Business logic
│   │   ├── content_extraction/    # Content extraction services
│   │   │   ├── base.py            # Base content extractor
│   │   │   └── jina_extractor.py  # Jina.ai implementation
│   │   ├── tts/                   # TTS services
│   │   │   ├── base.py            # Base TTS service
│   │   │   ├── local_tts.py       # Local TTS implementation
│   │   │   └── openai_tts.py      # OpenAI TTS implementation
│   │   └── http_client.py         # HTTP client with retry logic
├── tests/                         # Unit and integration tests
│   ├── integration/               # Integration tests
│   ├── routers/                   # Router tests
│   ├── services/                  # Service tests
│   └── run_coverage.py            # Coverage report script
├── logs/                          # Log files
├── Dockerfile                     # Docker configuration
├── docker-compose.yml             # Docker Compose configuration
├── requirements.txt               # Production dependencies
├── requirements-dev.txt           # Development dependencies
├── pyproject.toml                 # Project configuration
└── README.md                      # This file
```

### Running Tests

To run the tests, use the following command:

```bash
pytest
```

To run the tests with coverage:

```bash
python -m tests.run_coverage
```

Or:

```bash
pytest --cov=app
```

### Environment Variables

The application uses environment variables for configuration. Copy the `.env.example` file to `.env` and update the values:

```
APP_PORT=8142
APP_HOST=0.0.0.0
APP_LOG_LEVEL=INFO
APP_LOG_FILE=logs/app.log
APP_JINA_API_KEY=your_jina_api_key
APP_OPENAI_API_KEY=your_openai_api_key
```

## License

[MIT](LICENSE)
