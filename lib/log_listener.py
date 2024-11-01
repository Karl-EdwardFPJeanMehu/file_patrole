from os import path
from .logger import log
from .event import subscribe
from termcolor import colored

log_location = "log.txt"

def handle_file_added_event(data):
    file_path = data["file_path"]
    file_hash = data["file_hash"]
    file_name = path.basename(data["file_path"])
    description = "The file, {file_name}, found at {file_path} has been added by user, pete"

    print(colored(f"The file {file_name} has been added!\r\n", 'green'))

    # Write event to log file
    log(log_location, file_path, "pete", file_hash, "received_hashoaijsodifjoidje", description)

def handle_file_modified_event(data):
    file_path = data["file_path"]
    file_hash = data["file_hash"]
    file_name = path.basename(data["file_path"])
    description = "The file, {file_name}, found at {file_path} has been modified by user, pete"

    print(colored(f"The file {file_name} has been modified!\r\n", 'yellow'))

    # Write event to log file
    log(log_location, file_path, "pete", file_hash, "received_hashoaijsodifjoidje", description)

def setup_log_event_handlers():
    subscribe("file_added", handle_file_added_event)
    subscribe("file_modified", handle_file_modified_event)
