from pathlib import Path


def save_lines(lines: list[str], output_path: Path) -> None:
    """
    Сохраняет список строк в txt-файл.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        for line in lines:
            file.write(line + "\n")