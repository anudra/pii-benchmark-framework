// History table management
// Fetches and displays evaluation history, handles view/delete actions

let selectedEvaluations = [];

loadHistory();

async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        if (!response.ok) throw new Error('Failed to load history');
        
        const history = await response.json();
        
        const tbody = document.getElementById('historyBody');
        if (history.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;">No evaluations yet</td></tr>';
            return;
        }
        
        tbody.innerHTML = history.map(item => `
            <tr>
                <td><input type="checkbox" class="eval-checkbox" value="${item.id}" /></td>
                <td>${item.id}</td>
                <td>${new Date(item.timestamp).toLocaleString()}</td>
                <td>${item.model_name}</td>
                <td>${item.mode}</td>
                <td>${(item.accuracy * 100).toFixed(2)}%</td>
                <td>
                    <button onclick="viewResults(${item.id})" class="btn-primary" style="padding: 0.5rem 1rem; margin-right: 0.5rem;">View</button>
                    <button onclick="deleteEvaluation(${item.id})" class="btn-secondary" style="padding: 0.5rem 1rem; background-color: #dc3545;">Delete</button>
                </td>
            </tr>
        `).join('');
        
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
