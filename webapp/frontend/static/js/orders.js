/**
 * OrderTracker Class
 * Handles order tracking and real-time updates
 */
class OrderTracker {
    constructor() {
        this.orders = [];
        this.filteredOrders = [];
        this.autoRefresh = true;
        this.refreshInterval = null;
        this.currentSimulationTime = 0;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupWebSocket();
        this.loadOrderData();
        this.startAutoRefresh();
    }
    
    setupEventListeners() {
        // Refresh button
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.loadOrderData();
        });
        
        // Auto refresh toggle
        document.getElementById('autoRefreshBtn').addEventListener('click', () => {
            this.toggleAutoRefresh();
        });
        
        // Filters
        document.getElementById('statusFilter').addEventListener('change', () => {
            this.filterOrders();
        });
        
        document.getElementById('orderSearch').addEventListener('input', () => {
            this.filterOrders();
        });
        
        document.getElementById('vehicleSearch').addEventListener('input', () => {
            this.filterOrders();
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
        if (data && data.orders) {
            this.orders = data.orders || [];
            this.currentSimulationTime = data.stats ? data.stats.current_time : 0;
            this.updateStatistics();
            this.filterOrders();
        }
    }
    
    async loadOrderData() {
        try {
            const response = await fetch('/api/simulation/state');
            const result = await response.json();
            
            if (result.success && result.data) {
                this.orders = result.data.orders || [];
                this.currentSimulationTime = result.data.stats ? result.data.stats.current_time : 0;
                this.updateStatistics();
                this.filterOrders();
            } else {
                console.warn('No simulation data available');
                this.showNoData();
            }
        } catch (error) {
            console.error('Error loading order data:', error);
            this.showError('Failed to load order data');
        }
    }
    
    updateStatistics() {
        const stats = this.calculateStatistics();
        
        document.getElementById('totalOrders').textContent = stats.total;
        document.getElementById('pendingOrders').textContent = stats.pending;
        document.getElementById('activeOrders').textContent = stats.active;
        document.getElementById('completedOrders').textContent = stats.completed;
    }
    
    calculateStatistics() {
        const stats = {
            total: this.orders.length,
            pending: 0,
            active: 0,
            completed: 0
        };
        
        this.orders.forEach(order => {
            const status = this.getOrderStatus(order);
            switch (status) {
                case 'pending':
                    stats.pending++;
                    break;
                case 'assigned':
                case 'in_progress':
                    stats.active++;
                    break;
                case 'completed':
                    stats.completed++;
                    break;
            }
        });
        
        return stats;
    }
    
    getOrderStatus(order) {
        // Use the actual status from the order object
        if (order.status) {
            // Map backend status to frontend display status
            switch (order.status) {
                case 'pending':
                    return 'pending';
                case 'assigned':
                    return 'assigned';
                case 'picked_up':
                    return 'in_progress';
                case 'completed':
                    return 'completed';
                case 'cancelled':
                    return 'cancelled';
                default:
                    return 'pending';
            }
        }
        
        // Fallback logic
        if (order.completion_time) {
            return 'completed';
        }
        if (order.assigned_vehicle_id) {
            return order.pickup_completed ? 'in_progress' : 'assigned';
        }
        return 'pending';
    }
    
    getStatusDisplay(status) {
        const statusMap = {
            'pending': { text: 'Pending', class: 'warning', icon: 'clock' },
            'assigned': { text: 'Assigned', class: 'info', icon: 'car' },
            'in_progress': { text: 'In Progress', class: 'primary', icon: 'route' },
            'completed': { text: 'Completed', class: 'success', icon: 'check-circle' },
            'cancelled': { text: 'Cancelled', class: 'danger', icon: 'times-circle' }
        };
        
        return statusMap[status] || { text: 'Unknown', class: 'secondary', icon: 'question' };
    }
    
    filterOrders() {
        const statusFilter = document.getElementById('statusFilter').value.toLowerCase();
        const orderSearch = document.getElementById('orderSearch').value.toLowerCase();
        const vehicleSearch = document.getElementById('vehicleSearch').value.toLowerCase();
        
        this.filteredOrders = this.orders.filter(order => {
            const status = this.getOrderStatus(order);
            const orderId = order.order_id ? order.order_id.toString().toLowerCase() : '';
            const vehicleId = order.assigned_vehicle_id ? order.assigned_vehicle_id.toString().toLowerCase() : '';
            
            // Status filter
            if (statusFilter && status !== statusFilter) return false;
            
            // Order ID search
            if (orderSearch && !orderId.includes(orderSearch)) return false;
            
            // Vehicle ID search
            if (vehicleSearch && !vehicleId.includes(vehicleSearch)) return false;
            
            return true;
        });
        
        this.renderOrdersTable();
    }
    
    renderOrdersTable() {
        const tbody = document.getElementById('ordersTableBody');
        
        if (this.filteredOrders.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center text-muted">
                        <i class="fas fa-inbox"></i> No orders found
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = this.filteredOrders.map(order => {
            const status = this.getOrderStatus(order);
            const statusDisplay = this.getStatusDisplay(status);
            const duration = this.calculateDuration(order);
            
            return `
                <tr>
                    <td>
                        <strong>${order.order_id || 'N/A'}</strong>
                    </td>
                    <td>
                        <span class="badge bg-${statusDisplay.class}">
                            <i class="fas fa-${statusDisplay.icon}"></i>
                            ${statusDisplay.text}
                        </span>
                    </td>
                    <td>
                        ${order.assigned_vehicle_id ? 
                            `<a href="#" class="text-decoration-none" onclick="orderTracker.showVehicleDetails('${order.assigned_vehicle_id}')">
                                <i class="fas fa-car"></i> ${order.assigned_vehicle_id}
                            </a>` : 
                            '<span class="text-muted">Not assigned</span>'
                        }
                    </td>
                    <td>
                        <small class="text-muted">
                            ${this.formatLocation(order.pickup_position)}
                        </small>
                    </td>
                    <td>
                        <small class="text-muted">
                            ${this.formatLocation(order.dropoff_position)}
                        </small>
                    </td>
                    <td>
                        <small>${this.formatTimestamp(order.creation_time)}</small>
                    </td>
                    <td>
                        <small class="text-muted">${duration}</small>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary" onclick="orderTracker.showOrderDetails('${order.order_id}')">
                            <i class="fas fa-eye"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
    }
    
    calculateDuration(order) {
        if (order.creation_time === undefined || order.creation_time === null) return 'N/A';
        
        // For simulation time, get current simulation time or completion time
        let endTime;
        if (order.completion_time) {
            endTime = order.completion_time;
        } else {
            // For ongoing orders, use current simulation time
            endTime = this.currentSimulationTime;
        }
        
        const durationSeconds = endTime - order.creation_time;
        
        if (durationSeconds < 60) {
            return `${durationSeconds.toFixed(1)}s`;
        } else if (durationSeconds < 3600) {
            return `${Math.floor(durationSeconds / 60)}m ${(durationSeconds % 60).toFixed(0)}s`;
        } else {
            return `${Math.floor(durationSeconds / 3600)}h ${Math.floor((durationSeconds % 3600) / 60)}m`;
        }
    }
    
    formatLocation(location) {
        if (!location) return 'N/A';
        if (Array.isArray(location)) {
            return `${location[0].toFixed(4)}, ${location[1].toFixed(4)}`;
        }
        return location.toString();
    }
    
    formatTimestamp(timestamp) {
        if (!timestamp && timestamp !== 0) return 'N/A';
        // For simulation relative time, just show the time in seconds
        return `${timestamp.toFixed(1)}s`;
    }
    
    showOrderDetails(orderId) {
        const order = this.orders.find(o => o.order_id === orderId);
        if (!order) return;
        
        const status = this.getOrderStatus(order);
        const statusDisplay = this.getStatusDisplay(status);
        
        const modalContent = `
            <div class="row">
                <div class="col-md-6">
                    <h6><i class="fas fa-info-circle"></i> Basic Information</h6>
                    <table class="table table-sm">
                        <tr><td><strong>Order ID:</strong></td><td>${order.order_id || 'N/A'}</td></tr>
                        <tr><td><strong>Status:</strong></td><td>
                            <span class="badge bg-${statusDisplay.class}">
                                <i class="fas fa-${statusDisplay.icon}"></i> ${statusDisplay.text}
                            </span>
                        </td></tr>
                        <tr><td><strong>Created:</strong></td><td>${this.formatTimestamp(order.creation_time)} <small class="text-muted">(simulation time)</small></td></tr>
                        <tr><td><strong>Assigned:</strong></td><td>${this.formatTimestamp(order.assignment_time)}</td></tr>
                        <tr><td><strong>Picked up:</strong></td><td>${this.formatTimestamp(order.pickup_time)}</td></tr>
                        <tr><td><strong>Completed:</strong></td><td>${this.formatTimestamp(order.completion_time)}</td></tr>
                        <tr><td><strong>Duration:</strong></td><td>${this.calculateDuration(order)}</td></tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <h6><i class="fas fa-map-marker-alt"></i> Location Information</h6>
                    <table class="table table-sm">
                        <tr><td><strong>Pickup:</strong></td><td>${this.formatLocation(order.pickup_position)}</td></tr>
                        <tr><td><strong>Dropoff:</strong></td><td>${this.formatLocation(order.dropoff_position)}</td></tr>
                        <tr><td><strong>Distance:</strong></td><td>${order.estimated_distance ? order.estimated_distance.toFixed(2) + ' km' : 'N/A'}</td></tr>
                        <tr><td><strong>Price:</strong></td><td>${order.final_price ? '$' + order.final_price.toFixed(2) : 'N/A'}</td></tr>
                        <tr><td><strong>Pickup Completed:</strong></td><td>
                            ${order.pickup_completed ? 
                                '<span class="text-success"><i class="fas fa-check"></i> Yes</span>' : 
                                '<span class="text-muted">No</span>'
                            }
                        </td></tr>
                    </table>
                </div>
            </div>
            
            ${order.assigned_vehicle_id ? `
                <hr>
                <div class="row">
                    <div class="col-12">
                        <h6><i class="fas fa-car"></i> Vehicle Information</h6>
                        <p>
                            <strong>Assigned Vehicle:</strong> 
                            <a href="#" class="text-decoration-none" onclick="orderTracker.showVehicleDetails('${order.assigned_vehicle_id}')">
                                <i class="fas fa-external-link-alt"></i> Vehicle ${order.assigned_vehicle_id}
                            </a>
                        </p>
                    </div>
                </div>
            ` : ''}
        `;
        
        document.getElementById('orderDetailContent').innerHTML = modalContent;
        new bootstrap.Modal(document.getElementById('orderDetailModal')).show();
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
                this.loadOrderData();
            }, 3000); // Refresh every 3 seconds
        }
    }
    
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
    
    showError(message) {
        const tbody = document.getElementById('ordersTableBody');
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-danger">
                    <i class="fas fa-exclamation-triangle"></i> ${message}
                </td>
            </tr>
        `;
    }
    
    showNoData() {
        const tbody = document.getElementById('ordersTableBody');
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-muted">
                    <i class="fas fa-exclamation-triangle"></i> No simulation data available. Please create and start a simulation first.
                </td>
            </tr>
        `;
        
        // Clear statistics
        document.getElementById('totalOrders').textContent = '0';
        document.getElementById('pendingOrders').textContent = '0';
        document.getElementById('activeOrders').textContent = '0';
        document.getElementById('completedOrders').textContent = '0';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Setup WebSocket connection if not already done
    if (window.simulationWS) {
        window.simulationWS.connect();
    }
    
    // Initialize order tracker
    window.orderTracker = new OrderTracker();
}); 