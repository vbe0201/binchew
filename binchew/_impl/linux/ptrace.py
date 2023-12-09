import ctypes

from . import libc


def ptrace_attach(pid: int):
    libc.checked_ptrace(libc.PTRACE_ATTACH, pid, None, None)


def ptrace_detach(pid: int):
    libc.checked_ptrace(libc.PTRACE_DETACH, pid, None, None)


def ptrace_single_step(pid: int):
    libc.checked_ptrace(libc.PTRACE_SINGLESTEP, pid, None, None)


def ptrace_continue(pid: int):
    libc.checked_ptrace(libc.PTRACE_CONT, pid, None, None)


def ptrace_get_regs(pid: int) -> libc.user_regs_struct:
    regs = libc.user_regs_struct()
    ptrace_update_regs(pid, regs)
    return regs


def ptrace_update_regs(pid: int, regs: libc.user_regs_struct):
    libc.checked_ptrace(libc.PTRACE_GETREGS, pid, None, ctypes.byref(regs))


def ptrace_set_regs(pid: int, regs: libc.user_regs_struct):
    libc.checked_ptrace(libc.PTRACE_SETREGS, pid, None, ctypes.byref(regs))


def ptrace_peek_text(pid: int, addr: int) -> int:
    word = libc.ptrace(libc.PTRACE_PEEKTEXT, pid, ctypes.c_void_p(addr), None)
    if word == -1:
        libc.raise_errno_on_error()

    return word


def ptrace_poke_text(pid: int, addr: int, word: int):
    libc.checked_ptrace(libc.PTRACE_POKETEXT, pid, ctypes.c_void_p(addr), word)
