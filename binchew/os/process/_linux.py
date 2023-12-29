import ctypes
import mmap
import os
from typing import Self

from binchew._impl import ffi
from binchew._impl.linux import foreign_syscall, libc
from binchew.typing import BytesLike

from .interface import RawProcess


# https://man7.org/linux/man-pages/man2/kill.2.html
def _ensure_pid_exists(pid: int):
    # > If pid equals 0, then sig is sent to every process in the process
    # > group of the calling process.
    #
    # Therefore, we are the calling process and we always exist.
    if pid != 0:
        # > If sig is 0, then no signal is sent, but existence and permission
        # > checks are still performed; this can be used to check for the
        # > existence of a process ID or process group ID that the caller is
        # > permitted to signal.
        os.kill(pid, 0)


class LinuxProcess(RawProcess):
    def __init__(self, pid: int):
        super().__init__(pid)

    @classmethod
    def open(cls, pid: int) -> Self:
        # Ensure the requested process exists.
        _ensure_pid_exists(pid)
        return cls(pid)

    def read_memory(self, address: int, size: int) -> bytes:
        # TODO: In local process, just do memmove.
        buf = ctypes.create_string_buffer(size)

        local = libc.iovec(ctypes.cast(ctypes.byref(buf), ctypes.c_void_p), size)
        remote = libc.iovec(ctypes.c_void_p(address), size)

        res = libc.process_vm_readv(
            self.pid,
            ctypes.byref(local),
            1,
            ctypes.byref(remote),
            1,
            0
        )
        if res != size:
            # We bail for partial reads to be compatible with Windows.
            raise OSError("Partial read from process memory")

        return buf.raw

    def write_memory(self, address: int, buf: BytesLike) -> int:
        # TODO: In local process, just do memmove.
        size = len(buf)
        buf = ffi.make_c_buffer(buf, size)

        local = libc.iovec(ctypes.cast(ctypes.byref(buf), ctypes.c_void_p), size)
        remote = libc.iovec(ctypes.c_void_p(address), size)

        res = libc.process_vm_writev(
            self.pid,
            ctypes.byref(local),
            1,
            ctypes.byref(remote),
            1,
            0
        )
        if res != size:
            # We bail for partial writes to be compatible with Windows.
            raise OSError("Partial write to process memory")

        return res

    def allocate_memory(self, size: int, perms) -> int:
        prot = perms.mmap_perms
        flags = mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS

        if self.is_local:
            # NOTE: We can't use Python's `mmap.mmap` because it ignores
            # execute permission requests.
            addr = libc.mmap(
                None,
                size,
                prot,
                flags,
                -1,
                0
            )

        else:
            addr = foreign_syscall(
                self.pid,
                libc.SYS_mmap,
                0,
                size,
                prot,
                flags,
                -1,
                0
            )

            # Since syscalls cannot use errno, results are return values.
            # We are checking for a range which cannot be a legal address.
            if -4096 < addr < -1:
                raise OSError("Failed to allocate memory in remote process")

        return addr

    def free_memory(self, addr: int, size: int):
        if self.is_local:
            libc.munmap(addr, size)

        else:
            # Since syscalls cannot use errno, we use a generic result message.
            res = foreign_syscall(self.pid, libc.SYS_munmap, addr, size, 0, 0, 0, 0)
            if res != 0:
                raise OSError("Failed to free memory in remote process")
