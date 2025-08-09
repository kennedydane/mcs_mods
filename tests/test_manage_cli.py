import pytest
from unittest.mock import Mock, patch, call
import sys
from pathlib import Path
import json
sys.path.insert(0, str(Path(__file__).parent.parent))

import manage


class TestManageCLI:
    
    @pytest.fixture
    def mock_requests(self):
        with patch('manage.requests') as mock_req:
            yield mock_req
    
    def test_send_request_get_success(self, mock_requests):
        # Mock successful GET request
        mock_response = Mock()
        mock_response.json.return_value = {"status": "running"}
        mock_requests.get.return_value = mock_response
        
        result = manage.send_request("GET", "/status")
        
        assert result == {"status": "running"}
        mock_requests.get.assert_called_once_with("http://localhost:8000/status")
        mock_response.raise_for_status.assert_called_once()
    
    def test_send_request_post_success(self, mock_requests):
        # Mock successful POST request
        mock_response = Mock()
        mock_response.json.return_value = {"status": "sent"}
        mock_requests.post.return_value = mock_response
        
        data = {"command": "say Hello"}
        result = manage.send_request("POST", "/command", data)
        
        assert result == {"status": "sent"}
        mock_requests.post.assert_called_once_with("http://localhost:8000/command", json=data)
        mock_response.raise_for_status.assert_called_once()
    
    def test_send_request_connection_error(self, mock_requests, capsys):
        # Mock connection error - need to patch the exception access too
        with patch('manage.requests.exceptions') as mock_exceptions:
            import requests
            mock_exceptions.ConnectionError = requests.exceptions.ConnectionError
            mock_exceptions.RequestException = requests.exceptions.RequestException
            mock_requests.get.side_effect = requests.exceptions.ConnectionError()
            
            with pytest.raises(SystemExit) as exc_info:
                manage.send_request("GET", "/status")
            
            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "Could not connect to server API" in captured.out
    
    def test_send_request_http_error(self, mock_requests, capsys):
        # Mock HTTP error
        with patch('manage.requests.exceptions') as mock_exceptions:
            import requests
            mock_exceptions.ConnectionError = requests.exceptions.ConnectionError
            mock_exceptions.RequestException = requests.exceptions.RequestException
            mock_requests.get.side_effect = requests.exceptions.RequestException("500 Server Error")
            
            with pytest.raises(SystemExit) as exc_info:
                manage.send_request("GET", "/status")
            
            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "Error: 500 Server Error" in captured.out
    
    def test_send_request_unsupported_method(self):
        with pytest.raises(ValueError) as exc_info:
            manage.send_request("DELETE", "/status")
        
        assert "Unsupported method: DELETE" in str(exc_info.value)
    
    @patch('manage.send_request')
    @patch('sys.argv', ['manage.py'])
    def test_main_no_arguments(self, mock_send_request, capsys):
        manage.main()
        
        captured = capsys.readouterr()
        assert "Usage: python3 manage.py <command>" in captured.out
        assert "Commands:" in captured.out
        mock_send_request.assert_not_called()
    
    @patch('manage.send_request')
    @patch('sys.argv', ['manage.py', 'status'])
    def test_main_status_command(self, mock_send_request, capsys):
        mock_send_request.return_value = {"status": "running", "pid": 12345}
        
        manage.main()
        
        mock_send_request.assert_called_once_with("GET", "/status")
        captured = capsys.readouterr()
        assert '"status": "running"' in captured.out
        assert '"pid": 12345' in captured.out
    
    @patch('manage.send_request')
    @patch('sys.argv', ['manage.py', 'start'])
    def test_main_start_command(self, mock_send_request, capsys):
        mock_send_request.return_value = {"status": "started", "pid": 12345}
        
        manage.main()
        
        mock_send_request.assert_called_once_with("POST", "/server/start")
        captured = capsys.readouterr()
        assert '"status": "started"' in captured.out
    
    @patch('manage.send_request')
    @patch('sys.argv', ['manage.py', 'stop'])
    def test_main_stop_command(self, mock_send_request):
        mock_send_request.return_value = {"status": "stopped"}
        
        manage.main()
        
        mock_send_request.assert_called_once_with("POST", "/server/stop")
    
    @patch('manage.send_request')
    @patch('sys.argv', ['manage.py', 'restart'])
    def test_main_restart_command(self, mock_send_request):
        mock_send_request.return_value = {"status": "started", "pid": 12345}
        
        manage.main()
        
        mock_send_request.assert_called_once_with("POST", "/server/restart")
    
    @patch('manage.send_request')
    @patch('sys.argv', ['manage.py', 'cmd', 'say', 'Hello', 'World'])
    def test_main_cmd_command(self, mock_send_request, capsys):
        mock_send_request.return_value = {
            "status": "sent", 
            "command": "say Hello World",
            "timestamp": "2025-08-09T10:30:15"
        }
        
        manage.main()
        
        mock_send_request.assert_called_once_with("POST", "/command", {"command": "say Hello World"})
        captured = capsys.readouterr()
        assert '"command": "say Hello World"' in captured.out
    
    @patch('manage.send_request')
    @patch('sys.argv', ['manage.py', 'cmd'])
    def test_main_cmd_no_arguments(self, mock_send_request, capsys):
        manage.main()
        
        captured = capsys.readouterr()
        assert "Usage: python3 manage.py cmd <command>" in captured.out
        mock_send_request.assert_not_called()
    
    @patch('manage.send_request')
    @patch('sys.argv', ['manage.py', 'history'])
    def test_main_history_command(self, mock_send_request, capsys):
        mock_send_request.return_value = {
            "commands": [
                {"timestamp": "2025-08-09T10:30:15", "command": "say Hello"},
                {"timestamp": "2025-08-09T10:31:00", "command": "list"}
            ]
        }
        
        manage.main()
        
        mock_send_request.assert_called_once_with("GET", "/command/history")
        captured = capsys.readouterr()
        assert '"say Hello"' in captured.out
        assert '"list"' in captured.out
    
    @patch('manage.send_request')
    @patch('sys.argv', ['manage.py', 'unknown'])
    def test_main_unknown_command(self, mock_send_request, capsys):
        with pytest.raises(SystemExit) as exc_info:
            manage.main()
        
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Unknown command: unknown" in captured.out
        mock_send_request.assert_not_called()