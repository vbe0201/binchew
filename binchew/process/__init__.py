from typing import Self

from binchew.os import getpid
from binchew.os.process import RawProcess, open_raw_process


class Process:
    def __init__(self, impl: RawProcess):
        self._impl = impl

    @classmethod
    def open(cls, pid: int) -> Self:
        impl = open_raw_process(pid)
        return cls(impl)

    def pid(self) -> int:
        """Gets the ID of the represented process."""
        return self._impl.pid

    def is_foreign(self) -> bool:
        """Indicates whether this process is attached to a foreign process."""
        return self._impl.pid != getpid()

    # TODO: API
