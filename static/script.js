const folderName = document.getElementById('folderName');
const progressSection = document.getElementById('progressSection');
const progressPercent = document.getElementById('progressPercent');
const progressPercentRight = document.getElementById('progressPercentRight');
const progressFill = document.getElementById('progressFill');
const getTxtBtn = document.getElementById('getTxtBtn');
const resultInfo = document.getElementById('resultInfo');

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
        alert('Ошибка при выборе папки');
    }
}

async function startProcessing() {
    progressSection.style.display = 'block';
    getTxtBtn.disabled = true;
    resultInfo.textContent = '';
    
    try {
        await fetch('/api/process');
        pollProgress();
    } catch (error) {
        alert('Ошибка при запуске');
    }
}

function pollProgress() {
    const interval = setInterval(async () => {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            
            updateProgress(data.value);
            
            if (data.status === 'done' && data.result) {
                clearInterval(interval);
                getTxtBtn.disabled = false;
                const r = data.result;
                resultInfo.innerHTML = `
                    ✅ Готово!<br>
                    📊 Всего: ${r.total}<br>
                    ✅ Хороших: ${r.good}<br>
                    ❌ Плохих: ${r.bad}
                `;
            } else if (data.status === 'error') {
                clearInterval(interval);
                resultInfo.textContent = '❌ Ошибка: ' + data.error;
            }
        } catch (error) {
            clearInterval(interval);
        }
    }, 500);
}

function updateProgress(percent) {
    progressPercent.textContent = percent;
    progressPercentRight.textContent = percent + '%';
    progressFill.style.width = percent + '%';
}

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
            resultInfo.innerHTML += '<br>✅ Файл скачан!';
        }
    } catch (error) {
        alert('Ошибка скачивания');
    }
}