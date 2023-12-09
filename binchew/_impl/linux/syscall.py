import copy
import ctypes
import errno
import os
import signal

from . import libc, ptrace

# This is the shellcode we inject into foreign processes to trigger
# a Linux system call after prior register setup.
#
# Code:
#   syscall
#   int3
#   nop
#   nop
#   nop
#   nop
#   nop
SYSCALL_SHELLCODE = 0x9090_9090_90CC_050F


def foreign_syscall(pid: int, number: int, *args: int) -> int:
    # Attach to the remote process and wait for it to stop.
    ptrace.ptrace_attach(pid)
    while True:
        stat = os.waitpid(pid, 0)
        if stat[0] != -1:
            break
        else:
            err = ctypes.get_errno()
            if err != errno.EINTR:
                libc.raise_errno(err)

    # Get the current register state of the target process.
    regs = ptrace.ptrace_get_regs(pid)

    # Backup a copy of the registers and the currently running
    # code so that we can restore this state after we're done.
    regs_backup = copy.copy(regs)
    code_backup = ptrace.ptrace_peek_text(pid, regs.rip)

    # Prepare registers for a system call in the remote process.
    regs.rax = number
    regs.orig_rax = -1  # clear the interrupted syscall state
    regs.rdi = args[0]
    regs.rsi = args[1]
    regs.rdx = args[2]
    regs.r10 = args[3]
    regs.r8 = args[4]
    regs.r9 = args[5]

    try:
        # Load registers and shellcode into the target process,
        # then single-step to perform the syscall.
        ptrace.ptrace_poke_text(pid, regs.rip, SYSCALL_SHELLCODE)
        ptrace.ptrace_set_regs(pid, regs)
        ptrace.ptrace_single_step(pid)

        while True:
            stat = os.waitpid(pid, 0)

            if stat[0] == -1:
                err = ctypes.get_errno()
                if err == errno.EINTR:
                    continue
                libc.raise_errno(err)

            if os.WIFSTOPPED(stat[1]):
                match os.WSTOPSIG(stat[1]):
                    case signal.SIGTRAP:
                        # We succeeded, break out of this hole.
                        break
                    case signal.SIGSTOP:
                        ptrace.ptrace_single_step(pid)
                    case _:
                        sig = os.WSTOPSIG(stat[1])
                        raise OSError(f"Process unexpectedly stopped with {sig}")
            
            elif os.WIFEXITED(stat[1]):
                code = os.WEXITSTATUS(stat[1])
                raise OSError(f"Process terminated unexpectedly with exit code {code}")
            
            elif os.WIFSIGNALED(stat[1]):
                sig = os.WTERMSIG(stat[1])
                raise OSError(f"Process terminated unexpectedly by signal {sig}")

            else:
                raise OSError("Lord have mercy with us")

        # If we make it here, we succeeded. Now read registers one
        # more time to obtain the return value of the syscall.
        ptrace.ptrace_update_regs(pid, regs)
    finally:
        # Regardless of success or error, we need to restore the original
        # registers and code of the remote process.
        ptrace.ptrace_poke_text(pid, regs_backup.rip, code_backup)
        ptrace.ptrace_set_regs(pid, regs_backup)

        ptrace.ptrace_detach(pid)

    return regs.rax
