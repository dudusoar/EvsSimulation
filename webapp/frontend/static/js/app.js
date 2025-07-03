/**
 * Main Application Logic
 */

class EVSimulationApp {
    constructor() {
        this.isSimulationCreated = false;
        this.isRunning = false;
        this.isPaused = false;
        this.hasEverStarted = false;  // 记录是否曾经开始过
        this.currentState = null;
        this.loadingModal = null; // Store modal instance
        
        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }
    
    async init() {
        console.log('Initializing EV Simulation App...');
        
        // Setup UI event handlers
        this.setupEventHandlers();
        
        // Initialize WebSocket connection
        simulationWS.connect();
        
        // Setup WebSocket message handlers
        this.setupWebSocketHandlers();
        
        // Fetch initial simulation status
        await this.fetchInitialStatus();
        
        // Initialize map and charts
        this.initializeComponents();
        
        console.log('App initialization complete');
    }
    
    setupEventHandlers() {
        // Simulation control buttons
        document.getElementById('createBtn').addEventListener('click', () => this.createSimulation());
        document.getElementById('startBtn').addEventListener('click', () => this.startSimulation());
        document.getElementById('pauseBtn').addEventListener('click', () => this.pauseSimulation());
        document.getElementById('stopBtn').addEventListener('click', () => this.stopSimulation());
        
        // Speed control
        const speedSlider = document.getElementById('speedSlider');
        speedSlider.addEventListener('input', (e) => this.updateSpeed(e.target.value));
        
        // Map center button
        document.getElementById('centerMapBtn').addEventListener('click', () => {
            if (window.simulationMap) {
                window.simulationMap.centerMap();
            }
        });
    }
    
    setupWebSocketHandlers() {
        // Handle simulation state updates
        simulationWS.on('simulation_state', (data) => {
            this.updateSimulationState(data);
        });
        
        // Handle control responses
        simulationWS.on('control_response', (data) => {
            this.handleControlResponse(data);
        });
        
        // Handle errors
        simulationWS.on('error', (data) => {
            this.showError(`WebSocket Error: ${data.error}`);
        });
    }
    
    async initializeComponents() {
        // Initialize map if not already done
        if (typeof window.simulationMap === 'undefined') {
            // Map will be initialized by map.js
            console.log('Waiting for map initialization...');
        }
        
        // Initialize charts if not already done
        if (typeof window.simulationCharts === 'undefined') {
            // Charts will be initialized by charts.js
            console.log('Waiting for charts initialization...');
        }
    }
    
    async createSimulation() {
        try {
            this.showLoading('Creating simulation...');
            
            const config = {
                location: document.getElementById('location').value,
                num_vehicles: parseInt(document.getElementById('numVehicles').value),
                num_charging_stations: 5, // Fixed for now
                simulation_duration: parseInt(document.getElementById('duration').value),
                vehicle_speed: 400, // Fixed for now
                order_generation_rate: 1000 // Fixed for now
            };
            
            const response = await fetch('/api/simulation/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.isSimulationCreated = true;
                this.hideLoading(); // 🎯 成功后立即隐藏loading
                this.updateButtonStates();
                this.showSuccess('Simulation created successfully!');
            } else {
                this.hideLoading(); // 🎯 失败后也立即隐藏loading
                this.showError(`Failed to create simulation: ${result.error || result.message}`);
            }
            
        } catch (error) {
            console.error('Error creating simulation:', error);
            this.hideLoading(); // 🎯 出错后也立即隐藏loading
            this.showError('Failed to create simulation. Please check connection.');
        }
    }
    
    startSimulation() {
        let ok;
        if (this.isPaused) {
            // Resume from pause
            ok = simulationWS.resumeSimulation();
            console.log('Resume command sent');
        } else if (this.isRunning) {
            // Restart simulation - send restart command
            ok = simulationWS.sendMessage('control', { command: 'restart' });
            console.log('Restart command sent');
        } else {
            // Initial start
            ok = simulationWS.startSimulation();
            console.log('Start command sent');
        }
        if (!ok) {
            this.showError('Failed to send command');
        }
    }
    
    pauseSimulation() {
        if (this.isPaused) {
            // Resume
            if (simulationWS.resumeSimulation()) {
                console.log('Resume command sent');
            } else {
                this.showError('Failed to send resume command');
            }
        } else {
            // Pause
            if (simulationWS.pauseSimulation()) {
                console.log('Pause command sent');
            } else {
                this.showError('Failed to send pause command');
            }
        }
    }
    
    stopSimulation() {
        if (simulationWS.stopSimulation()) {
            console.log('Stop command sent');
        } else {
            this.showError('Failed to send stop command');
        }
    }
    
    updateSpeed(value) {
        const speed = parseFloat(value);
        document.getElementById('speedDisplay').textContent = `${speed}x`;
        
        if (simulationWS.setSpeed(speed)) {
            console.log(`Speed set to ${speed}x`);
        }
    }
    
    updateSimulationState(state) {
        this.currentState = state;
        
        // Update statistics display
        this.updateStatistics(state.stats);
        
        // Update map
        if (window.simulationMap) {
            window.simulationMap.updateVehicles(state.vehicles);
            window.simulationMap.updateChargingStations(state.charging_stations);
            window.simulationMap.updateOrders(state.orders);
        }
        
        // Update charts
        if (window.simulationCharts) {
            window.simulationCharts.updateCharts(state.stats);
        }
    }
    
    updateStatistics(stats) {
        // Update time
        document.getElementById('currentTime').textContent = `${stats.current_time.toFixed(1)}s`;
        
        // Update revenue
        document.getElementById('totalRevenue').textContent = `$${stats.total_revenue.toFixed(2)}`;
        
        // Update orders
        document.getElementById('totalOrders').textContent = stats.total_orders_completed;
        
        // Update utilization rates
        document.getElementById('vehicleUtil').textContent = `${(stats.vehicle_utilization_rate * 100).toFixed(0)}%`;
        document.getElementById('chargingUtil').textContent = `${(stats.charging_utilization_rate * 100).toFixed(0)}%`;
    }
    
    handleControlResponse(data) {
        const { command, success, message } = data;
        
        if (success) {
            this.showSuccess(`${command.charAt(0).toUpperCase() + command.slice(1)} command executed successfully`);
            // Update internal flags based on command
            switch (command) {
                case 'start':
                case 'resume':
                case 'restart':
                    this.isRunning = true;
                    this.isPaused = false;
                    this.hasEverStarted = true;  // 标记已经开始过
                    break;
                case 'pause':
                    this.isRunning = true; // still running but paused flag
                    this.isPaused = true;
                    break;
                case 'stop':
                    this.isRunning = false;
                    this.isPaused = false;
                    this.isSimulationCreated = false;
                    this.hasEverStarted = false;  // 重置开始标志
                    break;
            }
            this.updateButtonStates();
        } else {
            this.showError(`${command.charAt(0).toUpperCase() + command.slice(1)} command failed: ${message}`);
        }
    }
    
    // ====== Button Helper Methods ======
    setButtonText(buttonElement, text) {
        // 根据按钮文本设置合适的图标
        let iconClass = '';
        
        switch(text.toLowerCase()) {
            case 'start':
                iconClass = 'fas fa-play';
                break;
            case 'restart':
                iconClass = 'fas fa-redo';
                break;
            case 'pause':
                iconClass = 'fas fa-pause';
                break;
            case 'resume':
                iconClass = 'fas fa-play';
                break;
            default:
                // 保持原有图标
                const existingIcon = buttonElement.querySelector('i');
                iconClass = existingIcon ? existingIcon.className : 'fas fa-circle';
        }
        
        buttonElement.innerHTML = `<i class="${iconClass}"></i> ${text}`;
    }
    
    updateButtonStates() {
        const createBtn = document.getElementById('createBtn');
        const startBtn = document.getElementById('startBtn');
        const pauseBtn = document.getElementById('pauseBtn');
        const stopBtn = document.getElementById('stopBtn');
        
        if (!this.isSimulationCreated) {
            createBtn.disabled = false;
            startBtn.disabled = true;
            pauseBtn.disabled = true;
            stopBtn.disabled = true;
            this.setButtonText(startBtn, 'Start');
            this.setButtonText(pauseBtn, 'Pause');
            return;
        }
        
        // Simulation created
        createBtn.disabled = true;
        stopBtn.disabled = false;
        
        if (this.isRunning && !this.isPaused) {
            // Running: Start becomes Restart, Pause available
            startBtn.disabled = false;
            this.setButtonText(startBtn, 'Restart');
            pauseBtn.disabled = false;
            this.setButtonText(pauseBtn, 'Pause');
        } else if (this.isPaused) {
            // Paused: 根据是否曾经开始过决定Start按钮文本
            startBtn.disabled = false;
            if (this.hasEverStarted) {
                this.setButtonText(startBtn, 'Restart');
            } else {
                this.setButtonText(startBtn, 'Start');
            }
            pauseBtn.disabled = false;
            this.setButtonText(pauseBtn, 'Resume');
        } else {
            // Created but not started yet
            startBtn.disabled = false;
            this.setButtonText(startBtn, 'Start');
            pauseBtn.disabled = true;
            this.setButtonText(pauseBtn, 'Pause');
        }
    }
    
    showLoading(message = 'Loading...') {
        const modalElement = document.getElementById('loadingModal');
        if (!modalElement) return;
        
        // 设置文本
        const loadingText = document.getElementById('loadingText');
        if (loadingText) {
            loadingText.textContent = message;
        }
        
        // 显示modal
        modalElement.style.display = 'block';
        modalElement.classList.add('show');
        
        // 添加backdrop和body样式
        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop fade show';
        document.body.appendChild(backdrop);
        document.body.classList.add('modal-open');
    }
    
    hideLoading() {
        const modalElement = document.getElementById('loadingModal');
        if (modalElement) {
            modalElement.style.display = 'none';
            modalElement.classList.remove('show');
        }
        
        // 移除backdrop
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) {
            backdrop.remove();
        }
        
        // 清理body状态
        document.body.classList.remove('modal-open');
    }
    
    showSuccess(message) {
        this.showToast(message, 'success');
    }
    
    showError(message) {
        this.showToast(message, 'danger');
    }
    
    showToast(message, type = 'info') {
        // Create toast container if it doesn't exist
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        container.appendChild(toast);
        
        // Show toast
        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: 5000
        });
        bsToast.show();
        
        // Remove toast after hiding
        toast.addEventListener('hidden.bs.toast', () => {
            container.removeChild(toast);
        });
    }
    
    async fetchInitialStatus() {
        try {
            const resp = await fetch('/api/simulation/status');
            const result = await resp.json();
            if (result.success) {
                const status = result.data;
                if (status.has_engine) {
                    this.isSimulationCreated = true;
                    this.isRunning = status.is_running;
                    this.isPaused = status.is_paused;
                    this.hasEverStarted = status.is_running || status.is_paused;
                    this.updateButtonStates();
                }
            }
        } catch (err) {
            console.warn('Unable to fetch initial simulation status', err);
        }
    }
}

// Initialize app when script loads
window.evApp = new EVSimulationApp(); 