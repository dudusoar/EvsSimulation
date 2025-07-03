/**
 * Map Control Module - Simplified Version
 */

class SimulationMap {
    constructor() {
        this.map = null;
        this.vehicleMarkers = new Map();
        this.chargingStationMarkers = new Map();
        this.orderMarkers = new Map();
        
        // West Lafayette coordinates
        this.defaultCenter = [40.4259, -86.9081];
        this.defaultZoom = 13;
        
        this.init();
    }
    
    init() {
        // Initialize Leaflet map
        this.map = L.map('map').setView(this.defaultCenter, this.defaultZoom);
        
        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(this.map);
        
        console.log('Map initialized');
    }
    
    updateVehicles(vehicles) {
        // Clear existing vehicle markers
        this.vehicleMarkers.forEach(marker => {
            this.map.removeLayer(marker);
        });
        this.vehicleMarkers.clear();
        
        // Add new vehicle markers
        vehicles.forEach(vehicle => {
            const marker = this.createVehicleMarker(vehicle);
            this.vehicleMarkers.set(vehicle.vehicle_id, marker);
            marker.addTo(this.map);
        });
    }
    
    updateChargingStations(stations) {
        // Clear existing station markers
        this.chargingStationMarkers.forEach(marker => {
            this.map.removeLayer(marker);
        });
        this.chargingStationMarkers.clear();
        
        // Add new station markers
        stations.forEach(station => {
            const marker = this.createChargingStationMarker(station);
            this.chargingStationMarkers.set(station.station_id, marker);
            marker.addTo(this.map);
        });
    }
    
    updateOrders(orders) {
        // Clear existing order markers
        this.orderMarkers.forEach(markers => {
            markers.pickup.remove();
            markers.dropoff.remove();
        });
        this.orderMarkers.clear();
        
        // Add new order markers
        orders.forEach(order => {
            const pickupMarker = this.createOrderMarker(order, 'pickup');
            const dropoffMarker = this.createOrderMarker(order, 'dropoff');
            
            this.orderMarkers.set(order.order_id, {
                pickup: pickupMarker,
                dropoff: dropoffMarker
            });
            
            pickupMarker.addTo(this.map);
            dropoffMarker.addTo(this.map);
        });
    }
    
    createVehicleMarker(vehicle) {
        const [lon, lat] = vehicle.position;
        
        // Choose icon color based on status
        const colors = {
            'idle': 'green',
            'to_pickup': 'blue',
            'with_passenger': 'orange',
            'to_charging': 'red',
            'charging': 'purple'
        };
        
        const color = colors[vehicle.status] || 'gray';
        
        const marker = L.circleMarker([lat, lon], {
            radius: 8,
            fillColor: color,
            color: '#000',
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8
        });
        
        // Add popup with vehicle info
        marker.bindPopup(`
            <div class="vehicle-popup">
                <h6><i class="fas fa-car"></i> ${vehicle.vehicle_id}</h6>
                <p><strong>Status:</strong> <span class="badge bg-primary">${vehicle.status}</span></p>
                <p><strong>Battery:</strong> ${vehicle.battery_percentage.toFixed(1)}%</p>
                <p><strong>Position:</strong> ${lat.toFixed(4)}, ${lon.toFixed(4)}</p>
            </div>
        `);
        
        return marker;
    }
    
    createChargingStationMarker(station) {
        const [lon, lat] = station.position;
        
        const marker = L.circleMarker([lat, lon], {
            radius: 12,
            fillColor: '#28a745',
            color: '#000',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        });
        
        // Add popup with station info
        marker.bindPopup(`
            <div>
                <h6><i class="fas fa-charging-station"></i> ${station.station_id}</h6>
                <p><strong>Available:</strong> ${station.available_slots}/${station.total_slots}</p>
                <p><strong>Utilization:</strong> ${(station.utilization_rate * 100).toFixed(1)}%</p>
            </div>
        `);
        
        return marker;
    }
    
    createOrderMarker(order, type) {
        const position = type === 'pickup' ? order.pickup_position : order.dropoff_position;
        const [lon, lat] = position;
        
        const colors = {
            'pickup': '#007bff',
            'dropoff': '#dc3545'
        };
        
        const icons = {
            'pickup': 'fas fa-map-marker-alt',
            'dropoff': 'fas fa-flag-checkered'
        };
        
        const marker = L.circleMarker([lat, lon], {
            radius: 6,
            fillColor: colors[type],
            color: '#000',
            weight: 1,
            opacity: 1,
            fillOpacity: 0.7
        });
        
        // Add popup with order info
        marker.bindPopup(`
            <div>
                <h6><i class="${icons[type]}"></i> ${type.charAt(0).toUpperCase() + type.slice(1)}</h6>
                <p><strong>Order:</strong> ${order.order_id}</p>
                <p><strong>Status:</strong> ${order.status}</p>
            </div>
        `);
        
        return marker;
    }
    
    centerMap() {
        this.map.setView(this.defaultCenter, this.defaultZoom);
    }
}

// Initialize map when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.simulationMap = new SimulationMap();
}); 