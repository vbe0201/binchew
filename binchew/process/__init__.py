from typing import Self

from ..system import is_linux
from ..typing import BytesLike


class Process:
    """A running process on the host system.

    This class allows interaction with processes by querying information or
    modifying the dedicated process memory.
    """

    def __init__(self, pid: int):
        self.pid = pid

    @classmethod
    def open(cls, pid: int) -> Self:
        if is_linux():
            from ._linux import LinuxProcess as ProcessImpl
        else:
            raise RuntimeError()

        return ProcessImpl.open(pid)

    def read_process_memory(self, address: int, size: int) -> bytes:
        raise NotImplementedError()

    def write_process_memory(self, address: int, buf: BytesLike):
        raise NotImplementedError()
