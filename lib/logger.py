import os
from datetime import datetime

def append_2_file(file_location: str, content: str):
    """
        Create given file if it does not exist
        and appends content to it
    """
    with open(file_location, "a") as f:
        f.write(content)

def log(log_location: str, file_location: str, user: str, control_hash: str, file_hash: str, description):

    #  Obtain current date
    cur_date = datetime.now()
    timestamp = cur_date.strftime("%Y-%m-%d %HH-%M-%S")
    file_name = os.path.basename(file_location)
    file_path = os.path.dirname(file_location)

    content =f"""
    Date and Time: {timestamp}
    File Path: {file_location}
    User: {user}
    Control Hash: {control_hash}
    File Hash: {file_hash}

    Description: {description}
    {"="*50}
    \r\n
    """

    #  Write log to file
    append_2_file(log_location, content)
