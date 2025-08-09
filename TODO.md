# TODO

## Project Tasks

### Completed
- ✅ Created CLAUDE.md for repository guidance
- ✅ Created TODO.md file
- ✅ Designed Docker containerization approach for Minecraft Bedrock server
- ✅ Created docker-compose.yml configuration
- ✅ Set up configuration file mounting (server.properties, allowlist.json, permissions.json)
- ✅ Implemented Python wrapper with REST API for command injection
- ✅ Implemented comprehensive logging strategy
- ✅ Re-engineered add-on system with staging, entrypoint script, and explicit pack validation/activation
- ✅ Created Dockerfile with uv dependency management
- ✅ Created management script (manage.py) for easy server control
- ✅ Tested the complete server setup and add-on workflow

### In Progress
- [ ] Document new add-on development workflow in a dedicated guide

### Pending
- [ ] Add authentication to management API
- [ ] Create backup/restore functionality
- [ ] Add health monitoring and alerts

### Usage Instructions

#### Build and Start
```bash
docker compose up --build
```

#### Send Commands
```bash
python3 manage.py cmd "say Hello World"
python3 manage.py status
python3 manage.py stop
```

#### API Endpoints
- GET `/status` - Server status
- POST `/command` - Send command
- GET `/command/history` - Command history
- POST `/server/start|stop|restart` - Server control

---
*Last updated: 2025-08-09*