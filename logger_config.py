import logging
import os

# Configure logger
logger = logging.getLogger('app_logger')
logger.setLevel(logging.INFO)

# Create handlers
log_file_path = os.path.join('./', 'armds.log')
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.INFO)

# Create formatters and add them to handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)

