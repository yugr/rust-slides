Rust performs stack probing i.e.g verifying that we do not touch stack guard page.
This incurs certain runtime overhead (function call, loop, touching memory).

Stack probing is analog of GCC's `-fstack-check`.
Compiler emits special code to touch each allocated page in prologue to detect stack overflow.
A very good explanation of [history of this feature in Rust](https://users.rust-lang.org/t/rust-guarantees-no-segfaults-with-only-safe-code-but-it-segfaults-stack-overflow/4305/2)
is here

Implementation:
  - Rustc adds special LLVM attribute to Rust functions
  - LLVM then generates calls to `__probestack` in prologues (or `__chkstk` in Windows)
    * This is different from `-fstack-check` which uses inline loop
  - `__probestack` implemented in Rust [compiler-builtings](https://github.com/rust-lang/compiler-builtins/blob/master/compiler-builtins/src/probestack.rs)
    * Seems only amd64 is supported...

Note that panic message is not guaranteed and [in some cases](https://github.com/rust-lang/rust/issues/79935) process will crash.

# TODO

- Run benchmarks w/ probing disabled
