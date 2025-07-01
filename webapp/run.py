#!/usr/bin/env python3
"""
EV Simulation Web Application Launcher
Quick start script for the web application
"""

import sys
import os
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import websockets
        import pydantic
        print("✅ Backend dependencies OK")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Install with: pip install -r webapp/backend/requirements.txt")
        return False

def main():
    """Main launcher function"""
    print("🚀 Starting EV Simulation Web Application")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Get paths
    project_root = Path(__file__).parent.parent
    backend_dir = Path(__file__).parent / "backend"
    
    # Add project root to Python path
    sys.path.insert(0, str(project_root))
    
    print(f"📁 Project root: {project_root}")
    print(f"🖥️  Backend dir: {backend_dir}")
    print()
    
    try:
        # Import and run the FastAPI app
        os.chdir(backend_dir)
        
        print("🌐 Starting FastAPI server...")
        print("📱 Frontend: http://localhost:8000")
        print("📡 API Docs: http://localhost:8000/docs")
        print("🔄 WebSocket: ws://localhost:8000/ws/simulation")
        print()
        print("🛑 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Run uvicorn server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app",
            "--host", "0.0.0.0",
            "--port", "8000", 
            "--reload",
            "--log-level", "info"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 