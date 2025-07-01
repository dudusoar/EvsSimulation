/**
 * Charts Control Module - Simplified Version
 */

class SimulationCharts {
    constructor() {
        this.revenueChart = null;
        this.batteryChart = null;
        this.revenueData = [];
        this.timeLabels = [];
        
        this.init();
    }
    
    init() {
        this.initRevenueChart();
        this.initBatteryChart();
        console.log('Charts initialized');
    }
    
    initRevenueChart() {
        const ctx = document.getElementById('revenueChart').getContext('2d');
        
        this.revenueChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.timeLabels,
                datasets: [{
                    label: 'Revenue ($)',
                    data: this.revenueData,
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Revenue ($)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Time (s)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    initBatteryChart() {
        const ctx = document.getElementById('batteryChart').getContext('2d');
        
        this.batteryChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Good (>60%)', 'Medium (30-60%)', 'Low (<30%)'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: [
                        '#28a745',
                        '#ffc107',
                        '#dc3545'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    updateCharts(stats) {
        this.updateRevenueChart(stats);
        this.updateBatteryChart(stats);
    }
    
    updateRevenueChart(stats) {
        // Add new data point
        const time = stats.current_time.toFixed(0);
        const revenue = stats.total_revenue;
        
        // Keep only last 20 data points
        if (this.timeLabels.length >= 20) {
            this.timeLabels.shift();
            this.revenueData.shift();
        }
        
        this.timeLabels.push(time);
        this.revenueData.push(revenue);
        
        // Update chart
        this.revenueChart.data.labels = this.timeLabels;
        this.revenueChart.data.datasets[0].data = this.revenueData;
        this.revenueChart.update('none'); // No animation for better performance
    }
    
    updateBatteryChart(stats) {
        // This is a simplified version - in reality, we'd need vehicle battery data
        // For now, we'll use dummy data based on utilization
        const util = stats.vehicle_utilization_rate;
        
        // Simulate battery distribution
        const good = Math.max(0, (1 - util) * 100);
        const medium = Math.min(util * 60, 40);
        const low = Math.max(0, 100 - good - medium);
        
        this.batteryChart.data.datasets[0].data = [good, medium, low];
        this.batteryChart.update('none');
    }
}

// Initialize charts when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.simulationCharts = new SimulationCharts();
}); 