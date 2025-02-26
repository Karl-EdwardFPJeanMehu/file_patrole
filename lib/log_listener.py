from os import path, getlogin, environ
import json
from .logger import log
from .event import subscribe, post_event
from .utils import normalize_path, get_timestamp, update_baseline_file, get_absolute_dirname
from config import Config
from typing import Literal
from termcolor import colored
import platform

# Get hostname
hostname = platform.node()

current_date = get_timestamp()
log_directory = environ.get("PT_LOG_LOCATION", "./")
log_file_name = "log_" + current_date + ".txt"
log_path = normalize_path(log_directory + "/" + log_file_name)

# Current user's name
current_user = getlogin()
config = Config()

def create_file_observer(update_function, verb=None, color=None):
    """ Function to create a file observer """
    def observer(subject, verb=verb, color=color):
        file_hash = subject["file_hash"]
        file_path = get_absolute_dirname(subject["file_path"])
        unique_key = f"{verb}_{current_date}_{file_hash}_{file_path}"

        last_seen = json.loads(config.get("LAST_SEEN"))
        print(f"last_seen: {last_seen}")

        # if last_seen is None:
        #     last_seen = {}

        # Invoke function only if the specific
        # actions has not already been recordted today
        if unique_key not in last_seen:
            new_last_seen = last_seen
            new_last_seen[file_path] = unique_key
            config.set("LAST_SEEN", json.dumps(new_last_seen))

            update_function(subject, verb, color)

    return observer


def base_file_observer(data, verb="added", color: Literal["green", "magenta", "yellow", "red"] = "green"):
    file_path = data["file_path"]
    file_hash = data["file_hash"]
    file_name = path.basename(data["file_path"])

    file_permission = None

    if "file_permission" in data:
        file_permission = data["file_permission"]

    control_hash = data["control_hash"]

    description = (f"The file, {file_name}, found at {file_path} has been {verb} by {current_user}")
    description = f"The file, {file_name}, with permission {file_permission} found at {file_path} has been {verb} by {current_user}"

    log(log_path, file_path, current_user, control_hash, file_hash, description, hostname,)
    print(colored(f"[{current_date}] The file {file_name} has been {verb}! file hash: {file_hash}, control hash: {control_hash}\r\n", color,))
    update_baseline_file(file_path, file_hash)


handle_file_added = create_file_observer(base_file_observer, verb="added", color="green")
handle_file_copied = create_file_observer(base_file_observer, verb="copied", color="magenta")
handle_file_modified = create_file_observer(base_file_observer, verb="modified", color="yellow")
handle_file_deleted = create_file_observer(base_file_observer, verb="deleted", color="red")


# Subscribe all handlers to their respective event types
def setup_log_event_handlers():
    subscribe("file_added", handle_file_added)
    subscribe("file_copied", handle_file_copied)
    subscribe("file_modified", handle_file_modified)
    subscribe("file_deleted", handle_file_deleted)


def message_daemon(_queue):
    """Dequeues messages and invokes the appropriate handler"""
    try:
        while True:
            items = _queue.get()
            print(f"items: {items}")
            event_type, event_data = items
            basename = path.basename(event_data["file_path"])
            print(f"Processing {event_type} file {basename}...")
            post_event(event_type, event_data)
            print(f"Done processing {event_type} file {basename}")
            _queue.task_done()

    except Exception as e:
        print(f"Error {e}")
