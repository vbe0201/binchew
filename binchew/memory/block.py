import ctypes
import mmap
from enum import IntFlag, auto
from typing import Any

from binchew.os.process import RawProcess
from binchew.typing import BytesLike


class Permissions(IntFlag):
    """
    Access permissions associated with pointers.

    Permissions are associated with memory pointers and enable sanity
    checks to prevent invalid interfacing with foreign memory.
    """

    #: Memory can be read from the pointer address.
    READ = auto()
    #: Memory can be written to the pointer address.
    WRITE = auto()
    #: Memory at the pointer address is executable.
    EXECUTE = auto()

    #: All permissions that can be granted.
    ALL = READ | WRITE | EXECUTE

    @property
    def mmap_perms(self) -> int:
        """Gets the current permission set for use with mmap."""

        read = mmap.PROT_READ if (self & Permissions.READ) else 0
        write = mmap.PROT_WRITE if (self & Permissions.WRITE) else 0
        execute = mmap.PROT_EXEC if (self & Permissions.EXECUTE) else 0

        return read | write | execute


class MemoryBlock:
    """
    Representation of an allocated memory region in a process.

    Memory blocks span a slice of memory and detect out of bounds
    access within it. Attempts to perform operations without the
    necessary permissions are rejected.
    """

    def __init__(self, proc: RawProcess, addr: int, size: int, perms: Permissions):
        self._process = proc

        self.addr = addr
        self.size = size
        self.perms = perms

    def __len__(self) -> int:
        return self.size

    def _deallocate(self):
        self._process.free_memory(self.addr, self.size)

    def read(self, size: int) -> bytes:
        if not self.perms & Permissions.READ:
            # TODO: Proper exception type.
            raise Exception()

        # TODO: Check OOB read
        return self._process.read_memory(self.addr, size)

    def write(self, data: BytesLike) -> int:
        if not self.perms & Permissions.WRITE:
            # TODO: Proper exception type.
            raise Exception()

        # TODO: Check OOB write
        return self._process.write_memory(self.addr, data)

    def execute(self, functype, *args) -> Any:
        if not self.perms & Permissions.EXECUTE:
            # TODO: Proper exception type.
            raise Exception()
        # TODO: Check for foreign processes and reject those.

        func = ctypes.cast(ctypes.c_void_p(self.addr), functype)
        return func(*args)


# TODO: read, write, execute, fill, copy_to, clear
# TODO: Permissions; upgrading and downgrading
# TODO: Slicing the memory range
