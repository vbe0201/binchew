def align_down(value: int, align: int) -> int:
    """Aligns a value down to the next multiple of align."""
    return value & -align


def align_up(value: int, align: int) -> int:
    """Aligns a value up to the next multiple of align."""
    return align_down(value + align - 1, align)


def is_aligned(value: int, align: int) -> bool:
    """Checks if a value is aligned to a multiple of align."""
    return value & (align - 1) == 0


def alignment(size: int) -> int:
    """Gets the largest possible alignment for a value of the size."""
    return align_down(size, size)
