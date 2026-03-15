import os
import threading
import time
from pathlib import Path
 
import webview
from flask import Flask, jsonify, render_template
 
from core.pipeline import analyze_folder
 
app = Flask(__name__)
 
progress_state = {
    "value": 0,
    "status": "idle",
    "result": None,
    "error": None,
}
 
selected_folder_path = None
 
 
class API:
    def select_folder(self):
        """Открывает диалог выбора папки."""
        global selected_folder_path
 
        try:
            folder = webview.windows[0].create_file_dialog(
                webview.FOLDER_DIALOG,
                directory=os.path.expanduser("~"),
            )
 
            if folder and len(folder) > 0:
                selected_folder_path = folder[0]
                return {
                    "success": True,
                    "path": selected_folder_path,
                    "name": os.path.basename(selected_folder_path),
                }
 
            return {"success": False, "error": "No folder selected"}
 
        except Exception as e:
            return {"success": False, "error": str(e)}
 
 
@app.route("/")
def index():
    return render_template("index.html")
 
 
@app.route("/api/process")
def process():
    """Запускает анализ папки через backend pipeline."""
    global progress_state, selected_folder_path
 
    if not selected_folder_path or not os.path.isdir(selected_folder_path):
        return jsonify({"error": "Folder not selected or invalid"}), 400
 
    progress_state = {
        "value": 0,
        "status": "processing",
        "result": None,
        "error": None,
    }
 
    def process_photos():
        global progress_state
 
        try:
            progress_state["value"] = 10
 
            result = analyze_folder(selected_folder_path)
 
            progress_state["value"] = 100
            progress_state["status"] = "done"
            progress_state["result"] = result
 
        except Exception as e:
            progress_state["status"] = "error"
            progress_state["error"] = str(e)
 
    threading.Thread(target=process_photos, daemon=True).start()
    return jsonify({"message": "Processing started"})
 
 
@app.route("/api/status")
def get_status():
    return jsonify(progress_state)
 
 
@app.route("/api/download_txt")
def download_txt():
    """Возвращает содержимое готового good_photos.txt."""
    if progress_state.get("status") != "done":
        return jsonify({"error": "Processing not complete"}), 400
 
    result = progress_state.get("result")
    if not result:
        return jsonify({"error": "No result available"}), 400
 
    good_txt_path = result.get("good_txt")
    if not good_txt_path:
        return jsonify({"error": "good_txt path not found"}), 400
 
    txt_file = Path(good_txt_path)
 
    if not txt_file.exists():
        return jsonify({"error": "TXT file not found"}), 404
 
    content = txt_file.read_text(encoding="utf-8")
 
    return jsonify({
        "content": content,
        "filename": txt_file.name,
    })
 
 
def start_flask():
    app.run(host="127.0.0.1", port=5000)
 
 
def run_app():
    api = API()
 
    threading.Thread(target=start_flask, daemon=True).start()
    time.sleep(1)
 
    webview.create_window(
        "Frame App",
        "http://127.0.0.1:5000",
        js_api=api,
        width=900,
        height=700,
        resizable=True,
    )
 
    webview.start()
 
 
if __name__ == "__main__":
    run_app()