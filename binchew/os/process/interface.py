from binchew.typing import BytesLike


class RawProcess:
    """
    Raw abstraction for operating system processes.

    This is a building block for higher-level code which enables raw
    access to process memory through system calls.
    """

    def __init__(self, pid: int):
        self.pid = pid

    def read_memory(self, address: int, size: int) -> bytes:
        """
        Reads exactly size bytes from process memory.

        .. info::
            The underlying implementation has the semantics of `ReadProcessMemory`
            on Windows, or `process_vm_readv` on Linux.

            This method further does not make any guarantees about atomicity of
            the access and no partial reads will occur in the error case.

        :param address: The virtual address in the memory space to read from.
        :param size: The number of bytes to read.
        :returns: The raw bytes read from memory.

        :raises OSError: Failed to access the described memory region.
        """
        raise NotImplementedError()

    def write_memory(self, address: int, buf: BytesLike) -> int:
        """
        Writes the given buffer to process memory.

        .. info::
            The underlying implementation has the semantics of `WriteProcessMemory`
            on Windows, or `process_vm_writev` on Linux.

            This method further does not make any guarantees about atomicity of the
            access and no partial writes will occur in the error case.

        .. warning::
            Bears a risk of making the process behave unpredictably when misused.

        :param address: The virtual address in the memory space to write to.
        :param buf: The raw byte buffer to be written.
        :returns: The number of bytes written.

        :raises OSError: Failed to access the described memory region.
        """
        raise NotImplementedError()
