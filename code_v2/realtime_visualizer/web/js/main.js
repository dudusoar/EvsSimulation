<<<<<<< HEAD
/**
 * Main Application Controller for Real-time Simulation
 */
class SimulationApp {
    constructor() {
        this.isSimulationRunning = false;
        this.isPaused = false;
        this.currentSpeed = 1.0;
        this.simulationStartTime = null;
        this.statistics = {};
        
        // UI elements
        this.elements = {};
        
        // Bind methods
        this.init = this.init.bind(this);
        this.setupEventHandlers = this.setupEventHandlers.bind(this);
        this.setupWebSocketHandlers = this.setupWebSocketHandlers.bind(this);
        this.updateUI = this.updateUI.bind(this);
    }

    /**
     * Initialize the application
     */
    async init() {
        console.log('Initializing Simulation App...');
        
        try {
            // Cache UI elements
            this.cacheUIElements();
            
            // Initialize map
            if (!window.simulationMap.initialize()) {
                throw new Error('Failed to initialize map');
            }
            
            // Setup event handlers
            this.setupEventHandlers();
            this.setupWebSocketHandlers();
            
            // Connect to WebSocket
            window.simulationWS.connect();
            
            // Initial UI state
            this.updateControlButtons();
            
            console.log('Simulation App initialized successfully');
            
        } catch (error) {
            console.error('Error initializing app:', error);
            this.showError('Failed to initialize application: ' + error.message);
        }
    }

    /**
     * Cache UI element references
     */
    cacheUIElements() {
        this.elements = {
            // Control buttons
            startBtn: document.getElementById('start-btn'),
            pauseBtn: document.getElementById('pause-btn'),
            resumeBtn: document.getElementById('resume-btn'),
            resetBtn: document.getElementById('reset-btn'),
            
            // Speed controls
            speedSlider: document.getElementById('speed-slider'),
            speedValue: document.getElementById('speed-value'),
            speedButtons: document.querySelectorAll('.speed-btn'),
            
            // Statistics
            statVehicles: document.getElementById('stat-vehicles'),
            statPendingOrders: document.getElementById('stat-pending-orders'),
            statActiveOrders: document.getElementById('stat-active-orders'),
            statCompletedOrders: document.getElementById('stat-completed-orders'),
            statRevenue: document.getElementById('stat-revenue'),
            statBattery: document.getElementById('stat-battery'),
            
            // Time display
            simulationTime: document.getElementById('simulation-time'),
            
            // Details panel
            detailsPanel: document.getElementById('details-panel'),
            detailsTitle: document.getElementById('details-title'),
            detailsContent: document.getElementById('details-content')
        };
    }

    /**
     * Setup UI event handlers
     */
    setupEventHandlers() {
        // Control buttons
        this.elements.startBtn?.addEventListener('click', () => {
            this.startSimulation();
        });

        this.elements.pauseBtn?.addEventListener('click', () => {
            this.pauseSimulation();
        });

        this.elements.resumeBtn?.addEventListener('click', () => {
            this.resumeSimulation();
        });

        this.elements.resetBtn?.addEventListener('click', () => {
            this.resetSimulation();
        });

        // Speed controls
        this.elements.speedSlider?.addEventListener('input', (e) => {
            this.setSpeed(parseFloat(e.target.value));
        });

        this.elements.speedButtons?.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const speed = parseFloat(e.target.dataset.speed);
                this.setSpeed(speed);
            });
        });

        // Window resize
        window.addEventListener('resize', () => {
            window.simulationMap.resize();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboard(e);
        });
    }

    /**
     * Setup WebSocket event handlers
     */
    setupWebSocketHandlers() {
        const ws = window.simulationWS;

        // Connection events
        ws.on('connected', () => {
            console.log('Connected to simulation server');
            this.updateControlButtons();
        });

        ws.on('disconnected', () => {
            console.log('Disconnected from simulation server');
            this.updateControlButtons();
        });

        ws.on('error', (error) => {
            console.error('WebSocket error:', error);
            this.showError('Connection error: ' + error.message);
        });

        ws.on('maxReconnectAttemptsReached', () => {
            this.showError('Failed to connect to simulation server after multiple attempts');
        });

        // Simulation data events
        ws.on('map_data', (data) => {
            this.handleMapData(data);
        });

        ws.on('control_state', (data) => {
            this.handleControlState(data);
        });

        ws.on('simulation_update', (data) => {
            this.handleSimulationUpdate(data);
        });

        ws.on('vehicle_details', (data) => {
            this.showVehicleDetails(data);
        });

        ws.on('order_details', (data) => {
            this.showOrderDetails(data);
        });
    }

    /**
     * Handle map initialization data
     */
    handleMapData(data) {
        console.log('Received map data');
        
        if (data.charging_stations) {
            window.simulationMap.updateChargingStations(data.charging_stations);
            window.simulationMap.updateMapBounds(data.charging_stations);
        }
    }

    /**
     * Handle control state updates
     */
    handleControlState(data) {
        this.isSimulationRunning = data.is_running;
        this.isPaused = data.is_paused;
        this.currentSpeed = data.speed_multiplier;
        
        this.updateControlButtons();
        this.updateSpeedControls();
    }

    /**
     * Handle simulation data updates
     */
    handleSimulationUpdate(data) {
        // Update map with vehicles and orders
        if (data.vehicles) {
            window.simulationMap.updateVehicles(data.vehicles);
        }
        
        if (data.orders) {
            window.simulationMap.updateOrders(data.orders);
        }

        // Update statistics
        if (data.statistics) {
            this.statistics = data.statistics;
            this.updateStatistics();
        }

        // Update simulation time
        if (data.simulation_time !== undefined) {
            this.updateSimulationTime(data.simulation_time);
        }
    }

    /**
     * Start simulation
     */
    startSimulation() {
        if (window.simulationWS.isConnected) {
            window.simulationWS.startSimulation();
            this.simulationStartTime = Date.now();
        } else {
            this.showError('Not connected to simulation server');
        }
    }

    /**
     * Pause simulation
     */
    pauseSimulation() {
        if (window.simulationWS.isConnected) {
            window.simulationWS.pauseSimulation();
        }
    }

    /**
     * Resume simulation
     */
    resumeSimulation() {
        if (window.simulationWS.isConnected) {
            window.simulationWS.resumeSimulation();
        }
    }

    /**
     * Reset simulation
     */
    resetSimulation() {
        if (confirm('Are you sure you want to reset the simulation? All progress will be lost.')) {
            if (window.simulationWS.isConnected) {
                window.simulationWS.resetSimulation();
                window.simulationMap.clearAllMarkers();
                this.resetStatistics();
                this.hideDetails();
            }
        }
    }

    /**
     * Set simulation speed
     */
    setSpeed(speed) {
        this.currentSpeed = speed;
        
        if (window.simulationWS.isConnected) {
            window.simulationWS.setSpeed(speed);
        }
        
        this.updateSpeedControls();
    }

    /**
     * Update control buttons state
     */
    updateControlButtons() {
        const connected = window.simulationWS.isConnected;
        
        if (this.elements.startBtn) {
            this.elements.startBtn.disabled = !connected || this.isSimulationRunning;
        }
        
        if (this.elements.pauseBtn) {
            this.elements.pauseBtn.disabled = !connected || !this.isSimulationRunning || this.isPaused;
        }
        
        if (this.elements.resumeBtn) {
            this.elements.resumeBtn.disabled = !connected || !this.isSimulationRunning || !this.isPaused;
        }
        
        if (this.elements.resetBtn) {
            this.elements.resetBtn.disabled = !connected;
        }
    }

    /**
     * Update speed controls
     */
    updateSpeedControls() {
        // Update slider
        if (this.elements.speedSlider) {
            this.elements.speedSlider.value = this.currentSpeed;
        }
        
        // Update speed display
        if (this.elements.speedValue) {
            this.elements.speedValue.textContent = this.currentSpeed.toFixed(1);
        }
        
        // Update speed buttons
        this.elements.speedButtons?.forEach(btn => {
            const btnSpeed = parseFloat(btn.dataset.speed);
            btn.classList.toggle('active', Math.abs(btnSpeed - this.currentSpeed) < 0.1);
        });
    }

    /**
     * Update statistics display
     */
    updateStatistics() {
        const stats = this.statistics;
        
        if (this.elements.statVehicles && stats.total_vehicles !== undefined) {
            this.elements.statVehicles.textContent = stats.total_vehicles;
        }
        
        if (this.elements.statPendingOrders && stats.pending_orders !== undefined) {
            this.elements.statPendingOrders.textContent = stats.pending_orders;
        }
        
        if (this.elements.statActiveOrders && stats.active_orders !== undefined) {
            this.elements.statActiveOrders.textContent = stats.active_orders;
        }
        
        if (this.elements.statCompletedOrders && stats.completed_orders !== undefined) {
            this.elements.statCompletedOrders.textContent = stats.completed_orders;
        }
        
        if (this.elements.statRevenue && stats.total_revenue !== undefined) {
            this.elements.statRevenue.textContent = '$' + Math.round(stats.total_revenue);
        }
        
        if (this.elements.statBattery && stats.average_battery !== undefined) {
            this.elements.statBattery.textContent = Math.round(stats.average_battery) + '%';
        }
    }

    /**
     * Reset statistics display
     */
    resetStatistics() {
        this.statistics = {};
        
        if (this.elements.statVehicles) this.elements.statVehicles.textContent = '0';
        if (this.elements.statPendingOrders) this.elements.statPendingOrders.textContent = '0';
        if (this.elements.statActiveOrders) this.elements.statActiveOrders.textContent = '0';
        if (this.elements.statCompletedOrders) this.elements.statCompletedOrders.textContent = '0';
        if (this.elements.statRevenue) this.elements.statRevenue.textContent = '$0';
        if (this.elements.statBattery) this.elements.statBattery.textContent = '0%';
        if (this.elements.simulationTime) this.elements.simulationTime.textContent = '00:00:00';
    }

    /**
     * Update simulation time display
     */
    updateSimulationTime(timeInSeconds) {
        if (this.elements.simulationTime) {
            const hours = Math.floor(timeInSeconds / 3600);
            const minutes = Math.floor((timeInSeconds % 3600) / 60);
            const seconds = Math.floor(timeInSeconds % 60);
            
            const timeString = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            this.elements.simulationTime.textContent = timeString;
        }
    }

    /**
     * Show vehicle details
     */
    showVehicleDetails(data) {
        if (!data.data) return;
        
        const vehicle = data.data;
        const content = `
            <div class="detail-row">
                <span class="detail-label">Vehicle ID:</span>
                <span>${data.vehicle_id}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Status:</span>
                <span>${vehicle.status}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Battery:</span>
                <span>${Math.round(vehicle.battery_percentage)}%</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Position:</span>
                <span>${vehicle.position[0].toFixed(4)}, ${vehicle.position[1].toFixed(4)}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Current Task:</span>
                <span>${vehicle.current_task || 'None'}</span>
            </div>
        `;
        
        this.showDetails('🚗 Vehicle Details', content);
    }

    /**
     * Show order details
     */
    showOrderDetails(data) {
        if (!data.data) return;
        
        const order = data.data;
        const content = `
            <div class="detail-row">
                <span class="detail-label">Order ID:</span>
                <span>${data.order_id}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Status:</span>
                <span>${order.status}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Pickup:</span>
                <span>${order.pickup_position[0].toFixed(4)}, ${order.pickup_position[1].toFixed(4)}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Dropoff:</span>
                <span>${order.dropoff_position[0].toFixed(4)}, ${order.dropoff_position[1].toFixed(4)}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Assigned Vehicle:</span>
                <span>${order.assigned_vehicle || 'Unassigned'}</span>
            </div>
        `;
        
        this.showDetails('📦 Order Details', content);
    }

    /**
     * Show details panel
     */
    showDetails(title, content) {
        if (this.elements.detailsPanel && this.elements.detailsTitle && this.elements.detailsContent) {
            this.elements.detailsTitle.textContent = title;
            this.elements.detailsContent.innerHTML = content;
            this.elements.detailsPanel.style.display = 'block';
        }
    }

    /**
     * Hide details panel
     */
    hideDetails() {
        if (this.elements.detailsPanel) {
            this.elements.detailsPanel.style.display = 'none';
        }
    }

    /**
     * Handle keyboard shortcuts
     */
    handleKeyboard(e) {
        // Only handle shortcuts when not typing in inputs
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            return;
        }

        switch (e.key) {
            case ' ':
                e.preventDefault();
                if (this.isSimulationRunning && !this.isPaused) {
                    this.pauseSimulation();
                } else if (this.isSimulationRunning && this.isPaused) {
                    this.resumeSimulation();
                } else {
                    this.startSimulation();
                }
                break;
            case 'r':
            case 'R':
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    this.resetSimulation();
                }
                break;
            case 'Escape':
                this.hideDetails();
                break;
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        console.error(message);
        // You could implement a toast notification system here
        alert('Error: ' + message);
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        console.log(message);
        // You could implement a toast notification system here
    }
}

/**
 * Initialize application when DOM is ready
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing simulation app...');
    
    // Create global app instance
    window.simulationApp = new SimulationApp();
    
    // Initialize the application
    window.simulationApp.init();
});

/**
 * Handle page unload
 */
window.addEventListener('beforeunload', () => {
    if (window.simulationWS) {
        window.simulationWS.disconnect();
    }
=======
/**
 * Main Application Controller for Real-time Simulation
 */
class SimulationApp {
    constructor() {
        this.isSimulationRunning = false;
        this.isPaused = false;
        this.currentSpeed = 1.0;
        this.simulationStartTime = null;
        this.statistics = {};
        
        // UI elements
        this.elements = {};
        
        // Bind methods
        this.init = this.init.bind(this);
        this.setupEventHandlers = this.setupEventHandlers.bind(this);
        this.setupWebSocketHandlers = this.setupWebSocketHandlers.bind(this);
        this.updateUI = this.updateUI.bind(this);
    }

    /**
     * Initialize the application
     */
    async init() {
        console.log('Initializing Simulation App...');
        
        try {
            // Cache UI elements
            this.cacheUIElements();
            
            // Initialize map
            if (!window.simulationMap.initialize()) {
                throw new Error('Failed to initialize map');
            }
            
            // Setup event handlers
            this.setupEventHandlers();
            this.setupWebSocketHandlers();
            
            // Connect to WebSocket
            window.simulationWS.connect();
            
            // Initial UI state
            this.updateControlButtons();
            
            console.log('Simulation App initialized successfully');
            
        } catch (error) {
            console.error('Error initializing app:', error);
            this.showError('Failed to initialize application: ' + error.message);
        }
    }

    /**
     * Cache UI element references
     */
    cacheUIElements() {
        this.elements = {
            // Control buttons
            startBtn: document.getElementById('start-btn'),
            pauseBtn: document.getElementById('pause-btn'),
            resumeBtn: document.getElementById('resume-btn'),
            resetBtn: document.getElementById('reset-btn'),
            
            // Speed controls
            speedSlider: document.getElementById('speed-slider'),
            speedValue: document.getElementById('speed-value'),
            speedButtons: document.querySelectorAll('.speed-btn'),
            
            // Statistics
            statVehicles: document.getElementById('stat-vehicles'),
            statPendingOrders: document.getElementById('stat-pending-orders'),
            statActiveOrders: document.getElementById('stat-active-orders'),
            statCompletedOrders: document.getElementById('stat-completed-orders'),
            statRevenue: document.getElementById('stat-revenue'),
            statBattery: document.getElementById('stat-battery'),
            
            // Time display
            simulationTime: document.getElementById('simulation-time'),
            
            // Details panel
            detailsPanel: document.getElementById('details-panel'),
            detailsTitle: document.getElementById('details-title'),
            detailsContent: document.getElementById('details-content')
        };
    }

    /**
     * Setup UI event handlers
     */
    setupEventHandlers() {
        // Control buttons
        this.elements.startBtn?.addEventListener('click', () => {
            this.startSimulation();
        });

        this.elements.pauseBtn?.addEventListener('click', () => {
            this.pauseSimulation();
        });

        this.elements.resumeBtn?.addEventListener('click', () => {
            this.resumeSimulation();
        });

        this.elements.resetBtn?.addEventListener('click', () => {
            this.resetSimulation();
        });

        // Speed controls
        this.elements.speedSlider?.addEventListener('input', (e) => {
            this.setSpeed(parseFloat(e.target.value));
        });

        this.elements.speedButtons?.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const speed = parseFloat(e.target.dataset.speed);
                this.setSpeed(speed);
            });
        });

        // Window resize
        window.addEventListener('resize', () => {
            window.simulationMap.resize();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboard(e);
        });
    }

    /**
     * Setup WebSocket event handlers
     */
    setupWebSocketHandlers() {
        const ws = window.simulationWS;

        // Connection events
        ws.on('connected', () => {
            console.log('Connected to simulation server');
            this.updateControlButtons();
        });

        ws.on('disconnected', () => {
            console.log('Disconnected from simulation server');
            this.updateControlButtons();
        });

        ws.on('error', (error) => {
            console.error('WebSocket error:', error);
            this.showError('Connection error: ' + error.message);
        });

        ws.on('maxReconnectAttemptsReached', () => {
            this.showError('Failed to connect to simulation server after multiple attempts');
        });

        // Simulation data events
        ws.on('map_data', (data) => {
            this.handleMapData(data);
        });

        ws.on('control_state', (data) => {
            this.handleControlState(data);
        });

        ws.on('simulation_update', (data) => {
            this.handleSimulationUpdate(data);
        });

        ws.on('vehicle_details', (data) => {
            this.showVehicleDetails(data);
        });

        ws.on('order_details', (data) => {
            this.showOrderDetails(data);
        });
    }

    /**
     * Handle map initialization data
     */
    handleMapData(data) {
        console.log('Received map data');
        
        if (data.charging_stations) {
            window.simulationMap.updateChargingStations(data.charging_stations);
            window.simulationMap.updateMapBounds(data.charging_stations);
        }
    }

    /**
     * Handle control state updates
     */
    handleControlState(data) {
        this.isSimulationRunning = data.is_running;
        this.isPaused = data.is_paused;
        this.currentSpeed = data.speed_multiplier;
        
        this.updateControlButtons();
        this.updateSpeedControls();
    }

    /**
     * Handle simulation data updates
     */
    handleSimulationUpdate(data) {
        // Update map with vehicles and orders
        if (data.vehicles) {
            window.simulationMap.updateVehicles(data.vehicles);
        }
        
        if (data.orders) {
            window.simulationMap.updateOrders(data.orders);
        }

        // Update statistics
        if (data.statistics) {
            this.statistics = data.statistics;
            this.updateStatistics();
        }

        // Update simulation time
        if (data.simulation_time !== undefined) {
            this.updateSimulationTime(data.simulation_time);
        }
    }

    /**
     * Start simulation
     */
    startSimulation() {
        if (window.simulationWS.isConnected) {
            window.simulationWS.startSimulation();
            this.simulationStartTime = Date.now();
        } else {
            this.showError('Not connected to simulation server');
        }
    }

    /**
     * Pause simulation
     */
    pauseSimulation() {
        if (window.simulationWS.isConnected) {
            window.simulationWS.pauseSimulation();
        }
    }

    /**
     * Resume simulation
     */
    resumeSimulation() {
        if (window.simulationWS.isConnected) {
            window.simulationWS.resumeSimulation();
        }
    }

    /**
     * Reset simulation
     */
    resetSimulation() {
        if (confirm('Are you sure you want to reset the simulation? All progress will be lost.')) {
            if (window.simulationWS.isConnected) {
                window.simulationWS.resetSimulation();
                window.simulationMap.clearAllMarkers();
                this.resetStatistics();
                this.hideDetails();
            }
        }
    }

    /**
     * Set simulation speed
     */
    setSpeed(speed) {
        this.currentSpeed = speed;
        
        if (window.simulationWS.isConnected) {
            window.simulationWS.setSpeed(speed);
        }
        
        this.updateSpeedControls();
    }

    /**
     * Update control buttons state
     */
    updateControlButtons() {
        const connected = window.simulationWS.isConnected;
        
        if (this.elements.startBtn) {
            this.elements.startBtn.disabled = !connected || this.isSimulationRunning;
        }
        
        if (this.elements.pauseBtn) {
            this.elements.pauseBtn.disabled = !connected || !this.isSimulationRunning || this.isPaused;
        }
        
        if (this.elements.resumeBtn) {
            this.elements.resumeBtn.disabled = !connected || !this.isSimulationRunning || !this.isPaused;
        }
        
        if (this.elements.resetBtn) {
            this.elements.resetBtn.disabled = !connected;
        }
    }

    /**
     * Update speed controls
     */
    updateSpeedControls() {
        // Update slider
        if (this.elements.speedSlider) {
            this.elements.speedSlider.value = this.currentSpeed;
        }
        
        // Update speed display
        if (this.elements.speedValue) {
            this.elements.speedValue.textContent = this.currentSpeed.toFixed(1);
        }
        
        // Update speed buttons
        this.elements.speedButtons?.forEach(btn => {
            const btnSpeed = parseFloat(btn.dataset.speed);
            btn.classList.toggle('active', Math.abs(btnSpeed - this.currentSpeed) < 0.1);
        });
    }

    /**
     * Update statistics display
     */
    updateStatistics() {
        const stats = this.statistics;
        
        if (this.elements.statVehicles && stats.total_vehicles !== undefined) {
            this.elements.statVehicles.textContent = stats.total_vehicles;
        }
        
        if (this.elements.statPendingOrders && stats.pending_orders !== undefined) {
            this.elements.statPendingOrders.textContent = stats.pending_orders;
        }
        
        if (this.elements.statActiveOrders && stats.active_orders !== undefined) {
            this.elements.statActiveOrders.textContent = stats.active_orders;
        }
        
        if (this.elements.statCompletedOrders && stats.completed_orders !== undefined) {
            this.elements.statCompletedOrders.textContent = stats.completed_orders;
        }
        
        if (this.elements.statRevenue && stats.total_revenue !== undefined) {
            this.elements.statRevenue.textContent = '$' + Math.round(stats.total_revenue);
        }
        
        if (this.elements.statBattery && stats.average_battery !== undefined) {
            this.elements.statBattery.textContent = Math.round(stats.average_battery) + '%';
        }
    }

    /**
     * Reset statistics display
     */
    resetStatistics() {
        this.statistics = {};
        
        if (this.elements.statVehicles) this.elements.statVehicles.textContent = '0';
        if (this.elements.statPendingOrders) this.elements.statPendingOrders.textContent = '0';
        if (this.elements.statActiveOrders) this.elements.statActiveOrders.textContent = '0';
        if (this.elements.statCompletedOrders) this.elements.statCompletedOrders.textContent = '0';
        if (this.elements.statRevenue) this.elements.statRevenue.textContent = '$0';
        if (this.elements.statBattery) this.elements.statBattery.textContent = '0%';
        if (this.elements.simulationTime) this.elements.simulationTime.textContent = '00:00:00';
    }

    /**
     * Update simulation time display
     */
    updateSimulationTime(timeInSeconds) {
        if (this.elements.simulationTime) {
            const hours = Math.floor(timeInSeconds / 3600);
            const minutes = Math.floor((timeInSeconds % 3600) / 60);
            const seconds = Math.floor(timeInSeconds % 60);
            
            const timeString = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            this.elements.simulationTime.textContent = timeString;
        }
    }

    /**
     * Show vehicle details
     */
    showVehicleDetails(data) {
        if (!data.data) return;
        
        const vehicle = data.data;
        const content = `
            <div class="detail-row">
                <span class="detail-label">Vehicle ID:</span>
                <span>${data.vehicle_id}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Status:</span>
                <span>${vehicle.status}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Battery:</span>
                <span>${Math.round(vehicle.battery_percentage)}%</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Position:</span>
                <span>${vehicle.position[0].toFixed(4)}, ${vehicle.position[1].toFixed(4)}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Current Task:</span>
                <span>${vehicle.current_task || 'None'}</span>
            </div>
        `;
        
        this.showDetails('🚗 Vehicle Details', content);
    }

    /**
     * Show order details
     */
    showOrderDetails(data) {
        if (!data.data) return;
        
        const order = data.data;
        const content = `
            <div class="detail-row">
                <span class="detail-label">Order ID:</span>
                <span>${data.order_id}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Status:</span>
                <span>${order.status}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Pickup:</span>
                <span>${order.pickup_position[0].toFixed(4)}, ${order.pickup_position[1].toFixed(4)}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Dropoff:</span>
                <span>${order.dropoff_position[0].toFixed(4)}, ${order.dropoff_position[1].toFixed(4)}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Assigned Vehicle:</span>
                <span>${order.assigned_vehicle || 'Unassigned'}</span>
            </div>
        `;
        
        this.showDetails('📦 Order Details', content);
    }

    /**
     * Show details panel
     */
    showDetails(title, content) {
        if (this.elements.detailsPanel && this.elements.detailsTitle && this.elements.detailsContent) {
            this.elements.detailsTitle.textContent = title;
            this.elements.detailsContent.innerHTML = content;
            this.elements.detailsPanel.style.display = 'block';
        }
    }

    /**
     * Hide details panel
     */
    hideDetails() {
        if (this.elements.detailsPanel) {
            this.elements.detailsPanel.style.display = 'none';
        }
    }

    /**
     * Handle keyboard shortcuts
     */
    handleKeyboard(e) {
        // Only handle shortcuts when not typing in inputs
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            return;
        }

        switch (e.key) {
            case ' ':
                e.preventDefault();
                if (this.isSimulationRunning && !this.isPaused) {
                    this.pauseSimulation();
                } else if (this.isSimulationRunning && this.isPaused) {
                    this.resumeSimulation();
                } else {
                    this.startSimulation();
                }
                break;
            case 'r':
            case 'R':
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    this.resetSimulation();
                }
                break;
            case 'Escape':
                this.hideDetails();
                break;
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        console.error(message);
        // You could implement a toast notification system here
        alert('Error: ' + message);
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        console.log(message);
        // You could implement a toast notification system here
    }
}

/**
 * Initialize application when DOM is ready
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing simulation app...');
    
    // Create global app instance
    window.simulationApp = new SimulationApp();
    
    // Initialize the application
    window.simulationApp.init();
});

/**
 * Handle page unload
 */
window.addEventListener('beforeunload', () => {
    if (window.simulationWS) {
        window.simulationWS.disconnect();
    }
>>>>>>> b9bd6771fbd7f2273a429016a9b2c009e69bada8
}); 