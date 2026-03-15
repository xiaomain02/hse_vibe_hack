import os
import subprocess
from pathlib import Path
from  config import Config

def build_exe():
    """Сборка EXE через PyInstaller"""
    spec_path = Path('photo-analyzer.spec')
    
    if not spec_path.exists():
        print("❌ Создайте photo-analyzer.spec")
        return False
    
    cmd = ['pyinstaller', str(spec_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ EXE собран: dist/PhotoAnalyzer.exe")
        return True
    else:
        print("❌ Ошибка сборки:", result.stderr)
        return False

def build_portable_zip():
    """Portable ZIP архив"""
    exe_path = Path('dist') / 'PhotoAnalyzer.exe'
    if not exe_path.exists():
        print("❌ Сначала соберите EXE: make build")
        return
    
    version = Config.VERSION
    zip_name = f"PhotoAnalyzer_portable_v{version}.zip"
    
    cmd = ['powershell', '-Command', 
           f'Compress-Archive -Path dist\\PhotoAnalyzer.exe, README.md -DestinationPath {zip_name}']
    
    subprocess.run(cmd)
    print(f"✅ Portable ZIP: {zip_name}")

if __name__ == '__main__':
    build_exe()
