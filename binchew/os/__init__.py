import os


def getpid() -> int:
    """Gets the ID of this process."""
    return os.getpid()


def addrof(x) -> int:
    """Gets the address of any Python object in host memory."""
    return id(x)
