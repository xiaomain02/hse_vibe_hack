from pathlib import Path

def save_lines(lines, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(", ".join(lines))