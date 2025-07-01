/**
 * Vehicle Tracking Page Logic
 */

class VehicleTracker {
    constructor() {
        this.vehicles = [];
        this.filteredVehicles = [];
        this.chargingStations = [];
        this.orders = [];
        this.autoRefresh = true;
        this.refreshInterval = null;
        
        this.init();
    }
    
    init() {
        console.log('Initializing Vehicle Tracker...');
        
        // Setup event handlers
        this.setupEventHandlers();
        
        // Setup WebSocket connection
        this.setupWebSocket();
        
        // Initial data fetch
        this.fetchVehicleData();
        
        // Start auto refresh
        this.startAutoRefresh();
        
        // Check for highlight parameter
        this.checkHighlightParameter();
    }
    
    setupEventHandlers() {
        // Manual refresh button
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.fetchVehicleData();
        });
        
        // Auto refresh toggle
        const autoRefreshBtn = document.getElementById('autoRefreshBtn');
        autoRefreshBtn.addEventListener('click', () => {
            this.toggleAutoRefresh();
        });
        
        // Filters
        document.getElementById('statusFilter').addEventListener('change', () => {
            this.applyFilters();
        });
        
        document.getElementById('vehicleSearch').addEventListener('input', () => {
            this.applyFilters();
        });
    }
    
    setupWebSocket() {
        if (window.simulationWS) {
            // Handle simulation state updates
            window.simulationWS.on('simulation_state', (data) => {
                this.updateData(data);
            });
        }
    }
    
    async fetchVehicleData() {
        try {
            const response = await fetch('/api/simulation/state');
            const result = await response.json();
            
            if (result.success && result.data) {
                this.updateData(result.data);
            } else {
                console.warn('No simulation data available');
                this.showNoData();
            }
        } catch (error) {
            console.error('Error fetching vehicle data:', error);
            this.showError('Failed to load vehicle data');
        }
    }
    
    updateData(data) {
        this.vehicles = data.vehicles || [];
        this.chargingStations = data.charging_stations || [];
        this.orders = data.orders || [];
        
        this.updateStatistics();
        this.applyFilters();
    }
    
    updateStatistics() {
        const statusCounts = this.getStatusCounts();
        
        document.getElementById('totalVehicles').textContent = this.vehicles.length;
        document.getElementById('idleVehicles').textContent = statusCounts.idle;
        document.getElementById('busyVehicles').textContent = 
            statusCounts.to_pickup + statusCounts.with_passenger;
        document.getElementById('chargingVehicles').textContent = 
            statusCounts.charging + statusCounts.to_charging;
    }
    
    getStatusCounts() {
        const counts = {
            idle: 0,
            to_pickup: 0,
            with_passenger: 0,
            to_charging: 0,
            charging: 0
        };
        
        this.vehicles.forEach(vehicle => {
            if (counts.hasOwnProperty(vehicle.status)) {
                counts[vehicle.status]++;
            }
        });
        
        return counts;
    }
    
    applyFilters() {
        const statusFilter = document.getElementById('statusFilter').value;
        const searchTerm = document.getElementById('vehicleSearch').value.toLowerCase();
        
        this.filteredVehicles = this.vehicles.filter(vehicle => {
            const matchesStatus = !statusFilter || vehicle.status === statusFilter;
            const matchesSearch = !searchTerm || 
                vehicle.vehicle_id.toLowerCase().includes(searchTerm);
            
            return matchesStatus && matchesSearch;
        });
        
        this.renderVehicleTable();
    }
    
    renderVehicleTable() {
        const tbody = document.getElementById('vehiclesTableBody');
        
        if (this.filteredVehicles.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center text-muted">
                        <i class="fas fa-search"></i> No vehicles found matching criteria
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = this.filteredVehicles.map(vehicle => 
            this.renderVehicleRow(vehicle)
        ).join('');
    }
    
    renderVehicleRow(vehicle) {
        const statusInfo = this.getStatusInfo(vehicle.status);
        const position = `${vehicle.position[1].toFixed(4)}, ${vehicle.position[0].toFixed(4)}`;
        const batteryColor = this.getBatteryColor(vehicle.battery_percentage);
        const currentOrder = this.getCurrentOrder(vehicle);
        const chargingStation = this.getChargingStation(vehicle);
        const lastUpdate = new Date().toLocaleTimeString();
        
        return `
            <tr data-vehicle-id="${vehicle.vehicle_id}">
                <td>
                    <strong>${vehicle.vehicle_id}</strong>
                </td>
                <td>
                    <span class="badge bg-${statusInfo.color}">
                        <i class="${statusInfo.icon}"></i> ${statusInfo.text}
                    </span>
                </td>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="progress me-2" style="width: 60px; height: 8px;">
                            <div class="progress-bar bg-${batteryColor}" 
                                 style="width: ${vehicle.battery_percentage}%"></div>
                        </div>
                        <small>${vehicle.battery_percentage.toFixed(1)}%</small>
                    </div>
                </td>
                <td>
                    <small class="text-muted">${position}</small>
                </td>
                <td>
                    ${currentOrder || '<span class="text-muted">-</span>'}
                </td>
                <td>
                    ${chargingStation || '<span class="text-muted">-</span>'}
                </td>
                <td>
                    <small class="text-muted">${lastUpdate}</small>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" 
                            onclick="vehicleTracker.showVehicleDetail('${vehicle.vehicle_id}')">
                        <i class="fas fa-info-circle"></i> Details
                    </button>
                </td>
            </tr>
        `;
    }
    
    getStatusInfo(status) {
        const statusMap = {
            'idle': { color: 'success', icon: 'fas fa-check-circle', text: 'Idle' },
            'to_pickup': { color: 'primary', icon: 'fas fa-arrow-right', text: 'To Pickup' },
            'with_passenger': { color: 'warning', icon: 'fas fa-user', text: 'With Passenger' },
            'to_charging': { color: 'danger', icon: 'fas fa-arrow-right', text: 'To Charging' },
            'charging': { color: 'info', icon: 'fas fa-charging-station', text: 'Charging' }
        };
        
        return statusMap[status] || { color: 'secondary', icon: 'fas fa-question', text: 'Unknown' };
    }
    
    getBatteryColor(percentage) {
        if (percentage > 60) return 'success';
        if (percentage > 30) return 'warning';
        return 'danger';
    }
    
    getCurrentOrder(vehicle) {
        if (!vehicle.current_order_id) return null;
        
        const order = this.orders.find(o => o.order_id === vehicle.current_order_id);
        if (!order) return `<span class="text-primary">Order ${vehicle.current_order_id}</span>`;
        
        return `
            <span class="text-primary">Order ${order.order_id}</span><br>
            <small class="text-muted">${order.status}</small>
        `;
    }
    
    getChargingStation(vehicle) {
        if (vehicle.status !== 'charging' && vehicle.status !== 'to_charging') {
            return null;
        }
        
        // Simple logic: find nearest charging station as target
        if (this.chargingStations.length > 0) {
            const nearestStation = this.findNearestChargingStation(vehicle.position);
            if (nearestStation) {
                return `
                    <a href="#" class="text-decoration-none" onclick="vehicleTracker.showChargingStationDetails('${nearestStation.station_id}')">
                        <span class="text-info">${nearestStation.station_id}</span>
                    </a><br>
                    <small class="text-muted">${nearestStation.available_slots}/${nearestStation.total_slots} available</small>
                `;
            }
        }
        
        return `<span class="text-muted">Finding station...</span>`;
    }
    
    findNearestChargingStation(vehiclePosition) {
        if (this.chargingStations.length === 0) return null;
        
        let nearest = this.chargingStations[0];
        let minDistance = this.calculateDistance(vehiclePosition, nearest.position);
        
        this.chargingStations.forEach(station => {
            const distance = this.calculateDistance(vehiclePosition, station.position);
            if (distance < minDistance) {
                minDistance = distance;
                nearest = station;
            }
        });
        
        return nearest;
    }
    
    calculateDistance(pos1, pos2) {
        const [lon1, lat1] = pos1;
        const [lon2, lat2] = pos2;
        return Math.sqrt(Math.pow(lon2 - lon1, 2) + Math.pow(lat2 - lat1, 2));
    }
    
    showVehicleDetail(vehicleId) {
        const vehicle = this.vehicles.find(v => v.vehicle_id === vehicleId);
        if (!vehicle) return;
        
        const modalContent = document.getElementById('vehicleDetailContent');
        modalContent.innerHTML = this.renderVehicleDetailContent(vehicle);
        
        const modal = new bootstrap.Modal(document.getElementById('vehicleDetailModal'));
        modal.show();
    }
    
    renderVehicleDetailContent(vehicle) {
        const statusInfo = this.getStatusInfo(vehicle.status);
        const currentOrder = this.getCurrentOrder(vehicle);
        const chargingStation = this.getChargingStation(vehicle);
        
        return `
            <div class="row">
                <div class="col-md-6">
                    <h6><i class="fas fa-info-circle"></i> Basic Information</h6>
                    <table class="table table-sm">
                        <tr>
                            <td><strong>Vehicle ID:</strong></td>
                            <td>${vehicle.vehicle_id}</td>
                        </tr>
                        <tr>
                            <td><strong>Status:</strong></td>
                            <td>
                                <span class="badge bg-${statusInfo.color}">
                                    <i class="${statusInfo.icon}"></i> ${statusInfo.text}
                                </span>
                            </td>
                        </tr>
                        <tr>
                            <td><strong>Battery:</strong></td>
                            <td>
                                <div class="progress" style="height: 12px;">
                                    <div class="progress-bar bg-${this.getBatteryColor(vehicle.battery_percentage)}" 
                                         style="width: ${vehicle.battery_percentage}%">
                                        ${vehicle.battery_percentage.toFixed(1)}%
                                    </div>
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <td><strong>Position:</strong></td>
                            <td>
                                Longitude: ${vehicle.position[0].toFixed(6)}<br>
                                Latitude: ${vehicle.position[1].toFixed(6)}
                            </td>
                        </tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <h6><i class="fas fa-tasks"></i> Task Information</h6>
                    <table class="table table-sm">
                        <tr>
                            <td><strong>Current Order:</strong></td>
                            <td>${currentOrder || '<span class="text-muted">None</span>'}</td>
                        </tr>
                        <tr>
                            <td><strong>Charging Station:</strong></td>
                            <td>${chargingStation || '<span class="text-muted">None</span>'}</td>
                        </tr>
                        <tr>
                            <td><strong>Destination:</strong></td>
                            <td>
                                ${vehicle.destination ? 
                                    `${vehicle.destination[1].toFixed(4)}, ${vehicle.destination[0].toFixed(4)}` : 
                                    '<span class="text-muted">None</span>'
                                }
                            </td>
                        </tr>
                    </table>
                </div>
            </div>
            
            <div class="mt-3">
                <h6><i class="fas fa-chart-line"></i> Real-time Status</h6>
                <div class="alert alert-info">
                    <i class="fas fa-info-circle"></i> 
                    This vehicle was last updated at ${new Date().toLocaleString()}
                </div>
            </div>
        `;
    }
    
    toggleAutoRefresh() {
        this.autoRefresh = !this.autoRefresh;
        const btn = document.getElementById('autoRefreshBtn');
        
        if (this.autoRefresh) {
            btn.innerHTML = '<i class="fas fa-pause"></i> Pause Refresh';
            btn.className = 'btn btn-outline-warning';
            this.startAutoRefresh();
        } else {
            btn.innerHTML = '<i class="fas fa-play"></i> Auto Refresh';
            btn.className = 'btn btn-outline-secondary';
            this.stopAutoRefresh();
        }
    }
    
    startAutoRefresh() {
        if (this.autoRefresh && !this.refreshInterval) {
            this.refreshInterval = setInterval(() => {
                this.fetchVehicleData();
            }, 3000); // Refresh every 3 seconds
        }
    }
    
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
    
    showNoData() {
        const tbody = document.getElementById('vehiclesTableBody');
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-muted">
                    <i class="fas fa-exclamation-triangle"></i> No simulation data available. Please create and start a simulation first.
                </td>
            </tr>
        `;
        
        // Clear statistics
        document.getElementById('totalVehicles').textContent = '0';
        document.getElementById('idleVehicles').textContent = '0';
        document.getElementById('busyVehicles').textContent = '0';
        document.getElementById('chargingVehicles').textContent = '0';
    }
    
    showError(message) {
        const tbody = document.getElementById('vehiclesTableBody');
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-danger">
                    <i class="fas fa-exclamation-circle"></i> ${message}
                </td>
            </tr>
        `;
    }
    
    checkHighlightParameter() {
        const urlParams = new URLSearchParams(window.location.search);
        const highlightVehicle = urlParams.get('highlight');
        
        if (highlightVehicle) {
            // Set search filter to the highlighted vehicle
            document.getElementById('vehicleSearch').value = highlightVehicle;
            this.highlightVehicleId = highlightVehicle;
            
            // Apply filters to show the highlighted vehicle
            setTimeout(() => {
                this.applyFilters();
                this.scrollToHighlightedVehicle();
            }, 1000); // Wait for data to load
        }
    }
    
    scrollToHighlightedVehicle() {
        if (this.highlightVehicleId) {
            const vehicleRow = document.querySelector(`[data-vehicle-id="${this.highlightVehicleId}"]`);
            if (vehicleRow) {
                vehicleRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
                vehicleRow.classList.add('table-warning');
                
                // Remove highlight after 5 seconds
                setTimeout(() => {
                    vehicleRow.classList.remove('table-warning');
                }, 5000);
            }
        }
    }
    
    showChargingStationDetails(stationId) {
        // Open charging station page with specific station highlighted
        window.open(`/charging-stations?highlight=${stationId}`, '_blank');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Setup WebSocket connection if not already done
    if (window.simulationWS) {
        window.simulationWS.connect();
    }
    
    // Initialize vehicle tracker
    window.vehicleTracker = new VehicleTracker();
}); 