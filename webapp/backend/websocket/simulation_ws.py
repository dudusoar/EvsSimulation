"""
WebSocket Real-time Communication for Simulation
"""

import json
import time
import asyncio
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from webapp.backend.models.response import WebSocketMessage, SimulationState
from webapp.backend.services.simulation_service import simulation_service

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"New WebSocket connection. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific WebSocket connection"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """Broadcast message to all connected clients"""
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_simulation_state(self, state: SimulationState):
        """Send simulation state to all connected clients"""
        message = WebSocketMessage(
            type="simulation_state",
            data=state.dict(),
            timestamp=time.time()
        )
        
        await self.broadcast(message.json())


# Global connection manager
manager = ConnectionManager()


@router.websocket("/simulation")
async def simulation_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time simulation updates"""
    await manager.connect(websocket)
    
    # Subscribe to simulation updates
    simulation_service.subscribe(manager.send_simulation_state)
    
    try:
        # Send initial status
        initial_message = WebSocketMessage(
            type="connection",
            data={"status": "connected", "message": "WebSocket connection established"},
            timestamp=time.time()
        )
        await manager.send_personal_message(initial_message.json(), websocket)
        
        # Send current state if available
        current_state = simulation_service.get_current_state()
        if current_state:
            await manager.send_personal_message(
                WebSocketMessage(
                    type="simulation_state",
                    data=current_state.dict(),
                    timestamp=time.time()
                ).json(),
                websocket
            )
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for client messages (commands, etc.)
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle client commands
                await handle_client_message(message, websocket)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                # Send error message for invalid JSON
                error_message = WebSocketMessage(
                    type="error",
                    data={"error": "Invalid JSON format"},
                    timestamp=time.time()
                )
                await manager.send_personal_message(error_message.json(), websocket)
            except Exception as e:
                # Send error message for other exceptions
                error_message = WebSocketMessage(
                    type="error",
                    data={"error": str(e)},
                    timestamp=time.time()
                )
                await manager.send_personal_message(error_message.json(), websocket)
                
    except WebSocketDisconnect:
        pass
    finally:
        # Cleanup
        manager.disconnect(websocket)
        simulation_service.unsubscribe(manager.send_simulation_state)


async def handle_client_message(message: dict, websocket: WebSocket):
    """Handle messages from WebSocket clients"""
    try:
        message_type = message.get("type", "")
        data = message.get("data", {})
        
        if message_type == "control":
            # Handle simulation control commands
            command = data.get("command", "")
            
            if command == "start":
                success = simulation_service.start_simulation()
            elif command == "pause":
                success = simulation_service.pause_simulation()
            elif command == "resume":
                success = simulation_service.resume_simulation()
            elif command == "stop":
                success = simulation_service.stop_simulation()
            elif command == "speed":
                multiplier = data.get("multiplier", 1.0)
                success = simulation_service.set_speed_multiplier(multiplier)
            else:
                success = False
            
            # Send response
            response = WebSocketMessage(
                type="control_response",
                data={
                    "command": command,
                    "success": success,
                    "message": f"Command '{command}' {'executed' if success else 'failed'}"
                },
                timestamp=time.time()
            )
            await manager.send_personal_message(response.json(), websocket)
            
        elif message_type == "ping":
            # Handle ping/keepalive
            pong_message = WebSocketMessage(
                type="pong",
                data={"message": "pong"},
                timestamp=time.time()
            )
            await manager.send_personal_message(pong_message.json(), websocket)
            
        else:
            # Unknown message type
            error_message = WebSocketMessage(
                type="error",
                data={"error": f"Unknown message type: {message_type}"},
                timestamp=time.time()
            )
            await manager.send_personal_message(error_message.json(), websocket)
            
    except Exception as e:
        error_message = WebSocketMessage(
            type="error",
            data={"error": f"Error handling message: {str(e)}"},
            timestamp=time.time()
        )
        await manager.send_personal_message(error_message.json(), websocket)


@router.get("/connections")
async def get_websocket_connections():
    """Get number of active WebSocket connections"""
    return {
        "active_connections": len(manager.active_connections),
        "status": "healthy"
    } 