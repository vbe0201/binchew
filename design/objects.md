# Object Model

On top of the raw memory and process abstractions, `binchew` features a
layer for defining structures inside process memory.

## Definition

dataclasses-like declarations with `Field`s representing readable units.

`Field`s will be subclasses of `property`.

## Layout calculations

`Field`s optionally take an offset into the type which will be respected
during layout calculations.

If fields do not have an offset specified, they will be assumed to follow
in order.

## Types

Types in OS memory are defined using variations of `Field`s. Each `Field`
stores size, alignment for itself. Alignment can optionally be overridden
by users.

### Primitives

The primitive integer types. Signed, unsigned, and IEEE-754 floats.

### Pointer

Pointers point to a typed value and allow reading from it or writing to it.
The exception is a pointer to the `Void` type which cannot be read or written
to.

They are different from the low-level memory pointers.

We also support shifted pointers by specifying a reference to a field in a
different object rather than the object type.

### Reference

References are pointers to Python objects.

Unlike regular pointers, accesses to those are always to the object behind it
and never to the pointer value itself.

### Strings

Both null-terminated and fixed-length need to be supported. It's raw bytes
without interpretation, decoding is always up to the user. Based on pointer.

Length is either `None`, static or another length field in the object.

### Arrays

Contiguously stored values of the same type with a fixed length. Based on pointer.

Length is either `None`, static or another length field in the object.

### Unions

Allows reinterpretation of a memory region as different types.

The size and alignment is that of the biggest specified type.

### Enums

Enums are the underlying value type and and some validation for the pre-defined values.

Can be C or C++ style.

### Objects

This might be slightly surprising, but every object is also a subclass of `Field` and
can be used as such.

The object in that case will be treated as an inline value.
