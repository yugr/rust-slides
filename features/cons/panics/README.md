All info about performance overhead of panics.

Panics involve stack unwinding and destructors so are definitely not free.
E.g. they complicate compiler analyses due to presence of landing pads.

Rust has `panic=abort` (similar to C++ `-fno-exceptions`)

Panicking causes significant code bloat in small functions (e.g. [here](https://www.rottedfrog.co.uk/?p=24)).

# Combining panics

In some cases Rust needs to perform several checks at once
(see example in [bounds-checks](../bounds-checks/README.md)).

RFC 560 explicitly allows [delayed panics](https://github.com/rust-lang/rfcs/blob/master/text/0560-integer-overflow.md#delayed-panics)
i.e. combining these checks and emitting one final panic if any of them failed.
Also [this comment](https://github.com/rust-lang/rfcs/pull/560#issuecomment-69382228):
> it should be permitted but not required to abort the process when a overflowed value would have been observed

Unfortunately for LLVM each panic is an unknown function call with distinct parameters
so this can not be done at LLVM level and there is not dedicated MIR pass for this.

As a workaround, developers need to use manual `assert!`'s (or `core::hint::unreachable_unchecked`).

# TODO

Does `panic=abort` avoid all overheads ? I couldn't get it to do anything in [this](https://news.ycombinator.com/item?id=30867188) example.

Check if optimizations from https://www.youtube.com/watch?v=ItemByR4PRg (LICM, ADCE, etc.) are also disabled for Rust ?

Check if C++ also has same overhead due to exceptions: https://www.rottedfrog.co.uk/?p=24
  - If not, we need a slide on this
