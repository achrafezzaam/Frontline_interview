#!/usr/bin/env python3

import os
import yaml
import logging
from src.database import DatabaseHandler
import src.file_handler as fh
import src.logger as logger

def load_config():
    """Loads the configuration from config.yaml."""
    # The __file__ trick gets the directory of the currently running script
    basedir = os.path.abspath(os.path.dirname(__file__))
    config_path = os.path.join(basedir, 'config.yaml')
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("Error: config.yaml not found. Please create it.")
        return None
    except Exception as e:
        print(f"Error loading config.yaml: {e}")
        return None

def main():
    """Main function to run the file archiver application."""
    config = load_config()
    if not config:
        return

    # Set up logging
    logger.setup_logger(config['log_file'])
    logging.info("Application starting...")

    # Instantiate and connect to the database
    db_handler = DatabaseHandler(config['database_name'])
    
    try:
        if not db_handler.connect():
            logging.critical("Could not connect to the database. Exiting.")
            return
        
        # Ensure the database table is set up
        db_handler.setup_table()

        # --- Main Application Loop ---
        exit_loop = False
        while not exit_loop:
            print("\n--- File Archiver Menu ---")
            print("1. Scan for and archive inactive files")
            print("2. Purge old archived files (delete them)")
            print("3. List currently archived files")
            print("4. Restore an archived file")
            print("5. Force delete an archived file")
            print("0. Exit")
            
            entry = input("==> ")
            
            if entry == "1":
                logging.info("Starting file scan and archive process...")
                fh.scan_and_archive_files(db_handler, config)
            elif entry == "2":
                logging.info("Starting purge process for old files...")
                fh.purge_old_files(db_handler, config)
            elif entry == "3":
                files = db_handler.get_files_by_status('archived')
                print("\n--- Archived Files ---")
                if not files:
                    print("No files are currently in the archive.")
                else:
                    for file in files:
                        # file format: (id, file_path, status, date_archived)
                        print(f"  ID: {file[0]} | Path: {file[1]} | Archived on: {file[3]}")
                print("----------------------")
            elif entry == "4":
                file_id = input("Enter the ID of the file to restore: ")
                fh.restore_file(db_handler, config, file_id)
            elif entry == "5":
                file_id = input("Enter the ID of the file to delete: ")
                fh.delete_archived_file(db_handler, config, file_id)
            elif entry == "0":
                exit_loop = True
            else:
                print("Invalid entry. Please try again.")

    except Exception as e:
        logging.error(f"An unexpected error occurred in the main loop: {e}", exc_info=True)
    finally:
        # This ensures the database connection is always closed
        db_handler.close()
        logging.info("Application finished.")


if __name__ == "__main__":
    main()
