// File upload and form handling
// Handles file selection, validation, and POST to /api/evaluate

document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    
    loading.style.display = 'block';
    error.style.display = 'none';
    
    try {
        const originalFile = document.getElementById('originalFile').files[0];
        const redactedFile = document.getElementById('redactedFile').files[0];
        const groundTruthFile = document.getElementById('groundTruthFile').files[0];
        const predictionsFile = document.getElementById('predictionsFile').files[0];
        const mode = document.getElementById('mode').value;
        const modelName = document.getElementById('modelName').value || 'Default';
        
        if (!originalFile || !redactedFile || !groundTruthFile || !predictionsFile) {
            throw new Error('Please select all required files');
        }
        
        // Read files
        const originalText = await readTextFile(originalFile);
        const redactedText = await readTextFile(redactedFile);
        const groundTruthStr = await readTextFile(groundTruthFile);
        const predictionsStr = await readTextFile(predictionsFile);
        
        // Parse JSON
        let groundTruth, predictions;
        try {
            groundTruth = JSON.parse(groundTruthStr);
            predictions = JSON.parse(predictionsStr);
        } catch (e) {
            throw new Error('Invalid JSON format: ' + e.message);
        }
        
        // Send request
        const response = await fetch('/api/evaluate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                original_text: originalText,
                redacted_text: redactedText,
                ground_truth: groundTruth,
                predictions: predictions,
                mode: mode,
                model_name: modelName
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Evaluation failed');
        }
        
        const result = await response.json();
        
        // Store result ID and redirect
        localStorage.setItem('lastEvaluationId', result.id);
        window.location.href = `results.html?id=${result.id}`;
        
    } catch (err) {
        error.textContent = err.message;
        error.style.display = 'block';
        loading.style.display = 'none';
    }
});

// Helper function to read text files
function readTextFile(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = (e) => reject(new Error('Failed to read file'));
        reader.readAsText(file);
    });
}

// Preview files before submission
async function previewFiles() {
    try {
        const originalFile = document.getElementById('originalFile').files[0];
        const redactedFile = document.getElementById('redactedFile').files[0];
        const groundTruthFile = document.getElementById('groundTruthFile').files[0];
        const predictionsFile = document.getElementById('predictionsFile').files[0];
        
        if (!originalFile || !redactedFile || !groundTruthFile || !predictionsFile) {
            alert('Please select all files first');
            return;
        }
        
        // Read files
        const originalText = await readTextFile(originalFile);
        const redactedText = await readTextFile(redactedFile);
        const groundTruthStr = await readTextFile(groundTruthFile);
        const predictionsStr = await readTextFile(predictionsFile);
        
        // Display previews
        document.getElementById('previewOriginal').textContent = originalText;
        document.getElementById('previewRedacted').textContent = redactedText;
        
        // Format JSON with highlighting
        try {
            const groundTruthObj = JSON.parse(groundTruthStr);
            const predictionsObj = JSON.parse(predictionsStr);
            
            document.getElementById('previewGroundTruth').textContent = JSON.stringify(groundTruthObj, null, 2);
            document.getElementById('previewPredictions').textContent = JSON.stringify(predictionsObj, null, 2);
        } catch (e) {
            document.getElementById('previewGroundTruth').textContent = 'Invalid JSON: ' + groundTruthStr;
            document.getElementById('previewPredictions').textContent = 'Invalid JSON: ' + predictionsStr;
        }
        
        // Show preview section
        document.getElementById('previewSection').style.display = 'block';
        
        // Scroll to preview
        document.getElementById('previewSection').scrollIntoView({ behavior: 'smooth' });
        
    } catch (err) {
        alert('Error previewing files: ' + err.message);
    }
}
