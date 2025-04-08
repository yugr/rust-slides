All info about performance overhead of panics.

Panics involve stack unwinding and destructors so are definitely not free.
E.g. they complicate compiler analyses due to presence of landing pads.

Rust has `panic=abort` (similar to C++ `-fno-exceptions`)

Panicking causes significant code bloat in small functions (e.g. [here](https://www.rottedfrog.co.uk/?p=24)).

# TODO

Does `panic=abort` avoid all overheads ? I couldn't get it to do anything in [this](https://news.ycombinator.com/item?id=30867188) example.

Check if optimizations from https://www.youtube.com/watch?v=ItemByR4PRg (LICM, ADCE, etc.) are also disabled for Rust ?

Check if C++ also has same overhead due to exceptions: https://www.rottedfrog.co.uk/?p=24
  - If not, we need a slide on this
