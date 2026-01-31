let trendChartInstance = null;
let modelChartInstance = null;
let errorChartInstance = null;

loadDashboard();

async function loadDashboard() {
    try {
        const response = await fetch('/api/dashboard/stats');
        if (!response.ok) throw new Error('Failed to load dashboard data');
        
        const data = await response.json();
        
        document.getElementById('totalEvaluations').textContent = data.total_evaluations;
        document.getElementById('avgDetection').textContent = (data.avg_detection_accuracy * 100).toFixed(2) + '%';
        document.getElementById('avgRedaction').textContent = (data.avg_redaction_accuracy * 100).toFixed(2) + '%';
        document.getElementById('totalErrors').textContent = data.total_errors;
        
        document.getElementById('bestModel').textContent = data.best_model || 'N/A';
        document.getElementById('latestEval').textContent = data.latest_eval ? 
            `#${data.latest_eval.id} - ${data.latest_eval.model_name}` : 'N/A';
        
        createTrendChart(data.trend_data);
        createModelChart(data.model_performance);
        createErrorChart(data.error_distribution);
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
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    borderWidth: 3
                },
                {
                    label: 'Redaction Accuracy',
                    data: redactionData,
                    borderColor: '#F59E0B',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    tension: 0.4,
                    borderWidth: 3
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
                    backgroundColor: '#10B981'
                },
                {
                    label: 'Redaction Accuracy',
                    data: redactionData,
                    backgroundColor: '#F59E0B'
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
                    '#EF4444',
                    '#3B82F6',
                    '#F59E0B',
                    '#10B981',
                    '#8B5CF6'
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
                <td><span class="metric-detection" style="color: #10B981; font-weight: bold;">${detectionAccuracy}%</span></td>
                <td><span class="metric-redaction" style="color: #F59E0B; font-weight: bold;">${redactionAccuracy}%</span></td>
                <td>
                    <a href="results.html?id=${item.id}" class="view-btn">View</a>
                </td>
            </tr>
        `;
    }).join('');
}

function viewResults(id) {
    window.location.href = `results.html?id=${id}`;
}
