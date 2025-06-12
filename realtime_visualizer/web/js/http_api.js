/**
 * HTTP API Client for Real-time Simulation Communication
 * Simple HTTP polling to replace WebSocket
 */
class SimulationHttpApi {
    constructor() {
        this.baseUrl = window.location.origin + '/api';
        this.pollInterval = 2000; // 2 seconds polling
        this.isConnected = false;
        this.messageHandlers = {};
        
        this.pollTimer = null;
        this.connectionCheckTimer = null;
        
        // Bind methods
        this.connect = this.connect.bind(this);
        this.disconnect = this.disconnect.bind(this);
        this.startPolling = this.startPolling.bind(this);
        this.stopPolling = this.stopPolling.bind(this);
    }

    /**
     * Connect to API server
     */
    async connect() {
        console.log('🔗 Attempting to connect to API server...');
        
        try {
            // Test connection with status endpoint
            const response = await fetch(`${this.baseUrl}/status`);
            if (response.ok) {
                this.isConnected = true;
                console.log('✅ Connected to API server successfully');
                
                // Load initial data
                await this.loadInitialData();
                
                // Start polling for updates
                this.startPolling();
                
                // Update connection status
                this.updateConnectionStatus(true);
                this.emit('connected');
                
                return true;
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.error('❌ Failed to connect to API server:', error);
            this.isConnected = false;
            this.updateConnectionStatus(false);
            this.emit('error', error);
            return false;
        }
    }

    /**
     * Load initial data from server
     */
    async loadInitialData() {
        try {
            const response = await fetch(`${this.baseUrl}/initial_data`);
            const result = await response.json();
            
            if (result.success) {
                // Emit map data
                this.emit('map_data', {
                    charging_stations: result.charging_stations
                });
                
                // Get current status
                await this.updateStatus();
                
                console.log('📊 Initial data loaded successfully');
            } else {
                console.error('Failed to load initial data:', result.error);
            }
        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    }

    /**
     * Update status from server
     */
    async updateStatus() {
        try {
            const response = await fetch(`${this.baseUrl}/status`);
            const status = await response.json();
            
            // Emit control state
            this.emit('control_state', {
                is_running: status.is_running,
                is_paused: status.is_paused,
                speed_multiplier: status.speed_multiplier
            });
            
        } catch (error) {
            console.error('Error updating status:', error);
        }
    }

    /**
     * Start polling for simulation data
     */
    startPolling() {
        if (this.pollTimer) {
            clearInterval(this.pollTimer);
        }
        
        this.pollTimer = setInterval(async () => {
            if (this.isConnected) {
                await this.pollSimulationData();
            }
        }, this.pollInterval);
        
        console.log(`🔄 Started polling every ${this.pollInterval}ms`);
    }

    /**
     * Stop polling
     */
    stopPolling() {
        if (this.pollTimer) {
            clearInterval(this.pollTimer);
            this.pollTimer = null;
        }
    }

    /**
     * Poll simulation data from server
     */
    async pollSimulationData() {
        try {
            const response = await fetch(`${this.baseUrl}/simulation_data`);
            const result = await response.json();
            
            if (result.success) {
                // Emit simulation update
                this.emit('simulation_update', result.data);
            } else {
                console.error('Failed to get simulation data:', result.error);
            }
            
        } catch (error) {
            console.error('Error polling simulation data:', error);
            // Handle connection loss
            this.handleConnectionLoss();
        }
    }

    /**
     * Handle connection loss
     */
    handleConnectionLoss() {
        if (this.isConnected) {
            console.warn('🔌 Connection lost, attempting to reconnect...');
            this.isConnected = false;
            this.updateConnectionStatus(false);
            this.emit('disconnected');
            
            // Try to reconnect
            setTimeout(() => {
                this.connect();
            }, 5000);
        }
    }

    /**
     * Send control command
     */
    async sendCommand(command, params = {}) {
        try {
            const response = await fetch(`${this.baseUrl}/control`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    command: command,
                    ...params
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                console.log(`✅ Command ${command} executed successfully`);
                // Update status after command
                setTimeout(() => this.updateStatus(), 100);
                return true;
            } else {
                console.error(`Failed to execute command ${command}:`, result.error);
                return false;
            }
            
        } catch (error) {
            console.error(`Error sending command ${command}:`, error);
            return false;
        }
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
    async getVehicleDetails(vehicleId) {
        try {
            const response = await fetch(`${this.baseUrl}/vehicle/${vehicleId}`);
            const result = await response.json();
            
            if (result.success) {
                this.emit('vehicle_details', {
                    vehicle_id: vehicleId,
                    data: result.data
                });
                return true;
            } else {
                console.error(`Failed to get vehicle details for ${vehicleId}:`, result.error);
                return false;
            }
            
        } catch (error) {
            console.error(`Error getting vehicle details for ${vehicleId}:`, error);
            return false;
        }
    }

    /**
     * Get order details
     */
    async getOrderDetails(orderId) {
        try {
            // Note: This endpoint needs to be implemented in Flask server
            console.log(`Order details for ${orderId} - endpoint not yet implemented`);
            return false;
            
        } catch (error) {
            console.error(`Error getting order details for ${orderId}:`, error);
            return false;
        }
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
                statusText.textContent = 'Connected to Simulation API';
            } else {
                statusIndicator.classList.remove('connected');
                statusText.textContent = 'Disconnected - Trying to reconnect...';
            }
        }
    }

    /**
     * Disconnect from server
     */
    disconnect() {
        console.log('🔌 Disconnecting from API server...');
        
        this.isConnected = false;
        this.stopPolling();
        this.updateConnectionStatus(false);
        
        if (this.connectionCheckTimer) {
            clearTimeout(this.connectionCheckTimer);
            this.connectionCheckTimer = null;
        }
    }

    /**
     * Get connection status
     */
    getConnectionStatus() {
        return {
            isConnected: this.isConnected
        };
    }
}

// Create global API instance
window.simulationWS = new SimulationHttpApi(); // Keep same name for compatibility 