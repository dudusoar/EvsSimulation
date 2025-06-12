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

from realtime_visualizer.flask_api_server import FlaskApiServer
from core.simulation_engine import SimulationEngine

class RealtimeVisualizer:
    """
    Main controller for real-time simulation visualization
    """
    
    def __init__(self, config: dict = None, config_path: str = None):
        self.config = config  # Configuration from main.py
        self.config_path = config_path or "simulation_config.json"
        self.simulation_engine = None
        self.api_server = None
        
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
            
            # Initialize Flask API server
            await self._initialize_api_server()
            
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
    
    async def _initialize_api_server(self):
        """Initialize Flask API server"""
        self.logger.info("Initializing Flask API server...")
        
        # Flask API server integrates HTTP and API in one
        self.api_server = FlaskApiServer(self.simulation_engine, port=8080)
        
        self.logger.info("Flask API server initialized")
    
    # Note: Message handling is now managed by WebSocketServer class
    
    async def start(self):
        """Start the real-time visualizer"""
        try:
            # Initialize components
            if not await self.initialize():
                raise Exception("Initialization failed")
            
            # Start Flask API server
            self.api_server.start_server()
            
            self.logger.info("Real-time Visualizer started successfully")
            self.logger.info("Frontend available at: http://localhost:8080")
            self.logger.info("API endpoints available at: http://localhost:8080/api/")
            
        except Exception as e:
            self.logger.error(f"Failed to start: {e}")
            raise
    
    async def stop(self):
        """Stop the real-time visualizer"""
        try:
            self.logger.info("Stopping Real-time Visualizer...")
            
            # Stop Flask API server
            if self.api_server:
                self.api_server.stop_server()
            
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