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

import json
from lib import log_listener, utils
from config import Config
from queue import Queue
from cli import parse_arguments, handle_command, show_menu

if __name__ == "__main__":

    #  Listen to loger events
    log_listener.setup_log_event_handlers()

    #  Initialize config
    config = Config()

    # Parse arguments
    args = parse_arguments()
    handle_command(args)

    #  Initialize loaded baseline
    config.set("PT_LOADED_BASELINE", json.dumps({}))

    # Queue for messages to be processed by a separate event handler
    message_queue = Queue()

    # Queue for hash calculations to offload heavy processing
    hash_calc_queue = Queue()

    # Directory to monitor:
    monitor_dirs = config.get("PT_MONITOR_DIRS")

    curFile = utils.get_absolute_dirname("__file__")

    #  Display the main menu
    show_menu(curFile, message_queue)

    # Setup logging
    utils.setup_logging()

