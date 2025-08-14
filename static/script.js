document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('upload-form');
    const loader = document.getElementById('loader');
    const resultContainer = document.getElementById('result-container');
    const resultDiv = document.getElementById('result');
    const historyDiv = document.getElementById('history');
    const fileInput = document.getElementById('pdf-file');
    const API_BASE_URL = 'http://127.0.0.1:8000';

    async function loadHistory() {
        try {
            const response = await fetch(`${API_BASE_URL}/history/`);
            if (!response.ok) {
                throw new Error('Unable to load history.');
            }
            const data = await response.json();
            historyDiv.innerHTML = '';
            if (data.length === 0) {
                historyDiv.innerHTML = '<p>The history is currently empty.</p>';
                return;
            }
            data.forEach(item => {
                const historyItem = document.createElement('div');
                historyItem.className = 'history-item';
                historyItem.innerHTML = `<strong>${item.filename}</strong>`;
                historyDiv.appendChild(historyItem);
            });
        } catch (error) {
            historyDiv.innerHTML = `<p class="error">${error.message}</p>`;
        }
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (!fileInput.files || fileInput.files.length === 0) {
            resultDiv.innerHTML = `<p class="error">Please select a file.</p>`;
            resultContainer.classList.remove('hidden');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        loader.classList.remove('hidden');
        resultContainer.classList.add('hidden');
        resultDiv.innerHTML = '';

        try {
            const response = await fetch(`${API_BASE_URL}/upload/`, {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                const errorMessage = data.message ||
                                   data.detail?.message ||
                                   data.detail ||
                                   data.error ||
                                   'An unknown error has occurred.';
                throw new Error(errorMessage);
            }

            resultDiv.innerHTML = `<p>${data.summary.replace(/\n/g, '<br>')}</p>`;
            resultContainer.classList.remove('hidden');
            loadHistory();

        } catch (error) {
            resultDiv.innerHTML = `<p class="error">Error: ${error.message}</p>`;
            resultContainer.classList.remove('hidden');
        } finally {
            loader.classList.add('hidden');
            form.reset();
        }
    });

    loadHistory();
});