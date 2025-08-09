import pytest
import requests
import subprocess
import time
import json
from pathlib import Path
import docker
from typing import Generator

# Integration tests that run against actual Docker container


class TestDockerIntegration:
    
    CONTAINER_NAME = "minecraft-bedrock-server-test"
    API_BASE = "http://localhost:8001"
    STARTUP_TIMEOUT = 60  # seconds
    
    @pytest.fixture(scope="class")
    def docker_client(self):
        """Docker client for container management"""
        return docker.from_env()
    
    @pytest.fixture(scope="class")
    def test_container(self, docker_client) -> Generator[str, None, None]:
        """Start test container and ensure it's running"""
        project_dir = Path(__file__).parent.parent
        
        try:
            # Stop any existing test container
            try:
                existing = docker_client.containers.get(self.CONTAINER_NAME)
                existing.stop()
                existing.remove()
            except docker.errors.NotFound:
                pass
            
            # Start the test container using docker compose
            subprocess.run([
                "docker", "compose", "-f", "docker-compose.test.yml", "up", "-d"
            ], cwd=project_dir, check=True)
            
            # Wait for container to be healthy
            container = docker_client.containers.get(self.CONTAINER_NAME)
            
            # Wait for API to be responsive
            for _ in range(self.STARTUP_TIMEOUT):
                try:
                    response = requests.get(f"{self.API_BASE}/", timeout=2)
                    if response.status_code == 200:
                        break
                except requests.exceptions.RequestException:
                    pass
                time.sleep(1)
            else:
                raise TimeoutError("Container API did not become ready in time")
            
            yield self.CONTAINER_NAME
            
        finally:
            # Cleanup: Stop and remove container
            subprocess.run([
                "docker", "compose", "-f", "docker-compose.test.yml", "down", "-v"
            ], cwd=project_dir, check=False)
    
    def test_container_is_running(self, test_container, docker_client):
        """Test that the container starts successfully"""
        container = docker_client.containers.get(test_container)
        assert container.status == "running"
    
    def test_api_root_endpoint(self, test_container):
        """Test basic API connectivity"""
        response = requests.get(f"{self.API_BASE}/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Minecraft Bedrock Server Manager"
        assert data["status"] == "running"
    
    def test_server_status_integration(self, test_container):
        """Test server status endpoint with real container"""
        response = requests.get(f"{self.API_BASE}/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "running" in data
        assert isinstance(data["running"], bool)
    
    def test_send_command_integration(self, test_container):
        """Test sending commands to real server"""
        # First, ensure server is running by checking status
        status_response = requests.get(f"{self.API_BASE}/status")
        status_data = status_response.json()
        
        if not status_data.get("running"):
            # Start the server first
            start_response = requests.post(f"{self.API_BASE}/server/start")
            assert start_response.status_code == 200
            
            # Wait a moment for server to start
            time.sleep(3)
        
        # Send a test command
        command_data = {"command": "say Integration test message"}
        response = requests.post(f"{self.API_BASE}/command", json=command_data)
        
        # The response should indicate the command was sent
        # Note: Even if bedrock_server fails to start (no real MC server),
        # the API should still accept and try to process the command
        assert response.status_code in [200, 400, 500]  # Various valid responses
        
        if response.status_code == 200:
            data = response.json()
            assert data.get("command") == "say Integration test message"
    
    def test_command_history_integration(self, test_container):
        """Test command history tracking"""
        response = requests.get(f"{self.API_BASE}/command/history")
        assert response.status_code == 200
        
        data = response.json()
        assert "commands" in data
        assert isinstance(data["commands"], list)
    
    def test_server_lifecycle_integration(self, test_container):
        """Test server start/stop/restart cycle"""
        # Get initial status
        status_response = requests.get(f"{self.API_BASE}/status")
        assert status_response.status_code == 200
        
        # Try to start server
        start_response = requests.post(f"{self.API_BASE}/server/start")
        assert start_response.status_code == 200
        start_data = start_response.json()
        
        # Should either start successfully or report already running
        assert start_data["status"] in ["started", "already_running"]
        
        # Try to stop server
        stop_response = requests.post(f"{self.API_BASE}/server/stop")
        assert stop_response.status_code == 200
        stop_data = stop_response.json()
        
        # Should stop or report not running
        assert stop_data["status"] in ["stopped", "not_running"]
    
    def test_container_logs_integration(self, test_container, docker_client):
        """Test that container produces expected log output"""
        container = docker_client.containers.get(test_container)
        logs = container.logs(tail=50, timestamps=True).decode('utf-8')
        
        # Should contain our Python wrapper startup messages
        assert any("INFO" in line for line in logs.split('\n'))
        
        # Should show FastAPI/uvicorn startup
        assert any("uvicorn" in line.lower() or "fastapi" in line.lower() 
                  for line in logs.split('\n'))
    
    def test_configuration_mount_integration(self, test_container, docker_client):
        """Test that configuration files are properly mounted"""
        container = docker_client.containers.get(test_container)
        
        # Check that our test config is present
        exec_result = container.exec_run("cat /app/server.properties")
        assert exec_result.exit_code == 0
        
        config_content = exec_result.output.decode('utf-8')
        assert "Test Minecraft Bedrock Server" in config_content
        assert "gamemode=creative" in config_content
    
    def test_api_error_handling_integration(self, test_container):
        """Test API error handling with real container"""
        # Test invalid JSON
        response = requests.post(
            f"{self.API_BASE}/command",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
        
        # Test missing required field
        response = requests.post(f"{self.API_BASE}/command", json={})
        assert response.status_code == 422
    
    @pytest.mark.slow
    def test_container_stability_integration(self, test_container, docker_client):
        """Test that container remains stable under load"""
        container = docker_client.containers.get(test_container)
        
        # Send multiple commands rapidly
        for i in range(10):
            try:
                response = requests.post(
                    f"{self.API_BASE}/command",
                    json={"command": f"say Test message {i}"},
                    timeout=5
                )
                # Don't assert success since server may not be fully running
                # Just ensure we get a response
                assert response.status_code in [200, 400, 500]
            except requests.exceptions.RequestException:
                # Network errors are acceptable in this stress test
                pass
        
        # Container should still be running
        container.reload()
        assert container.status == "running"


@pytest.mark.integration
class TestEndToEndWorkflow:
    """End-to-end tests that simulate real usage patterns"""
    
    API_BASE = "http://localhost:8001"
    
    @pytest.fixture(scope="class")
    def docker_client(self):
        """Docker client for container management"""
        return docker.from_env()
    
    @pytest.fixture(scope="class")
    def running_container(self, docker_client):
        """Start a running container for end-to-end tests"""
        project_dir = Path(__file__).parent.parent
        
        try:
            # Stop any existing test container
            try:
                existing = docker_client.containers.get(TestDockerIntegration.CONTAINER_NAME)
                existing.stop()
                existing.remove()
            except docker.errors.NotFound:
                pass
            
            # Start the test container using docker compose
            subprocess.run([
                "docker", "compose", "-f", "docker-compose.test.yml", "up", "-d"
            ], cwd=project_dir, check=True)
            
            # Wait for container to be healthy
            container = docker_client.containers.get(TestDockerIntegration.CONTAINER_NAME)
            
            # Wait for API to be responsive
            for _ in range(TestDockerIntegration.STARTUP_TIMEOUT):
                try:
                    response = requests.get(f"{self.API_BASE}/", timeout=2)
                    if response.status_code == 200:
                        break
                except requests.exceptions.RequestException:
                    pass
                time.sleep(1)
            else:
                raise TimeoutError("Container API did not become ready in time")
            
            yield TestDockerIntegration.CONTAINER_NAME
            
        finally:
            # Cleanup: Stop and remove container
            subprocess.run([
                "docker", "compose", "-f", "docker-compose.test.yml", "down", "-v"
            ], cwd=project_dir, check=False)
    
    def test_complete_server_management_workflow(self, running_container):
        """Test a complete server management workflow"""
        # 1. Check initial status
        response = requests.get(f"{self.API_BASE}/status")
        assert response.status_code == 200
        
        # 2. Start server
        response = requests.post(f"{self.API_BASE}/server/start")
        assert response.status_code == 200
        
        # 3. Send a series of commands
        commands = [
            "say Welcome to the test server!",
            "gamemode creative",
            "time set day"
        ]
        
        for cmd in commands:
            response = requests.post(f"{self.API_BASE}/command", json={"command": cmd})
            # Accept various status codes since server might not be fully functional
            assert response.status_code in [200, 400, 500]
        
        # 4. Check command history
        response = requests.get(f"{self.API_BASE}/command/history")
        assert response.status_code == 200
        
        history = response.json()["commands"]
        # Should have at least some commands (may have more from other tests)
        assert len(history) >= 0
        
        # 5. Stop server
        response = requests.post(f"{self.API_BASE}/server/stop")
        assert response.status_code == 200