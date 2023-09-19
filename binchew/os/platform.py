import sys


def is_linux() -> bool:
    """Checks whether the process is running Linux."""
    return sys.platform == "linux"
