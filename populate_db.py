#!/usr/bin/env python3

import os
import yaml
import logging
import sys
from src.database import DatabaseHandler

def setup_console_logger():
    """Sets up a simple logger to print messages to the console."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if not logger.hasHandlers():
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

def load_config():
    """Loads the configuration from config.yaml."""
    basedir = os.path.abspath(os.path.dirname(__file__))
    config_path = os.path.join(basedir, 'config.yaml')
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logging.error("FATAL: config.yaml not found. Please ensure it exists in the project root.")
        return None
    except Exception as e:
        logging.error(f"FATAL: Error loading or parsing config.yaml: {e}")
        return None

def populate_from_directories(db_handler, config):
    """
    Scans directories from the config file and adds a record for each file
    to the database with an 'active' status.
    """
    scan_dirs = config.get('scan_directories', [])
    if not scan_dirs:
        logging.warning("No 'scan_directories' found in config.yaml. Nothing to populate.")
        return

    logging.info(f"Starting scan of directories: {scan_dirs}")
    files_added = 0
    files_skipped = 0

    for directory in scan_dirs:
        # Check if the directory exists before trying to scan it
        if not os.path.isdir(directory):
            logging.warning(f"Directory '{directory}' not found. Skipping.")
            continue

        # os.walk is great for recursively finding all files in a directory tree
        for root, _, files in os.walk(directory):
            for filename in files:
                # Get the full, absolute path of the file
                full_path = os.path.abspath(os.path.join(root, filename))
                
                # The add_file_record method returns the ID of the new row, or None on failure
                # We set the initial status to 'active' and date_archived to None
                result = db_handler.add_file_record(full_path, 'active', None)
                
                if result is not None:
                    files_added += 1
                else:
                    # This typically happens if the file already exists in the DB
                    # due to the UNIQUE constraint on the file_path column.
                    files_skipped += 1
    
    logging.info(f"Population complete. Added: {files_added} new files. Skipped: {files_skipped} (already exist).")


def main():
    """Main function to run the database population script."""
    setup_console_logger()
    
    config = load_config()
    if not config:
        return # Exit if config loading failed

    db_handler = DatabaseHandler(config['database_name'])
    
    try:
        if not db_handler.connect():
            # The connect method already logs the specific error
            logging.critical("Could not connect to the database. Aborting script.")
            return
        
        # Ensure the table exists before we try to add data to it
        db_handler.setup_table()
        
        # Run the main population logic
        populate_from_directories(db_handler, config)

    except Exception as e:
        logging.critical(f"An unexpected error occurred during the script's execution: {e}", exc_info=True)
    finally:
        # This 'finally' block ensures that the database connection is
        # always closed, even if errors occurred.
        logging.info("Closing database connection.")
        db_handler.close()


if __name__ == "__main__":
    main()
