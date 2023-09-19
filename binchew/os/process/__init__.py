from binchew.os import platform

from .interface import RawProcess

if platform.is_linux():
    from ._linux import LinuxProcess as _ProcessImpl
else:
    raise RuntimeError("This platform is currently not supported by binchew")


def open_raw_process(pid: int) -> RawProcess:
    """
    Opens a handle to the raw process given its ID.
    
    :param pid: The ID of the process to open.

    :raises OSError: The process does not exist.
    """
    return _ProcessImpl.open(pid)
