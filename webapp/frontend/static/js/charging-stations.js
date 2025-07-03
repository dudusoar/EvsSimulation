/**
 * ChargingStationTracker Class
 * Handles charging station tracking and real-time updates
 */
class ChargingStationTracker {
    constructor() {
        this.chargingStations = [];
        this.filteredStations = [];
        this.vehicles = [];
        this.autoRefresh = true;
        this.refreshInterval = null;
        this.highlightStationId = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupWebSocket();
        this.loadStationData();
        this.startAutoRefresh();
        this.checkHighlightParameter();
    }
    
    setupEventListeners() {
        // Refresh button
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.loadStationData();
        });
        
        // Auto refresh toggle
        document.getElementById('autoRefreshBtn').addEventListener('click', () => {
            this.toggleAutoRefresh();
        });
        
        // Filters
        document.getElementById('availabilityFilter').addEventListener('change', () => {
            this.filterStations();
        });
        
        document.getElementById('stationSearch').addEventListener('input', () => {
            this.filterStations();
        });
        
        // Utilization range slider
        const utilizationRange = document.getElementById('utilizationRange');
        utilizationRange.addEventListener('input', () => {
            document.getElementById('utilizationValue').textContent = utilizationRange.value;
            this.filterStations();
        });
    }
    
    setupWebSocket() {
        if (window.simulationWS) {
            // Handle simulation state updates
            window.simulationWS.on('simulation_state', (data) => {
                this.handleWebSocketUpdate(data);
            });
        }
    }
    
    handleWebSocketUpdate(data) {
        if (data && data.charging_stations) {
            this.chargingStations = data.charging_stations || [];
            this.vehicles = data.vehicles || [];
            this.updateStatistics();
            this.filterStations();
        }
    }
    
    async loadStationData() {
        try {
            const response = await fetch('/api/simulation/state');
            const result = await response.json();
            
            if (result.success && result.data) {
                this.chargingStations = result.data.charging_stations || [];
                this.vehicles = result.data.vehicles || [];
                this.updateStatistics();
                this.filterStations();
            } else {
                console.warn('No simulation data available');
                this.showNoData();
            }
        } catch (error) {
            console.error('Error loading station data:', error);
            this.showError('Failed to load charging station data');
        }
    }
    
    updateStatistics() {
        const stats = this.calculateStatistics();
        
        document.getElementById('totalStations').textContent = stats.total;
        document.getElementById('availableSlots').textContent = stats.availableSlots;
        document.getElementById('occupiedSlots').textContent = stats.occupiedSlots;
        document.getElementById('utilizationRate').textContent = stats.avgUtilization + '%';
    }
    
    calculateStatistics() {
        const stats = {
            total: this.chargingStations.length,
            availableSlots: 0,
            occupiedSlots: 0,
            avgUtilization: 0
        };
        
        if (this.chargingStations.length > 0) {
            let totalUtilization = 0;
            
            this.chargingStations.forEach(station => {
                stats.availableSlots += station.available_slots;
                stats.occupiedSlots += (station.total_slots - station.available_slots);
                totalUtilization += station.utilization_rate * 100;
            });
            
            stats.avgUtilization = Math.round(totalUtilization / this.chargingStations.length);
        }
        
        return stats;
    }
    
    filterStations() {
        const availabilityFilter = document.getElementById('availabilityFilter').value;
        const stationSearch = document.getElementById('stationSearch').value.toLowerCase();
        const minUtilization = parseInt(document.getElementById('utilizationRange').value) / 100;
        
        this.filteredStations = this.chargingStations.filter(station => {
            // Availability filter
            if (availabilityFilter) {
                const availability = this.getStationAvailability(station);
                if (availability !== availabilityFilter) return false;
            }
            
            // Station ID search
            const stationId = station.station_id ? station.station_id.toString().toLowerCase() : '';
            if (stationSearch && !stationId.includes(stationSearch)) return false;
            
            // Utilization filter
            if (station.utilization_rate < minUtilization) return false;
            
            return true;
        });
        
        this.renderStationsTable();
    }
    
    getStationAvailability(station) {
        if (station.available_slots === station.total_slots) {
            return 'available';
        } else if (station.available_slots === 0) {
            return 'full';
        } else {
            return 'partial';
        }
    }
    
    renderStationsTable() {
        const tbody = document.getElementById('stationsTableBody');
        
        if (this.filteredStations.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center text-muted">
                        <i class="fas fa-search"></i> No charging stations found matching criteria
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = this.filteredStations.map(station => 
            this.renderStationRow(station)
        ).join('');
    }
    
    renderStationRow(station) {
        const statusInfo = this.getStatusInfo(station);
        const position = `${station.position[1].toFixed(4)}, ${station.position[0].toFixed(4)}`;
        const utilizationPercent = Math.round(station.utilization_rate * 100);
        const chargingVehicles = this.getChargingVehicles(station);
        
        return `
            <tr data-station-id="${station.station_id}">
                <td>
                    <strong>${station.station_id}</strong>
                </td>
                <td>
                    <span class="badge bg-${statusInfo.color}">
                        <i class="${statusInfo.icon}"></i> ${statusInfo.text}
                    </span>
                </td>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="me-2">
                            <span class="text-success">${station.available_slots}</span> / 
                            <span class="text-primary">${station.total_slots}</span>
                        </div>
                        <div class="progress" style="width: 60px; height: 8px;">
                            <div class="progress-bar bg-${this.getUtilizationColor(utilizationPercent)}" 
                                 style="width: ${utilizationPercent}%"></div>
                        </div>
                    </div>
                </td>
                <td>
                    <strong class="text-${this.getUtilizationColor(utilizationPercent)}">
                        ${utilizationPercent}%
                    </strong>
                </td>
                <td>
                    <small class="text-muted">${position}</small>
                </td>
                <td>
                    ${chargingVehicles.length > 0 ? 
                        chargingVehicles.map(v => 
                            `<a href="#" class="text-decoration-none me-1" onclick="stationTracker.showVehicleDetails('${v}')">
                                <span class="badge bg-secondary">${v}</span>
                            </a>`
                        ).join('') : 
                        '<span class="text-muted">None</span>'
                    }
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" 
                            onclick="stationTracker.showStationDetails('${station.station_id}')">
                        <i class="fas fa-info-circle"></i> Details
                    </button>
                </td>
            </tr>
        `;
    }
    
    getStatusInfo(station) {
        const availability = this.getStationAvailability(station);
        
        switch (availability) {
            case 'available':
                return { color: 'success', icon: 'fas fa-check-circle', text: 'Available' };
            case 'full':
                return { color: 'danger', icon: 'fas fa-times-circle', text: 'Full' };
            case 'partial':
                return { color: 'warning', icon: 'fas fa-exclamation-circle', text: 'Partial' };
            default:
                return { color: 'secondary', icon: 'fas fa-question', text: 'Unknown' };
        }
    }
    
    getUtilizationColor(percentage) {
        if (percentage >= 80) return 'danger';
        if (percentage >= 50) return 'warning';
        return 'success';
    }
    
    getChargingVehicles(station) {
        // Find vehicles that are charging at this station
        return this.vehicles
            .filter(vehicle => 
                (vehicle.status === 'charging' || vehicle.status === 'to_charging') &&
                this.isVehicleNearStation(vehicle, station)
            )
            .map(vehicle => vehicle.vehicle_id);
    }
    
    isVehicleNearStation(vehicle, station) {
        // Simple distance check (could be improved with actual distance calculation)
        const vehicleLat = vehicle.position[1];
        const vehicleLon = vehicle.position[0];
        const stationLat = station.position[1];
        const stationLon = station.position[0];
        
        const distance = Math.sqrt(
            Math.pow(vehicleLat - stationLat, 2) + 
            Math.pow(vehicleLon - stationLon, 2)
        );
        
        return distance < 0.001; // Very close proximity threshold
    }
    
    formatLocation(location) {
        if (!location) return 'N/A';
        if (Array.isArray(location)) {
            return `${location[0].toFixed(4)}, ${location[1].toFixed(4)}`;
        }
        return location.toString();
    }
    
    showStationDetails(stationId) {
        const station = this.chargingStations.find(s => s.station_id === stationId);
        if (!station) return;
        
        const statusInfo = this.getStatusInfo(station);
        const chargingVehicles = this.getChargingVehicles(station);
        const utilizationPercent = Math.round(station.utilization_rate * 100);
        
        const modalContent = `
            <div class="row">
                <div class="col-md-6">
                    <h6><i class="fas fa-info-circle"></i> Basic Information</h6>
                    <table class="table table-sm">
                        <tr>
                            <td><strong>Station ID:</strong></td>
                            <td>${station.station_id}</td>
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
                            <td><strong>Position:</strong></td>
                            <td>
                                Longitude: ${station.position[0].toFixed(6)}<br>
                                Latitude: ${station.position[1].toFixed(6)}
                            </td>
                        </tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <h6><i class="fas fa-chart-bar"></i> Capacity Information</h6>
                    <table class="table table-sm">
                        <tr>
                            <td><strong>Total Slots:</strong></td>
                            <td>${station.total_slots}</td>
                        </tr>
                        <tr>
                            <td><strong>Available Slots:</strong></td>
                            <td><span class="text-success">${station.available_slots}</span></td>
                        </tr>
                        <tr>
                            <td><strong>Occupied Slots:</strong></td>
                            <td><span class="text-warning">${station.total_slots - station.available_slots}</span></td>
                        </tr>
                        <tr>
                            <td><strong>Utilization Rate:</strong></td>
                            <td>
                                <div class="progress" style="height: 15px;">
                                    <div class="progress-bar bg-${this.getUtilizationColor(utilizationPercent)}" 
                                         style="width: ${utilizationPercent}%">
                                        ${utilizationPercent}%
                                    </div>
                                </div>
                            </td>
                        </tr>
                    </table>
                </div>
            </div>
            
            ${chargingVehicles.length > 0 ? `
                <hr>
                <div class="row">
                    <div class="col-12">
                        <h6><i class="fas fa-car"></i> Currently Charging Vehicles</h6>
                        <div class="d-flex flex-wrap gap-2">
                            ${chargingVehicles.map(vehicleId => `
                                <a href="#" class="text-decoration-none" onclick="stationTracker.showVehicleDetails('${vehicleId}')">
                                    <span class="badge bg-primary">
                                        <i class="fas fa-car"></i> ${vehicleId}
                                    </span>
                                </a>
                            `).join('')}
                        </div>
                    </div>
                </div>
            ` : `
                <hr>
                <div class="row">
                    <div class="col-12">
                        <h6><i class="fas fa-car"></i> Currently Charging Vehicles</h6>
                        <p class="text-muted">No vehicles currently charging at this station.</p>
                    </div>
                </div>
            `}
        `;
        
        document.getElementById('stationDetailContent').innerHTML = modalContent;
        new bootstrap.Modal(document.getElementById('stationDetailModal')).show();
    }
    
    showVehicleDetails(vehicleId) {
        // Open vehicle tracking page with specific vehicle
        window.open(`/vehicles?highlight=${vehicleId}`, '_blank');
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
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        if (this.autoRefresh) {
            this.refreshInterval = setInterval(() => {
                this.loadStationData();
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
        const tbody = document.getElementById('stationsTableBody');
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-muted">
                    <i class="fas fa-exclamation-triangle"></i> No simulation data available. Please create and start a simulation first.
                </td>
            </tr>
        `;
        
        // Clear statistics
        document.getElementById('totalStations').textContent = '0';
        document.getElementById('availableSlots').textContent = '0';
        document.getElementById('occupiedSlots').textContent = '0';
        document.getElementById('utilizationRate').textContent = '0%';
    }
    
    showError(message) {
        const tbody = document.getElementById('stationsTableBody');
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-danger">
                    <i class="fas fa-exclamation-triangle"></i> ${message}
                </td>
            </tr>
        `;
    }
    
    checkHighlightParameter() {
        const urlParams = new URLSearchParams(window.location.search);
        const highlightStation = urlParams.get('highlight');
        
        if (highlightStation) {
            // Set search filter to the highlighted station
            document.getElementById('stationSearch').value = highlightStation;
            this.highlightStationId = highlightStation;
            
            // Apply filters to show the highlighted station
            setTimeout(() => {
                this.filterStations();
                this.scrollToHighlightedStation();
            }, 1000); // Wait for data to load
        }
    }
    
    scrollToHighlightedStation() {
        if (this.highlightStationId) {
            const stationRow = document.querySelector(`[data-station-id="${this.highlightStationId}"]`);
            if (stationRow) {
                stationRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
                stationRow.classList.add('table-warning');
                
                // Remove highlight after 5 seconds
                setTimeout(() => {
                    stationRow.classList.remove('table-warning');
                }, 5000);
            }
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Setup WebSocket connection if not already done
    if (window.simulationWS) {
        window.simulationWS.connect();
    }
    
    // Initialize charging station tracker
    window.stationTracker = new ChargingStationTracker();
}); 