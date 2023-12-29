from typing import Self

from . import utils


class Layout:
    """
    The layout of a memory block.

    An instance describes a particular layout of memory, and is
    composed from other layout descriptions. It consists of a
    byte size and a power-of-two alignment.

    Layouts are presented to the allocator to obtain a matching
    block of memory to populate.
    """

    def __init__(self, size: int, align: int):
        self.size = size
        self.align = align

    def align_to(self, align: int):
        """Aligns to a new given alignment, still able to hold the same value."""
        self.align = max(self.align, align)

    def _next_padding(self, align: int) -> int:
        return utils.align_up(self.size, align) - self.size

    def pad_align(self) -> Self:
        """Rounds the layout size up to a multiple of the layout alignment."""
        self.size += self._next_padding(self.align)

    def to_array(self, count: int) -> int:
        """
        Turns the layout into an array of ``self`` values, including
        all necessary padding between the elements.

        :param count: The number of array elements.
        :returns: The byte offset between the start of each element.
        """

        self.pad_align()
        padded_size = self.size
        self.size *= count
        return padded_size

    def to_packed_array(self, count: int) -> int:
        """
        Turns the layout into an array of ``self`` values, with no
        padding inserted between the elements.

        :param count: The number of array elements.
        :returns: The byte offset between the start of each element.
        """
        self.size *= count

    def extend(self, other: "Layout") -> int:
        """
        Extends this layout so that ``self`` is followed by ``other``,
        including all necessary padding in-between.

        .. info::

            This does not add the trailing padding necessary to conform
            to C representation. When the layouts for all fields have
            been extended in order, don't forget to call :meth:`pad_align`.

        :param other: The layout of the next logical value in memory.
        :returns: The logical offset into the new layout where ``other`` starts.
        """

        self.align = max(self.align, other.align)
        padding = self._next_padding(other.align)

        offset = self.size + padding
        self.size = offset + other.size

        return offset

    def extend_packed(self, other: "Layout") -> int:
        """
        Extends this layout so that ``self`` is followed by ``other``,
        with no padding inserted between the values.

        The alignment of ``other`` is not respected in this.

        :param other: The layout of the next logical value in memory.
        :returns: The logical offset into the new layout where ``other`` starts.
        """
        self.size += other.size
