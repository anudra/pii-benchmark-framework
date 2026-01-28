let evaluationId = null;

const urlParams = new URLSearchParams(window.location.search);
evaluationId = urlParams.get('id') || localStorage.getItem('lastEvaluationId');

if (!evaluationId) {
    alert('No evaluation ID found');
    window.location.href = 'index.html';
} else {
    loadResults(evaluationId);
}

async function loadResults(id) {
    try {
        const response = await fetch(`/api/evaluation/${id}`);
        if (!response.ok) throw new Error('Failed to load results');
        
        const data = await response.json();
        
        // Display metadata
        document.getElementById('modelName').textContent = data.model_name;
        document.getElementById('mode').textContent = data.mode;
        document.getElementById('timestamp').textContent = new Date(data.timestamp).toLocaleString();
        
        // Display metrics
        document.getElementById('precision').textContent = (data.metrics.precision * 100).toFixed(2) + '%';
        document.getElementById('recall').textContent = (data.metrics.recall * 100).toFixed(2) + '%';
        document.getElementById('f1').textContent = (data.metrics.f1_score * 100).toFixed(2) + '%';
        document.getElementById('accuracy').textContent = (data.metrics.accuracy * 100).toFixed(2) + '%';
        
        // Display confusion matrix in 2x2 format
        const cm = data.confusion_matrix;
        document.getElementById('confusionMatrix').innerHTML = `
            <div style="display: inline-block; border: 2px solid #333; margin: 1rem 0;">
                <table style="border-collapse: collapse; text-align: center;">
                    <tr>
                        <td colspan="2" rowspan="2" style="border: none;"></td>
                        <th colspan="2" style="padding: 0.5rem; border-bottom: 2px solid #333;">Predicted</th>
                    </tr>
                    <tr>
                        <th style="padding: 0.5rem; border-bottom: 2px solid #333; border-left: 2px solid #333;">Positive</th>
                        <th style="padding: 0.5rem; border-bottom: 2px solid #333; border-left: 1px solid #ddd;">Negative</th>
                    </tr>
                    <tr>
                        <th rowspan="2" style="padding: 0.5rem; border-right: 2px solid #333; writing-mode: vertical-lr; transform: rotate(180deg);">Actual</th>
                        <th style="padding: 0.5rem; border-right: 2px solid #333; border-bottom: 1px solid #ddd;">Positive</th>
                        <td style="padding: 1rem 2rem; background: #c8e6c9; font-weight: bold; font-size: 1.2rem; border-left: 2px solid #333; border-bottom: 1px solid #ddd;">
                            <div style="font-size: 0.8rem; color: #2e7d32; margin-bottom: 0.25rem;">TP</div>
                            <div>${cm.TP}</div>
                        </td>
                        <td style="padding: 1rem 2rem; background: #ffccbc; font-weight: bold; font-size: 1.2rem; border-left: 1px solid #ddd; border-bottom: 1px solid #ddd;">
                            <div style="font-size: 0.8rem; color: #c62828; margin-bottom: 0.25rem;">FN</div>
                            <div>${cm.FN}</div>
                        </td>
                    </tr>
                    <tr>
                        <th style="padding: 0.5rem; border-right: 2px solid #333;">Negative</th>
                        <td style="padding: 1rem 2rem; background: #ffccbc; font-weight: bold; font-size: 1.2rem; border-left: 2px solid #333;">
                            <div style="font-size: 0.8rem; color: #c62828; margin-bottom: 0.25rem;">FP</div>
                            <div>${cm.FP}</div>
                        </td>
                        <td style="padding: 1rem 2rem; background: #c8e6c9; font-weight: bold; font-size: 1.2rem; border-left: 1px solid #ddd;">
                            <div style="font-size: 0.8rem; color: #2e7d32; margin-bottom: 0.25rem;">TN</div>
                            <div>${cm.TN}</div>
                        </td>
                    </tr>
                </table>
                <div style="margin-top: 0.5rem; padding: 0.5rem; font-size: 0.9rem; color: #666;">
                    <strong>TP:</strong> True Positive (Correctly identified as PII) &nbsp; <strong>TN:</strong> True Negative (Correctly identified as non-PII)<br>
                    <strong>FP:</strong> False Positive (Wrongly identified as PII) &nbsp; <strong>FN:</strong> False Negative (Missed PII)
                </div>
            </div>
        `;
        
        // Render chart
        const ctx = document.getElementById('metricsChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Precision', 'Recall', 'F1-Score', 'Accuracy'],
                datasets: [{
                    label: 'Metrics (%)',
                    data: [
                        data.metrics.precision * 100,
                        data.metrics.recall * 100,
                        data.metrics.f1_score * 100,
                        data.metrics.accuracy * 100
                    ],
                    backgroundColor: ['#4CAF50', '#2196F3', '#FFC107', '#9C27B0']
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
        
        // Display diff view
        document.getElementById('diffView').innerHTML = data.diff_html;
        
        // Display redaction quality metrics
        displayRedactionMetrics(data.redaction_analysis);
        
        // Check for existing AI summary or show generate button
        checkAISummary();
        
        // Display errors
        document.getElementById('errorCount').textContent = data.errors.length;
        const errorsList = document.getElementById('errorsList');
        if (data.errors.length > 0) {
            errorsList.innerHTML = '<table><tr><th>Type</th><th>Entity</th><th>Position</th><th>Description</th></tr>' +
                data.errors.slice(0, 20).map(err => `
                    <tr>
                        <td>${err.error_type}</td>
                        <td>${err.entity_type}</td>
                        <td>${err.position_start}-${err.position_end}</td>
                        <td>${err.description}</td>
                    </tr>
                `).join('') + '</table>';
        } else {
            errorsList.innerHTML = '<p>No errors found!</p>';
        }
        
    } catch (err) {
        alert('Error loading results: ' + err.message);
        window.location.href = 'index.html';
    }
}

function displayRedactionMetrics(redactionAnalysis) {
    console.log('Redaction Analysis:', redactionAnalysis);
    
    // Handle the nested structure: redactionAnalysis has 'summary' and 'categories'
    const summary = redactionAnalysis.summary || {};
    
    const correct = summary.correct_redactions || 0;
    const leak = summary.leaks || 0;
    const over = summary.over_redactions || 0;
    const under = summary.under_redactions || 0;
    const semi = summary.semi_redactions || 0;
    
    const total = summary.total_entities || 0;
    const redactionAccuracy = total > 0 ? ((correct / total) * 100).toFixed(2) : '0.00';
    const leakRate = total > 0 ? ((leak / total) * 100).toFixed(2) : '0.00';
    
    // Display metrics cards
    document.getElementById('redactionMetricsGrid').innerHTML = `
        <div class="metric-card" style="background-color: #e8f5e9;">
            <h3>Redaction Accuracy</h3>
            <p class="metric-value">${redactionAccuracy}%</p>
            <p class="metric-label">${correct} / ${total} correctly redacted</p>
        </div>
        <div class="metric-card" style="background-color: ${leak > 0 ? '#ffebee' : '#e8f5e9'};">
            <h3>Leak Rate</h3>
            <p class="metric-value">${leakRate}%</p>
            <p class="metric-label">${leak} unredacted entities</p>
        </div>
        <div class="metric-card" style="background-color: #fff3e0;">
            <h3>Quality Issues</h3>
            <p class="metric-value">${over + under + semi}</p>
            <p class="metric-label">Over/Under/Semi redactions</p>
        </div>
        <div class="metric-card">
            <h3>Total Entities</h3>
            <p class="metric-value">${total}</p>
            <p class="metric-label">Evaluated for redaction</p>
        </div>
    `;
    
    // Display redaction summary table
    document.getElementById('redactionSummary').innerHTML = `
        <table>
            <tr><th>Status</th><th>Count</th><th>Description</th></tr>
            <tr class="correct"><td>Correct</td><td>${correct}</td><td>Fully and properly redacted</td></tr>
            <tr class="leak"><td>Leak</td><td>${leak}</td><td>Not redacted at all - DATA LEAK!</td></tr>
            <tr class="over"><td>⚠ Over-redacted</td><td>${over}</td><td>More characters redacted than necessary</td></tr>
            <tr class="under"><td>⚠ Under-redacted</td><td>${under}</td><td>Partially visible - SECURITY RISK!</td></tr>
            <tr class="semi"><td>⚠ Semi-redacted</td><td>${semi}</td><td>Mostly redacted but some chars visible</td></tr>
        </table>
    `;
    
    // Create redaction quality chart only if there's data
    const ctxRedaction = document.getElementById('redactionChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (window.redactionChart instanceof Chart) {
        window.redactionChart.destroy();
    }
    
    // Only create chart if we have data
    if (total > 0) {
        window.redactionChart = new Chart(ctxRedaction, {
            type: 'doughnut',
            data: {
                labels: ['Correct', 'Leak', 'Over', 'Under', 'Semi'],
                datasets: [{
                    data: [correct, leak, over, under, semi],
                    backgroundColor: ['#4CAF50', '#F44336', '#FFC107', '#FF9800', '#FFB74D']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                aspectRatio: 2,
                plugins: {
                    legend: {
                        position: 'right'
                    },
                    title: {
                        display: true,
                        text: 'Redaction Status Distribution'
                    }
                }
            }
        });
    } else {
        // Show message when no data
        ctxRedaction.canvas.parentElement.innerHTML = '<p style="text-align: center; color: #888;">No redaction data available</p>';
    }
}

function exportJSON() {
    window.location.href = `/api/export/${evaluationId}/json`;
}

function exportPDF() {
    window.location.href = `/api/export/${evaluationId}/pdf`;
}

// ============= AI Summary Functions =============

async function checkAISummary() {
    try {
        const response = await fetch(`/api/evaluation/${evaluationId}/ai-summary`);
        if (response.ok) {
            const data = await response.json();
            displayAISummary(data.summary);
        } else {
            // No AI summary exists, show generate button
            document.getElementById('generateAIBtn').style.display = 'inline-block';
        }
    } catch (err) {
        // No AI summary, show generate button
        document.getElementById('generateAIBtn').style.display = 'inline-block';
    }
}

async function generateAISummary(regenerate = false) {
    const panel = document.getElementById('aiSummaryPanel');
    const loading = document.getElementById('aiLoading');
    const error = document.getElementById('aiError');
    const generateBtn = document.getElementById('generateAIBtn');
    
    // Show panel and loading state
    panel.style.display = 'block';
    loading.style.display = 'block';
    error.style.display = 'none';
    generateBtn.style.display = 'none';
    
    try {
        const response = await fetch(`/api/evaluation/${evaluationId}/generate-summary`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to generate AI summary');
        }
        
        const summary = await response.json();
        loading.style.display = 'none';
        displayAISummary(summary);
        
    } catch (err) {
        loading.style.display = 'none';
        error.style.display = 'block';
        error.innerHTML = `<strong>Error:</strong> ${err.message}<br><small>Make sure LLM service is enabled and API key is configured.</small>`;
    }
}

function displayAISummary(summary) {
    const panel = document.getElementById('aiSummaryPanel');
    const content = document.getElementById('aiSummaryContent');
    const quickInfo = document.getElementById('aiQuickInfo');
    
    // Show panel
    panel.style.display = 'block';
    
    // Set quick info (collapsed state)
    const issueCount = (summary.weaknesses?.length || 0) + 
                      (summary.recommendations?.filter(r => r.priority === 'high').length || 0);
    quickInfo.textContent = `Grade: ${summary.overall_grade} | Confidence: ${(summary.confidence_score * 100).toFixed(0)}% | ${issueCount} critical issues`;
    
    // Build detailed content
    let html = '';
    
    // Overall Assessment
    html += `
        <div class="ai-section">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                <span class="ai-grade grade-${summary.overall_grade?.toLowerCase() || 'c'}">${summary.overall_grade || 'N/A'}</span>
                <span style="color: #666;">Confidence: ${(summary.confidence_score * 100).toFixed(0)}%</span>
            </div>
            <p style="font-size: 1.05rem; color: #2c3e50; line-height: 1.8;">${summary.summary || 'No summary available'}</p>
        </div>
    `;
    
    // Strengths
    if (summary.strengths && summary.strengths.length > 0) {
        html += `
            <div class="ai-section">
                <h4>Strengths</h4>
                <ul class="ai-list">
                    ${summary.strengths.map(s => `<li>${s}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    // Weaknesses
    if (summary.weaknesses && summary.weaknesses.length > 0) {
        html += `
            <div class="ai-section">
                <h4>Weaknesses</h4>
                <ul class="ai-list">
                    ${summary.weaknesses.map(w => `<li>${w}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    // Recommendations
    if (summary.recommendations && summary.recommendations.length > 0) {
        html += `
            <div class="ai-section">
                <h4>Recommendations</h4>
        `;
        
        summary.recommendations.forEach(rec => {
            html += `
                <div class="ai-recommendation priority-${rec.priority}">
                    <div style="margin-bottom: 0.5rem;">
                        <span class="priority-badge priority-${rec.priority}">${rec.priority}</span>
                        <span style="margin-left: 0.5rem; color: #666; font-size: 0.9rem;">${rec.category}</span>
                    </div>
                    <div style="font-weight: bold; color: #2c3e50; margin-bottom: 0.5rem;">${rec.recommendation}</div>
                    <div style="color: #666; font-size: 0.95rem; margin-bottom: 0.25rem;"><strong>Why:</strong> ${rec.justification}</div>
                    <div style="color: #666; font-size: 0.95rem;"><strong>Impact:</strong> ${rec.expected_impact}</div>
                </div>
            `;
        });
        
        html += `</div>`;
    }
    
    // Entity Insights
    if (summary.entity_insights && Object.keys(summary.entity_insights).length > 0) {
        html += `
            <div class="ai-section">
                <h4>Per-Entity Analysis</h4>
        `;
        
        for (const [entityType, insight] of Object.entries(summary.entity_insights)) {
            html += `
                <div class="entity-insight">
                    <strong>${entityType}:</strong> ${insight}
                </div>
            `;
        }
        
        html += `</div>`;
    }
    
    // Redaction Analysis
    if (summary.redaction_analysis) {
        html += `
            <div class="ai-section">
                <h4>Redaction Quality Assessment</h4>
                <p style="color: #555; line-height: 1.6;">${summary.redaction_analysis}</p>
            </div>
        `;
    }
    
    content.innerHTML = html;
    
    // Expand panel by default after generation
    panel.classList.remove('collapsed');
    
    // Save state
    sessionStorage.setItem(`aiPanel_${evaluationId}`, 'expanded');
}

function toggleAIPanel() {
    const panel = document.getElementById('aiSummaryPanel');
    panel.classList.toggle('collapsed');
    
    // Save state
    const state = panel.classList.contains('collapsed') ? 'collapsed' : 'expanded';
    sessionStorage.setItem(`aiPanel_${evaluationId}`, state);
}

function exportAISummary() {
    // This could be extended to generate a PDF with just AI insights
    alert('AI Summary export feature - coming soon!');
}

// Restore AI panel state from session storage
window.addEventListener('load', () => {
    const savedState = sessionStorage.getItem(`aiPanel_${evaluationId}`);
    if (savedState === 'collapsed') {
        document.getElementById('aiSummaryPanel')?.classList.add('collapsed');
    }
});

