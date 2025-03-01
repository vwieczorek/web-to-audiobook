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

Once the application is running, you can access the Swagger UI at `http://localhost:8142/docs`

### Main Endpoints

- **GET /health**: Check the health status of the service
- **POST /content/extract**: Extract content from a URL
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

### Configuration

#### Environment Variables

The application uses environment variables for configuration. Copy the `.env.example` file to `.env` and update the values:

```
# Server settings
APP_PORT=8142                      # Port the application will listen on
APP_HOST=0.0.0.0                   # Host the application will bind to

# Logging settings
APP_LOG_LEVEL=INFO                 # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
APP_LOG_FILE=logs/app.log          # Path to log file
APP_LOG_ROTATION_MAX_BYTES=10485760  # 10MB - Maximum size before log rotation
APP_LOG_ROTATION_BACKUP_COUNT=5    # Number of backup log files to keep

# External services API keys
APP_JINA_API_KEY=your_jina_api_key # API key for Jina.ai content extraction
APP_OPENAI_API_KEY=your_openai_api_key # API key for OpenAI TTS service

# TTS Configuration
APP_TTS_DEFAULT_VOICE=alloy        # Default voice for TTS
APP_TTS_DEFAULT_MODEL=tts-1        # Default TTS model
APP_TTS_CHUNK_SIZE=4000            # Maximum characters per TTS chunk
APP_TTS_TEMP_DIR=/tmp/tts          # Directory for temporary audio files

# HTTP Client Configuration
APP_HTTP_MAX_RETRIES=3             # Maximum number of retry attempts for HTTP requests
APP_HTTP_RETRY_DELAY=1.0           # Delay between retry attempts (seconds)
APP_HTTP_TIMEOUT=30.0              # HTTP request timeout (seconds)

# Content Extraction Configuration
APP_JINA_BASE_URL=https://r.jina.ai/ # Base URL for Jina.ai API
```

#### Configuration Precedence

The application loads configuration in the following order (later sources override earlier ones):

1. Default values in the `Settings` class
2. Environment variables
3. `.env` file
4. Command line arguments (when applicable)

## Contributing

Contributions are welcome! Please follow these guidelines to contribute to the project:

### Code of Conduct

- Be respectful and inclusive in your communications
- Provide constructive feedback
- Focus on the issue, not the person

### Contribution Process

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure they pass (`pytest`)
5. Update documentation if needed
6. Commit your changes (`git commit -m 'Add some amazing feature'`)
   - Use clear, descriptive commit messages
   - Reference issue numbers when applicable
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Pull Request Guidelines

- Provide a clear description of the changes
- Link to any related issues
- Include screenshots or examples if UI changes are made
- Ensure all tests pass
- Make sure code follows the project's style guidelines
- Keep pull requests focused on a single concern

### Development Environment Setup

1. Clone your fork of the repository
2. Set up the development environment:
   ```bash
   ./setup_venv.sh
   ```
3. Activate the virtual environment:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Code Style

- Follow PEP 8 guidelines
- Use Black for code formatting
- Use isort for import sorting
- Use meaningful variable and function names
- Write docstrings for all functions, classes, and modules

## License

[MIT](LICENSE)
