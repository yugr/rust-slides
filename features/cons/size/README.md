All info about large Rust binaries.

Rust binaries are known to be significantly larger than for C.
This is true for small programs but becomes even larger ones
(hundreds of MBs are not uncommon, see [upstream #66348](https://github.com/rust-lang/rust/issues/66348)).

This area is studied very well: see [min-sized-rust](https://github.com/johnthagen/min-sized-rust)
for complete guide.

There are several reasons for this:
  - release binaries are not stripped by default (for `RUST_BACKTRACE`)
    * can be worked around in Cargo.toml or just running `strip` on binary
  - remove parts of stdlib:
    * jemalloc linked in by default (statically)
      + can be turned off (in Cargo.toml ?)
    * stack unwinding code and symbolizer
      + can be disabled via `panic=abort` in Cargo.toml
  - code dup due to monomorphization (see analysis [here](https://nickb.dev/blog/the-dark-side-of-inlining-and-monomorphization/))
    * can be fixed by not-template-base hack from C++: [What’s the name of this technique for cutting down compile times from monomorphization?](https://users.rust-lang.org/t/whats-the-name-of-this-technique-for-cutting-down-compile-times-from-monomorphization/89172)
  - shared libraries are not widely used (if at all)
    * unfixable until stable ABI and binary package distributions are introduced
    * `cargo bloat` can be used to identify the most problematic dependencies
    * need to watch out for different versions of same library (see example [here](https://oknozor.github.io/blog/optimize-rust-binary-size/))

LTO and opt-level Z may also help (see [here](https://rustwasm.github.io/docs/book/reference/code-size.html)).
