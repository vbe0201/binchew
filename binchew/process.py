from typing import Self

from binchew.memory import MemoryBlock, Permissions
from binchew.os.process import RawProcess, open_raw_process


class Process:
    """
    Representation of an OS process.

    This class exposes portable primitives for low-level interaction
    with the local Python process and foreign remote processes.
    """

    def __init__(self, impl: RawProcess):
        self._impl = impl

    @classmethod
    def open(cls, pid: int) -> Self:
        impl = open_raw_process(pid)
        return cls(impl)

    def pid(self) -> int:
        """Gets the ID of the represented process."""
        return self._impl.pid

    def is_local(self) -> bool:
        """Indicates whether this instance is attached to the local Python process."""
        return self._impl.is_local

    def is_foreign(self) -> bool:
        """Indicates whether this instance is attached to a foreign process."""
        return not self._impl.is_local

    def _allocate(self, size: int, perms: Permissions) -> MemoryBlock:
        ptr = self._impl.allocate_memory(size, perms)
        return MemoryBlock(self._impl, ptr, size, perms)
