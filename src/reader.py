import os
from logger import logger

def read_text_files(root_path, max_file_size_kb=50):
    """
    Walks the root folder and reads the content of text and code files.
    Skips files larger than 'max_file_size_kb'.
    Returns a dictionary: { 'file_name': 'file_content' }
    """
    text_files = {}

    # File extensions we want to read
    allowed_extensions = ('.py', '.txt', '.md', '.js')

    max_bytes = max_file_size_kb * 1024 # Convert KB to bytes

    # os.walk goes through all subfolders automatically
    for root, _, files in os.walk(root_path):
        for file in files:
            if file.endswith(allowed_extensions): # Check the file extension
                file_path = os.path.join(root, file) # Join the folder path with the file name

                file_size = os.path.getsize(file_path) # Check the size before opening the file

                if file_size > max_bytes:
                    logger.warning(f"File {file_path} skipped for exceeding the size limit: ({file_size/1024:.1f} KB).")
                    continue # Go to the next file

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        # Keep the relative path so the LLM understands the structure
                        relative_path = os.path.relpath(file_path, root_path) # Path relative to the root folder
                        text_files[relative_path] = f.read()
                        logger.info(f"File read successfully: {relative_path}")
                except Exception as e:
                    logger.error(f"Error reading {file_path}: {e}")

    return text_files
