import os

def normalize_path(path):
    """Normalizes a path and removes double slashes.

    Args:
        path (str): The path to normalize.

    Returns:
        str: The normalized path without double slashes.
    """

    normalized_path = os.path.normpath(path)
    return normalized_path.replace('//', '/')
