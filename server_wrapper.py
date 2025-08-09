#!/usr/bin/env python3

import asyncio
import logging
import subprocess
import threading
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn


# Configure logging
def setup_logging():
    handlers = [logging.StreamHandler()]
    
    # Only add file handler if directory exists (for production)
    log_path = Path('/app/server.log')
    if log_path.parent.exists():
        handlers.append(logging.FileHandler(log_path))
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

setup_logging()
logger = logging.getLogger(__name__)


class Command(BaseModel):
    command: str


class ServerManager:
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.running = False
        self.command_history = []
        
    async def start_server(self):
        if self.running:
            return {"status": "already_running"}
            
        logger.info("Starting Minecraft Bedrock server...")
        
        try:
            # Start the bedrock server process
            self.process = subprocess.Popen(
                ['./bedrock_server'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd='/app'
            )
            
            self.running = True
            
            # Start output monitoring in a separate thread
            self.output_thread = threading.Thread(target=self._monitor_output, daemon=True)
            self.output_thread.start()
            
            logger.info("Minecraft server started successfully")
            return {"status": "started", "pid": self.process.pid}
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            return {"status": "error", "message": str(e)}
    
    def _monitor_output(self):
        """Monitor server output and log it"""
        if not self.process or not self.process.stdout:
            return
            
        try:
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    # Log server output with timestamp
                    logger.info(f"[SERVER] {line.strip()}")
                    
        except Exception as e:
            logger.error(f"Error monitoring server output: {e}")
    
    async def send_command(self, command: str) -> dict:
        if not self.running or not self.process or not self.process.stdin:
            raise HTTPException(status_code=400, detail="Server is not running")
        
        try:
            # Log the command
            timestamp = datetime.now().isoformat()
            self.command_history.append({"timestamp": timestamp, "command": command})
            logger.info(f"[COMMAND] Sending: {command}")
            
            # Send command to server
            self.process.stdin.write(f"{command}\n")
            self.process.stdin.flush()
            
            return {
                "status": "sent",
                "command": command,
                "timestamp": timestamp
            }
            
        except Exception as e:
            logger.error(f"Failed to send command '{command}': {e}")
            raise HTTPException(status_code=500, detail=f"Failed to send command: {e}")
    
    async def stop_server(self) -> dict:
        if not self.running or not self.process:
            return {"status": "not_running"}
        
        try:
            logger.info("Stopping Minecraft server...")
            
            # Send stop command first
            await self.send_command("stop")
            
            # Wait for graceful shutdown
            try:
                self.process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                logger.warning("Server didn't stop gracefully, terminating...")
                self.process.terminate()
                self.process.wait(timeout=10)
            
            self.running = False
            logger.info("Minecraft server stopped")
            return {"status": "stopped"}
            
        except Exception as e:
            logger.error(f"Error stopping server: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_status(self) -> dict:
        if not self.running or not self.process:
            return {"status": "stopped", "running": False}
        
        # Check if process is still alive
        poll = self.process.poll()
        if poll is not None:
            self.running = False
            return {"status": "stopped", "running": False, "exit_code": poll}
        
        return {
            "status": "running",
            "running": True,
            "pid": self.process.pid,
            "command_count": len(self.command_history)
        }


# Initialize server manager
server_manager = ServerManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    # Startup
    await server_manager.start_server()
    yield
    # Shutdown
    await server_manager.stop_server()


# FastAPI app
app = FastAPI(
    title="Minecraft Bedrock Server Manager", 
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    return {"message": "Minecraft Bedrock Server Manager", "status": "running"}


@app.get("/status")
async def get_status():
    return server_manager.get_status()


@app.post("/command")
async def send_command(cmd: Command):
    return await server_manager.send_command(cmd.command)


@app.get("/command/history")
async def get_command_history():
    return {"commands": server_manager.command_history}


@app.post("/server/start")
async def start_server():
    return await server_manager.start_server()


@app.post("/server/stop")
async def stop_server():
    return await server_manager.stop_server()


@app.post("/server/restart")
async def restart_server():
    stop_result = await server_manager.stop_server()
    if stop_result["status"] in ["stopped", "not_running"]:
        await asyncio.sleep(2)  # Give it a moment
        return await server_manager.start_server()
    return stop_result


if __name__ == "__main__":
    uvicorn.run(
        "server_wrapper:app",
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )