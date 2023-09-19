import ctypes

from binchew.typing import BytesLike


def make_c_buffer(buf: BytesLike, size: int):
    """Converts a bytes-like object into a raw C byte buffer."""
    buffer_type = ctypes.c_char * size

    if isinstance(buf, bytearray):
        return buffer_type.from_buffer(buf)
    else:
        return buffer_type.from_buffer_copy(buf)
