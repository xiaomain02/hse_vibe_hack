# 📸 Frame App

Frame App — это десктопное приложение для автоматического отбора неудачных фотографий.  
Оно анализирует изображения в выбранной папке и разделяет их на **хорошие** и **плохие** на основе алгоритмов компьютерного зрения.

Проект предназначен для фотографов, которые работают с большими наборами изображений и хотят быстро отсеять брак.

---

# 🚀 Возможности

Frame App автоматически проверяет фотографии на:

- 🔍 **Размытие изображения** (blur detection)
- 💡 **Пересветы** (blown highlights)
- 🙂 **Размытие лица** на портретах
- 📷 **Размытие всего изображения**, если лицо не обнаружено
- 📷 **Поддержку RAW-файлов** (`.NEF`, `.CR2`, `.ARW`, `.DNG`, `.RAF`, `.RW2`)

После анализа приложение создаёт отчёт:

- `good_photos.txt` — список хороших фотографий
- `bad_photos.txt` — список плохих фотографий с причинами

---

# 🖥 Интерфейс

Приложение имеет простой графический интерфейс:

1. Нажать **Select Folder**
2. Выбрать папку с фотографиями
3. Дождаться завершения анализа
4. Скачать список хороших фотографий (`.txt`)

---

# ⚙️ Используемые технологии

Проект построен на следующих технологиях:

- **Python**
- **OpenCV** — обработка изображений
- **MediaPipe** — детекция лиц
- **NumPy** — математические вычисления
- **RawPy** — обработка RAW-файлов
- **Flask** — backend для GUI
- **PyWebView** — desktop интерфейс

---

# 📂 Структура проекта

```
PhotoAnalyzer
│
├── core/            # Основная логика обработки
│   ├── pipeline.py
│   ├── file_utils.py
│   └── report.py
│
├── cv/              # CV алгоритмы
│   ├── analyzer.py
│   └── cv_processing.py
│
├── frontend/        # GUI
│   ├── app.py
│   └── templates/
│
├── app_platform/    # Конфигурация и запуск
│   ├── runner.py
│   └── config.py
│
├── requirements.txt
└── README.md
```

---

# 🛠 Установка

Клонировать репозиторий:

```bash
git clone https://github.com/xiaomain02/hse_vibe_hack
cd hse_vibe_hack
```

Создать виртуальное окружение:

```bash
python -m venv .venv
```

Активировать окружение

Windows:

```bash
.venv\Scripts\activate
```

Linux / Mac:

```bash
source .venv/bin/activate
```

Установить зависимости:

```bash
pip install -r requirements.txt
```

---

# ▶️ Запуск

### GUI режим

```bash
python -m app_platform.runner
```

После запуска откроется окно приложения.

---

### CLI режим

Можно запускать анализ папки напрямую:

```bash
python -m app_platform.runner --cli path_to_photos
```

Пример:

```bash
python -m app_platform.runner --cli C:\Photos
```

---

# 📄 Результаты анализа

После обработки создаются два файла:

```
good_photos.txt
bad_photos.txt
```

Пример `good_photos.txt`:

```
photo1.jpg, photo2.jpg, photo3.jpg
```

Пример `bad_photos.txt`:

```
photo4.jpg - quality_check_failed
photo5.jpg - cv_error
```

---

# 🧠 Как работает анализ

Алгоритм анализа состоит из нескольких этапов:

1. Проверка пересветов

```
detect_blown_highlights()
```

2. Детекция лиц с помощью MediaPipe

```
FaceDetection
```

3. Проверка размытия лица

```
variance_of_laplacian
tenengrad
```

4. Если лицо не найдено — проверка размытия всего изображения.

---

# 📷 Поддерживаемые форматы

Обычные изображения:

```
jpg
jpeg
png
bmp
tiff
nef
```

RAW форматы:

```
nef
cr2
arw
dng
raf
rw2
```

---

# 👥 Команда проекта

Проект разработан командой студентов.

Основные направления работы:

- Backend — обработка изображений и пайплайн
- Computer Vision — алгоритмы анализа фотографий
- Frontend — пользовательский интерфейс
- Platform / DevOps — конфигурация и запуск приложения