# Electric Vehicle Simulation System - Project Overview

## Project Goals
NSF research project for studying electric vehicle charging behaviors and their impact on fleet optimization.

**Primary Objectives:**
1. Enable researchers to explore different charging policies
2. Maximize objective functions through reinforcement learning
3. Provide real-time visualization without storing massive frame data

## System Architecture

```
├── core/                    # Core simulation engine
│   ├── simulation_engine.py # Main simulation controller
│   ├── vehicle_manager.py   # Vehicle fleet management
│   ├── order_system.py      # Order generation & dispatch
│   ├── charging_manager.py  # Charging station management
│   └── map_manager.py       # OpenStreetMap integration
├── models/                  # Data models
│   ├── vehicle.py          # Vehicle state & behavior
│   ├── order.py            # Order lifecycle
│   └── charging_station.py # Charging infrastructure
├── realtime_visualizer/     # Real-time visualization (NEW)
│   ├── websocket_server.py # WebSocket communication
│   └── 实时可视化方案设计.txt # Design document
├── visualization/           # Traditional visualization
└── main.py                  # Entry point
```

## Key Components

### 1. Simulation Engine
- Real-world map data (OpenStreetMap)
- Complete business process: order → dispatch → pickup → dropoff → charging
- Supports any global city location

### 2. Vehicle Management
- Battery management with realistic consumption
- Intelligent charging decisions
- Route planning on actual road networks

### 3. Order System
- Dynamic order generation
- Proximity-based vehicle assignment
- Real-time status tracking

### 4. Real-time Visualizer (In Development)
- WebSocket-based live updates
- Game-like controls (play/pause/speed)
- No frame storage requirement

## Research Applications
- Testing different charging policies
- Analyzing impact on fleet performance
- Reinforcement learning for charging optimization
- Multi-agent coordination strategies 