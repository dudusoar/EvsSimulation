#!/usr/bin/env python3
"""
Real-time Visualizer Controller
Bridges the simulation engine with the WebSocket server for real-time visualization
"""

import asyncio
import json
import logging
import signal
import sys
import threading
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from realtime_visualizer.websocket_server import WebSocketServer
from core.simulation_engine import SimulationEngine
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver

class RealtimeVisualizer:
    """
    Main controller for real-time simulation visualization
    """
    
    def __init__(self, config: dict = None, config_path: str = None):
        self.config = config  # Configuration from main.py
        self.config_path = config_path or "simulation_config.json"
        self.simulation_engine = None
        self.websocket_server = None
        self.http_server = None
        self.http_thread = None
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('realtime_visualizer.log')
            ]
        )
        
    async def initialize(self):
        """Initialize all components"""
        try:
            self.logger.info("Initializing Real-time Visualizer...")
            
            # Initialize simulation engine
            await self._initialize_simulation_engine()
            
            # Initialize WebSocket server
            await self._initialize_websocket_server()
            
            # Start HTTP server for frontend
            self._start_http_server()
            
            self.logger.info("Real-time Visualizer initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize: {e}")
            return False
    
    async def _initialize_simulation_engine(self):
        """Initialize the simulation engine"""
        self.logger.info("Initializing simulation engine...")
        
        # Use config from main.py if provided, otherwise load from file
        if self.config:
            config = self.config
        elif Path(self.config_path).exists():
            with open(self.config_path, 'r') as f:
                config = json.load(f)
        else:
            # Use default configuration
            from config.simulation_config import SIMULATION_CONFIG
            config = SIMULATION_CONFIG.copy()
        
        # Create simulation engine instance with config
        self.simulation_engine = SimulationEngine(config)
        
        self.logger.info("Simulation engine initialized")
    
    async def _initialize_websocket_server(self):
        """Initialize WebSocket server with message handlers"""
        self.logger.info("Initializing WebSocket server...")
        
        # WebSocketServer needs the simulation engine
        self.websocket_server = WebSocketServer(self.simulation_engine, port=8765)
        
        self.logger.info("WebSocket server initialized")
    
    def _start_http_server(self):
        """Start HTTP server to serve frontend files"""
        web_dir = Path(__file__).parent / "web"
        
        class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(web_dir), **kwargs)
                
            def log_message(self, format, *args):
                # Suppress HTTP server logs
                pass
        
        try:
            self.http_server = HTTPServer(('localhost', 8080), CustomHTTPRequestHandler)
            self.http_thread = threading.Thread(
                target=self.http_server.serve_forever,
                daemon=True
            )
            self.http_thread.start()
            self.logger.info("HTTP server started on http://localhost:8080")
            
        except Exception as e:
            self.logger.error(f"Failed to start HTTP server: {e}")
    
    # Note: Message handling is now managed by WebSocketServer class
    
    async def start(self):
        """Start the real-time visualizer"""
        try:
            # Initialize components
            if not await self.initialize():
                raise Exception("Initialization failed")
            
            # Start WebSocket server
            self.websocket_server.start_server()
            
            self.logger.info("Real-time Visualizer started successfully")
            self.logger.info("Frontend available at: http://localhost:8080")
            self.logger.info("WebSocket server running on: ws://localhost:8765")
            
        except Exception as e:
            self.logger.error(f"Failed to start: {e}")
            raise
    
    async def stop(self):
        """Stop the real-time visualizer"""
        try:
            self.logger.info("Stopping Real-time Visualizer...")
            
            # Stop WebSocket server
            if self.websocket_server:
                self.websocket_server.stop_server()
            
            # Stop HTTP server
            if self.http_server:
                self.http_server.shutdown()
                
            if self.http_thread and self.http_thread.is_alive():
                self.http_thread.join(timeout=2.0)
            
            self.logger.info("Real-time Visualizer stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping: {e}")


async def main():
    """Main entry point"""
    visualizer = RealtimeVisualizer()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print("\nReceived interrupt signal. Shutting down...")
        asyncio.create_task(visualizer.stop())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await visualizer.start()
        
        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        await visualizer.stop()
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        await visualizer.stop()


if __name__ == "__main__":
    asyncio.run(main()) 