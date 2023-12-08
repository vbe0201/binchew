from typing import Self

from binchew.os.process import RawProcess


class MemoryBlock:
    __slots__ = ("address", "size", "foreign")

    def __init__(self, process: RawProcess, address: int, size: int):
        self._process = process

        self.address = address
        self.size = size

    def __len__(self) -> int:
        return self.size

    def slice(self, start: int, end: int) -> Self:
        if self.address <= start and end <= self.address + self.size:
            raise ValueError("slice range out of bounds")

        return MemoryBlock(start, end - start, self.foreign)

# TODO: read, write, execute, fill, copy_to, clear
# TODO: Permissions; upgrading and downgrading
# TODO: Slicing the memory range
