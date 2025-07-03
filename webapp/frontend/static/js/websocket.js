/**
 * WebSocket Client for Real-time Communication
 */

class SimulationWebSocket {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectInterval = 3000; // 3 seconds
        this.messageHandlers = new Map();
        
        // Bind methods
        this.connect = this.connect.bind(this);
        this.onOpen = this.onOpen.bind(this);
        this.onMessage = this.onMessage.bind(this);
        this.onClose = this.onClose.bind(this);
        this.onError = this.onError.bind(this);
    }
    
    connect() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/simulation`;
            
            console.log('Connecting to WebSocket:', wsUrl);
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = this.onOpen;
            this.ws.onmessage = this.onMessage;
            this.ws.onclose = this.onClose;
            this.ws.onerror = this.onError;
            
        } catch (error) {
            console.error('WebSocket connection error:', error);
            this.updateConnectionStatus('error');
        }
    }
    
    onOpen(event) {
        console.log('WebSocket connected');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.updateConnectionStatus('connected');
        
        // Send initial ping
        this.sendMessage('ping', { message: 'hello' });
    }
    
    onMessage(event) {
        try {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    }
    
    onClose(event) {
        console.log('WebSocket disconnected:', event.code, event.reason);
        this.isConnected = false;
        this.updateConnectionStatus('disconnected');
        
        // Attempt to reconnect
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
            this.updateConnectionStatus('connecting');
            
            setTimeout(this.connect, this.reconnectInterval);
        } else {
            console.error('Max reconnection attempts reached');
            this.updateConnectionStatus('error');
        }
    }
    
    onError(error) {
        console.error('WebSocket error:', error);
        this.updateConnectionStatus('error');
    }
    
    sendMessage(type, data = {}) {
        if (!this.isConnected || !this.ws) {
            console.warn('WebSocket not connected, cannot send message');
            return false;
        }
        
        const message = {
            type: type,
            data: data,
            timestamp: Date.now()
        };
        
        try {
            this.ws.send(JSON.stringify(message));
            return true;
        } catch (error) {
            console.error('Error sending WebSocket message:', error);
            return false;
        }
    }
    
    handleMessage(message) {
        const { type, data, timestamp } = message;
        
        switch (type) {
            case 'connection':
                console.log('Connection established:', data.message);
                break;
                
            case 'simulation_state':
                this.notifyHandlers('simulation_state', data);
                break;
                
            case 'control_response':
                this.notifyHandlers('control_response', data);
                break;
                
            case 'pong':
                // Handle ping/pong for keepalive
                break;
                
            case 'error':
                console.error('WebSocket error message:', data.error);
                this.notifyHandlers('error', data);
                break;
                
            default:
                console.warn('Unknown message type:', type);
        }
    }
    
    // Event handler registration
    on(event, handler) {
        if (!this.messageHandlers.has(event)) {
            this.messageHandlers.set(event, []);
        }
        this.messageHandlers.get(event).push(handler);
    }
    
    off(event, handler) {
        if (this.messageHandlers.has(event)) {
            const handlers = this.messageHandlers.get(event);
            const index = handlers.indexOf(handler);
            if (index > -1) {
                handlers.splice(index, 1);
            }
        }
    }
    
    notifyHandlers(event, data) {
        if (this.messageHandlers.has(event)) {
            this.messageHandlers.get(event).forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error('Error in message handler:', error);
                }
            });
        }
    }
    
    updateConnectionStatus(status) {
        const statusElement = document.getElementById('connectionStatus');
        if (!statusElement) return;
        
        const icon = statusElement.querySelector('i');
        const text = statusElement.querySelector('.status-text') || 
                    document.createElement('span');
        
        // Remove existing classes
        icon.className = 'fas fa-circle';
        statusElement.className = 'navbar-text';
        
        switch (status) {
            case 'connected':
                icon.classList.add('text-success');
                text.textContent = ' Connected';
                break;
                
            case 'connecting':
                icon.classList.add('text-warning', 'pulse');
                text.textContent = ' Connecting...';
                break;
                
            case 'disconnected':
                icon.classList.add('text-secondary');
                text.textContent = ' Disconnected';
                break;
                
            case 'error':
                icon.classList.add('text-danger');
                text.textContent = ' Connection Error';
                break;
        }
        
        if (!text.classList.contains('status-text')) {
            text.classList.add('status-text');
            statusElement.appendChild(text);
        }
    }
    
    // Control commands
    startSimulation() {
        return this.sendMessage('control', { command: 'start' });
    }
    
    pauseSimulation() {
        return this.sendMessage('control', { command: 'pause' });
    }
    
    resumeSimulation() {
        return this.sendMessage('control', { command: 'resume' });
    }
    
    stopSimulation() {
        return this.sendMessage('control', { command: 'stop' });
    }
    
    setSpeed(multiplier) {
        return this.sendMessage('control', { 
            command: 'speed', 
            multiplier: multiplier 
        });
    }
    
    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
        this.isConnected = false;
    }
}

// Global WebSocket instance
window.simulationWS = new SimulationWebSocket(); 