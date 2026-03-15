// Элементы DOM
const folderName = document.getElementById('folderName');
const progressSection = document.getElementById('progressSection');
const progressPercent = document.getElementById('progressPercent');
const progressPercentRight = document.getElementById('progressPercentRight');
const progressFill = document.getElementById('progressFill');
const getTxtBtn = document.getElementById('getTxtBtn');
const resultInfo = document.getElementById('resultInfo');

// Выбор папки через нативный диалог
async function selectFolder() {
    try {
        const result = await pywebview.api.select_folder();
        
        if (result.success) {
            folderName.textContent = `Папка: ${result.name}`;
            startProcessing();
        } else {
            alert('Ошибка: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Ошибка при выборе папки');
    }
}

// Запуск обработки
async function startProcessing() {
    progressSection.style.display = 'block';
    getTxtBtn.disabled = true;
    resultInfo.textContent = '';
    
    try {
        const response = await fetch('/api/process');
        const data = await response.json();
        
        if (data.error) {
            alert('Ошибка: ' + data.error);
            return;
        }
        
        pollProgress();
    } catch (error) {
        console.error('Error:', error);
        alert('Ошибка при запуске');
    }
}

// Опрос прогресса
function pollProgress() {
    const interval = setInterval(async () => {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            
            updateProgress(data.value);
            
            if (data.status === 'done') {
                clearInterval(interval);
                getTxtBtn.disabled = false;
                const result = data.result;
                resultInfo.textContent = `✅ Готово! Найдено: ${result.good} из ${result.total}`;
            } else if (data.status === 'error') {
                clearInterval(interval);
                resultInfo.textContent = '❌ Ошибка: ' + data.error;
            }
        } catch (error) {
            console.error('Poll error:', error);
            clearInterval(interval);
        }
    }, 500);
}

// Обновление прогресс-бара
function updateProgress(percent) {
    progressPercent.textContent = percent;
    progressPercentRight.textContent = percent + '%';
    progressFill.style.width = percent + '%';
}

// Скачивание TXT
async function getTxt() {
    try {
        const response = await fetch('/api/download_txt');
        const data = await response.json();
        
        if (data.content) {
            const blob = new Blob([data.content], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = data.filename || 'good_photos.txt';
            a.click();
            window.URL.revokeObjectURL(url);
            
            resultInfo.textContent = '✅ Файл скачан!';
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Ошибка скачивания');
    }
}