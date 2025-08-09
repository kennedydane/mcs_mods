import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock
import subprocess
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from server_wrapper import ServerManager


class TestServerManager:
    
    @pytest.fixture
    def server_manager(self):
        return ServerManager()
    
    def test_init(self, server_manager):
        assert server_manager.process is None
        assert server_manager.running is False
        assert server_manager.command_history == []
    
    def test_get_status_not_running(self, server_manager):
        status = server_manager.get_status()
        
        assert status == {"status": "stopped", "running": False}
    
    def test_get_status_running(self, server_manager):
        # Mock a running process
        mock_process = Mock()
        mock_process.poll.return_value = None  # Process is still running
        mock_process.pid = 12345
        
        server_manager.process = mock_process
        server_manager.running = True
        
        status = server_manager.get_status()
        
        assert status == {
            "status": "running", 
            "running": True, 
            "pid": 12345,
            "command_count": 0
        }
    
    def test_get_status_process_exited(self, server_manager):
        # Mock a process that has exited
        mock_process = Mock()
        mock_process.poll.return_value = 0  # Process has exited with code 0
        
        server_manager.process = mock_process
        server_manager.running = True  # Initially set as running
        
        status = server_manager.get_status()
        
        # Should detect the process has stopped and update state
        assert status == {"status": "stopped", "running": False, "exit_code": 0}
        assert server_manager.running is False
    
    @pytest.mark.asyncio
    @patch('subprocess.Popen')
    async def test_start_server_success(self, mock_popen, server_manager):
        # Mock successful process creation
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.stdout = Mock()
        mock_popen.return_value = mock_process
        
        with patch('threading.Thread') as mock_thread:
            result = await server_manager.start_server()
        
        assert result == {"status": "started", "pid": 12345}
        assert server_manager.running is True
        assert server_manager.process == mock_process
        
        # Verify subprocess was called correctly
        mock_popen.assert_called_once_with(
            ['./bedrock_server'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            cwd='/app'
        )
        
        # Verify thread was started for output monitoring
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_start_server_already_running(self, server_manager):
        server_manager.running = True
        
        result = await server_manager.start_server()
        
        assert result == {"status": "already_running"}
    
    @pytest.mark.asyncio
    @patch('subprocess.Popen')
    async def test_start_server_failure(self, mock_popen, server_manager):
        # Mock process creation failure
        mock_popen.side_effect = Exception("Failed to start process")
        
        result = await server_manager.start_server()
        
        assert result["status"] == "error"
        assert "Failed to start process" in result["message"]
        assert server_manager.running is False
    
    @pytest.mark.asyncio
    async def test_send_command_success(self, server_manager):
        # Mock running process
        mock_process = Mock()
        mock_stdin = Mock()
        mock_process.stdin = mock_stdin
        
        server_manager.process = mock_process
        server_manager.running = True
        
        result = await server_manager.send_command("say Hello World")
        
        # Verify command was sent to process
        mock_stdin.write.assert_called_once_with("say Hello World\n")
        mock_stdin.flush.assert_called_once()
        
        # Verify result
        assert result["status"] == "sent"
        assert result["command"] == "say Hello World"
        assert "timestamp" in result
        
        # Verify command history
        assert len(server_manager.command_history) == 1
        assert server_manager.command_history[0]["command"] == "say Hello World"
    
    @pytest.mark.asyncio
    async def test_send_command_server_not_running(self, server_manager):
        # Server not running
        server_manager.running = False
        
        with pytest.raises(Exception) as exc_info:
            await server_manager.send_command("say Hello")
        
        # Should raise HTTPException (but we're testing the underlying logic)
        assert "Server is not running" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_send_command_process_error(self, server_manager):
        # Mock process with stdin that raises an error
        mock_process = Mock()
        mock_stdin = Mock()
        mock_stdin.write.side_effect = Exception("Broken pipe")
        mock_process.stdin = mock_stdin
        
        server_manager.process = mock_process
        server_manager.running = True
        
        with pytest.raises(Exception) as exc_info:
            await server_manager.send_command("say Hello")
        
        assert "Failed to send command" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_stop_server_not_running(self, server_manager):
        server_manager.running = False
        
        result = await server_manager.stop_server()
        
        assert result == {"status": "not_running"}
    
    @pytest.mark.asyncio
    async def test_stop_server_success(self, server_manager):
        # Mock running process
        mock_process = Mock()
        mock_process.wait.return_value = 0  # Graceful shutdown
        mock_stdin = Mock()
        mock_process.stdin = mock_stdin
        
        server_manager.process = mock_process
        server_manager.running = True
        
        result = await server_manager.stop_server()
        
        # Verify stop command was sent
        mock_stdin.write.assert_called_once_with("stop\n")
        mock_stdin.flush.assert_called_once()
        
        # Verify wait was called
        mock_process.wait.assert_called_with(timeout=30)
        
        assert result == {"status": "stopped"}
        assert server_manager.running is False
    
    @pytest.mark.asyncio
    async def test_stop_server_timeout_and_terminate(self, server_manager):
        # Mock process that doesn't stop gracefully
        mock_process = Mock()
        mock_process.wait.side_effect = [subprocess.TimeoutExpired("bedrock_server", 30), None]
        mock_stdin = Mock()
        mock_process.stdin = mock_stdin
        
        server_manager.process = mock_process
        server_manager.running = True
        
        result = await server_manager.stop_server()
        
        # Verify terminate was called after timeout
        mock_process.terminate.assert_called_once()
        
        assert result == {"status": "stopped"}
        assert server_manager.running is False