"""
EV Simulation Web Backend
FastAPI application entry point
"""

import sys
import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

# Add parent directories to path to import from existing simulation system
sys.path.append(str(Path(__file__).parent.parent.parent))

from webapp.backend.api import simulation, data, config
from webapp.backend.websocket import simulation_ws

# Create FastAPI app
app = FastAPI(
    title="EV Simulation Web API",
    description="Real-time Electric Vehicle Simulation with Interactive Web Interface",
    version="2.0.0"  # 升级版本号以反映YAML配置支持
)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (CSS, JS, images)
frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_path / "static")), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory=str(frontend_path / "templates"))

# Include API routers
app.include_router(simulation.router, prefix="/api/simulation", tags=["simulation"])
app.include_router(data.router, prefix="/api/data", tags=["data"])
app.include_router(config.router, prefix="/api/config", tags=["configuration"])  # 新增配置管理API
app.include_router(simulation_ws.router, prefix="/ws", tags=["websocket"])

@app.get("/")
async def root(request: Request):
    """Main application page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/vehicles")
async def vehicles_page(request: Request):
    """Vehicle tracking page"""
    return templates.TemplateResponse("vehicles.html", {"request": request})

@app.get("/orders")
async def orders_page(request: Request):
    """Order tracking page"""
    return templates.TemplateResponse("orders.html", {"request": request})

@app.get("/charging-stations")
async def charging_stations_page(request: Request):
    """Charging station tracking page"""
    return templates.TemplateResponse("charging-stations.html", {"request": request})

@app.get("/dashboard")
async def dashboard(request: Request):
    """Simulation dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "EV Simulation Web Backend is running"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting EV Simulation Web Backend...")
    print("📱 Frontend: http://localhost:8000")
    print("📡 API Docs: http://localhost:8000/docs")
    print("🔄 WebSocket: ws://localhost:8000/ws/simulation")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 