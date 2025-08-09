# Minecraft Bedrock Server with Docker

A comprehensive Docker-based solution for running Minecraft Bedrock Edition servers with advanced management capabilities, command injection, and add-on support.

## Features

- **🐳 Docker Containerization** - Complete server isolation and easy deployment
- **🎮 Command Injection** - Send commands to the server via REST API or CLI
- **📊 Comprehensive Logging** - Structured logging with timestamps and command tracking
- **⚙️ Configuration Management** - External config files (server.properties, allowlist.json, permissions.json)
- **🎨 Add-on Support** - Behavior packs and resource packs mounting
- **🔧 Management API** - RESTful API for server control and monitoring
- **📱 CLI Tool** - Easy-to-use command-line interface for server management

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Python 3.13+ (for the management CLI)
- `uv` package manager

### 1. Clone and Setup

```bash
git clone <repository-url>
cd mcs_mods
```

### 2. Build and Start

```bash
docker compose up --build
```

This will:
- Build the container with the Minecraft Bedrock server
- Start the Python wrapper with management API
- Expose the server on port 19132 (UDP) and API on port 8000 (TCP)

### 3. Verify Setup

```bash
# Check server status
python3 manage.py status

# Send a test command
python3 manage.py cmd "say Server is running!"
```

## Usage

### Management CLI

The `manage.py` script provides easy access to server management:

```bash
# Server Control
python3 manage.py start      # Start the server
python3 manage.py stop       # Stop the server  
python3 manage.py restart    # Restart the server
python3 manage.py status     # Get server status

# Send Commands
python3 manage.py cmd "say Hello World"
python3 manage.py cmd "tp Player1 0 100 0"
python3 manage.py cmd "gamemode creative Player1"

# View History
python3 manage.py history    # Show command history
```

### REST API

The management API is available at `http://localhost:8000`:

#### Endpoints

- **GET** `/status` - Get server status
- **POST** `/command` - Send command to server
  ```json
  {"command": "say Hello World"}
  ```
- **GET** `/command/history` - Get command history
- **POST** `/server/start` - Start server
- **POST** `/server/stop` - Stop server
- **POST** `/server/restart` - Restart server

#### Example API Usage

```bash
# Get status
curl http://localhost:8000/status

# Send command
curl -X POST http://localhost:8000/command \
  -H "Content-Type: application/json" \
  -d '{"command": "list"}'

# Stop server
curl -X POST http://localhost:8000/server/stop
```

### Configuration

#### Server Properties

Edit `config/server.properties` to customize server settings:

```properties
server-name=My Bedrock Server
gamemode=survival
difficulty=easy
max-players=10
allow-cheats=false
# ... more settings
```

#### Player Management

- **Allow List**: Edit `config/allowlist.json` to control who can join
- **Permissions**: Edit `config/permissions.json` to set operator privileges

```json
// allowlist.json
[
  {
    "ignoresPlayerLimit": false,
    "name": "PlayerName",
    "xuid": "1234567890123456"
  }
]

// permissions.json  
[
  {
    "permission": "operator",
    "xuid": "1234567890123456"
  }
]
```

### Add-ons

#### Behavior Packs

Place behavior packs in the `behavior_packs/` directory:

```
behavior_packs/
├── my-custom-pack/
│   ├── manifest.json
│   ├── pack_icon.png
│   └── behaviors/
└── another-pack/
```

#### Resource Packs

Place resource packs in the `resource_packs/` directory:

```
resource_packs/
├── texture-pack/
│   ├── manifest.json
│   ├── pack_icon.png
│   └── textures/
└── ui-pack/
```

## Project Structure

```
mcs_mods/
├── config/                     # Server configuration files
│   ├── server.properties
│   ├── allowlist.json
│   └── permissions.json
├── behavior_packs/             # Behavior pack add-ons
├── resource_packs/             # Resource pack add-ons  
├── logs/                       # Server logs (host accessible)
├── server_wrapper.py           # Python server management wrapper
├── manage.py                   # CLI management tool
├── docker-compose.yml          # Container orchestration
├── Dockerfile                  # Container definition
├── pyproject.toml              # Python dependencies (uv)
└── bedrock-server-1.21.100.7.zip  # Server binary
```

## Architecture

The system uses a **Python wrapper approach** for maximum flexibility:

1. **Docker Container** runs Ubuntu with Python and the Bedrock server
2. **Python Wrapper** (`server_wrapper.py`) manages the server process:
   - Starts `bedrock_server` as a subprocess
   - Captures and logs all server output
   - Exposes REST API for command injection
   - Handles graceful startup/shutdown
3. **FastAPI** provides the REST interface for external control
4. **Docker Compose** orchestrates the container with volume mounts

## Logging

Logs are structured and timestamped:

- **Container logs**: `docker compose logs -f`
- **Host-accessible logs**: `logs/server.log`
- **API logs**: Included in container output

Example log output:
```
2025-08-09 10:30:15,123 - __main__ - INFO - [SERVER] Starting up server...
2025-08-09 10:30:16,456 - __main__ - INFO - [COMMAND] Sending: say Hello World
2025-08-09 10:30:16,789 - __main__ - INFO - [SERVER] Hello World
```

## Troubleshooting

### Common Issues

**Container won't start:**
```bash
# Check logs
docker compose logs minecraft-server

# Rebuild container
docker compose down
docker compose up --build
```

**Can't connect to API:**
```bash
# Verify container is running
docker compose ps

# Check if port 8000 is accessible
curl http://localhost:8000/status
```

**Server commands not working:**
```bash
# Check server status first
python3 manage.py status

# Verify server is actually running
docker compose exec minecraft-server ps aux
```

### Development

To modify the Python wrapper:

1. Edit `server_wrapper.py`
2. Rebuild container: `docker compose up --build`
3. Test with: `python3 manage.py status`

## Testing

The project includes comprehensive test coverage using pytest.

### Running Tests

```bash
# Run unit tests (fast, no Docker required)
uv run pytest -m "not integration"

# Run all tests including integration
uv run pytest

# Run only integration tests (requires Docker)
uv run pytest -m integration
python3 run_integration_tests.py

# Run tests with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_server_manager.py

# Run with coverage (if pytest-cov is installed)
uv run pytest --cov=server_wrapper --cov=manage

# Use the test runner scripts
python3 run_tests.py                    # Unit tests only
python3 run_integration_tests.py        # Integration tests
```

### Test Structure

- **`tests/test_server_manager.py`** - Unit tests for the ServerManager class
- **`tests/test_api.py`** - Unit tests for FastAPI endpoints
- **`tests/test_manage_cli.py`** - Unit tests for the management CLI tool
- **`tests/test_integration.py`** - Integration tests against real Docker containers
- **`tests/conftest.py`** - Shared fixtures and test configuration
- **`tests/fixtures/`** - Test configuration files and data

### Test Coverage

The test suite covers:
- **Unit Tests**: Server lifecycle management, command injection, API endpoints, CLI tool
- **Integration Tests**: Real Docker container testing, API connectivity, configuration mounting
- **Error Handling**: Network failures, validation errors, server startup issues
- **End-to-End Workflows**: Complete server management scenarios

#### Integration Test Requirements

Integration tests require Docker to be running and will:
1. Build the container image
2. Start a test container with test configuration
3. Run tests against the real API
4. Clean up containers automatically

Use different ports (8001, 19133) to avoid conflicts with development containers.

## Contributing

1. Make changes to the code
2. Run tests: `uv run pytest`
3. Test with Docker: `docker compose up --build`
4. Update documentation as needed
5. Submit pull request

## License

This project is for educational and personal use. Minecraft is a trademark of Microsoft/Mojang Studios.