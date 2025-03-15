All info about performance overhead of panics.

Panics involve stack unwinding and destructors so are definitely not free.
E.g. they complicate compiler analyses due to presence of landing pads.

Rust has `panic=abort` (similar to C++ `-fno-exceptions`)

# TODO

Does `panic=abort` avoid all overheads ?
