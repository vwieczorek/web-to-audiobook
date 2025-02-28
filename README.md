# Web to Audiobook Conversion Tool

This application converts web articles to audiobooks by extracting text using Jina.ai and converting it to speech using OpenAI's TTS API. The audio is then processed into M4B files for Plex compatibility.

## Features

- Extract text from web articles using Jina.ai
- Convert text to speech using OpenAI's TTS API
- Process audio into M4B audiobook files for Plex compatibility
- Containerized deployment with Docker
- API-first design with FastAPI

## Requirements

- Python 3.10+
- Docker and Docker Compose (for containerized deployment)

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

## Development

### Project Structure

```
web_to_audiobook/
├── app/                  # Application code
│   ├── main.py           # Entry point for FastAPI
│   ├── config.py         # Configuration management
│   ├── logging.py        # Logging setup
│   ├── routers/          # API routes
│   ├── services/         # Business logic
│   └── utils/            # Utility functions
├── tests/                # Unit tests
├── logs/                 # Log files
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
└── README.md             # This file
```

### Running Tests

To run the tests, use the following command:

```bash
pytest
```

To run the tests with coverage:

```bash
pytest --cov=app
```

## License

[MIT](LICENSE)