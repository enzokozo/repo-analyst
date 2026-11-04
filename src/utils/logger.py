import logging
import os
from datetime import datetime

def setup_logger():
    # Make sure the logs folder exists
    log_dir = "data/logs"
    os.makedirs(log_dir, exist_ok=True)

    # Create a file named with today's date
    log_filename = datetime.now().strftime("%Y-%m-%d_run.log")
    log_filepath = os.path.join(log_dir, log_filename)

    # Message format: Date/Time - Level - Message
    log_format = "%(asctime)s - %(levelname)s - %(message)s"

    # Configure the logger
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(log_filepath, encoding="utf-8"), # Write to the log file
            logging.StreamHandler() # Show in the terminal
        ]
    )

    return logging.getLogger(__name__)

# Keep a logger instance ready for the other files
logger = setup_logger()
