document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    
    loading.style.display = 'block';
    error.style.display = 'none';
    
    try {
        const files = {
            original: document.getElementById('originalFile').files[0],
            redacted: document.getElementById('redactedFile').files[0],
            groundTruth: document.getElementById('groundTruthFile').files[0],
            predictions: document.getElementById('predictionsFile').files[0]
        };
        
        if (!files.original || !files.redacted || !files.groundTruth || !files.predictions) {
            throw new Error('Please select all required files');
        }
        
        const [originalText, redactedText, groundTruthStr, predictionsStr] = await Promise.all([
            readTextFile(files.original),
            readTextFile(files.redacted),
            readTextFile(files.groundTruth),
            readTextFile(files.predictions)
        ]);
        
        let groundTruth, predictions;
        try {
            groundTruth = JSON.parse(groundTruthStr);
            predictions = JSON.parse(predictionsStr);
        } catch (e) {
            throw new Error('Invalid JSON format: ' + e.message);
        }
        
        const response = await fetch('/api/evaluate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                original_text: originalText,
                redacted_text: redactedText,
                ground_truth: groundTruth,
                predictions: predictions,
                mode: document.getElementById('mode').value,
                model_name: document.getElementById('modelName').value || 'Default'
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Evaluation failed');
        }
        
        const result = await response.json();
        localStorage.setItem('lastEvaluationId', result.id);
        window.location.href = `results.html?id=${result.id}`;
        
    } catch (err) {
        error.textContent = err.message;
        error.style.display = 'block';
        loading.style.display = 'none';
    }
});

// Update file name display when files are selected
document.getElementById('originalFile').addEventListener('change', function() {
    document.getElementById('originalFileName').textContent = this.files[0]?.name || 'No file chosen';
});

document.getElementById('redactedFile').addEventListener('change', function() {
    document.getElementById('redactedFileName').textContent = this.files[0]?.name || 'No file chosen';
});

document.getElementById('groundTruthFile').addEventListener('change', function() {
    document.getElementById('groundTruthFileName').textContent = this.files[0]?.name || 'No file chosen';
});

document.getElementById('predictionsFile').addEventListener('change', function() {
    document.getElementById('predictionsFileName').textContent = this.files[0]?.name || 'No file chosen';
});

function readTextFile(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = () => reject(new Error('Failed to read file'));
        reader.readAsText(file);
    });
}

async function previewFiles() {
    try {
        const files = {
            original: document.getElementById('originalFile').files[0],
            redacted: document.getElementById('redactedFile').files[0],
            groundTruth: document.getElementById('groundTruthFile').files[0],
            predictions: document.getElementById('predictionsFile').files[0]
        };
        
        if (!files.original || !files.redacted || !files.groundTruth || !files.predictions) {
            alert('Please select all files first');
            return;
        }
        
        const [originalText, redactedText, groundTruthStr, predictionsStr] = await Promise.all([
            readTextFile(files.original),
            readTextFile(files.redacted),
            readTextFile(files.groundTruth),
            readTextFile(files.predictions)
        ]);
        
        document.getElementById('previewOriginal').textContent = originalText;
        document.getElementById('previewRedacted').textContent = redactedText;
        
        try {
            document.getElementById('previewGroundTruth').textContent = JSON.stringify(JSON.parse(groundTruthStr), null, 2);
            document.getElementById('previewPredictions').textContent = JSON.stringify(JSON.parse(predictionsStr), null, 2);
        } catch (e) {
            document.getElementById('previewGroundTruth').textContent = 'Invalid JSON: ' + groundTruthStr;
            document.getElementById('previewPredictions').textContent = 'Invalid JSON: ' + predictionsStr;
        }
        
        document.getElementById('previewSection').style.display = 'block';
        document.getElementById('previewSection').scrollIntoView({ behavior: 'smooth' });
        
    } catch (err) {
        alert('Error previewing files: ' + err.message);
    }
}
