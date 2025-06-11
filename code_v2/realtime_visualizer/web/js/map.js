<<<<<<< HEAD
/**
 * Map Manager for Real-time Simulation Visualization
 */
class SimulationMap {
    constructor() {
        this.map = null;
        this.vehicleMarkers = new Map();
        this.orderMarkers = new Map();
        this.chargingStationMarkers = new Map();
        this.isInitialized = false;
        this.defaultCenter = [40.4237, -86.9212]; // West Lafayette, IN
        this.defaultZoom = 13;
        
        // Vehicle status colors
        this.vehicleColors = {
            'idle': '#22c55e',      // Green - Available
            'pickup': '#f59e0b',    // Orange - Going to pickup
            'dropoff': '#3b82f6',   // Blue - In service
            'charging': '#ef4444'   // Red - Charging
        };
        
        // Order status colors
        this.orderColors = {
            'pending': '#fbbf24',   // Yellow - Waiting
            'active': '#3b82f6',    // Blue - Active
            'completed': '#22c55e'  // Green - Completed
        };
    }

    /**
     * Initialize the map
     */
    initialize() {
        try {
            // Create map instance
            this.map = L.map('map', {
                center: this.defaultCenter,
                zoom: this.defaultZoom,
                zoomControl: true,
                attributionControl: true
            });

            // Add tile layer
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 19
            }).addTo(this.map);

            // Add custom controls
            this.addCustomControls();

            this.isInitialized = true;
            console.log('Map initialized successfully');
            
            return true;
        } catch (error) {
            console.error('Error initializing map:', error);
            return false;
        }
    }

    /**
     * Add custom map controls
     */
    addCustomControls() {
        // Legend control
        const legend = L.control({ position: 'bottomleft' });
        legend.onAdd = function() {
            const div = L.DomUtil.create('div', 'map-legend');
            div.innerHTML = `
                <div class="legend-content">
                    <h4>Map Legend</h4>
                    <div><span class="legend-dot" style="background: #22c55e;"></span> Available Vehicle</div>
                    <div><span class="legend-dot" style="background: #f59e0b;"></span> Pickup Vehicle</div>
                    <div><span class="legend-dot" style="background: #3b82f6;"></span> In Service</div>
                    <div><span class="legend-dot" style="background: #ef4444;"></span> Charging</div>
                    <div><span class="legend-square" style="background: #fbbf24;"></span> Pending Order</div>
                    <div><span class="legend-square" style="background: #3b82f6;"></span> Active Order</div>
                </div>
            `;
            return div;
        };
        legend.addTo(this.map);

        // Add legend styles
        const style = document.createElement('style');
        style.textContent = `
            .map-legend {
                background: rgba(255, 255, 255, 0.9);
                backdrop-filter: blur(10px);
                border-radius: 8px;
                padding: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                font-size: 12px;
            }
            .map-legend h4 {
                margin: 0 0 8px 0;
                color: #374151;
            }
            .map-legend div {
                display: flex;
                align-items: center;
                margin: 4px 0;
                color: #4b5563;
            }
            .legend-dot, .legend-square {
                width: 12px;
                height: 12px;
                margin-right: 8px;
                border: 2px solid white;
                box-shadow: 0 1px 3px rgba(0,0,0,0.3);
            }
            .legend-dot {
                border-radius: 50%;
            }
            .legend-square {
                border-radius: 2px;
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Update map bounds based on charging stations
     */
    updateMapBounds(chargingStations) {
        if (!this.isInitialized || !chargingStations || chargingStations.length === 0) {
            return;
        }

        try {
            const bounds = L.latLngBounds();
            chargingStations.forEach(station => {
                if (station.position && station.position.length >= 2) {
                    bounds.extend([station.position[0], station.position[1]]);
                }
            });

            if (bounds.isValid()) {
                this.map.fitBounds(bounds, { padding: [50, 50] });
            }
        } catch (error) {
            console.error('Error updating map bounds:', error);
        }
    }

    /**
     * Add or update charging stations
     */
    updateChargingStations(stations) {
        if (!this.isInitialized || !stations) return;

        try {
            // Clear existing charging station markers
            this.chargingStationMarkers.forEach(marker => {
                this.map.removeLayer(marker);
            });
            this.chargingStationMarkers.clear();

            // Add new charging station markers
            stations.forEach(station => {
                if (station.position && station.position.length >= 2) {
                    const marker = L.circleMarker([station.position[0], station.position[1]], {
                        radius: 8,
                        fillColor: '#8b5cf6',
                        color: 'white',
                        weight: 2,
                        opacity: 1,
                        fillOpacity: 0.8
                    }).addTo(this.map);

                    // Add popup
                    marker.bindPopup(`
                        <div class="popup-content">
                            <div class="popup-title">⚡ Charging Station</div>
                            <div class="popup-info">
                                <div class="popup-row">
                                    <span class="popup-label">ID:</span>
                                    <span class="popup-value">${station.id}</span>
                                </div>
                                <div class="popup-row">
                                    <span class="popup-label">Capacity:</span>
                                    <span class="popup-value">${station.capacity}</span>
                                </div>
                            </div>
                        </div>
                    `);

                    this.chargingStationMarkers.set(station.id, marker);
                }
            });

            console.log(`Updated ${stations.length} charging stations`);
        } catch (error) {
            console.error('Error updating charging stations:', error);
        }
    }

    /**
     * Update vehicles on the map
     */
    updateVehicles(vehicles) {
        if (!this.isInitialized || !vehicles) return;

        try {
            // Keep track of current vehicle IDs
            const currentVehicleIds = new Set(vehicles.map(v => v.id));

            // Remove markers for vehicles that no longer exist
            this.vehicleMarkers.forEach((marker, vehicleId) => {
                if (!currentVehicleIds.has(vehicleId)) {
                    this.map.removeLayer(marker);
                    this.vehicleMarkers.delete(vehicleId);
                }
            });

            // Update or create markers for current vehicles
            vehicles.forEach(vehicle => {
                if (vehicle.position && vehicle.position.length >= 2) {
                    this.updateVehicleMarker(vehicle);
                }
            });

            console.log(`Updated ${vehicles.length} vehicles`);
        } catch (error) {
            console.error('Error updating vehicles:', error);
        }
    }

    /**
     * Update or create a single vehicle marker
     */
    updateVehicleMarker(vehicle) {
        const position = [vehicle.position[0], vehicle.position[1]];
        const color = this.vehicleColors[vehicle.status] || '#6b7280';

        if (this.vehicleMarkers.has(vehicle.id)) {
            // Update existing marker
            const marker = this.vehicleMarkers.get(vehicle.id);
            marker.setLatLng(position);
            marker.setStyle({ fillColor: color });
        } else {
            // Create new marker
            const marker = L.circleMarker(position, {
                radius: 6,
                fillColor: color,
                color: 'white',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.9
            }).addTo(this.map);

            // Add click event for details
            marker.on('click', () => {
                window.simulationWS.getVehicleDetails(vehicle.id);
            });

            // Add popup
            this.updateVehiclePopup(marker, vehicle);

            this.vehicleMarkers.set(vehicle.id, marker);
        }

        // Update popup content
        const marker = this.vehicleMarkers.get(vehicle.id);
        this.updateVehiclePopup(marker, vehicle);
    }

    /**
     * Update vehicle popup content
     */
    updateVehiclePopup(marker, vehicle) {
        const statusText = vehicle.status.charAt(0).toUpperCase() + vehicle.status.slice(1);
        const batteryColor = vehicle.battery_percentage > 50 ? '#22c55e' : 
                           vehicle.battery_percentage > 20 ? '#f59e0b' : '#ef4444';

        marker.bindPopup(`
            <div class="popup-content">
                <div class="popup-title">🚗 Vehicle ${vehicle.id}</div>
                <div class="popup-info">
                    <div class="popup-row">
                        <span class="popup-label">Status:</span>
                        <span class="popup-value">${statusText}</span>
                    </div>
                    <div class="popup-row">
                        <span class="popup-label">Battery:</span>
                        <span class="popup-value" style="color: ${batteryColor}">
                            ${Math.round(vehicle.battery_percentage)}%
                        </span>
                    </div>
                    <div class="popup-row">
                        <span class="popup-label">Passenger:</span>
                        <span class="popup-value">${vehicle.has_passenger ? 'Yes' : 'No'}</span>
                    </div>
                </div>
                <div style="margin-top: 8px; font-size: 11px; color: #6b7280;">
                    Click for detailed information
                </div>
            </div>
        `);
    }

    /**
     * Update orders on the map
     */
    updateOrders(orders) {
        if (!this.isInitialized || !orders) return;

        try {
            // Keep track of current order IDs
            const currentOrderIds = new Set(orders.map(o => o.id));

            // Remove markers for orders that no longer exist
            this.orderMarkers.forEach((markers, orderId) => {
                if (!currentOrderIds.has(orderId)) {
                    markers.forEach(marker => this.map.removeLayer(marker));
                    this.orderMarkers.delete(orderId);
                }
            });

            // Update or create markers for current orders
            orders.forEach(order => {
                if (order.pickup_position && order.pickup_position.length >= 2) {
                    this.updateOrderMarker(order);
                }
            });

            console.log(`Updated ${orders.length} orders`);
        } catch (error) {
            console.error('Error updating orders:', error);
        }
    }

    /**
     * Update or create order markers (pickup and dropoff)
     */
    updateOrderMarker(order) {
        const color = this.orderColors[order.status] || '#6b7280';

        // Remove existing markers for this order
        if (this.orderMarkers.has(order.id)) {
            this.orderMarkers.get(order.id).forEach(marker => {
                this.map.removeLayer(marker);
            });
        }

        const markers = [];

        // Create pickup marker
        if (order.pickup_position && order.pickup_position.length >= 2) {
            const pickupMarker = L.marker([order.pickup_position[0], order.pickup_position[1]], {
                icon: L.divIcon({
                    className: 'order-pickup-marker',
                    html: `<div style="background: ${color}; width: 12px; height: 12px; border: 2px solid white; border-radius: 2px; box-shadow: 0 1px 3px rgba(0,0,0,0.3);"></div>`,
                    iconSize: [16, 16],
                    iconAnchor: [8, 8]
                })
            }).addTo(this.map);

            // Add click event
            pickupMarker.on('click', () => {
                window.simulationWS.getOrderDetails(order.id);
            });

            markers.push(pickupMarker);
        }

        // Create dropoff marker (if different from pickup)
        if (order.dropoff_position && order.dropoff_position.length >= 2 &&
            (order.pickup_position[0] !== order.dropoff_position[0] || 
             order.pickup_position[1] !== order.dropoff_position[1])) {
            
            const dropoffMarker = L.marker([order.dropoff_position[0], order.dropoff_position[1]], {
                icon: L.divIcon({
                    className: 'order-dropoff-marker',
                    html: `<div style="background: ${color}; width: 10px; height: 10px; border: 2px solid white; border-radius: 50%; box-shadow: 0 1px 3px rgba(0,0,0,0.3);"></div>`,
                    iconSize: [14, 14],
                    iconAnchor: [7, 7]
                })
            }).addTo(this.map);

            markers.push(dropoffMarker);
        }

        // Add popup to the first marker
        if (markers.length > 0) {
            const statusText = order.status.charAt(0).toUpperCase() + order.status.slice(1);
            markers[0].bindPopup(`
                <div class="popup-content">
                    <div class="popup-title">📦 Order ${order.id}</div>
                    <div class="popup-info">
                        <div class="popup-row">
                            <span class="popup-label">Status:</span>
                            <span class="popup-value">${statusText}</span>
                        </div>
                        <div class="popup-row">
                            <span class="popup-label">Vehicle:</span>
                            <span class="popup-value">${order.assigned_vehicle || 'Unassigned'}</span>
                        </div>
                    </div>
                    <div style="margin-top: 8px; font-size: 11px; color: #6b7280;">
                        Click for detailed information
                    </div>
                </div>
            `);
        }

        this.orderMarkers.set(order.id, markers);
    }

    /**
     * Clear all markers
     */
    clearAllMarkers() {
        // Clear vehicles
        this.vehicleMarkers.forEach(marker => {
            this.map.removeLayer(marker);
        });
        this.vehicleMarkers.clear();

        // Clear orders
        this.orderMarkers.forEach(markers => {
            markers.forEach(marker => this.map.removeLayer(marker));
        });
        this.orderMarkers.clear();

        // Clear charging stations
        this.chargingStationMarkers.forEach(marker => {
            this.map.removeLayer(marker);
        });
        this.chargingStationMarkers.clear();

        console.log('All markers cleared');
    }

    /**
     * Get map instance
     */
    getMap() {
        return this.map;
    }

    /**
     * Check if map is initialized
     */
    isMapInitialized() {
        return this.isInitialized;
    }

    /**
     * Resize map (call when container size changes)
     */
    resize() {
        if (this.isInitialized && this.map) {
            setTimeout(() => {
                this.map.invalidateSize();
            }, 100);
        }
    }
}

// Create global map instance
=======
/**
 * Map Manager for Real-time Simulation Visualization
 */
class SimulationMap {
    constructor() {
        this.map = null;
        this.vehicleMarkers = new Map();
        this.orderMarkers = new Map();
        this.chargingStationMarkers = new Map();
        this.isInitialized = false;
        this.defaultCenter = [40.4237, -86.9212]; // West Lafayette, IN
        this.defaultZoom = 13;
        
        // Vehicle status colors
        this.vehicleColors = {
            'idle': '#22c55e',      // Green - Available
            'pickup': '#f59e0b',    // Orange - Going to pickup
            'dropoff': '#3b82f6',   // Blue - In service
            'charging': '#ef4444'   // Red - Charging
        };
        
        // Order status colors
        this.orderColors = {
            'pending': '#fbbf24',   // Yellow - Waiting
            'active': '#3b82f6',    // Blue - Active
            'completed': '#22c55e'  // Green - Completed
        };
    }

    /**
     * Initialize the map
     */
    initialize() {
        try {
            // Create map instance
            this.map = L.map('map', {
                center: this.defaultCenter,
                zoom: this.defaultZoom,
                zoomControl: true,
                attributionControl: true
            });

            // Add tile layer
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 19
            }).addTo(this.map);

            // Add custom controls
            this.addCustomControls();

            this.isInitialized = true;
            console.log('Map initialized successfully');
            
            return true;
        } catch (error) {
            console.error('Error initializing map:', error);
            return false;
        }
    }

    /**
     * Add custom map controls
     */
    addCustomControls() {
        // Legend control
        const legend = L.control({ position: 'bottomleft' });
        legend.onAdd = function() {
            const div = L.DomUtil.create('div', 'map-legend');
            div.innerHTML = `
                <div class="legend-content">
                    <h4>Map Legend</h4>
                    <div><span class="legend-dot" style="background: #22c55e;"></span> Available Vehicle</div>
                    <div><span class="legend-dot" style="background: #f59e0b;"></span> Pickup Vehicle</div>
                    <div><span class="legend-dot" style="background: #3b82f6;"></span> In Service</div>
                    <div><span class="legend-dot" style="background: #ef4444;"></span> Charging</div>
                    <div><span class="legend-square" style="background: #fbbf24;"></span> Pending Order</div>
                    <div><span class="legend-square" style="background: #3b82f6;"></span> Active Order</div>
                </div>
            `;
            return div;
        };
        legend.addTo(this.map);

        // Add legend styles
        const style = document.createElement('style');
        style.textContent = `
            .map-legend {
                background: rgba(255, 255, 255, 0.9);
                backdrop-filter: blur(10px);
                border-radius: 8px;
                padding: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                font-size: 12px;
            }
            .map-legend h4 {
                margin: 0 0 8px 0;
                color: #374151;
            }
            .map-legend div {
                display: flex;
                align-items: center;
                margin: 4px 0;
                color: #4b5563;
            }
            .legend-dot, .legend-square {
                width: 12px;
                height: 12px;
                margin-right: 8px;
                border: 2px solid white;
                box-shadow: 0 1px 3px rgba(0,0,0,0.3);
            }
            .legend-dot {
                border-radius: 50%;
            }
            .legend-square {
                border-radius: 2px;
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Update map bounds based on charging stations
     */
    updateMapBounds(chargingStations) {
        if (!this.isInitialized || !chargingStations || chargingStations.length === 0) {
            return;
        }

        try {
            const bounds = L.latLngBounds();
            chargingStations.forEach(station => {
                if (station.position && station.position.length >= 2) {
                    bounds.extend([station.position[0], station.position[1]]);
                }
            });

            if (bounds.isValid()) {
                this.map.fitBounds(bounds, { padding: [50, 50] });
            }
        } catch (error) {
            console.error('Error updating map bounds:', error);
        }
    }

    /**
     * Add or update charging stations
     */
    updateChargingStations(stations) {
        if (!this.isInitialized || !stations) return;

        try {
            // Clear existing charging station markers
            this.chargingStationMarkers.forEach(marker => {
                this.map.removeLayer(marker);
            });
            this.chargingStationMarkers.clear();

            // Add new charging station markers
            stations.forEach(station => {
                if (station.position && station.position.length >= 2) {
                    const marker = L.circleMarker([station.position[0], station.position[1]], {
                        radius: 8,
                        fillColor: '#8b5cf6',
                        color: 'white',
                        weight: 2,
                        opacity: 1,
                        fillOpacity: 0.8
                    }).addTo(this.map);

                    // Add popup
                    marker.bindPopup(`
                        <div class="popup-content">
                            <div class="popup-title">⚡ Charging Station</div>
                            <div class="popup-info">
                                <div class="popup-row">
                                    <span class="popup-label">ID:</span>
                                    <span class="popup-value">${station.id}</span>
                                </div>
                                <div class="popup-row">
                                    <span class="popup-label">Capacity:</span>
                                    <span class="popup-value">${station.capacity}</span>
                                </div>
                            </div>
                        </div>
                    `);

                    this.chargingStationMarkers.set(station.id, marker);
                }
            });

            console.log(`Updated ${stations.length} charging stations`);
        } catch (error) {
            console.error('Error updating charging stations:', error);
        }
    }

    /**
     * Update vehicles on the map
     */
    updateVehicles(vehicles) {
        if (!this.isInitialized || !vehicles) return;

        try {
            // Keep track of current vehicle IDs
            const currentVehicleIds = new Set(vehicles.map(v => v.id));

            // Remove markers for vehicles that no longer exist
            this.vehicleMarkers.forEach((marker, vehicleId) => {
                if (!currentVehicleIds.has(vehicleId)) {
                    this.map.removeLayer(marker);
                    this.vehicleMarkers.delete(vehicleId);
                }
            });

            // Update or create markers for current vehicles
            vehicles.forEach(vehicle => {
                if (vehicle.position && vehicle.position.length >= 2) {
                    this.updateVehicleMarker(vehicle);
                }
            });

            console.log(`Updated ${vehicles.length} vehicles`);
        } catch (error) {
            console.error('Error updating vehicles:', error);
        }
    }

    /**
     * Update or create a single vehicle marker
     */
    updateVehicleMarker(vehicle) {
        const position = [vehicle.position[0], vehicle.position[1]];
        const color = this.vehicleColors[vehicle.status] || '#6b7280';

        if (this.vehicleMarkers.has(vehicle.id)) {
            // Update existing marker
            const marker = this.vehicleMarkers.get(vehicle.id);
            marker.setLatLng(position);
            marker.setStyle({ fillColor: color });
        } else {
            // Create new marker
            const marker = L.circleMarker(position, {
                radius: 6,
                fillColor: color,
                color: 'white',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.9
            }).addTo(this.map);

            // Add click event for details
            marker.on('click', () => {
                window.simulationWS.getVehicleDetails(vehicle.id);
            });

            // Add popup
            this.updateVehiclePopup(marker, vehicle);

            this.vehicleMarkers.set(vehicle.id, marker);
        }

        // Update popup content
        const marker = this.vehicleMarkers.get(vehicle.id);
        this.updateVehiclePopup(marker, vehicle);
    }

    /**
     * Update vehicle popup content
     */
    updateVehiclePopup(marker, vehicle) {
        const statusText = vehicle.status.charAt(0).toUpperCase() + vehicle.status.slice(1);
        const batteryColor = vehicle.battery_percentage > 50 ? '#22c55e' : 
                           vehicle.battery_percentage > 20 ? '#f59e0b' : '#ef4444';

        marker.bindPopup(`
            <div class="popup-content">
                <div class="popup-title">🚗 Vehicle ${vehicle.id}</div>
                <div class="popup-info">
                    <div class="popup-row">
                        <span class="popup-label">Status:</span>
                        <span class="popup-value">${statusText}</span>
                    </div>
                    <div class="popup-row">
                        <span class="popup-label">Battery:</span>
                        <span class="popup-value" style="color: ${batteryColor}">
                            ${Math.round(vehicle.battery_percentage)}%
                        </span>
                    </div>
                    <div class="popup-row">
                        <span class="popup-label">Passenger:</span>
                        <span class="popup-value">${vehicle.has_passenger ? 'Yes' : 'No'}</span>
                    </div>
                </div>
                <div style="margin-top: 8px; font-size: 11px; color: #6b7280;">
                    Click for detailed information
                </div>
            </div>
        `);
    }

    /**
     * Update orders on the map
     */
    updateOrders(orders) {
        if (!this.isInitialized || !orders) return;

        try {
            // Keep track of current order IDs
            const currentOrderIds = new Set(orders.map(o => o.id));

            // Remove markers for orders that no longer exist
            this.orderMarkers.forEach((markers, orderId) => {
                if (!currentOrderIds.has(orderId)) {
                    markers.forEach(marker => this.map.removeLayer(marker));
                    this.orderMarkers.delete(orderId);
                }
            });

            // Update or create markers for current orders
            orders.forEach(order => {
                if (order.pickup_position && order.pickup_position.length >= 2) {
                    this.updateOrderMarker(order);
                }
            });

            console.log(`Updated ${orders.length} orders`);
        } catch (error) {
            console.error('Error updating orders:', error);
        }
    }

    /**
     * Update or create order markers (pickup and dropoff)
     */
    updateOrderMarker(order) {
        const color = this.orderColors[order.status] || '#6b7280';

        // Remove existing markers for this order
        if (this.orderMarkers.has(order.id)) {
            this.orderMarkers.get(order.id).forEach(marker => {
                this.map.removeLayer(marker);
            });
        }

        const markers = [];

        // Create pickup marker
        if (order.pickup_position && order.pickup_position.length >= 2) {
            const pickupMarker = L.marker([order.pickup_position[0], order.pickup_position[1]], {
                icon: L.divIcon({
                    className: 'order-pickup-marker',
                    html: `<div style="background: ${color}; width: 12px; height: 12px; border: 2px solid white; border-radius: 2px; box-shadow: 0 1px 3px rgba(0,0,0,0.3);"></div>`,
                    iconSize: [16, 16],
                    iconAnchor: [8, 8]
                })
            }).addTo(this.map);

            // Add click event
            pickupMarker.on('click', () => {
                window.simulationWS.getOrderDetails(order.id);
            });

            markers.push(pickupMarker);
        }

        // Create dropoff marker (if different from pickup)
        if (order.dropoff_position && order.dropoff_position.length >= 2 &&
            (order.pickup_position[0] !== order.dropoff_position[0] || 
             order.pickup_position[1] !== order.dropoff_position[1])) {
            
            const dropoffMarker = L.marker([order.dropoff_position[0], order.dropoff_position[1]], {
                icon: L.divIcon({
                    className: 'order-dropoff-marker',
                    html: `<div style="background: ${color}; width: 10px; height: 10px; border: 2px solid white; border-radius: 50%; box-shadow: 0 1px 3px rgba(0,0,0,0.3);"></div>`,
                    iconSize: [14, 14],
                    iconAnchor: [7, 7]
                })
            }).addTo(this.map);

            markers.push(dropoffMarker);
        }

        // Add popup to the first marker
        if (markers.length > 0) {
            const statusText = order.status.charAt(0).toUpperCase() + order.status.slice(1);
            markers[0].bindPopup(`
                <div class="popup-content">
                    <div class="popup-title">📦 Order ${order.id}</div>
                    <div class="popup-info">
                        <div class="popup-row">
                            <span class="popup-label">Status:</span>
                            <span class="popup-value">${statusText}</span>
                        </div>
                        <div class="popup-row">
                            <span class="popup-label">Vehicle:</span>
                            <span class="popup-value">${order.assigned_vehicle || 'Unassigned'}</span>
                        </div>
                    </div>
                    <div style="margin-top: 8px; font-size: 11px; color: #6b7280;">
                        Click for detailed information
                    </div>
                </div>
            `);
        }

        this.orderMarkers.set(order.id, markers);
    }

    /**
     * Clear all markers
     */
    clearAllMarkers() {
        // Clear vehicles
        this.vehicleMarkers.forEach(marker => {
            this.map.removeLayer(marker);
        });
        this.vehicleMarkers.clear();

        // Clear orders
        this.orderMarkers.forEach(markers => {
            markers.forEach(marker => this.map.removeLayer(marker));
        });
        this.orderMarkers.clear();

        // Clear charging stations
        this.chargingStationMarkers.forEach(marker => {
            this.map.removeLayer(marker);
        });
        this.chargingStationMarkers.clear();

        console.log('All markers cleared');
    }

    /**
     * Get map instance
     */
    getMap() {
        return this.map;
    }

    /**
     * Check if map is initialized
     */
    isMapInitialized() {
        return this.isInitialized;
    }

    /**
     * Resize map (call when container size changes)
     */
    resize() {
        if (this.isInitialized && this.map) {
            setTimeout(() => {
                this.map.invalidateSize();
            }, 100);
        }
    }
}

// Create global map instance
>>>>>>> b9bd6771fbd7f2273a429016a9b2c009e69bada8
window.simulationMap = new SimulationMap(); 