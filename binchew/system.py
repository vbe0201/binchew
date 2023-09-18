import os
import sys


def is_windows() -> bool:
    """Checks whether the process is running on Windows."""
    return os.name == "nt"


def is_linux() -> bool:
    """Checks whether the process is running on Linux."""
    return sys.platform.startswith("linux")
