from genericpath import isfile
import logging
#import os
from pathlib import Path
from datetime import datetime

# Configure logger
logger = logging.getLogger('app_logger')
logger.setLevel(logging.INFO)

# Create handlers
log_file_path = Path('./Tests/', 'rmds.log')
if log_file_path.exists(): log_file_path.unlink()

# if it already exists, archive it
""" if log_file_path.exists():
    log_file_path.rename(log_file_path.stem 
                         + datetime.now().strftime("%Y%m%d.%H%M%S")
                         + ".log")
"""
# file_handler will initiate a new log file
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.INFO)

# Create formatters and add them to handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)

