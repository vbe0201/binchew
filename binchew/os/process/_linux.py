import ctypes
import os
from ctypes.util import find_library
from typing import Self

from binchew.typing import BytesLike

from . import ffi
from .interface import RawProcess

_libc = ctypes.CDLL(find_library("c"), use_errno=True)


def _checked_process_vm_result(res):
    if res == -1:
        errno = ctypes.get_errno()
        raise OSError(errno, os.strerror(errno))
    return res


# https://man7.org/linux/man-pages/man2/process_vm_readv.2.html
_libc.process_vm_readv.argtypes = (
    ctypes.c_int,  # pid_t pid
    ctypes.c_void_p,  # const struct iovec *local_iov
    ctypes.c_ulong,  # unsigned long liovcnt
    ctypes.c_void_p,  # const struct iovec *remote_iov
    ctypes.c_ulong,  # unsigned long riovcnt
    ctypes.c_ulong,  # unsigned long flags
)
_libc.process_vm_readv.restype = _checked_process_vm_result

_libc.process_vm_writev.argtypes = (
    ctypes.c_int,  # pid_t pid
    ctypes.c_void_p,  # const struct iovec *local_iov
    ctypes.c_ulong,  # unsigned long liovcnt
    ctypes.c_void_p,  # const struct iovec *remote_iov
    ctypes.c_ulong,  # unsigned long riovcnt
    ctypes.c_ulong,  # unsigned long flags
)
_libc.process_vm_writev.restype = _checked_process_vm_result


# https://man7.org/linux/man-pages/man3/iovec.3type.html
class iovec(ctypes.Structure):
    _fields_ = [
        ("iov_base", ctypes.c_void_p),
        ("iov_len", ctypes.c_size_t),
    ]


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
    @classmethod
    def open(cls, pid: int) -> Self:
        # We don't need a handle to the process in order to read its memory.
        # Therefore, we just ensure the requested process exists.
        _ensure_pid_exists(pid)
        return cls(pid)

    def read_memory(self, address: int, size: int) -> bytes:
        buf = ctypes.create_string_buffer(size)

        local = iovec(ctypes.cast(ctypes.byref(buf), ctypes.c_void_p), size)
        remote = iovec(ctypes.c_void_p(address), size)

        res = _libc.process_vm_readv(
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
        size = len(buf)
        buf = ffi.make_c_buffer(buf, size)

        local = iovec(ctypes.cast(ctypes.byref(buf), ctypes.c_void_p), size)
        remote = iovec(ctypes.c_void_p(address), size)

        res = _libc.process_vm_writev(
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
