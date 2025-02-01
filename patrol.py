#!/usr/bin/env python3

#  The MIT License (MIT) with Attribution and Liability Protection

#  Permission is hereby granted, free of charge, to any person obtaining a copy of
#  this software and associated documentation files (the "Software"), to deal in
#  the Software without restriction, including without limitation the rights to
#  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
#  the Software, and to permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:

#  1. The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.

#  2. Attribution Requirement: Any use, distribution, or modification of the
#  Software must provide clear attribution to the original author.

#  THE SOFTWARE IS PROVIDED "AS IS," WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE, AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT, OR OTHERWISE, ARISING
#  FROM, OUT OF, OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#  IN THE SOFTWARE.

#  File Integrity Monitor (FIM)

import os
import sys
import time
import json
import enquiries
import hashlib
from lib import log_listener, utils, divider
import threading
from config import Config
from queue import Queue

__author__ = "Karl-Edward F. P. Jean-Mehu"
__credits__ = "Karl-Edward F. P. Jean-Mehu"
__copyright__ = "Copyright 2023, Karl-Edward F. P. Jean-Mehu"
__maintainer__ = "Copyright 2023, Karl-Edward F. P. Jean-Mehu"
__license__ = "MIT"
__email__ = "kwebdever@protonmail.com"
__status__ = "Development"

"""\
This is a basic agented,
standalone File Integrity Monitor
that checks whether files are either
deleted, modified or added

Date: Oct 4, 2023
"""

#  Listen to loger events
log_listener.setup_log_event_handlers()

#  Initialize config
config = Config()

#  Get baseline path
baseline_path = str(config.get("PT_BASELINE_PATH"))

#  Initialize choice
choice = None

#  Initialize loaded baseline
loaded_baseline = {}

# Queue for messages to be processed by a separate event handler
message_queue = Queue()

# Queue for hash calculations to offload heavy processing
hash_calc_queue = Queue()

# Directory to monitor:
monitor_dirs = config.get("PT_MONITOR_DIRS")

# Directory to ignore:
ignored_dirs: list = os.environ.get("PT_IGNORED_DIRS", f"{os.path.dirname(baseline_path)}, .git").split(",")

curFile = utils.get_absolute_dirname("__file__")
print(f"Current working file: {curFile}")


def quit():
    print("Bye!")
    sys.exit(1)

#  return existing baselines if they
#  exist
def get_baseline_files():
    existing_baseline_files = []

    for root, _, files in os.walk(baseline_path):
        for f in files:
            if utils.is_valid_baseline_file(f):
                existing_baseline_files.append(os.path.join(root, f))
            else:
                print(f"Invalid baseline file, '{f}', detected!")

    return existing_baseline_files


#  Allow user to choose baseline file
#  if more than one exists otherwise use the one
def selected_baseline_file() -> str:
    existing_baseline_files = get_baseline_files()

    if len(existing_baseline_files) == 1:
        return existing_baseline_files[0]

    else:
        selected_baseline = enquiries.choose("Select a baseline: ", existing_baseline_files)
        # TODO: check if selected baseline is valid
        return selected_baseline[0]


def hash_worker():
    """Worker function to process hash calculations"""
    while True:
        try:
            # Get a file path from the queue
            params = hash_calc_queue.get()
            
            (file_path, control_hash) = params

            if file_path is None:
                break
            # Calculate the hash of the file
            file_hash = calc_file_hash(file_path)

            # Put the file hash to the message queue
            message_queue.put(("File_added", {"file_path": file_path, "file_hash": file_hash, "control_hash": control_hash}))

        finally:
            hash_calc_queue.task_done()




#  Use the existing baseline or display a menu
#  to choose from existing ones before monitoring begins
def load_baseline():
    try:
        selected_baseline = selected_baseline_file()
        config.set("SELECTED_BASELINE_FILE", selected_baseline)

        encoding = utils.get_file_encoding(selected_baseline)

        with open(selected_baseline, "r", encoding=encoding) as file:
            for file_line in file:
                fields = file_line.split("|")

                key = fields[0].strip()
                value = fields[1].strip()

                loaded_baseline[key] = value

        time.sleep(3)

        # Display the absolute path of the directories being monitored
        directories = json.dumps(config.get("PT_MONITOR_DIRS")).split(",")

        print(f"Directories before adding trailing slash: {directories}")

        for f in directories:
            # f = utils.get_absolute_dirname(f)
            # Add trailing slash if not present
            if not f.endswith("/"):
                # remove trailing "/"
                directories[directories.index(f)] = f.strip().rstrip("/")

            directories[directories.index(f)] = f

        directories = ", ".join(directories)

        print(f"{divider}\r\nNow monitoring integrity of file(s) in directories: {directories}...")

        threading.Thread(target=log_listener.message_daemon, args=(message_queue,), daemon=True).start()

        """ MONITORING """
        threading.Thread(target=start_monitoring_worker, daemon=False).start()

    except Exception as e:
        print("Error: ", e)


def show_menu():
    global choice

    baselines_exist = len(get_baseline_files()) >= 1
    print(f"{len(get_baseline_files())} baseline files")

    menu_options = [
        "No existing baselines found. Create a new one.",
        "Exit",
    ]

    #  Add the monitoring menu option
    #  if baseline files exist
    if baselines_exist:
        menu_options[0] = "Create a new baseline."
        menu_options.insert(1, "Begin monitoring with existing baseline")

    choice = enquiries.choose("Please select an option", menu_options)

    if choice == menu_options[0]:
        create_new_baseline()
    elif choice == menu_options[1] and baselines_exist:
        load_baseline()
    else:
        quit()


while choice is None:
    utils.banner()
    show_menu()
