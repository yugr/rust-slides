All info about performance overhead of panics.

Panics involve stack unwinding and destructors so are definitely not free.
E.g. they complicate compiler analyses due to presence of landing pads.

Rust has `panic=abort` (similar to C++ `-fno-exceptions`)

# TODO

Does `panic=abort` avoid all overheads ?

Check if optimizations from https://www.youtube.com/watch?v=ItemByR4PRg (LICM, ADCE, etc.) are also disabled for Rust ?
