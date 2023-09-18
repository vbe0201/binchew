import ctypes
import os
from ctypes.util import find_library
from typing import Self

from .. import hazmat
from ..typing import BytesLike
from . import Process

libc = ctypes.CDLL(find_library("c"), use_errno=True)


def _checked_process_vm_result(ret):
    if ret == -1:
        errno = ctypes.get_errno()
        raise OSError(errno, os.strerror(errno))
    return ret


# https://man7.org/linux/man-pages/man2/process_vm_readv.2.html
libc.process_vm_readv.argtypes = [
    ctypes.c_int,  # pid_t pid
    ctypes.c_void_p,  # const struct iovec *local_iov
    ctypes.c_ulong,  # unsigned long liovcnt
    ctypes.c_void_p,  # const struct iovec *remote_iov
    ctypes.c_ulong,  # unsigned long riovcnt
    ctypes.c_ulong,  # unsigned long flags
]
libc.process_vm_readv.restype = _checked_process_vm_result

libc.process_vm_writev.argtypes = [
    ctypes.c_int,  # pid_t pid
    ctypes.c_void_p,  # const struct iovec *local_iov
    ctypes.c_ulong,  # unsigned long liovcnt
    ctypes.c_void_p,  # const struct iovec *remote_iov
    ctypes.c_ulong,  # unsigned long riovcnt
    ctypes.c_ulong,  # unsigned long flags
]
libc.process_vm_writev.restype = _checked_process_vm_result


# https://man7.org/linux/man-pages/man3/iovec.3type.html
class iovec(ctypes.Structure):
    _fields_ = [
        ("iov_base", ctypes.c_void_p),
        ("iov_len", ctypes.c_size_t),
    ]


class LinuxProcess(Process):
    @classmethod
    def open(cls, pid: int) -> Self:
        # On Linux, this is a no-op. We don't require an active
        # handle to the process in order to access its memory.
        return cls(pid)

    def read_process_memory(self, address: int, size: int) -> bytes:
        buf = ctypes.create_string_buffer(size)

        local = iovec(ctypes.cast(ctypes.byref(buf), ctypes.c_void_p), size)
        remote = iovec(ctypes.c_void_p(address), size)

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


    def write_process_memory(self, address: int, buf: BytesLike):
        size = len(buf)
        buf = hazmat.make_c_buffer(buf)

        local = iovec(ctypes.cast(ctypes.byref(buf), ctypes.c_void_p), size)
        remote = iovec(ctypes.cast(address, ctypes.c_void_p), size)

        res = libc.process_vm_writev(
            self.pid,
            ctypes.byref(local),
            1,
            ctypes.byref(remote),
            1,
            0
        )
        if res != size:
            # We bail for partial reads to be compatible with Windows.
            raise OSError("Partial write to process memory")
