import pytest
from unittest.mock import Mock, patch
import tempfile
import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from server_wrapper import ServerManager


@pytest.fixture
def temp_minecraft_dir():
    """Create a temporary directory structure mimicking the minecraft server layout"""
    with tempfile.TemporaryDirectory() as temp_dir:
        minecraft_dir = Path(temp_dir) / "minecraft"
        minecraft_dir.mkdir()
        
        # Create fake bedrock_server executable
        bedrock_server = minecraft_dir / "bedrock_server"
        bedrock_server.write_text("#!/bin/bash\necho 'Fake bedrock server'\n")
        bedrock_server.chmod(0o755)
        
        # Create config files
        (minecraft_dir / "server.properties").write_text("server-name=Test Server\n")
        (minecraft_dir / "allowlist.json").write_text("[]")
        (minecraft_dir / "permissions.json").write_text("[]")
        
        # Create directories
        (minecraft_dir / "worlds").mkdir()
        (minecraft_dir / "behavior_packs").mkdir()
        (minecraft_dir / "resource_packs").mkdir()
        
        yield str(minecraft_dir)


@pytest.fixture
def mock_subprocess():
    """Mock subprocess.Popen for testing server startup"""
    with patch('subprocess.Popen') as mock_popen:
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.stdin = Mock()
        mock_process.stdout = Mock()
        mock_process.poll.return_value = None  # Process is running
        mock_process.wait.return_value = 0     # Process exits cleanly
        
        mock_popen.return_value = mock_process
        yield mock_popen, mock_process


@pytest.fixture
def mock_threading():
    """Mock threading.Thread for testing output monitoring"""
    with patch('threading.Thread') as mock_thread:
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance
        yield mock_thread, mock_thread_instance


@pytest.fixture
def server_manager_with_mocks(mock_subprocess, mock_threading):
    """ServerManager with mocked dependencies"""
    server_manager = ServerManager()
    yield server_manager, mock_subprocess, mock_threading


@pytest.fixture
def sample_command_history():
    """Sample command history for testing"""
    return [
        {
            "timestamp": "2025-08-09T10:30:15.123456",
            "command": "say Hello World"
        },
        {
            "timestamp": "2025-08-09T10:31:00.789012", 
            "command": "list"
        },
        {
            "timestamp": "2025-08-09T10:31:30.456789",
            "command": "tp Player1 0 100 0"
        }
    ]


@pytest.fixture
def sample_server_config():
    """Sample server configuration for testing"""
    return {
        "server-name": "Test Minecraft Server",
        "gamemode": "creative", 
        "difficulty": "easy",
        "max-players": "5",
        "allow-cheats": "true"
    }


@pytest.fixture(autouse=True)
def cleanup_server_state():
    """Ensure clean server state before and after each test"""
    # Reset before test
    yield
    # Reset after test (cleanup)
    # This runs after each test to ensure clean state