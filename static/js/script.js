document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    
    try {
        const response = await fetch('/convert', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert(data.error);
            return;
        }
        
        // Show result
        document.getElementById('result').classList.remove('hidden');
        document.getElementById('resultText').textContent = data.result;
        document.getElementById('downloadBtn').href = `/download/${data.filename}`;
        
    } catch (error) {
        alert('An error occurred during conversion');
        console.error(error);
    }
});

document.getElementById('copyBtn').addEventListener('click', () => {
    const resultText = document.getElementById('resultText').textContent;
    navigator.clipboard.writeText(resultText).then(() => {
        alert('Copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy text: ', err);
    });
}); 