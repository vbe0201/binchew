# Process

One of `binchew`'s goals is the ability to interact with OS processes without needing
to inject ourselves into the address space of said process.

The `binchew.Process` class implements this functionality.

## Principles

`binchew.Process` has the following design goals above everything else:

- Feature an API that is hard to misuse; it shouldn't be easy to crash host processes
  in trivial ways.

- Make sure `binchew` properly cleans after itself and doesn't leave holes to
  be leveraged by malicious third-parties, e.g. leaving unfavorable page permissions.

Beyond that, when a function has invariants that would cause UB, those need
to be documented and, to the best of our ability, checked on the Python side.

When APIs are platform-specific, they are marked as such.

The end goal is for users to interact with processes responsibly, ergonomics are
favored over raw performance where they stand in conflict with each other.

## Memory allocation

Memory allocation is based on the `binchew.Allocator` API discussed in a
[separate document](./memory.md).

A `Process` exposes access to two types of allocators; the `binchew.ProcessAllocator`
and the `binchew.ProcessDebugAllocator`.

Users should be able to configure concrete subclasses of these types to implement
custom allocation strategies.

Both allocators should serve as drop-in replacements to each other. The debug allocator
will internally store a lot of state information to prevent OOB accesses, UAFs, and
permission violations.

The other allocator is more focussed on performance, it will do close to no checks and
can overcome limitations of the debug allocator for certain situations.

That being said, users are strongly encouraged to develop their code against the debug
allocator and swap it out for the other one after testing has been conducted and only
if this really proves to be necessary.

## Memory reading & writing

Memory reading & writing is done through `MemoryBlock`s (see [this document](memory.md)).

These may or may not be owned by a process allocator. Depending on the type of allocator,
different types of blocks featuring checked or unchecked access may be provided.

Other ways to obtain memory are:

- Providing a fixed address in some way.

- Scanning the memory space of the process for a specific signature.

- Querying sections through the executable.

## Metadata

`binchew.process.Metadata` objects can be queried for running processes.

These objects feature information on paging, memory usage, process start time,
bitness, etc.
