#!/usr/bin/env python3

"""\
This is a basic agented, 
standalone File Integrity Monitor
that checks whether files are either
deleted, modified or added

Usage: myscript.py BAR1 BAR2
Author: Karl-Edward F. P. Jean-Mehu
Email: kwebdever@protonmail.com
Date: Oct 4, 2023
License: Oct 4, 2023
"""
#  File Integrity Monitor (FIM)

import os
import sys
import time
import enquiries
import hashlib
from twilio.rest import Client
from termcolor import colored
from datetime import datetime

smsClient = Client()

line = "*" * 50
baseline_path = "./baselines"
choice = None

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
def list_files_recursively(skip_file_name, directory = "./"):
    file_list = []

    for root, _, files in os.walk(directory):
        for file in files:
            # Check if the root directory is the "baseline" directory.
            if (os.path.basename(root) == os.path.basename(baseline_path)) or file == skip_file_name:
                continue  # Skip the file in the "baseline" directory.

            file_path = os.path.join(root, file).strip()

            #  Ensure file exists
            if os.path.exists(file_path):
                file_hash = calc_file_hash(file_path)
                file_list.append((file_path + " | " + file_hash))
    return file_list

def create_new_baseline():
    print("\r\n\r\n", line)

    timestamp = str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))

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
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                contents = list_files_recursively(skip_file_name=os.path.basename(__file__), directory="./")
                for value in contents:
                    f.write(str(value) + "\n")

            print("Baseline file created!")
        else:
            raise ValueError(F"Invalid baseline file, '{file_path}', detected!")
    except ValueError as e:
        print("Error: ", e)


loaded_baseline = {}

#  Return existing baselines if they
#  exist
def get_baseline_files():
    existing_baseline_files = []

    for root, _, files in os.walk(baseline_path):
        for f in files:
            existing_baseline_files.append(os.path.join(root, f))

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


#  Use the existing baseline or display a menu
#  to choose from existing ones before monitoring begins
def load_baseline():
    #  Make sure no baseline is already loaded 
    loaded_baseline = {}
    try:
        selected_baseline = selected_baseline_file()

        with open(selected_baseline, 'r') as file:
            for file_line in file:
                fields = file_line.strip().split('|')

                key = fields[0].strip()
                value = fields[1].strip()

                loaded_baseline[key] = value

            print('Baseline loaded!\n')

        time.sleep(3)
        print(f"{line}\r\nNow monitoring integrity of file(s)...")

        print('sending sms')
        smsClient.message.create(
            from_="(509)36888755",
            to="(509)36881455",
            body="(509)36888755"
        )

        last_seen = []

        while(True):
            """ BEGIN MONITORING FILES """
            files = list_files_recursively(skip_file_name=os.path.basename(__file__), directory="./")

            for file in files:
                file_path = file.split('|')[0].strip()
                file_hash = file.split('|')[1].strip()

                if file_path not in loaded_baseline:
                    if file_path not in last_seen:
                        print(colored(f"The file {file_path} has been added!\r\n", 'green'))
                        last_seen.append(file_path)
                elif calc_file_hash(file_path) != loaded_baseline[file_path]:
                    if file_path not in last_seen:
                        print(colored(f"The file {file} has been modified!\r\n", 'yellow'))
                        last_seen.append(file_path)

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
        print("Bye!")
        sys.exit(1)

while choice is None:
    show_menu()

