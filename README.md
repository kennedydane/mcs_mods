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

This project uses a robust staging and configuration system to manage add-ons, ensuring that custom packs are safely merged with vanilla packs without overwriting them.

#### 1. Place Your Add-on Files

- Place your custom **behavior packs** in the `addons/behavior_packs/` directory.
- Place your custom **resource packs** in the `addons/resource_packs/` directory.

```
addons/
├── behavior_packs/
│   └── enhanced_pickaxe/
└── resource_packs/
    └── lightsaber_resources/
```

#### 2. Register Your Packs with the Server

The server needs to know that your packs are valid.

- Open `valid_known_packs.json`.
- Add an entry for each of your packs, specifying its path, UUID, and version from its `manifest.json`.

```json
// valid_known_packs.json
[
    {
        "file_system": "RawPath",
        "path": "behavior_packs/enhanced_pickaxe",
        "uuid": "f4a1f1e0-1b2a-4b8e-9d4c-5a6b7c8d9e0f",
        "version": "1.0.0"
    },
    {
        "file_system": "RawPath",
        "path": "resource_packs/lightsaber_resources",
        "uuid": "a1b2c3d4-e5f6-4a5b-b6c7-d8e9f0a1b2c3",
        "version": "1.0.0"
    }
]
```

#### 3. Activate Packs for Your World

To automatically activate packs for a specific world, you must configure them.

- Open `world_configs/world_behavior_packs.json` and `world_configs/world_resource_packs.json`.
- Add an entry for each pack you want to be active, specifying its `pack_id` (the UUID from its manifest) and `version`.

The `docker-compose.yml` is configured to mount these files into the `Bedrock level` world by default. If your world has a different name, you will need to update the paths in `docker-compose.yml`.

#### 4. Restart the Server

After making changes to your add-ons or configuration files, you must restart the server for them to take effect. If you've changed the `Dockerfile` or `entrypoint.sh`, you must rebuild.

```bash
# If you only changed add-ons or configs
docker compose restart

# If you changed Dockerfile or entrypoint.sh
docker compose up --build -d
```

## Project Structure

```
mcs_mods/
├── addons/                     # Staging directory for custom add-ons
│   ├── behavior_packs/
│   └── resource_packs/
├── config/                     # Main server configuration
│   ├── server.properties
│   ├── allowlist.json
│   └── permissions.json
├── world_configs/              # World-specific pack activation
│   ├── world_behavior_packs.json
│   └── world_resource_packs.json
├── logs/                       # Server logs (host accessible)
├── valid_known_packs.json      # Master list of valid server packs
├── server_wrapper.py           # Python server management wrapper
├── manage.py                   # CLI management tool
├── entrypoint.sh               # Script to merge add-ons on start
├── docker-compose.yml          # Container orchestration
├── Dockerfile                  # Container definition
└── pyproject.toml              # Python dependencies
```

## Architecture

The system uses a **Python wrapper and an entrypoint script** for maximum flexibility:

1. **Docker Container** runs Ubuntu with Python and the Bedrock server.
2. **Entrypoint Script** (`entrypoint.sh`) runs first. It intelligently copies the custom add-ons from the `/app/custom_addons` staging directory into the server's live `behavior_packs` and `resource_packs` directories.
3. **Python Wrapper** (`server_wrapper.py`) then starts and manages the `bedrock_server` as a subprocess, capturing its output and exposing the REST API.
4. **FastAPI** provides the REST interface for external control.
5. **Docker Compose** orchestrates the container and uses volume mounts to inject configurations, the `addons` staging directory, and world-specific pack activation files.

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