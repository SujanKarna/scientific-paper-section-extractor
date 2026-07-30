from src.config.constants import RAW_DATA_DIR
from pathlib import Path
import shutil

def save_uploaded_file(file):
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Case 1: Gradio file object (temp file path)
    if hasattr(file, "name"):
        src_path = Path(file.name)  # Gradio temp file path
        filename = src_path.name
        destination = RAW_DATA_DIR / filename

        shutil.copyfile(src_path, destination)
        return str(destination)

    # Case 2: CLI path
    if isinstance(file, str):
        src_path = Path(file)
        filename = src_path.name
        destination = RAW_DATA_DIR / filename

        shutil.copyfile(src_path, destination)
        return str(destination)

    raise ValueError("Invalid file input")
