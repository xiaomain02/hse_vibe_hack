let pollInterval = null;

async function selectFolder() {
    try {
        const result = await window.pywebview.api.select_folder();

        if (result.success) {
            document.getElementById("folderName").textContent = `Папка: ${result.name}`;
            document.getElementById("resultInfo").textContent = "";
            document.getElementById("getTxtBtn").disabled = true;

            await startProcessing();
        } else {
            alert(result.error || "Папка не выбрана");
        }
    } catch (error) {
        alert("Ошибка выбора папки: " + error);
    }
}

async function startProcessing() {
    try {
        document.getElementById("progressSection").style.display = "block";
        document.getElementById("getTxtBtn").disabled = true;
        document.getElementById("resultInfo").textContent = "";

        const response = await fetch("/api/process");
        const data = await response.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        pollStatus();
    } catch (error) {
        alert("Ошибка запуска обработки: " + error);
    }
}

function pollStatus() {
    if (pollInterval) {
        clearInterval(pollInterval);
    }

    pollInterval = setInterval(async () => {
        try {
            const response = await fetch("/api/status");
            const data = await response.json();

            const progress = data.value || 0;
            document.getElementById("progressPercent").textContent = progress;
            document.getElementById("progressPercentRight").textContent = `${progress}%`;
            document.getElementById("progressFill").style.width = `${progress}%`;

            if (data.status === "done") {
                clearInterval(pollInterval);

                const result = data.result || {};
                const total = result.total ?? 0;
                const good = result.good ?? 0;
                const bad = result.bad ?? 0;

                document.getElementById("getTxtBtn").disabled = false;
                document.getElementById("resultInfo").innerHTML = `
                    ✅ Готово!<br>
                    📊 Всего: ${total}<br>
                    ✅ Хороших: ${good}<br>
                    ❌ Плохих: ${bad}
                `;
            }

            if (data.status === "error") {
                clearInterval(pollInterval);
                document.getElementById("resultInfo").textContent =
                    "Ошибка: " + (data.error || "Unknown error");
            }
        } catch (error) {
            clearInterval(pollInterval);
            document.getElementById("resultInfo").textContent =
                "Ошибка при получении статуса: " + error;
        }
    }, 1000);
}

async function getTxt() {
    try {
        const response = await fetch("/api/download_txt");
        const data = await response.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        const saveResult = await window.pywebview.api.save_good_txt(data.path);

        if (!saveResult.success) {
            alert(saveResult.error || "Не удалось сохранить файл");
            return;
        }

        document.getElementById("resultInfo").innerHTML += `
            <br>📥 Файл сохранён: ${saveResult.filename}
            <br>📂 Путь: ${saveResult.saved_to}
        `;
    } catch (error) {
        alert("Ошибка сохранения TXT: " + error);
    }
}