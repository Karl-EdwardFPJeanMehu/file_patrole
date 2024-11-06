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
import enquiries
import hashlib
from datetime import datetime, timezone
from dotenv import load_dotenv
from lib import log_listener, event, utils
import threading
from config import Config


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

line = "*" * 50
config = Config()
baseline_path = config.get("BASELINE_PATH") 
choice = None
loaded_baseline = {}

# Directory to monitor:
monitor_dir = config.get("MONITOR_DIR")

# Directory to ignore:
ignored_dirs = os.environ.get("PT_IGNORED_DIRS", f"{os.path.dirname(baseline_path)}, .git").split(",")

curFile = os.path.dirname(os.path.abspath('__file__'))

def quit():
    print("Bye!")
    sys.exit(1)

#  Calculate and return the hash of a file
def calc_file_hash(file_path, hash_algorithm="sha256"):
    try:
        hash_object = hashlib.new(hash_algorithm)

        with open(file_path, "rb") as file:
            while True:
                data = file.read(65536)  # Read data in 64KB chunks
                if not data:
                    break
                hash_object.update(data)
        return hash_object.hexdigest().strip()
    except ValueError as e:
        print('Failed calculating hash for ', file_path)

#  recursively obtain a list of all file paths and
#  their hashes in the given or cwd
def list_files_recursively(skip_file_name, directory = monitor_dir):
    file_list = []

    for root, _, files in os.walk(directory):
        for file in files:
            # Check if the root directory is the "baseline" directory.
            if (os.path.dirname(os.path.abspath(root)) in ignored_dirs ) or file == skip_file_name:
                continue  # Skip the file in the "baseline" directory.

            file_path = os.path.join(root, file).strip()

            #  Ensure file exists
            if os.path.exists(file_path):
                file_hash = calc_file_hash(file_path)
                file_list.append((file_path + " | " + file_hash))
    return file_list

def create_new_baseline():
    print("\r\n\r\n", line)

    timestamp = utils.get_current_timestamp()

    print("Creating new baseline in CWD...")
    file_name = "baseline_" + timestamp + ".txt"
    file_path = os.path.join(baseline_path, file_name)

    #  Ensure the baseline path exists
    #  if not create it
    if not os.path.exists(baseline_path):
        os.makedirs(baseline_path)

    #  Check whether the baseline file exists
    #  if so throw an error
    try:
        if os.path.isdir(baseline_path):
            with open(file_path, 'a') as f:
                contents = list_files_recursively(skip_file_name=curFile)
                for value in contents:
                    f.write(str(value) + "\n")
            print("baseline file created!")
        else:
            raise ValueError(f"Baseline path '{baseline_path}' does not exist!")
    except ValueError as e:
        print("error: ", e)

#  return existing baselines if they
#  exist
def get_baseline_files():
    existing_baseline_files = []

    for root, _, files in os.walk(baseline_path):
        for f in files:
            if (utils.is_valid_baseline_file(f)):
                existing_baseline_files.append(os.path.join(root, f))
            else:
                print(f"Invalid baseline file, '{f}', detected!")

    return existing_baseline_files

#  Allow user to choose baseline file
#  if more than one exists otherwise use the one
def selected_baseline_file():
    existing_baseline_files = get_baseline_files()

    if len(existing_baseline_files) == 1:
        return existing_baseline_files[0]
    else:
        selected_baseline = enquiries.choose("Select a baseline: ", existing_baseline_files)
        return selected_baseline

def start_monitoring_worker():
    # monitoring
    last_seen = []

    while (True):
        """ begin monitoring files """
        files = list_files_recursively(skip_file_name=curFile)

        for file in files:
            file_path = file.split('|')[0].strip()
            file_name = os.path.basename(file_path)
            file_hash = file.split('|')[1].strip()

            if file_path not in loaded_baseline:
                if file_path not in last_seen:
                    event.post_event('File_added', {"file_path": file_path, "file_hash": file_hash})
                    utils.update_baseline_file(file_path, file_hash)
            elif calc_file_hash(file_path) != loaded_baseline[file_path]:
                if file_path not in last_seen:
                    event.post_event('File_modified', {"file_path": file_path, "file_hash": file_hash})

            last_seen.append(file_path)

#  Use the existing baseline or display a menu
#  to choose from existing ones before monitoring begins
def load_baseline():
    try:
        selected_baseline = selected_baseline_file()
        config.set("SELECTED_BASELINE_FILE", selected_baseline)

        encoding = utils.get_file_encoding(selected_baseline)

        with open(selected_baseline, 'r', encoding=encoding) as file:
            for file_line in file:
                fields = file_line.split('|')

                key = fields[0].strip()
                value = fields[1].strip()

                loaded_baseline[key] = value

        time.sleep(3)
        print(f"{line}\r\nNow monitoring integrity of file(s)...")

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
        #  print(f"Now monitoring integrity of files in {os.getcwd()}")
    else:
        quit()

while choice is None:
    utils.banner()
    show_menu()
