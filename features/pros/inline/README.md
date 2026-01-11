Compared to C++, Rust's `#[inline]` supports some limited form of cross-crate inlining
(function's MIR is stored in object file or rlib).

# TODO

- Measure how much perf benefit is due to cross-module inlining (by patching compiler)
- Isn't this same as `inline` functions in C++ headers ?
