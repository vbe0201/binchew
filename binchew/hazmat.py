import ctypes

from .typing import BytesLike


def addrof(x):
    """Gets the memory address of the given interpreter object."""
    return id(x)


def make_c_buffer(buf: BytesLike):
    """Converts a bytes-like object into a raw C byte buffer.
    
    .. warning::
        The contents of the original `buf` remain in undefined
        state after a call to this function.

        Do NOT use it anymore and interact only with the returned
        C buffer.
    """

    size = len(buf)
    buffer_type = ctypes.c_byte * size

    if isinstance(buf, bytearray):
        return buffer_type.from_buffer(buf)
    else:
        new = buffer_type()
        ctypes.memmove(ctypes.byref(new), buf, size)
        return new
