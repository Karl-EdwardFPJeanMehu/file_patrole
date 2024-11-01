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

def banner():
    print(f"{"=" * 80}\r\n FilePatrole v1.0\r\n Copyright (c) 2023, Karl-Edward F. P. Jean-Mehu <kwebdever@protonmail.com>\r\n licensed under MIT\r\n{"=" * 80}")
