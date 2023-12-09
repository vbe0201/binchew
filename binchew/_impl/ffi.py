import ctypes

from binchew.typing import BytesLike


def copy_ctypes_struct(type_):
    """
    Returns a function to copy a given ctypes structure type.
    
    The resulting function is called with a reference to the
    value that should be copied.
    """

    def impl(ptr):
        new = type_()
        ctypes.memmove(ctypes.byref(new), ptr, ctypes.sizeof(type_))
        return new

    impl.argtypes = [ctypes.POINTER(type_)]
    impl.restype = type_

    return impl


def make_c_buffer(buf: BytesLike, size: int):
    """Converts a bytes-like object into a raw C byte buffer."""

    buffer_type = ctypes.c_char * size
    if isinstance(buf, bytearray):
        return buffer_type.from_buffer(buf)
    else:
        return buffer_type.from_buffer_copy(buf)
