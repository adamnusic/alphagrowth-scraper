#!/usr/bin/env python3
import os
import shutil
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_data_directory():
    """Set up the data directory and copy files to the correct location."""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(script_dir)
    project_root = os.path.dirname(os.path.dirname(backend_dir))
    
    # Define source and destination directories
    source_dirs = [
        os.path.join(project_root, 'data'),  # Root data directory
        os.path.join(backend_dir, 'data'),   # Backend data directory
    ]
    
    # Define destination directories in order of preference
    dest_dirs = [
        os.path.join(backend_dir, 'data'),  # Local development
        '/opt/render/project/src/alphagrowth-visualizer/backend/data',  # Render deployment backend
        '/opt/render/project/src/alphagrowth-visualizer/data',  # Render deployment root
        '/opt/render/project/src/data',  # Root data directory
    ]
    
    # Required files
    required_files = ['participants_data.json', 'network_data.json', 'total_spaces.txt']
    
    # Find source files
    source_files = {}
    for source_dir in source_dirs:
        if os.path.exists(source_dir):
            logger.info(f"Checking source directory: {source_dir}")
            for file in required_files:
                file_path = os.path.join(source_dir, file)
                if os.path.exists(file_path):
                    source_files[file] = file_path
                    logger.info(f"Found {file} at {file_path}")
    
    if not source_files:
        logger.error("No source files found!")
        return False
    
    # Copy files to destination directories
    for dest_dir in dest_dirs:
        if not os.path.exists(dest_dir):
            try:
                os.makedirs(dest_dir)
                logger.info(f"Created directory: {dest_dir}")
            except Exception as e:
                logger.error(f"Failed to create directory {dest_dir}: {str(e)}")
                continue
        
        # Copy each file
        for file, source_path in source_files.items():
            dest_path = os.path.join(dest_dir, file)
            try:
                shutil.copy2(source_path, dest_path)
                logger.info(f"Copied {file} to {dest_path}")
            except Exception as e:
                logger.error(f"Failed to copy {file} to {dest_path}: {str(e)}")
    
    return True

if __name__ == '__main__':
    logger.info("Starting data directory setup...")
    if setup_data_directory():
        logger.info("Data directory setup completed successfully!")
    else:
        logger.error("Data directory setup failed!")
        exit(1) 