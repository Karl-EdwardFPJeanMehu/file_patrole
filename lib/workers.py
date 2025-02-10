import os
import json
from lib import utils, file_handlers as fh
from config import Config


#  Initialize config
config = Config()


#  Worker to begin monitoring files
def start_monitoring_worker(message_queue, curFile):
    """Begin monitoring files"""

    #  Ensure LAST_SEEN exists
    if not config.exists("LAST_SEEN"):
        config.set("LAST_SEEN", json.dumps({}))

    # monitoring
    while True:
        """ begin monitoring files """
        files = fh.list_files_recursively(
            directories=config.get("PT_MONITOR_DIRS"),
            ignored_dirs=config.get("PT_IGNORED_DIRS"),
            skip_file_name=curFile,
        )

        last_seen = json.loads(config.get("LAST_SEEN"))

        # Loaded baseline
        loaded_baseline = json.loads(config.get("PT_LOADED_BASELINE"))

        for file in files:
            file_path, file_hash = [f.strip() for f in file.split("|")]

            file_abs_path = os.path.join(
                utils.get_absolute_dirname(file_path), os.path.basename(file_path)
            )

            if file_path not in loaded_baseline and file_abs_path not in last_seen:
                if file_hash not in loaded_baseline.values():
                    # The hash and control hash are
                    # the same for new files
                    control_hash = file_hash

                    message_queue.put(
                        (
                            "File_added",
                            {
                                "file_path": file_abs_path,
                                "file_hash": file_hash,
                                "control_hash": control_hash,
                            },
                        )
                    )
                else:
                    # A copied file has the same hash
                    # as the original therefore the
                    # control hash is the same
                    control_hash = file_hash
                    message_queue.put(
                        (
                            "File_copied",
                            {
                                "file_path": file_abs_path,
                                "file_hash": file_hash,
                                "control_hash": control_hash,
                            },
                        )
                    )
            else:
                # The control hash of a modified
                # file is equal to the original file's hash
                control_hash = loaded_baseline[file_path]

                if os.path.exists(file_path):
                    if fh.calc_file_hash(file_path) != loaded_baseline[file_path]:
                        message_queue.put(
                            (
                                "File_modified",
                                {
                                    "file_path": file_abs_path,
                                    "file_hash": file_hash,
                                    "control_hash": control_hash,
                                },
                            )
                        )
                else:
                    control_hash = loaded_baseline[file_path]
                    print(f"File deleted: {file_path}")
                    message_queue.put(
                        (
                            "File_deleted",
                            {
                                "file_path": file_abs_path,
                                "file_hash": file_hash,
                                "control_hash": control_hash,
                            },
                        )
                    )

            loaded_baseline[file_path] = file_hash
            config.set("PT_LOADED_BASELINE", json.dumps(loaded_baseline))


# Worker to calcculate hash
def hash_worker(message_queue):
    """Worker function to process hash calculations"""
    while True:
        try:
            # Get a file path from the queue
            params = fh.hash_calc_queue.get()

            (file_path, control_hash) = params

            if file_path is None:
                break
            # Calculate the hash of the file
            file_hash = fh.calc_file_hash(file_path)

            # Put the file hash to the message queue
            message_queue.put(
                (
                    "File_added",
                    {
                        "file_path": file_path,
                        "file_hash": file_hash,
                        "control_hash": control_hash,
                    },
                )
            )

        finally:
            fh.hash_calc_queue.task_done()
