Rust performs stack probing i.e.g verifying that we do not touch stack guard page.
This incurs certain runtime overhead (function call, loop, touching memory).

Looks very similar to `-fstack-check`.

# TODO

- Run benchmarks w/ probing disabled
