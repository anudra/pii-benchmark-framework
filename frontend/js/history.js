let selectedEvaluations = [];

loadHistory();

async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        if (!response.ok) throw new Error('Failed to load history');
        
        const history = await response.json();
        const tbody = document.getElementById('historyBody');
        if (history.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;">No evaluations yet</td></tr>';
            return;
        }
        
        tbody.innerHTML = history.map(item => {
            const detectionAccuracy = (item.accuracy * 100).toFixed(2);
            
            // Calculate redaction accuracy
            let redactionAccuracy = '0.00';
            if (item.redaction_analysis) {
                if (item.redaction_analysis.summary) {
                    const summary = item.redaction_analysis.summary;
                    if (summary.redaction_quality_score !== undefined) {
                        redactionAccuracy = (summary.redaction_quality_score * 100).toFixed(2);
                    } else if (summary.total_entities > 0) {
                        redactionAccuracy = ((summary.correct_redactions / summary.total_entities) * 100).toFixed(2);
                    }
                }
            }
            
            return `
            <tr>
                <td><input type="checkbox" class="eval-checkbox" value="${item.id}" /></td>
                <td>${item.id}</td>
                <td>${new Date(item.timestamp).toLocaleString()}</td>
                <td>${item.model_name}</td>
                <td>${item.mode}</td>
                <td style="color: #4CAF50; font-weight: bold;">${detectionAccuracy}%</td>
                <td style="color: #FF9800; font-weight: bold;">${redactionAccuracy}%</td>
                <td>
                    <button onclick="viewResults(${item.id})" class="btn-primary" style="padding: 0.5rem 1rem; margin-right: 0.5rem;">View</button>
                    <button onclick="deleteEvaluation(${item.id})" class="btn-secondary" style="padding: 0.5rem 1rem; background-color: #dc3545;">Delete</button>
                </td>
            </tr>
            `;
        }).join('');
        
        // Setup checkbox listeners
        document.querySelectorAll('.eval-checkbox').forEach(cb => {
            cb.addEventListener('change', updateSelection);
        });
        
    } catch (err) {
        alert('Error loading history: ' + err.message);
    }
}

function updateSelection() {
    selectedEvaluations = Array.from(document.querySelectorAll('.eval-checkbox:checked')).map(cb => cb.value);
    
    const compareSection = document.getElementById('compareSection');
    if (selectedEvaluations.length === 2) {
        compareSection.style.display = 'block';
    } else {
        compareSection.style.display = 'none';
    }
}

function viewResults(id) {
    window.location.href = `results.html?id=${id}`;
}

async function deleteEvaluation(id) {
    if (!confirm('Are you sure you want to delete this evaluation?')) return;
    
    try {
        const response = await fetch(`/api/evaluation/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to delete');
        
        loadHistory();
    } catch (err) {
        alert('Error deleting evaluation: ' + err.message);
    }
}

function compareSelected() {
    if (selectedEvaluations.length !== 2) {
        alert('Please select exactly 2 evaluations to compare');
        return;
    }
    window.location.href = `compare.html?id1=${selectedEvaluations[0]}&id2=${selectedEvaluations[1]}`;
}

function clearSelection() {
    document.querySelectorAll('.eval-checkbox').forEach(cb => cb.checked = false);
    updateSelection();
}
