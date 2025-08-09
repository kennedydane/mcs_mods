import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
import httpx
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from server_wrapper import app, server_manager


class TestAPI:
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture(autouse=True)
    def reset_server_manager(self):
        """Reset server manager state before each test"""
        server_manager.process = None
        server_manager.running = False
        server_manager.command_history = []
        yield
        # Cleanup after test
        server_manager.process = None
        server_manager.running = False
        server_manager.command_history = []
    
    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Minecraft Bedrock Server Manager"
        assert data["status"] == "running"
    
    def test_status_endpoint_stopped(self, client):
        response = client.get("/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "stopped"
        assert data["running"] is False
    
    def test_status_endpoint_running(self, client):
        # Mock running server
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_process.pid = 12345
        
        server_manager.process = mock_process
        server_manager.running = True
        
        response = client.get("/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert data["running"] is True
        assert data["pid"] == 12345
        assert data["command_count"] == 0
    
    @patch.object(server_manager, 'send_command')
    def test_send_command_success(self, mock_send_command, client):
        # Mock successful command sending
        mock_send_command.return_value = {
            "status": "sent",
            "command": "say Hello",
            "timestamp": "2025-08-09T10:30:15"
        }
        
        response = client.post("/command", json={"command": "say Hello"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "sent"
        assert data["command"] == "say Hello"
        assert "timestamp" in data
        
        mock_send_command.assert_called_once_with("say Hello")
    
    def test_send_command_invalid_json(self, client):
        response = client.post("/command", json={})
        assert response.status_code == 422  # Validation error
    
    def test_send_command_server_not_running(self, client):
        # Server not running, should get 400 error
        response = client.post("/command", json={"command": "say Hello"})
        assert response.status_code == 400
        
        data = response.json()
        assert "Server is not running" in data["detail"]
    
    @patch.object(server_manager, 'send_command')
    def test_send_command_server_error(self, mock_send_command, client):
        from fastapi import HTTPException
        
        # Mock server error
        mock_send_command.side_effect = HTTPException(status_code=500, detail="Server error")
        
        response = client.post("/command", json={"command": "say Hello"})
        assert response.status_code == 500
    
    def test_get_command_history_empty(self, client):
        response = client.get("/command/history")
        assert response.status_code == 200
        data = response.json()
        assert data["commands"] == []
    
    def test_get_command_history_with_commands(self, client):
        # Add some command history
        server_manager.command_history = [
            {"timestamp": "2025-08-09T10:30:15", "command": "say Hello"},
            {"timestamp": "2025-08-09T10:30:20", "command": "list"}
        ]
        
        response = client.get("/command/history")
        assert response.status_code == 200
        data = response.json()
        assert len(data["commands"]) == 2
        assert data["commands"][0]["command"] == "say Hello"
        assert data["commands"][1]["command"] == "list"
    
    @patch.object(server_manager, 'start_server')
    def test_start_server_success(self, mock_start_server, client):
        mock_start_server.return_value = {"status": "started", "pid": 12345}
        
        response = client.post("/server/start")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "started"
        assert data["pid"] == 12345
        
        mock_start_server.assert_called_once()
    
    @patch.object(server_manager, 'start_server')
    def test_start_server_already_running(self, mock_start_server, client):
        mock_start_server.return_value = {"status": "already_running"}
        
        response = client.post("/server/start")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "already_running"
    
    @patch.object(server_manager, 'stop_server')
    def test_stop_server_success(self, mock_stop_server, client):
        mock_stop_server.return_value = {"status": "stopped"}
        
        response = client.post("/server/stop")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "stopped"
        
        mock_stop_server.assert_called_once()
    
    @patch.object(server_manager, 'stop_server')
    def test_stop_server_not_running(self, mock_stop_server, client):
        mock_stop_server.return_value = {"status": "not_running"}
        
        response = client.post("/server/stop")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "not_running"
    
    @patch.object(server_manager, 'stop_server')
    @patch.object(server_manager, 'start_server')
    def test_restart_server_success(self, mock_start_server, mock_stop_server, client):
        # Mock successful stop and start
        mock_stop_server.return_value = {"status": "stopped"}
        mock_start_server.return_value = {"status": "started", "pid": 12345}
        
        response = client.post("/server/restart")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "started"
        assert data["pid"] == 12345
        
        mock_stop_server.assert_called_once()
        mock_start_server.assert_called_once()
    
    @patch.object(server_manager, 'stop_server')
    @patch.object(server_manager, 'start_server')
    def test_restart_server_stop_failure(self, mock_start_server, mock_stop_server, client):
        # Mock failed stop
        mock_stop_server.return_value = {"status": "error", "message": "Stop failed"}
        
        response = client.post("/server/restart")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "error"
        assert data["message"] == "Stop failed"
        
        mock_stop_server.assert_called_once()
        mock_start_server.assert_not_called()


class TestAPIValidation:
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_command_validation_missing_field(self, client):
        response = client.post("/command", json={})
        assert response.status_code == 422
        
        error_detail = response.json()["detail"][0]
        assert error_detail["loc"] == ["body", "command"]
        assert error_detail["type"] == "missing"
    
    def test_command_validation_wrong_type(self, client):
        response = client.post("/command", json={"command": 123})
        assert response.status_code == 422
        
        error_detail = response.json()["detail"][0]
        assert error_detail["loc"] == ["body", "command"]
        assert error_detail["type"] == "string_type"
    
    def test_command_validation_empty_string(self, client):
        # Empty string should be valid but will fail at business logic level
        response = client.post("/command", json={"command": ""})
        assert response.status_code == 400  # Server not running error
    
    def test_invalid_json_body(self, client):
        response = client.post(
            "/command", 
            data="invalid json", 
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422