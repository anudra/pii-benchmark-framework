// Dashboard functionality
// Loads and displays dashboard statistics and charts

let trendChartInstance = null;
let modelChartInstance = null;
let errorChartInstance = null;

loadDashboard();

async function loadDashboard() {
    try {
        const response = await fetch('/api/dashboard/stats');
        if (!response.ok) throw new Error('Failed to load dashboard data');
        
        const data = await response.json();
        
        // Update stats cards
        document.getElementById('totalEvaluations').textContent = data.total_evaluations;
        document.getElementById('avgDetection').textContent = (data.avg_detection_accuracy * 100).toFixed(2) + '%';
        document.getElementById('avgRedaction').textContent = (data.avg_redaction_accuracy * 100).toFixed(2) + '%';
        document.getElementById('totalErrors').textContent = data.total_errors;
        
        // Update performance summary
        document.getElementById('bestModel').textContent = data.best_model || 'N/A';
        document.getElementById('latestEval').textContent = data.latest_eval ? 
            `#${data.latest_eval.id} - ${data.latest_eval.model_name}` : 'N/A';
        
        // Create charts
        createTrendChart(data.trend_data);
        createModelChart(data.model_performance);
        createErrorChart(data.error_distribution);
        
        // Load recent evaluations
        loadRecentEvaluations(data.recent_evaluations);
        
    } catch (err) {
        console.error('Error loading dashboard:', err);
        alert('Error loading dashboard: ' + err.message);
    }
}

function createTrendChart(trendData) {
    const ctx = document.getElementById('trendChart').getContext('2d');
    
    if (trendChartInstance) {
        trendChartInstance.destroy();
    }
    
    const labels = trendData.map(item => new Date(item.timestamp).toLocaleDateString());
    const detectionData = trendData.map(item => item.detection_accuracy * 100);
    const redactionData = trendData.map(item => item.redaction_accuracy * 100);
    
    trendChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Detection Accuracy',
                    data: detectionData,
                    borderColor: '#4CAF50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Redaction Accuracy',
                    data: redactionData,
                    borderColor: '#FF9800',
                    backgroundColor: 'rgba(255, 152, 0, 0.1)',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        }
    });
}

function createModelChart(modelPerformance) {
    const ctx = document.getElementById('modelChart').getContext('2d');
    
    if (modelChartInstance) {
        modelChartInstance.destroy();
    }
    
    const labels = Object.keys(modelPerformance);
    const detectionData = labels.map(model => modelPerformance[model].avg_detection * 100);
    const redactionData = labels.map(model => modelPerformance[model].avg_redaction * 100);
    
    modelChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Detection Accuracy',
                    data: detectionData,
                    backgroundColor: '#4CAF50'
                },
                {
                    label: 'Redaction Accuracy',
                    data: redactionData,
                    backgroundColor: '#FF9800'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        }
    });
}

function createErrorChart(errorDistribution) {
    const ctx = document.getElementById('errorChart').getContext('2d');
    
    if (errorChartInstance) {
        errorChartInstance.destroy();
    }
    
    errorChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['False Positives', 'False Negatives', 'Leaks', 'Over-Redactions', 'Under-Redactions'],
            datasets: [{
                data: [
                    errorDistribution.false_positives || 0,
                    errorDistribution.false_negatives || 0,
                    errorDistribution.leaks || 0,
                    errorDistribution.over_redactions || 0,
                    errorDistribution.under_redactions || 0
                ],
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'right'
                }
            }
        }
    });
}

function loadRecentEvaluations(evaluations) {
    const tbody = document.getElementById('recentBody');
    
    if (evaluations.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No evaluations yet</td></tr>';
        return;
    }
    
    tbody.innerHTML = evaluations.map(item => {
        const detectionAccuracy = (item.detection_accuracy * 100).toFixed(2);
        const redactionAccuracy = (item.redaction_accuracy * 100).toFixed(2);
        
        return `
            <tr>
                <td>${item.id}</td>
                <td>${item.model_name}</td>
                <td>${new Date(item.timestamp).toLocaleString()}</td>
                <td style="color: #4CAF50; font-weight: bold;">${detectionAccuracy}%</td>
                <td style="color: #FF9800; font-weight: bold;">${redactionAccuracy}%</td>
                <td>
                    <button onclick="viewResults(${item.id})" class="btn-primary" style="padding: 0.5rem 1rem;">View</button>
                </td>
            </tr>
        `;
    }).join('');
}

function viewResults(id) {
    window.location.href = `results.html?id=${id}`;
}

function exportDashboard() {
    alert('Dashboard export functionality coming soon!');
    // TODO: Implement dashboard PDF export
}
