import os
import sys
import re
import chardet
from datetime import datetime, date
from dateutil.tz import tzlocal
from config import Config

class UpdateBaselineException(Exception):
    pass


def normalize_path(path):
    """Normalizes a path and removes double slashes.

    Args:
        path (str): The path to normalize.

    Returns:
        str: The normalized path without double slashes.
    """

    normalized_path = os.path.normpath(path)
    return normalized_path.replace("//", "/")


def banner():
    print(f"""{"=" * 80}
    \r\n FilePatrole v1.1.1
    \r\n Copyright (c) 2023, Karl-Edward F. P. Jean-Mehu <kwebdever@protonmail.com>
    \r\n This is a basic agented, standalone File Integrity Monitor that checks whether
    \r\n files are either deleted, modified or added.
    \r\n Licensed under MIT
    \r\n{"=" * 80}
    """)

def get_file_encoding(file_path):
    #  Get file encoding
    with open(file_path, "rb") as file:
        content = file.read()
        result = chardet.detect(content)
        encoding = result["encoding"]
    return encoding

def is_valid_baseline_file(file_path):
    #  Check whether the specified file is a
    #  valid baseline file
    #  if not throw an error
    try:
        regex = r"^baseline_\d{2}-\d{2}-\d{4}\.txt$"
        if re.match(regex, os.path.basename(file_path)):
            return True
        else:
            return False

    except ValueError as e:
        print("error: ", e)
        sys.exit(1)

def update_baseline_file(file_path, file_hash):
    # Verify if the baseline file is valid
    config = Config()
    selected_baseline_file = config.get("SELECTED_BASELINE_FILE")
    if not is_valid_baseline_file(selected_baseline_file):
        print(f"failed updating invalid baseline file '{file_path}'")
        return

    else:
        with open(selected_baseline_file, "a") as file:
            if os.path.exists(selected_baseline_file):
                content = f"{file_path} | {file_hash}\n"
                file.write(content)
            else:
                raise UpdateBaselineException(f"Error updating missing baseline with file '{selected_baseline_file}'.")

def get_timestamp(short=False):
    if short:
        return date.today().strftime("%d-%m-%Y")
    else:
        return datetime.now(tzlocal()).isoformat()

def get_absolute_dirname(path):
    return os.path.abspath(os.path.dirname(path))

# Divider
divider = "*" * 50
