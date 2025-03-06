import os
import sys
import enquiries
import argparse
from lib import utils, file_handlers as fh 
from config import Config
import logging

# Obtain configurations
config = Config()


def quit():
    """ Quits the program """

    print("Bye!")
    sys.exit(1)

def show_menu(curFile, message_queue):
    """ Displays the main menu """

    # Initialize choice
    choice = None
    
    while choice is None:
        utils.banner()
        #  Get baseline path
        baseline_path = str(config.get("PT_BASELINE_PATH"))

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

        choice = enquiries.choose("\r\nPlease select an option", menu_options)

        if choice == menu_options[0]:
            fh.create_new_baseline(baseline_path=baseline_path, curFile=curFile)
            fh.load_baseline(curFile=curFile, message_queue=message_queue)
        elif choice == menu_options[1] and baselines_exist:
            fh.load_baseline(curFile=curFile, message_queue=message_queue)
            # print the values of the params for load_baseline
        else:
            quit()


def parse_arguments():
    """ Parses command-line arguments """

    parser = argparse.ArgumentParser(description="Monitors the integrity of files for changes.")

     # Positional arguments
    parser.add_argument("monitor_dirs", type=fh.is_valid_directory, nargs="*", help="<Required>Directories to be monitored.")

    # Optional arguments
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Enable verbose output for additional details.")

    valid_file_types = config.get_valid_monitor_file_types()
    valid_file_types = ", ".join(valid_file_types)

    parser.add_argument("-p", "--path", type=str, help=f"File path, in {valid_file_types} format, containing a list of directories to monitor.")

    parser.add_argument("-n", "--notify", action="store_true", default=False, help="Enable notifications for file changes.")


   # TODO: 
   # parser.add_argument(
   #     "-l", "--log", type=str, help="List of directories to save log files."
   # )

    return parser.parse_args()


def handle_command(args):
    """ Handles command-line arguments """

    try:
        # Set verbose
        if (args.verbose):
            config.enable_option("verbose_mode")
            print("\r\nVERBOSE MODE ENABLED.\r\n")

        # Set notifications
        if (args.notify):
            config.enable_option("notify")
            print("\r\nNOTIFICATIONS ENABLED.\r\n")

        # Obtain the directories to be monitored
        # from either a positional argument, file, or stdin
        # in that same order of priority
        if args.monitor_dirs:
            monitor_dirs = args.monitor_dirs
            monitor_dirs = ",".join(monitor_dirs)
            config.set("PT_MONITOR_DIRS", monitor_dirs)

        elif args.path:
            if os.path.exists(args.path):
                logging.info(f"Loading monitor file: {args.path}")
                try:
                    with open(args.path, "r") as file:
                        fh.load_and_validate_monitor_file(args.path)
                        logging.info(f"Monitoring directories: \r\n{config.get("PT_MONITOR_DIRS").replace(',', '\r\n')}\r\n")

                    file.close()

                except argparse.ArgumentTypeError as e:
                    print(e)
            else:
                logging.error(f"No such file, {args.file}, exists. Enter a valid file path.")

        elif not sys.stdin.isatty():
            monitor_dirs = sys.stdin.read().strip()
            config.set("PT_MONITOR_DIRS", monitor_dirs)
            print("Directories to monitor: ", monitor_dirs)

        else:
            raise ValueError("No directories to monitor")

    except Exception as e:
        logging.critical(e)

