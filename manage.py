#!/usr/bin/env python3

import requests
import sys
import json
from typing import Optional

API_BASE = "http://localhost:8000"

def send_request(method: str, endpoint: str, data: Optional[dict] = None) -> dict:
    """Send request to server API"""
    try:
        url = f"{API_BASE}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server API. Is the container running?")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 manage.py <command>")
        print("Commands:")
        print("  status       - Get server status")
        print("  start        - Start server")
        print("  stop         - Stop server")
        print("  restart      - Restart server")
        print("  cmd <text>   - Send command to server")
        print("  history      - Show command history")
        return
    
    command = sys.argv[1]
    
    if command == "status":
        result = send_request("GET", "/status")
        print(json.dumps(result, indent=2))
    
    elif command == "start":
        result = send_request("POST", "/server/start")
        print(json.dumps(result, indent=2))
    
    elif command == "stop":
        result = send_request("POST", "/server/stop")
        print(json.dumps(result, indent=2))
    
    elif command == "restart":
        result = send_request("POST", "/server/restart")
        print(json.dumps(result, indent=2))
    
    elif command == "cmd":
        if len(sys.argv) < 3:
            print("Usage: python3 manage.py cmd <command>")
            return
        
        cmd_text = " ".join(sys.argv[2:])
        result = send_request("POST", "/command", {"command": cmd_text})
        print(json.dumps(result, indent=2))
    
    elif command == "history":
        result = send_request("GET", "/command/history")
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()