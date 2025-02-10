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

import sys
import json
import enquiries
from lib import log_listener, utils, file_handlers as fh
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
config.set("PT_LOADED_BASELINE", json.dumps({}))

# Queue for messages to be processed by a separate event handler
message_queue = Queue()

# Queue for hash calculations to offload heavy processing
hash_calc_queue = Queue()

# Directory to monitor:
monitor_dirs = config.get("PT_MONITOR_DIRS")

curFile = utils.get_absolute_dirname("__file__")
print(f"Current working file: {curFile}")


def quit():
    print("Bye!")
    sys.exit(1)


def show_menu():
    global choice

    baselines_exist = len(fh.get_baseline_files()) >= 1
    print(f"{len(fh.get_baseline_files())} baseline files")

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
        fh.create_new_baseline(baseline_path=baseline_path, curFile=curFile)
    elif choice == menu_options[1] and baselines_exist:
        fh.load_baseline(curFile=curFile, message_queue=message_queue)
        # print the values of the params for load_baseline
    else:
        quit()


while choice is None:
    utils.banner()
    show_menu()
