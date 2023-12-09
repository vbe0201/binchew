import ctypes
import os
from ctypes.util import find_library
from typing import Self

from binchew._impl import ffi

_libc = ctypes.CDLL(find_library("c"), use_errno=True)

SYS_mmap = 9
SYS_munmap = 11


def raise_errno(errno: int):
    raise OSError(errno, os.strerror(errno))


def raise_errno_on_error():
    errno = ctypes.get_errno()
    if errno != 0:
        raise_errno(errno)


def _checked_result(res):
    if res == -1:
        errno = ctypes.get_errno()
        raise_errno(errno)
    return res


# https://man7.org/linux/man-pages/man2/mmap.2.html
_libc.mmap.argtypes = (
    ctypes.c_void_p,  # void *addr
    ctypes.c_size_t,  # size_t length
    ctypes.c_int,  # int prot
    ctypes.c_int,  # int flags
    ctypes.c_int,  # int fd
    ctypes.c_size_t,  # off_t offset
)
_libc.mmap.restype = _checked_result

_libc.munmap.argtypes = (
    ctypes.c_void_p,  # void *addr
    ctypes.c_size_t,  # size_t length
)
_libc.munmap.restype = _checked_result

# https://man7.org/linux/man-pages/man2/process_vm_readv.2.html
_libc.process_vm_readv.argtypes = (
    ctypes.c_int,  # pid_t pid
    ctypes.c_void_p,  # const struct iovec *local_iov
    ctypes.c_ulong,  # unsigned long liovcnt
    ctypes.c_void_p,  # const struct iovec *remote_iov
    ctypes.c_ulong,  # unsigned long riovcnt
    ctypes.c_ulong,  # unsigned long flags
)
_libc.process_vm_readv.restype = _checked_result

_libc.process_vm_writev.argtypes = (
    ctypes.c_int,  # pid_t pid
    ctypes.c_void_p,  # const struct iovec *local_iov
    ctypes.c_ulong,  # unsigned long liovcnt
    ctypes.c_void_p,  # const struct iovec *remote_iov
    ctypes.c_ulong,  # unsigned long riovcnt
    ctypes.c_ulong,  # unsigned long flags
)
_libc.process_vm_writev.restype = _checked_result


# https://man7.org/linux/man-pages/man3/iovec.3type.html
class iovec(ctypes.Structure):
    _fields_ = [
        ("iov_base", ctypes.c_void_p),
        ("iov_len", ctypes.c_size_t),
    ]


# https://man7.org/linux/man-pages/man2/ptrace.2.html
PTRACE_PEEKTEXT = 1
PTRACE_POKETEXT = 4
PTRACE_CONT = 7
PTRACE_SINGLESTEP = 9
PTRACE_GETREGS = 12
PTRACE_SETREGS = 13
PTRACE_ATTACH = 16
PTRACE_DETACH = 17

_libc.ptrace.argtypes = (
    ctypes.c_int,  # enum __ptrace_request request
    ctypes.c_int,  # pid_t pid
    ctypes.c_void_p,  # void *addr
    ctypes.c_void_p,  # void *data
)
_libc.ptrace.restype = ctypes.c_long


class user_regs_struct(ctypes.Structure):
    _fields_ = [
        ("r15", ctypes.c_long),
        ("r14", ctypes.c_long),
        ("r13", ctypes.c_long),
        ("r12", ctypes.c_long),
        ("rbp", ctypes.c_long),
        ("rbx", ctypes.c_long),
        ("r11", ctypes.c_long),
        ("r10", ctypes.c_long),
        ("r9", ctypes.c_long),
        ("r8", ctypes.c_long),
        ("rax", ctypes.c_long),
        ("rcx", ctypes.c_long),
        ("rdx", ctypes.c_long),
        ("rsi", ctypes.c_long),
        ("rdi", ctypes.c_long),
        ("orig_rax", ctypes.c_long),
        ("rip", ctypes.c_long),
        ("cs", ctypes.c_long),
        ("eflags", ctypes.c_long),
        ("rsp", ctypes.c_long),
        ("ss", ctypes.c_long),
        ("fs_base", ctypes.c_long),
        ("gs_base", ctypes.c_long),
        ("ds", ctypes.c_long),
        ("es", ctypes.c_long),
        ("fs", ctypes.c_long),
        ("gs", ctypes.c_long),
    ]

    def __copy__(self) -> Self:
        copier = ffi.copy_ctypes_struct(user_regs_struct)
        return copier(ctypes.byref(self))


mmap = _libc.mmap
munmap = _libc.munmap
ptrace = _libc.ptrace
process_vm_readv = _libc.process_vm_readv
process_vm_writev = _libc.process_vm_writev


def checked_ptrace(request, pid, addr, data):
    res = ptrace(request, pid, addr, data)
    if res != 0:
        raise_errno(ctypes.get_errno())
