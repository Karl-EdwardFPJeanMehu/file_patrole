import os
import hashlib
import platform
from lib import utils, workers, log_listener
from config import Config
import enquiries
import threading
import time
import json
import stat
import argparse

config = Config()

# Get hostname
hostname = platform.node()


def get_file_permission(file_path: str) -> str:
    """ Gets file permission """

    # Get file stat
    file_stat = os.stat(file_path)

    # Linux campatible octal format
    linux_permissions = oct(file_stat.st_mode & 0o777)

    # Windows compatible string format
    is_readable = "r" if file_stat.st_mode & stat.S_IRUSR else "-"
    is_writable = "w" if file_stat.st_mode & stat.S_IWUSR else "-"
    is_executable = "x" if file_stat.st_mode & stat.S_IXUSR else "-"

    windows_permissions = f"{is_readable}{is_writable}{is_executable}"

    if platform.system() == "Linux" or platform.system() == "Darwin":
        return linux_permissions
    else:
        return windows_permissions


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
        print(f"Failed calculating hash for {file_path}. Error: {e}")


#  recursively obtain a list of all file paths and
#  their hashes in the given or cwd
def list_files_recursively(skip_file_name, directories, ignored_dirs):
    file_list = []

    for directory in directories.split(","):
        for root, _, files in os.walk(directory):
            for file in files:
                # Check if the root directory is the "baseline" directory.
                if (
                    os.path.dirname(os.path.abspath(root)) in ignored_dirs
                ) or file == skip_file_name:
                    continue  # Skip the file in the "baseline" directory.

                file_path = os.path.join(root, file).strip()

                #  Ensure file exists
                if os.path.exists(file_path):
                    file_hash = calc_file_hash(file_path)
                    file_list.append((f"{file_path} | {file_hash}"))

    return file_list


def create_new_baseline(baseline_path, curFile):
    print(f"\r\n\r\n{utils.divider}")

    timestamp = utils.get_timestamp(True)

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
            with open(file_path, "a") as f:
                contents = list_files_recursively(
                    directories=config.get("PT_MONITOR_DIRS"),
                    ignored_dirs=config.get("PT_IGNORED_DIRS"),
                    skip_file_name=curFile,
                )
                for value in contents:
                    f.write(str(value) + "\n")

            print("baseline file created!")

        else:
            raise ValueError(f"Baseline path '{baseline_path}' does not exist!")
    except ValueError as e:
        print("error: ", e)


# Returns existing baselines
def get_baseline_files():
    try:
        existing_baseline_files = []

        for root, _, files in os.walk(str(config.get("PT_BASELINE_PATH"))):
            for f in files:
                if utils.is_valid_baseline_file(f):
                    existing_baseline_files.append(os.path.join(root, f))
                else:
                    utils.verbose_print(f"Invalid baseline file, '{f}', detected!")

        return existing_baseline_files

    except Exception as e:
        print("Error retrieving baseline files: ", e)
        raise


#  Allow user to choose baseline file
#  if more than one exists otherwise use the one
def selected_baseline_file() -> str:
    existing_baseline_files = get_baseline_files()

    if len(existing_baseline_files) == 1:
        return existing_baseline_files[0]

    else:
        selected_baseline = enquiries.choose(
            "Select a baseline: ", existing_baseline_files
        )
        # TODO: check if selected baseline is valid
        return selected_baseline


#  Use the existing baseline or display a menu
#  to choose from existing ones before monitoring begins
def load_baseline(curFile, message_queue):
    try:
        selected_baseline = selected_baseline_file()
        config.set("SELECTED_BASELINE_FILE", selected_baseline)

        encoding = utils.get_file_encoding(selected_baseline)

        with open(selected_baseline, "r", encoding=encoding) as file:
            for file_line in file:
                fields = file_line.split("|")

                key = fields[0].strip()
                value = fields[1].strip()

                l_baseline = json.loads(config.get("PT_LOADED_BASELINE"))
                l_baseline[key] = value
                config.set("PT_LOADED_BASELINE", json.dumps(l_baseline))

        file.close()
        time.sleep(3)

        # Display the absolute path of the directories being monitored
        directories = json.dumps(config.get("PT_MONITOR_DIRS")).split(",")

        for f in directories:
            # f = utils.get_absolute_dirname(f)
            # Add trailing slash if not present
            if not f.endswith("/"):
                # remove trailing "/"
                directories[directories.index(f)] = f.strip().rstrip("/")

            directories[directories.index(f)] = f

        directories = "\r\n".join(directories).strip('"')

        print(
            f"{utils.divider}\r\nNow monitoring integrity of file(s) on host {hostname} in directories: \r\n\r\n{directories}\r\n{utils.divider}\r\n"
        )

        threading.Thread(
            target=log_listener.message_daemon, args=(message_queue,), daemon=True
        ).start()

        """ MONITORING """
        threading.Thread(
            target=workers.start_monitoring_worker(
                message_queue=message_queue, curFile=curFile
            ),
            daemon=False,
        ).start()

    except Exception as e:
        print("Failed loading baseline: ", e)
        raise


def is_valid_directory(path):
    """Check whether the specified path is a valid directory"""
    path = os.path.expanduser(path)
    if os.path.isdir(path) and path not in config.get("PT_IGNORED_DIRS"):
        return path
    else:
        raise argparse.ArgumentTypeError(f"'{path}' is not a valid directory")


def load_and_validate_monitor_file(file_path):
    """Check whether the specified path is a valid file with list of directories to monitor"""

    file_path = os.path.expanduser(file_path)
    if os.path.isfile(file_path):
        # list of valid directories to be monitored
        results = []

        try:
            file_extension = file_path.rsplit(".", 1)[1].lower()

            # TODO: validate file contents
            is_valid_extension = file_extension in [
                ext.lower() for ext in config.get_valid_monitor_file_types()
            ]

            if is_valid_extension:
                with open(file_path, "r") as file:
                    for line in file:
                        line = os.path.expanduser(line.strip())
                        if line and line not in results and is_valid_directory(line):
                            results.append(line)
                        else:
                            raise ValueError(f"'{line}' is a member of ignored directories.")

                if results:
                    config.set("PT_MONITOR_DIRS", ",".join(results))

            else:
                raise ValueError(
                    f"'{file_path}' is not a valid file with list of directories to monitor")
        except Exception as e:
            print(f"Monitor file error {e}")
            raise
    else:
        raise argparse.ArgumentTypeError(f"'{file_path}' is not a valid file")
