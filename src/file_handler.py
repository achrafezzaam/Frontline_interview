import os
import shutil
import logging
from datetime import datetime, timedelta

def find_inactive_files(directories, days_inactive):
    """
    Finds files in the given directories that haven't been modified recently.
    
    :param directories: A list of directory paths to scan.
    :param days_inactive: The threshold in days for a file to be considered inactive.
    :return: A list of full paths to inactive files.
    """
    inactive_files = []
    threshold = timedelta(days=days_inactive)
    now = datetime.now()

    for directory in directories:
        if not os.path.isdir(directory):
            logging.warning(f"Scan directory not found: {directory}")
            continue
        
        for root, _, files in os.walk(directory):
            for filename in files:
                file_path = os.path.join(root, filename)
                try:
                    modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if now - modified_time > threshold:
                        inactive_files.append(file_path)
                except FileNotFoundError:
                    logging.warning(f"File not found during scan: {file_path}")
                    continue
    return inactive_files

def scan_and_archive_files(db_handler, config):
    """
    Scans for inactive files and moves them to the archive directory,
    updating the database for each.
    """
    inactive_files = find_inactive_files(
        config['scan_directories'],
        config['days_until_archive']
    )
    
    archive_root = config['archive_directory']
    os.makedirs(archive_root, exist_ok=True)

    for file_path in inactive_files:
        try:
            # Move the file first
            filename = os.path.basename(file_path)
            destination_path = os.path.join(archive_root, filename)
            shutil.move(file_path, destination_path)
            
            # Check if the record already exists in the database
            existing_record = db_handler.get_file_by_path(file_path)

            if existing_record:
                # If it exists (e.g., it was restored), just update its status
                record_id = existing_record[0]
                db_handler.update_file_status(record_id, 'archived')
                logging.info(f"Re-archived '{file_path}' to '{destination_path}'")
            else:
                # If it's a new file, add a completely new record
                archive_date = datetime.now().isoformat()
                db_handler.add_file_record(file_path, 'archived', archive_date)
                logging.info(f"Archived new file '{file_path}' to '{destination_path}'")
            
        except Exception as e:
            logging.error(f"Failed to archive file {file_path}: {e}")

def purge_old_files(db_handler, config):
    """
    Finds files in the archive that are older than the deletion threshold
    and permanently deletes them.
    """
    archived_files = db_handler.get_files_by_status('archived')
    threshold = timedelta(days=config['days_until_delete'])
    now = datetime.now()
    
    for file_record in archived_files:
        file_id, original_path, _, date_archived_str = file_record
        
        try:
            if not date_archived_str:
                logging.warning(f"Skipping purge for file ID {file_id} due to missing archive date.")
                continue

            date_archived = datetime.fromisoformat(date_archived_str)
            if now - date_archived > threshold:
                filename = os.path.basename(original_path)
                archived_file_path = os.path.join(config['archive_directory'], filename)
                
                if os.path.exists(archived_file_path):
                    os.remove(archived_file_path)
                    logging.info(f"Deleted file from disk: {archived_file_path}")
                
                db_handler.remove_file_record(file_id)
        except Exception as e:
            logging.error(f"Failed to purge file with ID {file_id} ({original_path}): {e}")

def restore_file(db_handler, config, file_id):
    """Restores a single file from the archive to its original location."""
    file_record = db_handler.get_file_by_id(file_id)
    if not file_record:
        logging.error(f"Restore failed: No file found with ID {file_id}")
        return

    _, original_path, _, _ = file_record
    filename = os.path.basename(original_path)
    archived_file_path = os.path.join(config['archive_directory'], filename)
    original_dir = os.path.dirname(original_path)
    
    try:
        os.makedirs(original_dir, exist_ok=True)
        shutil.move(archived_file_path, original_path)
        
        # Update the modification time to now so it isn't immediately re-archived.
        os.utime(original_path, None)

        db_handler.update_file_status(file_id, 'restored')
        logging.info(f"Restored '{archived_file_path}' to '{original_path}'")
    except Exception as e:
        logging.error(f"Failed to restore file ID {file_id}: {e}")

def delete_archived_file(db_handler, config, file_id):
    """Force-deletes a file from the archive and the database."""
    file_record = db_handler.get_file_by_id(file_id)
    if not file_record:
        logging.error(f"Delete failed: No file found with ID {file_id}")
        return
        
    _, original_path, _, _ = file_record
    filename = os.path.basename(original_path)
    archived_file_path = os.path.join(config['archive_directory'], filename)

    try:
        if os.path.exists(archived_file_path):
            os.remove(archived_file_path)
        db_handler.remove_file_record(file_id)
        logging.info(f"Force-deleted file ID {file_id} ({archived_file_path})")
    except Exception as e:
        logging.error(f"Failed to force-delete file ID {file_id}: {e}")