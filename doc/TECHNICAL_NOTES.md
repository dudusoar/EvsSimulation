# Technical Notes & Design Decisions

## Core Design Principles

### 1. KISS Principle
- Keep system modular and simple
- Avoid over-engineering
- Prioritize functionality over complexity

### 2. Non-Breaking Architecture
- Real-time visualizer is completely independent
- Existing simulation engine remains untouched
- Optional feature that can be enabled/disabled

## Real-time Visualizer Architecture

### Data Flow Design
```
Simulation Engine → WebSocket Server → Browser Frontend
     ↑                    ↓
   Control Commands ← WebSocket ← User Interactions
```

### Key Technical Decisions

#### 1. No Frame Storage
**Problem**: Traditional visualization stores thousands of frames
**Solution**: Stream data in real-time, discard after sending
**Benefit**: Massive memory savings, better performance

#### 2. WebSocket over HTTP Polling
**Why**: Real-time bidirectional communication needed
**Alternative**: HTTP polling would be inefficient
**Implementation**: asyncio-based server for concurrent connections

#### 3. Thread Separation
**Simulation Thread**: Runs simulation engine loop
**WebSocket Thread**: Handles client communications
**Benefit**: Simulation continues even if no clients connected

### Performance Considerations

#### Data Compression
- Only send changed data (delta updates)
- Compress position data using appropriate precision
- Batch multiple updates when possible

#### Client Management
- Handle disconnected clients gracefully
- Support multiple simultaneous viewers
- Implement heartbeat for connection monitoring

## Reinforcement Learning Design

### Environment Interface
```python
class ChargingEnvironment:
    def get_state(self, vehicle_id) -> np.array:
        # Battery level, position, order density, station status
        
    def get_action_space(self) -> gym.Space:
        # Discrete: [no_action, charge_to_50%, charge_to_80%, charge_to_100%]
        # Continuous: charge_amount [0, 1]
        
    def calculate_reward(self, state, action, next_state) -> float:
        # Multi-objective: revenue, service_quality, efficiency
```

### Policy Interface
```python
class ChargingPolicy:
    def decide_action(self, vehicle_state, environment_state):
        # Return charging decision
        
    def learn(self, experience_batch):
        # Update policy parameters
```

### Reward Function Design
**Components:**
- Revenue: Direct income from completed orders
- Service Quality: Penalty for long wait times
- Efficiency: Reward for optimal charging timing
- Coordination: Bonus for avoiding charging station congestion

## Technical Stack

### Backend Dependencies
```
websockets>=10.0    # Real-time communication
aiohttp>=3.8.0      # HTTP server for frontend
asyncio             # Async programming
threading           # Simulation isolation
```

### Frontend Stack
```
Leaflet.js          # Map visualization
Chart.js            # Statistics charts
Native WebSocket    # Real-time communication
CSS Grid/Flexbox    # Responsive layout
```

### Future ML Dependencies
```
stable-baselines3   # RL algorithms
gymnasium          # RL environment interface
tensorboard        # Experiment tracking
```

## File Structure Decisions

### Current Organization
```
realtime_visualizer/
├── __init__.py                 # Module exports
├── websocket_server.py         # ✅ Complete
├── realtime_visualizer.py      # ❌ To be created
└── web/                        # ❌ To be created
    ├── index.html
    ├── css/style.css
    └── js/
        ├── main.js
        ├── map.js
        └── websocket.js
```

### Integration Points
- `main.py`: Add `--realtime` flag
- `requirements.txt`: Add websocket dependencies
- No changes to core simulation engine

## State Management

### WebSocket Server State
```python
{
    'clients': Set[WebSocketConnection],
    'simulation_state': {
        'is_running': bool,
        'is_paused': bool,
        'speed_multiplier': float
    },
    'simulation_data': {
        'vehicles': List[VehicleState],
        'orders': List[OrderState],
        'statistics': Dict
    }
}
```

### Frontend State
```javascript
{
    map: LeafletMap,
    vehicles: Map<id, VehicleMarker>,
    orders: Map<id, OrderMarker>,
    websocket: WebSocket,
    controls: {
        isRunning: boolean,
        speed: number
    }
}
```

## Error Handling Strategy

### Connection Failures
- Automatic reconnection with exponential backoff
- Graceful degradation when WebSocket unavailable
- Clear user feedback on connection status

### Simulation Errors
- Isolation: Frontend errors don't crash simulation
- Logging: Comprehensive error logging for debugging
- Recovery: Ability to reset simulation state

## Security Considerations

### Local Development
- WebSocket server bound to localhost only
- No authentication required for research use
- File serving restricted to web/ directory

### Future Production (if needed)
- Add basic authentication
- HTTPS/WSS for secure communication
- Input validation for control commands

## Performance Targets

### Real-time Requirements
- **Latency**: < 100ms for control commands
- **Update Rate**: 10-30 FPS for smooth visualization
- **Memory**: No accumulation, constant usage
- **Concurrent Users**: Support 5-10 simultaneous researchers

### Scalability Limits
- Single machine deployment
- ~100 vehicles maximum for real-time performance
- City-scale maps (not country-scale) 