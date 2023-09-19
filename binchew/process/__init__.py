from typing import Self

from binchew.os.process import RawProcess, open_raw_process


class Process:
    def __init__(self, impl: RawProcess):
        self._impl = impl

    @classmethod
    def open(cls, pid: int) -> Self:
        impl = open_raw_process(pid)
        return cls(impl)

    # TODO: API
