/**
 * WebSocket Client for Real-time Simulation Communication
 */
class SimulationWebSocket {
    constructor() {
        this.ws = null;
        this.reconnectInterval = 3000; // 3 seconds
        this.maxReconnectAttempts = 10;
        this.reconnectAttempts = 0;
        this.isConnected = false;
        this.messageHandlers = {};
        this.reconnectTimer = null;
        
        // Bind methods
        this.connect = this.connect.bind(this);
        this.onOpen = this.onOpen.bind(this);
        this.onMessage = this.onMessage.bind(this);
        this.onClose = this.onClose.bind(this);
        this.onError = this.onError.bind(this);
    }

    /**
     * Connect to WebSocket server
     */
    connect() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const host = window.location.hostname;
            const port = 8765; // Default WebSocket port
            const url = `${protocol}//${host}:${port}`;
            
            console.log(`Attempting to connect to WebSocket at ${url}`);
            this.ws = new WebSocket(url);
            
            this.ws.onopen = this.onOpen;
            this.ws.onmessage = this.onMessage;
            this.ws.onclose = this.onClose;
            this.ws.onerror = this.onError;
            
        } catch (error) {
            console.error('WebSocket connection error:', error);
            this.scheduleReconnect();
        }
    }

    /**
     * Handle WebSocket open event
     */
    onOpen(event) {
        console.log('WebSocket connected successfully');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        
        // Clear any pending reconnect timer
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
        
        // Update UI
        this.updateConnectionStatus(true);
        
        // Trigger connected event
        this.emit('connected');
    }

    /**
     * Handle WebSocket message event
     */
    onMessage(event) {
        try {
            const data = JSON.parse(event.data);
            console.log('Received message:', data.type);
            
            // Emit event based on message type
            this.emit(data.type, data);
            
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    }

    /**
     * Handle WebSocket close event
     */
    onClose(event) {
        console.log('WebSocket connection closed', event);
        this.isConnected = false;
        this.updateConnectionStatus(false);
        
        // Don't reconnect if it was a clean close
        if (event.code !== 1000) {
            this.scheduleReconnect();
        }
        
        this.emit('disconnected');
    }

    /**
     * Handle WebSocket error event
     */
    onError(error) {
        console.error('WebSocket error:', error);
        this.emit('error', error);
    }

    /**
     * Schedule reconnection attempt
     */
    scheduleReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnection attempts reached');
            this.emit('maxReconnectAttemptsReached');
            return;
        }

        this.reconnectAttempts++;
        console.log(`Scheduling reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${this.reconnectInterval}ms`);
        
        this.reconnectTimer = setTimeout(() => {
            this.connect();
        }, this.reconnectInterval);
    }

    /**
     * Send message to server
     */
    send(message) {
        if (this.isConnected && this.ws && this.ws.readyState === WebSocket.OPEN) {
            try {
                this.ws.send(JSON.stringify(message));
                console.log('Sent message:', message);
                return true;
            } catch (error) {
                console.error('Error sending message:', error);
                return false;
            }
        } else {
            console.warn('WebSocket not connected. Cannot send message:', message);
            return false;
        }
    }

    /**
     * Send simulation control command
     */
    sendCommand(command, params = {}) {
        return this.send({
            command: command,
            ...params
        });
    }

    /**
     * Start simulation
     */
    startSimulation() {
        return this.sendCommand('start');
    }

    /**
     * Pause simulation
     */
    pauseSimulation() {
        return this.sendCommand('pause');
    }

    /**
     * Resume simulation
     */
    resumeSimulation() {
        return this.sendCommand('resume');
    }

    /**
     * Reset simulation
     */
    resetSimulation() {
        return this.sendCommand('reset');
    }

    /**
     * Set simulation speed
     */
    setSpeed(speed) {
        return this.sendCommand('set_speed', { speed: speed });
    }

    /**
     * Get vehicle details
     */
    getVehicleDetails(vehicleId) {
        return this.sendCommand('get_vehicle_details', { vehicle_id: vehicleId });
    }

    /**
     * Get order details
     */
    getOrderDetails(orderId) {
        return this.sendCommand('get_order_details', { order_id: orderId });
    }

    /**
     * Register event handler
     */
    on(eventType, handler) {
        if (!this.messageHandlers[eventType]) {
            this.messageHandlers[eventType] = [];
        }
        this.messageHandlers[eventType].push(handler);
    }

    /**
     * Unregister event handler
     */
    off(eventType, handler) {
        if (this.messageHandlers[eventType]) {
            const index = this.messageHandlers[eventType].indexOf(handler);
            if (index > -1) {
                this.messageHandlers[eventType].splice(index, 1);
            }
        }
    }

    /**
     * Emit event to registered handlers
     */
    emit(eventType, data = null) {
        if (this.messageHandlers[eventType]) {
            this.messageHandlers[eventType].forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`Error in event handler for ${eventType}:`, error);
                }
            });
        }
    }

    /**
     * Update connection status in UI
     */
    updateConnectionStatus(connected) {
        const statusIndicator = document.getElementById('status-indicator');
        const statusText = document.getElementById('status-text');
        
        if (statusIndicator && statusText) {
            if (connected) {
                statusIndicator.classList.add('connected');
                statusText.textContent = 'Connected to Simulation Server';
            } else {
                statusIndicator.classList.remove('connected');
                if (this.reconnectAttempts >= this.maxReconnectAttempts) {
                    statusText.textContent = 'Connection Failed - Server Unavailable';
                    console.log('🔌 无法连接到实时仿真服务器，请检查后端是否正常运行');
                } else {
                    statusText.textContent = this.reconnectAttempts > 0 ? 
                        `Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})` : 
                        'Connecting to Simulation Server...';
                }
            }
        }
    }

    /**
     * Enable offline mode with static data
     */
    enableOfflineMode() {
        console.log('Enabling offline mode with static simulation data');
        
        // Simulate basic map data for demonstration
        setTimeout(() => {
            this.emit('map_data', {
                charging_stations: [
                    { id: 'cs1', position: [-86.9080, 40.4259], capacity: 4 },
                    { id: 'cs2', position: [-86.9200, 40.4300], capacity: 6 },
                    { id: 'cs3', position: [-86.9000, 40.4200], capacity: 8 }
                ]
            });
            
            // Simulate control state
            this.emit('control_state', {
                is_running: false,
                is_paused: false,
                speed_multiplier: 1.0
            });
            
            // Show demo vehicles
            const demoVehicles = [];
            for (let i = 0; i < 10; i++) {
                demoVehicles.push({
                    id: `vehicle_${i}`,
                    position: [-86.9080 + (Math.random() - 0.5) * 0.02, 40.4259 + (Math.random() - 0.5) * 0.02],
                    battery_percentage: 50 + Math.random() * 50,
                    status: ['idle', 'picking_up', 'en_route', 'charging'][Math.floor(Math.random() * 4)],
                    has_passenger: Math.random() > 0.7
                });
            }
            
            // Show demo orders
            const demoOrders = [];
            for (let i = 0; i < 5; i++) {
                demoOrders.push({
                    id: `order_${i}`,
                    pickup_position: [-86.9080 + (Math.random() - 0.5) * 0.02, 40.4259 + (Math.random() - 0.5) * 0.02],
                    dropoff_position: [-86.9080 + (Math.random() - 0.5) * 0.02, 40.4259 + (Math.random() - 0.5) * 0.02],
                    status: ['pending', 'active'][Math.floor(Math.random() * 2)],
                    assigned_vehicle: Math.random() > 0.5 ? `vehicle_${Math.floor(Math.random() * 10)}` : null
                });
            }
            
            this.emit('simulation_update', {
                timestamp: new Date().toISOString(),
                simulation_time: 0,
                vehicles: demoVehicles,
                orders: demoOrders,
                statistics: {
                    total_vehicles: 10,
                    pending_orders: 3,
                    active_orders: 2,
                    completed_orders: 15,
                    total_revenue: 287.50,
                    average_battery: 75
                }
            });
            
            // Start animation loop for demo mode
            this.startDemoAnimation(demoVehicles, demoOrders);
            
        }, 2000);
    }

    /**
     * Start demo animation loop
     */
    startDemoAnimation(vehicles, orders) {
        console.log('🎬 Starting demo animation...');
        
        let simulationTime = 0;
        let completedOrders = 15;
        let totalRevenue = 287.50;
        
        const animationInterval = setInterval(() => {
            // Update simulation time
            simulationTime += 5; // 5 seconds per update
            
            // Animate vehicles
            vehicles.forEach(vehicle => {
                // Slightly move vehicles
                vehicle.position[0] += (Math.random() - 0.5) * 0.0005;
                vehicle.position[1] += (Math.random() - 0.5) * 0.0005;
                
                // Randomly change battery (simulate charging/usage)
                vehicle.battery_percentage += (Math.random() - 0.5) * 2;
                vehicle.battery_percentage = Math.max(10, Math.min(100, vehicle.battery_percentage));
                
                // Randomly change status
                if (Math.random() < 0.1) { // 10% chance to change status
                    const statuses = ['idle', 'picking_up', 'en_route', 'charging'];
                    vehicle.status = statuses[Math.floor(Math.random() * statuses.length)];
                    vehicle.has_passenger = vehicle.status === 'en_route' && Math.random() > 0.3;
                }
            });
            
            // Animate orders
            orders.forEach(order => {
                // Randomly complete some orders
                if (order.status === 'active' && Math.random() < 0.05) { // 5% chance
                    order.status = 'completed';
                    completedOrders++;
                    totalRevenue += 15 + Math.random() * 20; // Add $15-35 revenue
                }
                
                // Create new orders occasionally
                if (order.status === 'completed' && Math.random() < 0.03) { // 3% chance
                    order.status = 'pending';
                    order.pickup_position = [-86.9080 + (Math.random() - 0.5) * 0.02, 40.4259 + (Math.random() - 0.5) * 0.02];
                    order.dropoff_position = [-86.9080 + (Math.random() - 0.5) * 0.02, 40.4259 + (Math.random() - 0.5) * 0.02];
                    order.assigned_vehicle = null;
                }
                
                // Assign vehicles to pending orders
                if (order.status === 'pending' && Math.random() < 0.08) { // 8% chance
                    order.status = 'active';
                    order.assigned_vehicle = `vehicle_${Math.floor(Math.random() * 10)}`;
                }
            });
            
            // Count order statuses
            const pendingOrders = orders.filter(o => o.status === 'pending').length;
            const activeOrders = orders.filter(o => o.status === 'active').length;
            
            // Calculate average battery
            const avgBattery = vehicles.reduce((sum, v) => sum + v.battery_percentage, 0) / vehicles.length;
            
            // Emit updated data
            this.emit('simulation_update', {
                timestamp: new Date().toISOString(),
                simulation_time: simulationTime,
                vehicles: vehicles,
                orders: orders,
                statistics: {
                    total_vehicles: 10,
                    pending_orders: pendingOrders,
                    active_orders: activeOrders,
                    completed_orders: completedOrders,
                    total_revenue: Math.round(totalRevenue * 100) / 100, // Round to 2 decimal places
                    average_battery: Math.round(avgBattery)
                }
            });
            
        }, 2000); // Update every 2 seconds
        
        // Store interval ID for potential cleanup
        this.demoAnimationInterval = animationInterval;
    }

    /**
     * Disconnect WebSocket
     */
    disconnect() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
        
        if (this.ws) {
            this.ws.close(1000, 'Manual disconnect');
            this.ws = null;
        }
        
        this.isConnected = false;
        this.updateConnectionStatus(false);
    }

    /**
     * Get connection status
     */
    getConnectionStatus() {
        return {
            isConnected: this.isConnected,
            reconnectAttempts: this.reconnectAttempts,
            maxReconnectAttempts: this.maxReconnectAttempts
        };
    }
}

// Create global WebSocket instance
window.simulationWS = new SimulationWebSocket(); 