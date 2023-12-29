import ctypes
import mmap
from enum import IntFlag, auto
import struct
from typing import Any

from binchew.os.process import RawProcess
from binchew.typing import BytesLike

from .errors import OutOfBounds
from .layout import Layout


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

    def __init__(self, proc: RawProcess, addr: int, layout: Layout, perms: Permissions):
        self._process = proc

        self.addr = addr
        self.layout = layout
        self.perms = perms

    def __len__(self) -> int:
        return self.size

    @property
    def size(self) -> int:
        """Gets the size of this memory block."""
        return self.layout.size

    @property
    def align(self) -> int:
        """Gets the alignment of this memory block."""
        return self.layout.align

    def _deallocate(self):
        self._process.free_memory(self.addr, self.size)

    def _is_in_bounds(self, addr: int, size: int) -> bool:
        start = self.addr
        end = start + self.size

        return start <= addr and (addr + size) <= end

    def read(self, size: int) -> bytes:
        """
        Reads exactly size bytes from the start of the block.

        :param size: The number of bytes to read.
        :returns: The raw bytes read from memory.

        :raises OSError: Failed to access the described memory region.
        :raises OutOfBounds: Read would violate block boundaries.
        :raises PermissionError: No read permissions to the block.
        """

        if not self.perms & Permissions.READ:
            raise PermissionError("missing read permissions to block memory")

        addr = self.addr
        if not self._is_in_bounds(addr, size):
            raise OutOfBounds("cannot read past the end of block")

        return self._process.read_memory(addr, size)

    def write(self, data: BytesLike) -> int:
        """
        Writes the full data to the start of the block.

        :param size: The raw bytes to write.
        :returns: The number of bytes written (equals ``len(data)``).

        :raises OSError: Failed to access the described memory region.
        :raises OutOfBounds: Write would violate block boundaries.
        :raises PermissionError: No write permissions to the block.
        """

        if not self.perms & Permissions.WRITE:
            raise PermissionError("missing write permissions to block memory")

        addr = self.addr
        if not self._is_in_bounds(addr, len(data)):
            raise OutOfBounds("cannot write past the end of block")

        return self._process.write_memory(addr, data)

    def fill(self, value: int) -> int:
        """
        Fills the entire memory region with a given byte value.

        Conversion of negative values to their two's complement representation
        as well as truncating too large values is silently handled internally.

        :param value: The byte to write.
        :returns: The number of bytes written (equals ``len(self)``).

        :raises OSError: Failed to access the described memory region.
        :raises OutOfBounds: Write would violate block boundaries.
        :raises PermissionError: No write permissions to the block.
        """

        buf = struct.pack("b", value & 0xFF) * self.size
        return self.write(buf)

    def clear(self) -> int:
        """
        Clears the entire memory region with zeroes.

        :returns: The number of bytes written (equals ``len(self)``).

        :raises OSError: Failed to access the described memory region.
        :raises OutOfBounds: Write would violate block boundaries.
        :raises PermissionError: No write permissions to the block.
        """
        return self.fill(0)

    def copy_to(self, other: "MemoryBlock"):
        """
        Copies the entire contents of this block to another one.

        :returns: The number of bytes written (equals ``len(self)``).

        :raises OSError: Failed to access the described memory regions.
        :raises OutOfBounds: Write would violate block boundaries.
        :raises PermissionError: No read permissions on self or write permissions on other.
        """

        tmp = self.read(self.size)
        return other.write(tmp)

    def execute(self, functype, *args) -> Any:
        """
        Executes the contents of the memory block as a native code function.

        .. warning::

            This method can trivially cause undefined behavior and lead to
            process crashes when used with bad data.
        
        :param functype: A ctypes function type describing the signature.
        :param args: Arbitrary arguments to be passed to the native function.

        :raises OSError: Memory is mapped in foreign process.
        :raises PermissionError: No execute permissions to the block.
        """

        if not self.perms & Permissions.EXECUTE:
            raise PermissionError("missing execute permissions to block memory")

        if not self._process.is_local:
            raise OSError("cannot execute code in foreign processes")

        func = ctypes.cast(ctypes.c_void_p(self.addr), functype)
        return func(*args)


# TODO: Permissions; upgrading and downgrading
# TODO: Slicing the memory range
