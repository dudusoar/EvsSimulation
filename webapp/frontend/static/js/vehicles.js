// Vehicle Management JavaScript
class VehicleManager {
    constructor() {
        this.vehicles = [];
        this.selectedVehicleId = null;
        this.wsClient = null;
        this.init();
    }

    init() {
        // Initialize WebSocket connection
        this.initWebSocket();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Initial data load
        this.requestVehicleData();
    }

    initWebSocket() {
        // Reuse the existing WebSocket utility
        if (typeof WebSocketClient !== 'undefined') {
            this.wsClient = new WebSocketClient();
            this.wsClient.onMessage = (data) => this.handleWebSocketMessage(data);
            this.wsClient.onConnect = () => {
                updateConnectionStatus(true);
                this.requestVehicleData();
            };
            this.wsClient.onDisconnect = () => {
                updateConnectionStatus(false);
            };
        }
    }

    setupEventListeners() {
        // Search functionality
        document.getElementById('searchVehicle').addEventListener('input', () => {
            this.filterVehicles();
        });

        // Status filter
        document.getElementById('statusFilter').addEventListener('change', () => {
            this.filterVehicles();
        });

        // Battery filter
        document.getElementById('batteryFilter').addEventListener('change', () => {
            this.filterVehicles();
        });

        // Auto refresh toggle
        document.getElementById('autoRefresh').addEventListener('change', (e) => {
            if (e.target.checked) {
                this.startAutoRefresh();
            } else {
                this.stopAutoRefresh();
            }
        });
    }

    handleWebSocketMessage(data) {
        if (data.type === 'simulation_data' && data.vehicles) {
            this.vehicles = data.vehicles;
            this.updateVehicleDisplay();
            this.updateStatistics();
        }
    }

    requestVehicleData() {
        if (this.wsClient && this.wsClient.isConnected()) {
            this.wsClient.send({
                type: 'get_status'
            });
        }
    }

    updateVehicleDisplay() {
        const tbody = document.getElementById('vehicleTableBody');
        
        if (!this.vehicles || this.vehicles.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-muted py-4">
                        <i class="fas fa-car fa-2x mb-2"></i><br>
                        No vehicles available. Start simulation first.
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = this.vehicles.map(vehicle => this.createVehicleRow(vehicle)).join('');
        
        // Re-select the previously selected vehicle
        if (this.selectedVehicleId) {
            const selectedRow = document.querySelector(`[data-vehicle-id="${this.selectedVehicleId}"]`);
            if (selectedRow) {
                selectedRow.classList.add('vehicle-selected');
                this.showVehicleDetails(this.selectedVehicleId);
            }
        }
    }

    createVehicleRow(vehicle) {
        const statusInfo = this.getStatusInfo(vehicle);
        const batteryInfo = this.getBatteryInfo(vehicle);
        const position = `(${vehicle.position.lat.toFixed(3)}, ${vehicle.position.lng.toFixed(3)})`;
        const currentTask = this.getCurrentTask(vehicle);

        return `
            <tr class="vehicle-row" data-vehicle-id="${vehicle.id}" onclick="vehicleManager.selectVehicle('${vehicle.id}')">
                <td><strong>${vehicle.id}</strong></td>
                <td>
                    <i class="${statusInfo.icon} ${statusInfo.class}"></i>
                    ${statusInfo.text}
                </td>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="progress flex-grow-1 me-2" style="height: 8px;">
                            <div class="progress-bar ${batteryInfo.class}" 
                                 style="width: ${vehicle.battery_percentage}%"></div>
                        </div>
                        <small class="${batteryInfo.textClass}">${vehicle.battery_percentage}%</small>
                    </div>
                </td>
                <td><small class="text-muted">${position}</small></td>
                <td>${currentTask}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="vehicleManager.locateVehicle('${vehicle.id}')">
                        <i class="fas fa-map-marker-alt"></i>
                    </button>
                </td>
            </tr>
        `;
    }

    getStatusInfo(vehicle) {
        const statusMap = {
            'idle': { 
                icon: 'fas fa-pause-circle', 
                class: 'status-idle', 
                text: 'Idle' 
            },
            'to_pickup': { 
                icon: 'fas fa-arrow-right', 
                class: 'status-to-pickup', 
                text: 'To Pickup' 
            },
            'with_passenger': { 
                icon: 'fas fa-user', 
                class: 'status-with-passenger', 
                text: 'With Passenger' 
            },
            'to_charging': { 
                icon: 'fas fa-battery-quarter', 
                class: 'status-to-charging', 
                text: 'To Charging' 
            },
            'charging': { 
                icon: 'fas fa-bolt', 
                class: 'status-charging', 
                text: 'Charging' 
            }
        };

        return statusMap[vehicle.status] || { 
            icon: 'fas fa-question-circle', 
            class: 'text-muted', 
            text: vehicle.status 
        };
    }

    getBatteryInfo(vehicle) {
        const battery = vehicle.battery_percentage;
        if (battery > 60) {
            return { class: 'bg-success', textClass: 'battery-high' };
        } else if (battery > 20) {
            return { class: 'bg-warning', textClass: 'battery-medium' };
        } else {
            return { class: 'bg-danger', textClass: 'battery-low' };
        }
    }

    getCurrentTask(vehicle) {
        if (vehicle.current_order_id) {
            return `<span class="badge bg-info">Order: ${vehicle.current_order_id}</span>`;
        } else if (vehicle.target_charging_station) {
            return `<span class="badge bg-purple">Station: ${vehicle.target_charging_station}</span>`;
        } else {
            return '<span class="text-muted">-</span>';
        }
    }

    selectVehicle(vehicleId) {
        // Remove previous selection
        document.querySelectorAll('.vehicle-selected').forEach(row => {
            row.classList.remove('vehicle-selected');
        });

        // Add selection to clicked row
        const row = document.querySelector(`[data-vehicle-id="${vehicleId}"]`);
        if (row) {
            row.classList.add('vehicle-selected');
            this.selectedVehicleId = vehicleId;
            this.showVehicleDetails(vehicleId);
        }
    }

    showVehicleDetails(vehicleId) {
        const vehicle = this.vehicles.find(v => v.id === vehicleId);
        if (!vehicle) return;

        const detailsPanel = document.getElementById('vehicleDetails');
        const statusInfo = this.getStatusInfo(vehicle);
        
        detailsPanel.innerHTML = `
            <div class="vehicle-details">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h6><i class="fas fa-car"></i> Vehicle ${vehicle.id}</h6>
                    <span class="badge ${statusInfo.class.replace('status-', 'bg-')}">${statusInfo.text}</span>
                </div>
                
                <div class="row mb-3">
                    <div class="col-6">
                        <strong>Battery Level</strong><br>
                        <div class="progress mb-1" style="height: 10px;">
                            <div class="progress-bar ${this.getBatteryInfo(vehicle).class}" 
                                 style="width: ${vehicle.battery_percentage}%"></div>
                        </div>
                        <small class="${this.getBatteryInfo(vehicle).textClass}">
                            ${vehicle.battery_percentage}% (${(vehicle.battery_kwh || 0).toFixed(1)} kWh)
                        </small>
                    </div>
                    <div class="col-6">
                        <strong>Speed</strong><br>
                        <span class="h5">${(vehicle.speed || 0).toFixed(1)}</span>
                        <small class="text-muted">km/h</small>
                    </div>
                </div>
                
                <div class="mb-3">
                    <strong>Position</strong><br>
                    <small class="text-muted">
                        Lat: ${vehicle.position.lat.toFixed(6)}<br>
                        Lng: ${vehicle.position.lng.toFixed(6)}
                    </small>
                </div>
                
                ${this.getTaskDetails(vehicle)}
                
                <div class="mb-3">
                    <strong>Performance Today</strong><br>
                    <small class="text-muted">
                        • Distance: ${(vehicle.distance_traveled || 0).toFixed(1)} km<br>
                        • Orders: ${vehicle.completed_orders || 0}<br>
                        • Runtime: ${this.formatRuntime(vehicle.runtime || 0)}
                    </small>
                </div>
                
                <div class="d-flex gap-2">
                    <button class="btn btn-sm btn-primary flex-grow-1" onclick="vehicleManager.locateVehicle('${vehicle.id}')">
                        <i class="fas fa-map-marker-alt"></i> Locate
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="vehicleManager.refreshVehicle('${vehicle.id}')">
                        <i class="fas fa-sync"></i>
                    </button>
                </div>
            </div>
        `;
    }

    getTaskDetails(vehicle) {
        if (vehicle.current_order_id) {
            return `
                <div class="mb-3">
                    <strong>Current Order</strong><br>
                    <span class="badge bg-info mb-1">${vehicle.current_order_id}</span><br>
                    <small class="text-muted">
                        ${vehicle.order_status ? `Status: ${vehicle.order_status}` : ''}<br>
                        ${vehicle.eta ? `ETA: ${vehicle.eta} min` : ''}
                    </small>
                </div>
            `;
        } else if (vehicle.target_charging_station) {
            return `
                <div class="mb-3">
                    <strong>Charging Task</strong><br>
                    <span class="badge bg-purple mb-1">Station: ${vehicle.target_charging_station}</span><br>
                    <small class="text-muted">
                        ${vehicle.charging_eta ? `ETA: ${vehicle.charging_eta} min` : ''}
                    </small>
                </div>
            `;
        } else {
            return `
                <div class="mb-3">
                    <strong>Current Task</strong><br>
                    <span class="text-muted">No active task</span>
                </div>
            `;
        }
    }

    formatRuntime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        return `${hours}h ${minutes}m`;
    }

    updateStatistics() {
        const stats = this.calculateStatistics();
        
        document.getElementById('vehicleCount').textContent = `${stats.total} Vehicles`;
        document.getElementById('idleCount').textContent = stats.idle;
        document.getElementById('activeCount').textContent = stats.active;
        document.getElementById('chargingCount').textContent = stats.charging;
        document.getElementById('lowBatteryCount').textContent = stats.lowBattery;
    }

    calculateStatistics() {
        if (!this.vehicles) {
            return { total: 0, idle: 0, active: 0, charging: 0, lowBattery: 0 };
        }

        const stats = {
            total: this.vehicles.length,
            idle: 0,
            active: 0,
            charging: 0,
            lowBattery: 0
        };

        this.vehicles.forEach(vehicle => {
            if (vehicle.status === 'idle') stats.idle++;
            if (['to_pickup', 'with_passenger'].includes(vehicle.status)) stats.active++;
            if (['charging', 'to_charging'].includes(vehicle.status)) stats.charging++;
            if (vehicle.battery_percentage < 20) stats.lowBattery++;
        });

        return stats;
    }

    filterVehicles() {
        const searchTerm = document.getElementById('searchVehicle').value.toLowerCase();
        const statusFilter = document.getElementById('statusFilter').value;
        const batteryFilter = document.getElementById('batteryFilter').value;

        const rows = document.querySelectorAll('.vehicle-row');
        
        rows.forEach(row => {
            const vehicleId = row.dataset.vehicleId;
            const vehicle = this.vehicles.find(v => v.id === vehicleId);
            
            if (!vehicle) {
                row.style.display = 'none';
                return;
            }

            let show = true;

            // Search filter
            if (searchTerm && !vehicle.id.toLowerCase().includes(searchTerm)) {
                show = false;
            }

            // Status filter
            if (statusFilter && vehicle.status !== statusFilter) {
                show = false;
            }

            // Battery filter
            if (batteryFilter) {
                const battery = vehicle.battery_percentage;
                if (batteryFilter === 'high' && battery <= 60) show = false;
                if (batteryFilter === 'medium' && (battery <= 20 || battery > 60)) show = false;
                if (batteryFilter === 'low' && battery >= 20) show = false;
            }

            row.style.display = show ? '' : 'none';
        });
    }

    locateVehicle(vehicleId) {
        // This would integrate with a map if available
        const vehicle = this.vehicles.find(v => v.id === vehicleId);
        if (vehicle) {
            alert(`Vehicle ${vehicleId} is located at:\nLat: ${vehicle.position.lat}\nLng: ${vehicle.position.lng}`);
        }
    }

    refreshVehicle(vehicleId) {
        this.requestVehicleData();
    }

    startAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
        }
        
        this.autoRefreshInterval = setInterval(() => {
            this.requestVehicleData();
        }, 2000); // Refresh every 2 seconds
    }

    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
    }
}

// Global functions
function clearFilters() {
    document.getElementById('searchVehicle').value = '';
    document.getElementById('statusFilter').value = '';
    document.getElementById('batteryFilter').value = '';
    vehicleManager.filterVehicles();
}

function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connectionStatus');
    if (connected) {
        statusElement.innerHTML = '<i class="fas fa-circle text-success"></i> Connected';
    } else {
        statusElement.innerHTML = '<i class="fas fa-circle text-danger"></i> Disconnected';
    }
}

// Initialize when page loads
let vehicleManager;
document.addEventListener('DOMContentLoaded', function() {
    vehicleManager = new VehicleManager();
    
    // Start auto refresh by default
    vehicleManager.startAutoRefresh();
}); 