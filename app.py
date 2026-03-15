import webview
import threading
from flask import Flask, render_template, jsonify
import time
import os
from PIL import Image

app = Flask(__name__)
progress_state = {'value': 0, 'status': 'idle'}
selected_folder_path = None

class API:
    def select_folder(self):
        """Открывает диалог выбора папки"""
        global selected_folder_path
        try:
            folder = webview.windows[0].create_file_dialog(
                webview.FOLDER_DIALOG,
                directory=os.path.expanduser('~')
            )
            if folder and len(folder) > 0:
                selected_folder_path = folder[0]
                return {'success': True, 'path': selected_folder_path, 'name': os.path.basename(selected_folder_path)}
            return {'success': False, 'error': 'No folder selected'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/process')
def process():
    """Обработка фото в папке"""
    global progress_state, selected_folder_path
    
    if not selected_folder_path or not os.path.isdir(selected_folder_path):
        return jsonify({'error': 'Folder not selected or invalid'}), 400
    
    progress_state = {'value': 0, 'status': 'processing'}
    
    def process_photos():
        global progress_state
        
        try:
            # Находим все изображения
            image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
            image_files = []
            
            for root, dirs, files in os.walk(selected_folder_path):
                for file in files:
                    if file.lower().endswith(image_extensions):
                        image_files.append(os.path.join(root, file))
            
            good_photos = []
            total = len(image_files)
            
            # Обрабатываем каждое фото
            for idx, img_path in enumerate(image_files):
                try:
                    # Простая логика: считаем хорошими фото больше 1MP
                    with Image.open(img_path) as img:
                        if img.size[0] * img.size[1] > 1000000:  # 1 мегапиксель
                            good_photos.append(os.path.basename(img_path))
                except Exception as e:
                    print(f"Error processing {img_path}: {e}")
                    pass
                
                # Обновляем прогресс
                progress_state['value'] = int((idx + 1) / total * 100) if total > 0 else 100
            
            # Сохраняем результат
            progress_state['status'] = 'done'
            progress_state['result'] = {
                'total': total,
                'good': len(good_photos),
                'photos': good_photos
            }
        except Exception as e:
            progress_state['status'] = 'error'
            progress_state['error'] = str(e)
    
    threading.Thread(target=process_photos, daemon=True).start()
    return jsonify({'message': 'Processing started'})

@app.route('/api/status')
def get_status():
    return jsonify(progress_state)

@app.route('/api/download_txt')
def download_txt():
    if progress_state.get('status') == 'done':
        photos = progress_state.get('result', {}).get('photos', [])
        content = '\n'.join(photos)
        return jsonify({
            'content': content,
            'filename': 'good_photos.txt'
        })
    return jsonify({'error': 'Processing not complete'}), 400

def start_flask():
    app.run(host='127.0.0.1', port=5000)

if __name__ == '__main__':
    api = API()
    
    threading.Thread(target=start_flask, daemon=True).start()
    time.sleep(1)
    
    window = webview.create_window(
        'Frame App',
        'http://127.0.0.1:5000',
        js_api=api,
        width=900,
        height=700,
        resizable=True
    )
    
    webview.start()