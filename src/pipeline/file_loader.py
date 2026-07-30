import os
from src.config.constants import RAW_DATA_DIR
import shutil
from typing import Union, Optional, IO



def save_uploaded_file(file: Union[str, IO]) -> Optional[str]:
    """
    :param file: Either a string path or a file-like object from Gradio.
    :return: Path to saved file inside data/raw/.
    """

    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    # Case 1: file is a string path (CLI usage)
    if isinstance(file, str): # checks if file is a string type

        #CLI path
        filename = os.path.basename(file)
        destination_path = os.path.join(RAW_DATA_DIR, filename)
        shutil.copy2(file, destination_path)
        return destination_path

    # Case 2: file is like a file object
    elif hasattr(file, "name"): # Checks is file has a file.name attribute, which is typical for file-like objects

        filename = os.path.basename(file.name)
        destination_path = os.path.join(RAW_DATA_DIR, filename)

        with open(destination_path, 'wb') as f:
            f.write(file.read())

        return destination_path

    else:
        raise ValueError("Invalid file input. Must be a string path or a file-like object.")


