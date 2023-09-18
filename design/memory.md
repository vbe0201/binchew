# Memory

A defining feature of `binchew` is interfacing with process memory; both the
host process (running the Python interpreter) and external target processes
are supported.

## Allocators

The easiest way to obtain *memory* is by using a `binchew.Allocator`.

Allocators feature a RAII-style API to acquire memory, which invalidates
outstanding references to interpreter objects when the memory is freed:

```py
with allocator.allocate(PAGE_LAYOUT) as ptr:
    # Do something with the `ptr` allocation.
    # It will be freed on scope exit.
    ...

# If anything stores a reference to `ptr` and tries to use it
# from here onwards, an exception will be thrown.
```

The two supported flavors of allocation are `.allocate()` and `.allocate_zeroed()`.

`.grow()`, `.grow_zeroed()`, `.shrink()` may be used to modify an allocation
during its lifespan after it has been issued.

## Layout

Allocators accept an instance of `Layout` which describes the size and alignment
of the allocation.

Layouts are composed from more layouts or convenience builder methods.

## Memory blocks

Allocators hand out `MemoryBlock`s which store a pointer and a size. They will do
internal bounds checking on access and can be used to derive new pointers within
range of their parent.

Pointers are untyped; raw bytes are read and written. The conversion between types
is handled at a higher level of abstraction.

## Permissions

Using [pointer tagging](https://en.wikipedia.org/wiki/Tagged_pointer) on the address,
we can keep track of what you are allowed to do with a pointer.

Deriving a new pointer with less permission should be supported, the inverse is
debatable but eventually also fine with a big disclaimer in docs?
