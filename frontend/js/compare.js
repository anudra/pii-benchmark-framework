let evaluations = [];

window.addEventListener('DOMContentLoaded', init);

async function init() {
    const urlParams = new URLSearchParams(window.location.search);
    const id1 = urlParams.get('id1');
    const id2 = urlParams.get('id2');
    
    if (id1 && id2) {
        document.getElementById('selectionForm').style.display = 'none';
        loadComparison(id1, id2);
    } else {
        await loadEvaluations();
    }
}

async function loadEvaluations() {
    try {
        const response = await fetch('/api/history');
        if (!response.ok) throw new Error('Failed to load evaluations');
        
        evaluations = await response.json();
        
        if (!evaluations || evaluations.length === 0) {
            document.getElementById('selectionForm').innerHTML = '<p>No evaluations found. Please run an evaluation first.</p>';
            return;
        }
        
        // Populate both dropdowns
        const eval1Select = document.getElementById('eval1Select');
        const eval2Select = document.getElementById('eval2Select');
        
        // Clear existing options except the first placeholder
        eval1Select.innerHTML = '<option value="">-- Choose Evaluation 1 --</option>';
        eval2Select.innerHTML = '<option value="">-- Choose Evaluation 2 --</option>';
        
        evaluations.forEach(eval => {
            const timestamp = new Date(eval.timestamp).toLocaleString();
            const optionText = `ID: ${eval.id} | ${eval.model_name || 'Unknown'} | ${eval.mode} | ${timestamp}`;
            
            const option1 = document.createElement('option');
            option1.value = eval.id;
            option1.textContent = optionText;
            
            const option2 = document.createElement('option');
            option2.value = eval.id;
            option2.textContent = optionText;
            
            eval1Select.appendChild(option1);
            eval2Select.appendChild(option2);
        });
        
        console.log(`Populated dropdowns with ${evaluations.length} evaluations`);
    } catch (error) {
        console.error('Error loading evaluations:', error);
        document.getElementById('selectionForm').innerHTML = `<p>Error loading evaluations: ${error.message}</p>`;
    }
}

function compareSelected() {
    const id1 = document.getElementById('eval1Select').value;
    const id2 = document.getElementById('eval2Select').value;
    
    if (!id1 || !id2) {
        alert('Please select both evaluations to compare');
        return;
    }
    
    if (id1 === id2) {
        alert('Please select two different evaluations');
        return;
    }
    
    // Hide selection form before loading comparison
    document.getElementById('selectionForm').style.display = 'none';
    loadComparison(id1, id2);
}

function resetComparison() {
    // Check if we came from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const fromHistory = urlParams.get('id1') && urlParams.get('id2');
    
    if (fromHistory) {
        // Go back to history page
        window.location.href = 'history.html';
    } else {
        // Reset to selection form
        document.getElementById('selectionForm').style.display = 'block';
        document.getElementById('comparisonResults').style.display = 'none';
        document.getElementById('eval1Select').value = '';
        document.getElementById('eval2Select').value = '';
    }
}

async function loadComparison(id1, id2) {
    try {
        const response = await fetch(`/api/compare/${id1}/${id2}`);
        if (!response.ok) throw new Error('Failed to load comparison');
        
        const data = await response.json();
        
        // Hide selection form and show results
        document.getElementById('selectionForm').style.display = 'none';
        document.getElementById('comparisonResults').style.display = 'block';
        
        // Extract redaction data
        const redaction1 = data.evaluation1.redaction_analysis?.summary || {};
        const redaction2 = data.evaluation2.redaction_analysis?.summary || {};
        
        // Display evaluation 1 - Detection
        document.getElementById('eval1Id').textContent = data.evaluation1.id;
        document.getElementById('model1').textContent = data.evaluation1.model_name;
        document.getElementById('mode1').textContent = data.evaluation1.mode;
        document.getElementById('timestamp1').textContent = new Date(data.evaluation1.timestamp).toLocaleString();
        document.getElementById('metrics1').innerHTML = `
            <p><strong>Precision:</strong> ${(data.evaluation1.metrics.precision * 100).toFixed(2)}%</p>
            <p><strong>Recall:</strong> ${(data.evaluation1.metrics.recall * 100).toFixed(2)}%</p>
            <p><strong>F1-Score:</strong> ${(data.evaluation1.metrics.f1_score * 100).toFixed(2)}%</p>
            <p><strong>Accuracy:</strong> ${(data.evaluation1.metrics.accuracy * 100).toFixed(2)}%</p>
        `;
        
        // Display evaluation 2 - Detection
        document.getElementById('eval2Id').textContent = data.evaluation2.id;
        document.getElementById('model2').textContent = data.evaluation2.model_name;
        document.getElementById('mode2').textContent = data.evaluation2.mode;
        document.getElementById('timestamp2').textContent = new Date(data.evaluation2.timestamp).toLocaleString();
        document.getElementById('metrics2').innerHTML = `
            <p><strong>Precision:</strong> ${(data.evaluation2.metrics.precision * 100).toFixed(2)}%</p>
            <p><strong>Recall:</strong> ${(data.evaluation2.metrics.recall * 100).toFixed(2)}%</p>
            <p><strong>F1-Score:</strong> ${(data.evaluation2.metrics.f1_score * 100).toFixed(2)}%</p>
            <p><strong>Accuracy:</strong> ${(data.evaluation2.metrics.accuracy * 100).toFixed(2)}%</p>
        `;
        
        // Display detection differences
        const diff = data.differences;
        document.getElementById('detectionDifferences').innerHTML = `
            <p><strong>Precision Δ:</strong> ${formatDiff(diff.precision_diff)}</p>
            <p><strong>Recall Δ:</strong> ${formatDiff(diff.recall_diff)}</p>
            <p><strong>F1-Score Δ:</strong> ${formatDiff(diff.f1_diff)}</p>
            <p><strong>Accuracy Δ:</strong> ${formatDiff(diff.accuracy_diff)}</p>
        `;
        
        // Display evaluation 1 - Redaction
        document.getElementById('eval1IdRed').textContent = data.evaluation1.id;
        const total1 = redaction1.total_entities || 0;
        const correct1 = redaction1.correct_redactions || 0;
        const redactionAcc1 = total1 > 0 ? ((correct1 / total1) * 100).toFixed(2) : '0.00';
        document.getElementById('redactionMetrics1').innerHTML = `
            <p><strong>Redaction Accuracy:</strong> ${redactionAcc1}%</p>
            <p><strong>Correct:</strong> ${correct1} / ${total1}</p>
            <p><strong>Leaks:</strong> ${redaction1.leaks || 0}</p>
            <p><strong>Under:</strong> ${redaction1.under_redactions || 0}</p>
            <p><strong>Over:</strong> ${redaction1.over_redactions || 0}</p>
        `;
        
        // Display evaluation 2 - Redaction
        document.getElementById('eval2IdRed').textContent = data.evaluation2.id;
        const total2 = redaction2.total_entities || 0;
        const correct2 = redaction2.correct_redactions || 0;
        const redactionAcc2 = total2 > 0 ? ((correct2 / total2) * 100).toFixed(2) : '0.00';
        document.getElementById('redactionMetrics2').innerHTML = `
            <p><strong>Redaction Accuracy:</strong> ${redactionAcc2}%</p>
            <p><strong>Correct:</strong> ${correct2} / ${total2}</p>
            <p><strong>Leaks:</strong> ${redaction2.leaks || 0}</p>
            <p><strong>Under:</strong> ${redaction2.under_redactions || 0}</p>
            <p><strong>Over:</strong> ${redaction2.over_redactions || 0}</p>
        `;
        
        // Display redaction differences
        const redDiff = parseFloat(redactionAcc2) - parseFloat(redactionAcc1);
        const leakDiff = (redaction2.leaks || 0) - (redaction1.leaks || 0);
        const underDiff = (redaction2.under_redactions || 0) - (redaction1.under_redactions || 0);
        const overDiff = (redaction2.over_redactions || 0) - (redaction1.over_redactions || 0);
        
        document.getElementById('redactionDifferences').innerHTML = `
            <p><strong>Redaction Accuracy Δ:</strong> ${formatDiff(redDiff / 100)}</p>
            <p><strong>Leaks Δ:</strong> ${formatCountDiff(leakDiff)}</p>
            <p><strong>Under-redactions Δ:</strong> ${formatCountDiff(underDiff)}</p>
            <p><strong>Over-redactions Δ:</strong> ${formatCountDiff(overDiff)}</p>
        `;
        
        // Create comparison charts
        createDetectionChart(data.evaluation1.metrics, data.evaluation2.metrics);
        createRedactionChart(redaction1, redaction2, data.evaluation1.id, data.evaluation2.id);
        
    } catch (error) {
        console.error('Error loading comparison:', error);
        alert('Failed to load comparison');
    }
}

function createDetectionChart(metrics1, metrics2) {
    const canvas = document.getElementById('detectionChart');
    if (!canvas) {
        console.error('Detection chart canvas not found');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    
    // Destroy existing chart if it exists
    if (window.detectionComparisonChart instanceof Chart) {
        window.detectionComparisonChart.destroy();
    }
    
    console.log('Creating detection chart with metrics:', metrics1, metrics2);
    
    window.detectionComparisonChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Precision', 'Recall', 'F1-Score', 'Accuracy'],
            datasets: [
                {
                    label: 'Evaluation 1',
                    data: [
                        metrics1.precision * 100,
                        metrics1.recall * 100,
                        metrics1.f1_score * 100,
                        metrics1.accuracy * 100
                    ],
                    backgroundColor: '#4CAF50'
                },
                {
                    label: 'Evaluation 2',
                    data: [
                        metrics2.precision * 100,
                        metrics2.recall * 100,
                        metrics2.f1_score * 100,
                        metrics2.accuracy * 100
                    ],
                    backgroundColor: '#2196F3'
                }
            ]
        },
        options: {
            responsive: true,
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
                title: {
                    display: true,
                    text: 'Detection Metrics Comparison'
                }
            }
        }
    });
}

function createRedactionChart(redaction1, redaction2, id1, id2) {
    const canvas = document.getElementById('redactionComparisonChart');
    if (!canvas) {
        console.error('Redaction chart canvas not found');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    
    // Destroy existing chart if it exists
    if (window.redactionComparisonChart instanceof Chart) {
        window.redactionComparisonChart.destroy();
    }
    
    console.log('Creating redaction chart with data:', redaction1, redaction2);
    
    const total1 = redaction1.total_entities || 0;
    const total2 = redaction2.total_entities || 0;
    
    window.redactionComparisonChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Correct', 'Leaks', 'Over', 'Under', 'Semi'],
            datasets: [
                {
                    label: `Evaluation ${id1}`,
                    data: [
                        redaction1.correct_redactions || 0,
                        redaction1.leaks || 0,
                        redaction1.over_redactions || 0,
                        redaction1.under_redactions || 0,
                        redaction1.semi_redactions || 0
                    ],
                    backgroundColor: '#4CAF50'
                },
                {
                    label: `Evaluation ${id2}`,
                    data: [
                        redaction2.correct_redactions || 0,
                        redaction2.leaks || 0,
                        redaction2.over_redactions || 0,
                        redaction2.under_redactions || 0,
                        redaction2.semi_redactions || 0
                    ],
                    backgroundColor: '#FF9800'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 2,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Redaction Quality Comparison'
                }
            }
        }
    });
}

function formatCountDiff(value) {
    if (value > 0) {
        return `<span style="color: red;">+${value}</span>`;
    } else if (value < 0) {
        return `<span style="color: green;">${value}</span>`;
    } else {
        return `<span>0</span>`;
    }
}

function formatDiff(value) {
    const percent = (value * 100).toFixed(2);
    if (value > 0) {
        return `<span style="color: green;">+${percent}%</span>`;
    } else if (value < 0) {
        return `<span style="color: red;">${percent}%</span>`;
    } else {
        return `<span>${percent}%</span>`;
    }
}
