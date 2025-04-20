Compared to C++, Rust's `#[inline]` supports cross-module inlining
(function's MIR is stored in object file).

# TODO

- Measure how much perf benefit is due to cross-module inlining (by patching compiler)
