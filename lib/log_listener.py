from os import path, getlogin, environ
from .logger import log
from .event import subscribe
from .utils import normalize_path, get_timestamp
from termcolor import colored

current_date = get_timestamp()
log_directory = environ.get("PT_LOG_LOCATION", "./")
log_file_name = "log_" + current_date + ".txt"
log_path = normalize_path(log_directory + "/" + log_file_name)

# Current user's name
current_user = getlogin()

def handle_file_added_event(data):
    file_path = data["file_path"]
    file_hash = data["file_hash"]
    file_name = path.basename(data["file_path"])
    description = f"The file, {file_name}, found at {file_path} has been added by {current_user}"

    print(colored(f"The file {file_name} has been added!\r\n", 'green'))

    # Write event to log file
    log(log_path, file_path, current_user, file_hash, file_hash, description)

def handle_file_modified_event(data):
    file_path = data["file_path"]
    file_hash = data["file_hash"]
    file_name = path.basename(data["file_path"])
    description = f"The file, {file_name}, found at {file_path} has been modified by {current_user}"

    print(colored(f"The file {file_name} has been modified!\r\n", 'yellow'))

    # Write event to log file
    log(log_path, file_path, current_user, file_hash, file_hash, description)

def setup_log_event_handlers():
    subscribe("file_added", handle_file_added_event)
    subscribe("file_modified", handle_file_modified_event)
