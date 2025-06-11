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
                statusText.textContent = 'Connected';
            } else {
                statusIndicator.classList.remove('connected');
                statusText.textContent = this.reconnectAttempts > 0 ? 
                    `Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})` : 
                    'Disconnected';
            }
        }
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